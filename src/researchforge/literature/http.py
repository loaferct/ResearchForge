"""Polite, cached, retrying HTTP access for literature APIs.

* Responses are cached on disk (per investigation), so a resumed or repeated
  investigation does not repeat expensive searches.
* 429 and 5xx responses are retried with ``Retry-After`` (capped) or
  exponential backoff with jitter; other 4xx responses fail immediately.
* Requests to the same host are spaced by a configurable minimum interval
  (arXiv asks for 3 seconds between API calls).
* Secret headers are never part of the cache key or the cached record.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit

import httpx

log = logging.getLogger("researchforge.http")

DEFAULT_MIN_INTERVAL = {"export.arxiv.org": 3.0, "api.github.com": 1.0, "api.semanticscholar.org": 1.0}
RETRYABLE = frozenset({408, 425, 429})
# Observed 2026-09: export.arxiv.org answers bursts of requests with an empty
# HTTP 406 that clears after a pause, i.e. it behaves as a throttle response.
RETRYABLE_BY_HOST = {"export.arxiv.org": frozenset({406})}
USER_AGENT = "ResearchForge/0.1 (+https://github.com/; research-idea investigation agent)"


class HttpError(RuntimeError):
    def __init__(self, message: str, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


@dataclass
class Response:
    status: int
    text: str
    url: str
    cached: bool
    content: bytes | None = None

    def json(self):
        return json.loads(self.text)


class CachedHttp:
    def __init__(
        self,
        cache_dir: Path | None,
        *,
        timeout_s: float = 30.0,
        max_retries: int = 4,
        max_backoff_s: float = 40.0,
        min_interval: dict[str, float] | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
        sleep=asyncio.sleep,
        shared_pacing: bool = False,
    ) -> None:
        self.cache_dir = cache_dir
        # With a cache shared by several processes (benchmark runs), pace each host across processes too.
        self.shared_pacing = shared_pacing and cache_dir is not None
        self.timeout_s = timeout_s
        self.max_retries = max_retries
        self.max_backoff_s = max_backoff_s
        self.min_interval = DEFAULT_MIN_INTERVAL if min_interval is None else min_interval
        self._transport = transport
        self._sleep = sleep
        self._last_request: dict[str, float] = {}
        self._host_locks: dict[str, asyncio.Lock] = {}
        self.stats = {"requests": 0, "cache_hits": 0, "retries": 0, "failures": 0}

    def _cache_path(self, key: str, binary: bool) -> Path | None:
        if self.cache_dir is None:
            return None
        digest = hashlib.sha256(key.encode()).hexdigest()[:40]
        return self.cache_dir / f"{digest}.{'bin' if binary else 'json'}"

    async def _pace(self, host: str) -> None:
        interval = self.min_interval.get(host, 0.0)
        if interval <= 0:
            return
        lock = self._host_locks.setdefault(host, asyncio.Lock())
        if self.shared_pacing:
            async with lock:
                await self._pace_shared(host, interval)
            return
        async with lock:
            wait = self._last_request.get(host, 0.0) + interval - time.monotonic()
            if wait > 0:
                await self._sleep(wait)
            self._last_request[host] = time.monotonic()

    async def _pace_shared(self, host: str, interval: float) -> None:
        """Cross-process pacing: a per-host file holds the last request time, guarded by a non-blocking flock."""
        import fcntl

        assert self.cache_dir is not None
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        path = self.cache_dir / f".pace-{re.sub(r'[^A-Za-z0-9.-]', '_', host)}"
        with open(path, "a+") as fh:
            while True:
                try:
                    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    await self._sleep(0.05)
            try:
                fh.seek(0)
                last = float(fh.read().strip() or 0.0)
                wait = last + interval - time.time()
                if wait > 0:
                    await self._sleep(wait)
                fh.seek(0)
                fh.truncate()
                fh.write(str(time.time()))
                fh.flush()
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    async def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        *,
        binary: bool = False,
        use_cache: bool = True,
        max_bytes: int | None = None,
    ) -> Response:
        full_url = f"{url}?{urlencode(sorted((params or {}).items()), doseq=True)}" if params else url
        cache_path = self._cache_path(full_url, binary) if use_cache else None
        if cache_path is not None and cache_path.exists():
            self.stats["cache_hits"] += 1
            if binary:
                return Response(200, "", full_url, True, cache_path.read_bytes())
            record = json.loads(cache_path.read_text(encoding="utf-8"))
            return Response(record["status"], record["text"], full_url, True)

        host = urlsplit(url).netloc
        req_headers = {"User-Agent": USER_AGENT, **(headers or {})}
        attempt = 0
        async with httpx.AsyncClient(
            timeout=self.timeout_s, follow_redirects=True, transport=self._transport
        ) as client:
            while True:
                await self._pace(host)
                self.stats["requests"] += 1
                try:
                    resp = await client.get(url, params=params, headers=req_headers)
                except (httpx.TimeoutException, httpx.TransportError) as exc:
                    resp, error = None, f"{type(exc).__name__}: {exc}"
                else:
                    error = None
                    if resp.status_code < 400:
                        if max_bytes is not None and len(resp.content) > max_bytes:
                            self.stats["failures"] += 1
                            raise HttpError(f"response from {host} exceeds {max_bytes} bytes", resp.status_code)
                        out = Response(resp.status_code, "" if binary else resp.text, full_url, False, resp.content if binary else None)
                        self._store(cache_path, out, binary)
                        return out
                    retryable = RETRYABLE | RETRYABLE_BY_HOST.get(host, frozenset())
                    if resp.status_code not in retryable and resp.status_code < 500:
                        self.stats["failures"] += 1
                        raise HttpError(f"{host} returned HTTP {resp.status_code}: {resp.text[:200]}", resp.status_code)
                    error = f"HTTP {resp.status_code}"
                if attempt >= self.max_retries:
                    self.stats["failures"] += 1
                    raise HttpError(f"{host} failed after {attempt + 1} attempts ({error})", resp.status_code if resp else None)
                delay = self._backoff(attempt, resp)
                log.info("retrying request", extra={"host": host, "attempt": attempt + 1, "delay_s": round(delay, 2), "error": error})
                self.stats["retries"] += 1
                attempt += 1
                await self._sleep(delay)

    def _backoff(self, attempt: int, resp: httpx.Response | None) -> float:
        if resp is not None:
            retry_after = resp.headers.get("Retry-After")
            if retry_after is None:
                try:
                    retry_after = resp.json().get("retryAfter")
                except (ValueError, AttributeError):
                    retry_after = None
            if retry_after is not None:
                try:
                    return min(float(retry_after), self.max_backoff_s)
                except ValueError:
                    pass
        return min(self.max_backoff_s, (2**attempt) * 1.5 + random.uniform(0, 1))

    def _store(self, path: Path | None, resp: Response, binary: bool) -> None:
        if path is None:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        if binary:
            path.write_bytes(resp.content or b"")
        else:
            record = {
                "url": resp.url,
                "status": resp.status,
                "text": resp.text,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
            }
            path.write_text(json.dumps(record), encoding="utf-8")
