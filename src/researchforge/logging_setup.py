"""Structured (JSON-lines) logging for ResearchForge processes.

The MCP server writes logs to stderr because stdout carries the MCP protocol.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

_RESERVED = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key not in _RESERVED and not key.startswith("_"):
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure(level: str = "INFO", json_format: bool = True) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter() if json_format else logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger("researchforge")
    root.handlers[:] = [handler]
    root.setLevel(level.upper())
    root.propagate = False
