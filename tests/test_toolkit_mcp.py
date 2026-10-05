import asyncio
import json

import pytest

from support import FakeApis, make_toolkit

from mcp.client.client import Client
from researchforge.mcp_server import build_server
from researchforge.toolkit import ToolError


def run(coro):
    return asyncio.run(coro)


def test_search_merges_sources_stores_provenance_and_dedupes_queries(tk, apis):
    res = run(tk.search_papers("kv cache eviction"))
    assert {s["source"]: s["status"] for s in res["sources"]} == {"arxiv": "ok", "openalex": "ok", "semantic_scholar": "ok", "crossref": "ok"}
    ids = {r["id"] for r in res["results"]}
    assert "arxiv:9999.00005" in ids and "doi:10.9999/test.1" in ids
    stored = tk.ws.paper("arxiv:9999.00005")
    assert set(stored.sources) >= {"openalex", "semantic_scholar"}
    assert stored.queries == ["kv cache eviction"]
    n_calls = len(apis.calls)
    again = run(tk.search_papers("eviction cache KV"))  # same terms, different order
    assert again["repeated"] is True and len(apis.calls) == n_calls
    assert len(tk.ws.searches()) == 1


def test_search_reports_failed_source_without_failing(ws, settings):
    tk = make_toolkit(ws, settings, FakeApis(fail={"api.semanticscholar.org"}))
    res = run(tk.search_papers("kv cache eviction"))
    status = {s["source"]: s for s in res["sources"]}
    assert status["semantic_scholar"]["status"] == "error"
    assert status["arxiv"]["status"] == "ok" and res["results"]


def test_record_validations(tk):
    run(tk.search_papers("kv cache eviction"))
    with pytest.raises(ToolError, match="unknown paper id"):
        tk.record_paper_analysis(paper_id="arxiv:0000.1", relevance_tier="high", problem="p", method="m", relation_to_idea={"problem_overlap": 1, "method_overlap": 1, "evaluation_overlap": 1, "conceptual_difference": "c"})
    with pytest.raises(ToolError, match="invalid PaperAnalysis"):
        tk.record_paper_analysis(paper_id="arxiv:9999.00001", relevance_tier="high", problem="p", method="m", relation_to_idea={"problem_overlap": 2, "method_overlap": 1, "evaluation_overlap": 1, "conceptual_difference": "c"})
    with pytest.raises(ToolError, match="full_text"):
        tk.record_paper_analysis(paper_id="arxiv:9999.00001", relevance_tier="high", problem="p", method="m", analyzed_from="full_text", relation_to_idea={"problem_overlap": 1, "method_overlap": 1, "evaluation_overlap": 1, "conceptual_difference": "c"})
    with pytest.raises(ToolError, match="unknown parent"):
        tk.record_landscape(field_name="f", idea_position="x", categories=[{"name": "A", "parent": "Nope"}])
    with pytest.raises(ToolError, match="never retrieved"):
        tk.record_landscape(field_name="f", idea_position="x", categories=[{"name": "A", "paper_ids": ["arxiv:fake"]}])
    with pytest.raises(ToolError, match="unknown claim ids"):
        tk.record_critique(strongest_for="a", strongest_against="b", most_important_unresolved_question="c", most_dangerous_confounder="d", closest_paper_ids=["arxiv:9999.00001"], closest_work_explanation="e", potential_contribution="f", overlap_summary="g", distinction_summary="h", overall_status="insufficient_evidence", status_rationale="i", novelty=[{"question": "q", "finding": "f", "severity": "low", "claim_ids": ["C999"]}])
    with pytest.raises(ToolError, match="experimental claims"):
        tk.record_claim(statement="s", kind="experimental", confidence="low")
    with pytest.raises(ToolError, match="cite at least one retrieved paper|paper_id or an experiment_run_id"):
        tk.record_gap(gap="g", evidence=[{"support": "weak"}], why_unaddressed="w", research_question="r", potential_experiment="p", confidence="low")


def test_modification_limit_and_plan_approval_status(tk, settings):
    run(tk.search_papers("kv cache eviction"))
    base = dict(description="d", why_differs="w", technical_mechanism="t", expected_benefit="b", potential_novelty="p", implementation_difficulty="low", implementation_difficulty_basis="x", experimental_difficulty="low", experimental_difficulty_basis="y", main_risk="r")
    for i in range(settings.investigation.max_modifications):
        tk.record_modification(title=f"m{i}", **base)
    with pytest.raises(ToolError, match="maximum"):
        tk.record_modification(title="too many", **base)
    assert tk.record_modification(id="M001", title="revised", **base)["modification_id"] == "M001"
    assert tk.ws.modifications()[0].title == "revised"

    plan = dict(title="t", research_question="q", hypothesis="h", proposed_method="m", baselines=["b"], metrics=["acc"])
    assert tk.record_experiment_plan(**plan)["status"] == "planned"
    with pytest.raises(ToolError, match="baseline"):
        tk.record_experiment_plan(**plan, execution={"arms": [{"name": "m", "role": "method", "command": "python run.py"}]})
    res = tk.record_experiment_plan(**plan, execution={"arms": [{"name": "b", "role": "baseline", "command": "python run.py"}]})
    assert res["status"] == "awaiting_approval" and "approval" in res["note"]


def test_state_digest_lists_outstanding_requirements(tk):
    state = tk.get_research_state()
    assert state["idea_analysis"] is None
    assert "formalize" in state["outstanding_requirements"]
    assert "experiments" in state["outstanding_requirements"]


def test_github_inspection_links_paper(tk):
    run(tk.search_papers("kv cache eviction"))
    res = run(tk.inspect_repository("https://github.com/test-org/testevict", paper_id="arxiv:9999.00001"))
    repo = res["repository"]
    assert "LongBench" in repo["benchmarks_mentioned"] and "Llama" in repo["models_mentioned"]
    assert "9999.00001" in repo["mentioned_arxiv_ids"]
    assert any("requirements.txt" in s for s in repo["reproducibility_signals"])
    assert "https://github.com/test-org/testevict" in tk.ws.paper("arxiv:9999.00001").code_urls


def test_mcp_server_exposes_tools_with_flat_schemas_and_errors(tk):
    async def main():
        async with Client(build_server(tk)) as c:
            tools = {t.name: t for t in (await c.list_tools()).tools}
            assert {"search_papers", "record_claim", "record_idea_analysis", "record_experiment_plan", "record_no_gap"} <= set(tools)
            schema = tools["record_idea_analysis"].input_schema
            assert "search_queries" in schema["properties"] and "recorded_at" not in schema["properties"]
            assert "raw_idea" not in schema["properties"]
            assert tools["search_papers"].annotations.read_only_hint is True

            r = await c.call_tool("search_papers", {"query": "kv cache eviction"})
            assert not r.is_error
            payload = json.loads(r.content[0].text)
            assert payload["results"]

            r = await c.call_tool("record_claim", {"statement": "x", "kind": "evidence", "confidence": "low", "evidence": [{"paper_id": "arxiv:nope", "support": "direct"}]})
            assert r.is_error and "never retrieved" in r.content[0].text

            r = await c.call_tool("record_claim", {"statement": "Eviction is evaluated under a static budget", "kind": "evidence", "confidence": "medium",
                                                   "evidence": [{"paper_id": "arxiv:9999.00001", "quote": "under a static cache budget", "support": "direct"}]})
            assert not r.is_error, r.content[0].text
            assert json.loads(r.content[0].text)["claim_id"] == "C001"

    asyncio.run(main())
