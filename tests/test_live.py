"""Live checks against the real literature APIs. Opt in with: pytest -m live

These make a handful of real requests; anonymous access is rate-limited, so a
source may report status "error" (e.g. HTTP 429). The test requires only that
at least one source answers and that every returned record carries provenance.
"""

import asyncio

import pytest

from researchforge.toolkit import ResearchToolkit

pytestmark = pytest.mark.live


def test_live_search_returns_provenanced_papers(ws, settings):
    tk = ResearchToolkit(ws, settings)
    res = asyncio.run(tk.search_papers("KV cache eviction large language model inference", limit_per_source=5))
    statuses = {s["source"]: s["status"] for s in res["sources"]}
    print(statuses)
    assert "ok" in statuses.values(), res["sources"]
    assert res["results"]
    for r in res["results"]:
        paper = ws.paper(r["id"])
        assert paper.title and paper.sources and paper.retrieved_at
        if paper.citation_count is not None:
            assert paper.citation_count_source in paper.sources
    again = asyncio.run(tk.search_papers("KV cache eviction large language model inference"))
    assert again["repeated"] is True
