import asyncio

import httpx
import pytest

from support import TITLES, arxiv_feed, crossref_item, openalex_work, s2_paper

from researchforge.literature.http import CachedHttp, HttpError
from researchforge.literature.merge import dedupe, merge_into, relevance
from researchforge.literature.sources import (
    ArxivClient,
    CrossrefClient,
    OpenAlexClient,
    SemanticScholarClient,
    arxiv_id_from_url,
    github_urls,
    normalize_doi,
    query_terms,
)


def test_arxiv_parse_strips_version_and_extracts_code_links():
    papers = ArxivClient.parse(arxiv_feed(["9999.00001", "9999.00002"]))
    assert [p.id for p in papers] == ["arxiv:9999.00001", "arxiv:9999.00002"]
    p = papers[0]
    assert p.title == TITLES["9999.00001"]
    assert p.authors == ["Alice Tester", "Bob Example"]
    assert p.venue == "arXiv (preprint)"
    assert p.url == "https://arxiv.org/abs/9999.00001"
    assert p.code_urls == ["https://github.com/test-org/testevict"]
    assert p.citation_count is None  # arXiv reports none; never invented


def test_openalex_reconstructs_abstract_and_finds_arxiv_id():
    p = OpenAlexClient.parse_work(openalex_work("9999.00003", 3))
    assert p.id == "arxiv:9999.00003"
    assert p.abstract.startswith("TestSnap selects important KV positions")
    assert p.citation_count == 103 and p.citation_count_source == "openalex"
    assert p.venue == "Test Conference on Systems"
    assert p.openalex_id == "W900003"


def test_semantic_scholar_and_crossref_parse():
    s = SemanticScholarClient.parse(s2_paper("9999.00005"))
    assert s.id == "arxiv:9999.00005" and s.citation_count_source == "semantic_scholar"
    c = CrossrefClient.parse(crossref_item(1))
    assert c.id == "doi:10.9999/test.1"
    assert c.abstract == "We study static KV cache budgets in serving."
    assert c.year == 2023 and c.venue == "Journal of Test Systems"


def test_helpers():
    assert arxiv_id_from_url("https://arxiv.org/pdf/2306.14048v3") == "2306.14048"
    assert normalize_doi("https://doi.org/10.1/ABC") == "10.1/abc"
    assert github_urls("see https://github.com/a/b.git, and https://github.com/a/b.") == ["https://github.com/a/b"]
    assert query_terms("How does the KV-cache eviction work?") == ["kv-cache", "eviction", "work"]


def test_dedupe_merges_sources_and_keeps_citation_provenance():
    a = ArxivClient.parse(arxiv_feed(["9999.00005"]))[0]
    s = SemanticScholarClient.parse(s2_paper("9999.00005"))
    merged = dedupe([a, s])
    assert len(merged) == 1
    m = merged[0]
    assert m.sources == ["arxiv", "semantic_scholar"]
    assert m.citation_count == 42 and m.citation_count_source == "semantic_scholar"
    assert m.venue == "TestConf"  # a real venue replaces the preprint placeholder


def test_merge_keep_id_preserves_identity():
    c = CrossrefClient.parse(crossref_item(1))
    other = c.model_copy(update={"arxiv_id": "9999.12345", "id": "arxiv:9999.12345"})
    assert merge_into(c, other, keep_id=True).id == "doi:10.9999/test.1"
    assert merge_into(c, other).id == "arxiv:9999.12345"


def test_relevance_is_bounded_heuristic():
    p = ArxivClient.parse(arxiv_feed(["9999.00001"]))[0]
    assert relevance(p, ["kv", "cache", "eviction"]) == 1.0
    assert relevance(p, ["quantum", "chemistry"]) == 0.0


class Clock:
    def __init__(self):
        self.slept = []

    async def sleep(self, s):
        self.slept.append(s)


def test_http_retries_429_with_retry_after_then_caches(tmp_path):
    calls = []

    def handler(req):
        calls.append(req)
        if len(calls) == 1:
            return httpx.Response(429, headers={"Retry-After": "7"}, text="slow down")
        return httpx.Response(200, text="ok")

    clock = Clock()
    http = CachedHttp(tmp_path, transport=httpx.MockTransport(handler), min_interval={}, sleep=clock.sleep)
    r = asyncio.run(http.get("https://api.example.org/x", {"q": "a"}))
    assert r.text == "ok" and not r.cached and clock.slept == [7.0]
    r2 = asyncio.run(http.get("https://api.example.org/x", {"q": "a"}))
    assert r2.cached and len(calls) == 2
    assert http.stats["retries"] == 1 and http.stats["cache_hits"] == 1


def test_http_non_retryable_and_exhausted(tmp_path):
    http = CachedHttp(None, transport=httpx.MockTransport(lambda r: httpx.Response(404)), min_interval={}, sleep=Clock().sleep)
    with pytest.raises(HttpError) as e:
        asyncio.run(http.get("https://api.example.org/x"))
    assert e.value.status == 404
    http = CachedHttp(None, transport=httpx.MockTransport(lambda r: httpx.Response(503)), min_interval={}, sleep=Clock().sleep, max_retries=2)
    with pytest.raises(HttpError, match="after 3 attempts"):
        asyncio.run(http.get("https://api.example.org/x"))


def test_http_arxiv_406_is_treated_as_throttling():
    responses = iter([httpx.Response(406), httpx.Response(200, text="<feed/>")])
    clock = Clock()
    http = CachedHttp(None, transport=httpx.MockTransport(lambda r: next(responses)), min_interval={}, sleep=clock.sleep)
    assert asyncio.run(http.get("https://export.arxiv.org/api/query")).text == "<feed/>"
    assert len(clock.slept) == 1
    other = CachedHttp(None, transport=httpx.MockTransport(lambda r: httpx.Response(406)), min_interval={}, sleep=Clock().sleep)
    with pytest.raises(HttpError):
        asyncio.run(other.get("https://api.example.org/x"))


def test_http_secret_headers_not_in_cache_key(tmp_path):
    http = CachedHttp(tmp_path, transport=httpx.MockTransport(lambda r: httpx.Response(200, text="x")), min_interval={})
    asyncio.run(http.get("https://api.example.org/y", headers={"x-api-key": "secret-1"}))
    r = asyncio.run(http.get("https://api.example.org/y", headers={"x-api-key": "secret-2"}))
    assert r.cached
    assert all("secret" not in p.read_text() for p in tmp_path.iterdir())
