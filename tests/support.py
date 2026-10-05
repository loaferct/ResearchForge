"""Test support: synthetic literature API responses and a scripted agent runtime.

All papers here are synthetic test data ("Test ..." titles, 9999.xxxxx ids).
They exercise the parsing, merging and evidence code paths without network.
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path

import httpx

from researchforge.config import Settings
from researchforge.literature.http import CachedHttp
from researchforge.runtime import EventSink, RunOutcome
from researchforge.toolkit import ResearchToolkit
from researchforge.workspace import Workspace

ABSTRACTS = {
    "9999.00001": "We propose TestEvict, a KV cache eviction policy that keeps heavy-hitter tokens. TestEvict reduces KV cache memory by 5x while preserving accuracy on long-context benchmarks under a static cache budget.",
    "9999.00002": "TestSink retains attention sink tokens and a recent window, enabling streaming inference with a fixed KV cache budget across all requests.",
    "9999.00003": "TestSnap selects important KV positions using an observation window at the end of the prompt. The cache budget is fixed per layer and shared by every request.",
    "9999.00004": "TestPaged manages KV cache memory in pages to reduce fragmentation in LLM serving systems, improving throughput under heterogeneous request workloads.",
    "9999.00005": "TestQuant quantizes the KV cache to 2 bits per value, reducing memory while accuracy degrades on retrieval-heavy tasks.",
    "9999.00006": "TestPyramid allocates different KV cache budgets to different layers, but the allocation is fixed before inference and does not adapt to individual requests.",
    "9999.00007": "TestAdaptive adapts compression per attention head based on profiling of head behaviour for each prompt.",
    "9999.00008": "TestQuery performs query-aware selection of KV cache pages for long-context decoding.",
    "9999.00009": "TestBench is a benchmark for long-context evaluation of cache compression methods under matched memory budgets.",
}
TITLES = {
    "9999.00001": "TestEvict: Heavy-Hitter KV Cache Eviction",
    "9999.00002": "TestSink: Streaming Inference with Attention Sinks",
    "9999.00003": "TestSnap: Observation-Window KV Selection",
    "9999.00004": "TestPaged: Paged KV Cache Memory Management for Serving",
    "9999.00005": "TestQuant: Two-Bit KV Cache Quantization",
    "9999.00006": "TestPyramid: Layer-Wise KV Cache Budgets",
    "9999.00007": "TestAdaptive: Head-Adaptive KV Cache Compression",
    "9999.00008": "TestQuery: Query-Aware KV Page Selection",
    "9999.00009": "TestBench: Evaluating KV Cache Compression Under Matched Budgets",
}


def arxiv_feed(ids: list[str]) -> str:
    entries = []
    for i in ids:
        entries.append(f"""
  <entry>
    <id>http://arxiv.org/abs/{i}v2</id>
    <published>2024-0{int(i[-1]) % 9 + 1}-15T00:00:00Z</published>
    <title>{TITLES[i]}</title>
    <summary>{ABSTRACTS[i]}</summary>
    <author><name>Alice Tester</name></author>
    <author><name>Bob Example</name></author>
    <arxiv:comment xmlns:arxiv="http://arxiv.org/schemas/atom">Code: https://github.com/test-org/{TITLES[i].split(':')[0].lower()}</arxiv:comment>
    <link href="http://arxiv.org/abs/{i}v2" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/{i}v2" rel="related" type="application/pdf"/>
  </entry>""")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">{''.join(entries)}
</feed>"""


def inverted_index(text: str) -> dict:
    idx: dict[str, list[int]] = {}
    for pos, word in enumerate(text.split()):
        idx.setdefault(word, []).append(pos)
    return idx


def openalex_work(i: str, n: int) -> dict:
    return {
        "id": f"https://openalex.org/W90000{n}",
        "doi": f"https://doi.org/10.48550/arxiv.{i}",
        "display_name": TITLES[i],
        "publication_year": 2024,
        "authorships": [{"author": {"display_name": "Alice Tester"}}, {"author": {"display_name": "Bob Example"}}],
        "primary_location": {"landing_page_url": f"https://arxiv.org/abs/{i}", "source": {"display_name": "Test Conference on Systems"}},
        "locations": [{"landing_page_url": f"https://arxiv.org/abs/{i}"}],
        "best_oa_location": {"pdf_url": f"https://arxiv.org/pdf/{i}"},
        "cited_by_count": 100 + n,
        "abstract_inverted_index": inverted_index(ABSTRACTS[i]),
    }


def s2_paper(i: str) -> dict:
    return {
        "paperId": f"s2{i.replace('.', '')}",
        "title": TITLES[i],
        "abstract": ABSTRACTS[i],
        "year": 2024,
        "venue": "TestConf",
        "authors": [{"name": "Alice Tester"}],
        "citationCount": 42,
        "externalIds": {"ArXiv": i},
        "url": f"https://www.semanticscholar.org/paper/s2{i}",
        "openAccessPdf": None,
    }


def crossref_item(n: int) -> dict:
    return {
        "DOI": f"10.9999/test.{n}",
        "title": [f"Test Journal Article on Cache Budgets {n}"],
        "author": [{"given": "Carol", "family": "Journal"}],
        "container-title": ["Journal of Test Systems"],
        "issued": {"date-parts": [[2023, 5]]},
        "is-referenced-by-count": 7,
        "abstract": "<jats:p>We study <jats:italic>static</jats:italic> KV cache budgets in serving.</jats:p>",
        "URL": f"https://doi.org/10.9999/test.{n}",
    }


class FakeApis:
    """Routes literature API requests to synthetic responses; records calls."""

    def __init__(self, fail: set[str] | None = None) -> None:
        self.calls: list[str] = []
        self.fail = fail or set()

    def handler(self, request: httpx.Request) -> httpx.Response:
        host = request.url.host
        self.calls.append(str(request.url))
        if host in self.fail:
            return httpx.Response(503, text="unavailable")
        q = request.url.params
        if host == "export.arxiv.org":
            query = q.get("search_query", "")
            ids = [i for i in TITLES if any(t.split(":")[1] in ABSTRACTS[i].lower() or t.split(":")[1] in TITLES[i].lower() for t in query.split(" AND "))] or list(TITLES)[:3]
            return httpx.Response(200, text=arxiv_feed(ids[:5]))
        if host == "api.openalex.org":
            return httpx.Response(200, json={"results": [openalex_work(i, n) for n, i in enumerate(list(TITLES)[2:8])]})
        if host == "api.semanticscholar.org":
            return httpx.Response(200, json={"data": [s2_paper(i) for i in list(TITLES)[4:9]]})
        if host == "api.crossref.org":
            return httpx.Response(200, json={"message": {"items": [crossref_item(n) for n in range(2)]}})
        if host == "api.github.com":
            path = request.url.path
            if path.startswith("/search/repositories"):
                return httpx.Response(200, json={"items": [{"full_name": "test-org/testevict", "html_url": "https://github.com/test-org/testevict", "stargazers_count": 10, "description": "test", "language": "Python", "topics": [], "license": {"spdx_id": "MIT"}, "pushed_at": "2025-01-01T00:00:00Z", "archived": False}]})
            if path.endswith("/languages"):
                return httpx.Response(200, json={"Python": 1000})
            if path.endswith("/contents/"):
                return httpx.Response(200, json=[{"name": "requirements.txt"}, {"name": "README.md"}, {"name": "scripts"}])
            if path.endswith("/readme"):
                import base64
                readme = "# TestEvict\nPaper: https://arxiv.org/abs/9999.00001\nEvaluated on LongBench with Llama models.\n```\npip install -r requirements.txt\npython run.py\n```"
                return httpx.Response(200, json={"encoding": "base64", "content": base64.b64encode(readme.encode()).decode()})
            return httpx.Response(200, json={"full_name": "test-org/testevict", "html_url": "https://github.com/test-org/testevict", "stargazers_count": 10, "license": {"spdx_id": "MIT"}})
        return httpx.Response(404, text="not found")

    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self.handler)


async def _no_sleep(_s: float) -> None:
    return None


def make_toolkit(ws: Workspace, settings: Settings, apis: FakeApis | None = None) -> ResearchToolkit:
    apis = apis or FakeApis()
    http = CachedHttp(ws.root / "cache" / "http", transport=apis.transport(), min_interval={}, sleep=_no_sleep, max_retries=1)
    return ResearchToolkit(ws, settings, http=http, env={})


def small_settings(tmp: Path) -> Settings:
    return Settings.model_validate({
        "projects_dir": str(tmp / "projects"),
        "investigation": {"min_papers": 5, "min_queries": 2, "papers_to_analyze": 3, "max_phase_attempts": 2},
        "dsh": {"home": str(tmp / "dshhome")},
    })


# ---------------------------------------------------------------- scripted agent


ACTION_RE = re.compile(r"^# ResearchForge step: (\w+)", re.M)
FOCUS_ID_RE = re.compile(r"investigates uncertainty (U\d+)")
FOCUS_RE = re.compile(r"^Focus: (.+)$", re.M)


def parse_prompt(prompt: str) -> tuple[str, str | None, str | None]:
    """Return (action, focus text, focused uncertainty id) from a loop prompt."""
    action = ACTION_RE.search(prompt).group(1)
    focus = FOCUS_RE.search(prompt)
    fid = FOCUS_ID_RE.search(prompt)
    return action, focus.group(1) if focus else None, fid.group(1) if fid else None


CHALLENGE_VERDICTS: dict[str, str] = {}  # target_ref -> verdict; tests set this to script contradicting evidence


def scripted_verdict(tk: ResearchToolkit, focus_id: str | None) -> str:
    u = tk.ws.uncertainty(focus_id or "")
    return CHALLENGE_VERDICTS.get(u.target_ref or "", "holds") if u else "holds"


def scripted_action(tk: ResearchToolkit, action: str, focus: str | None, focus_id: str | None) -> int:
    """Do what a competent agent would record for ``action``. Returns tool-call count."""
    run = lambda coro: asyncio.run(coro)  # noqa: E731
    calls = 0
    if action == "FORMALIZE":
        tk.record_idea_analysis(
            problem="KV cache memory limits long-context LLM inference",
            target_domain="LLM inference systems",
            proposed_method="request-aware dynamic KV cache budgets",
            hypothesis="Per-request budgets reduce memory at equal accuracy compared with static budgets",
            research_question="Does request-aware KV cache budgeting reduce peak memory at matched accuracy versus static-budget eviction?",
            expected_contribution="an adaptive budgeting policy",
            assumptions=["requests differ in how much context they need"],
            variables={"independent": ["budget policy"], "dependent": ["peak memory", "accuracy"], "controls": ["model", "dataset"]},
            ambiguities=[{"question": "which metric?", "resolution": "peak memory and task accuracy", "resolved_by": "assumption"}],
            keywords=["kv", "cache", "eviction", "budget", "memory"],
            search_queries=["kv cache eviction", "adaptive kv cache budget", "kv cache compression serving"],
        )
        calls = 1
    elif action == "PLAN":
        tk.record_investigation_plan(
            questions=["Which existing methods are closest?", "Is request-aware budgeting known under other terminology?"],
            search_topics=["kv cache eviction", "adaptive kv cache budget"],
            comparison_targets=["static-budget eviction"],
        )
        tk.record_uncertainty(question="Is request-aware budgeting already explored under other terminology?", importance="high", category="novelty", next_action="SEARCH", possible_actions=["COMPARE"])
        tk.record_uncertainty(question="Which baselines give a budget-matched comparison?", importance="medium", category="evaluation", next_action="COMPARE")
        calls = 3
    elif action == "SEARCH":
        run(tk.search_papers(focus.split(": ", 1)[-1] if focus_id else (focus or "kv cache eviction")))
        calls = 1
        if focus_id:
            tk.update_uncertainty(id=focus_id, status="resolved", resolution="Searched alternative terminology; retrieved work uses static budgets.", paper_ids=["arxiv:9999.00003"])
            calls += 1
    elif action == "READ":
        ids = [p["id"] for p in tk.list_papers(only_unanalyzed=True)["papers"]][: tk.settings.investigation.papers_to_analyze]
        for pid in ids:
            tk.record_paper_analysis(
                paper_id=pid, relevance_tier="high", problem="KV memory", method="eviction under a static budget",
                limitations=["static budget"], relation_to_idea={"problem_overlap": 0.8, "method_overlap": 0.5, "evaluation_overlap": 0.6, "conceptual_difference": "static vs per-request budgets", "basis": "abstract"},
            )
            calls += 1
    elif action == "SYNTHESIZE":
        ids = [a.paper_id for a in tk.ws.analyses()]
        tk.record_landscape(
            field_name="KV cache optimization",
            categories=[{"name": "Eviction", "paper_ids": ids[:2]}, {"name": "Static budgets", "parent": "Eviction", "paper_ids": ids[2:3]}, {"name": "Quantization"}],
            idea_position="Dynamic/request-aware budgets within Eviction",
            repeated_limitations=[{"description": "budgets are fixed across requests", "paper_ids": ids[:2]}],
        )
        calls = 1
    elif action == "CRITIQUE":
        c1 = tk.record_claim(
            statement="Existing eviction work evaluates under a static cache budget",
            kind="evidence", confidence="medium",
            evidence=[{"paper_id": "arxiv:9999.00001", "location": "abstract", "quote": "preserving accuracy on long-context benchmarks under a static cache budget", "support": "direct"}],
        )
        tk.record_claim(statement="Per-request budgets are not evaluated in the closest work", kind="inference", confidence="low",
                        evidence=[{"paper_id": "arxiv:9999.00003", "support": "indirect"}])
        tk.record_critique(
            strongest_for="requests differ", strongest_against="gains may vanish with matched compute",
            most_important_unresolved_question="does budget prediction cost offset savings?",
            most_dangerous_confounder="unmatched memory budgets", closest_paper_ids=["arxiv:9999.00001"],
            closest_work_explanation="same eviction mechanism", potential_contribution="request-level adaptation",
            overlap_summary="eviction policy overlaps", distinction_summary="budget varies per request",
            novelty=[{"question": "same idea exists?", "finding": "not found in searched literature", "severity": "moderate", "claim_ids": [c1["claim_id"]], "paper_ids": ["arxiv:9999.00001"]}],
            overall_status="promising_needs_validation", status_rationale="overlap exists but distinction is testable",
        )
        tk.record_uncertainty(question="Could the expected gain come from unmatched memory budgets?", importance="high", category="confounder", next_action="VERIFY", paper_ids=["arxiv:9999.00009"])
        calls = 4
    elif action in ("COMPARE", "VERIFY"):
        tk.record_claim(statement=f"{action.title()} finding: the closest work fixes the budget per layer",
                        kind="evidence", confidence="medium",
                        evidence=[{"paper_id": "arxiv:9999.00003", "quote": "The cache budget is fixed per layer and shared by every request", "support": "direct"}])
        calls = 1
        if focus_id:
            tk.update_uncertainty(id=focus_id, status="resolved", resolution="The text confirms budgets are fixed; a matched-memory control is required.", paper_ids=["arxiv:9999.00003"])
            calls += 1
    elif action in ("CHALLENGE", "INVESTIGATE_GAP"):
        # A real agent searches for contradicting work; the synthetic literature contains none, so the conclusion holds.
        run(tk.search_papers("contradicting evidence " + (focus or "")[:60]))
        tk.record_challenge_result(uncertainty_id=focus_id, verdict=scripted_verdict(tk, focus_id), rationale="Searched for work that solves the problem or contradicts the conclusion.",
                                   supporting_paper_ids=["arxiv:9999.00003"], contradicting_paper_ids=["arxiv:9999.00006"] if scripted_verdict(tk, focus_id) != "holds" else [])
        calls = 2
    elif action == "REFINE":
        if not tk.ws.gaps():
            tk.record_gap(
                gap="Budgets are static across heterogeneous requests",
                evidence=[{"paper_id": "arxiv:9999.00003", "quote": "The cache budget is fixed per layer and shared by every request", "support": "direct"}],
                related_paper_ids=["arxiv:9999.00001"], why_unaddressed="all evaluated methods fix the budget",
                research_question="Does per-request budgeting improve the accuracy/memory tradeoff?",
                potential_experiment="compare against static budgets at matched average memory", confidence="medium",
                verification_required="search 2025-2026 literature",
            )
        for title in ("Budget predictor", "Rate-matched evaluation")[len(tk.ws.modifications()):]:
            tk.record_modification(
                title=title, description="d", why_differs="w", technical_mechanism="t", expected_benefit="b", potential_novelty="p",
                implementation_difficulty="moderate", implementation_difficulty_basis="needs a predictor",
                experimental_difficulty="low", experimental_difficulty_basis="public benchmarks",
                main_risk="overhead", required_baselines=["static eviction"], related_paper_ids=["arxiv:9999.00001"],
                addresses_gap_ids=["G001"], recommended=title == "Budget predictor",
            )
        if focus_id:
            u = tk.ws.uncertainty(focus_id)
            tk.record_direction(direction="Request-aware allocation restricted to heterogeneous multi-tenant workloads",
                                hypothesis="Per-request budgets help only when request context needs differ widely",
                                rationale=f"Contradicting evidence narrowed the claim ({focus_id}).", change_type="REFINE_SCOPE",
                                confidence="low", paper_ids=(u.paper_ids if u else [])[:2], uncertainty_ids=[focus_id])
            tk.update_uncertainty(id=focus_id, status="resolved", resolution="Direction narrowed to where the distinction survives.")
            return 2
        tk.record_direction(direction="Request-aware budget allocation under heterogeneous workloads", hypothesis="Per-request budgets beat static budgets at matched average memory",
                            rationale="Overlap with eviction is strong; the budget policy is the remaining distinction.", modification_id="M001",
                            change_type="REFINE_SCOPE", paper_ids=["arxiv:9999.00003"])
        calls = 4
    elif action == "PLAN_EXPERIMENT":
        tk.record_experiment_plan(
            title="Request-aware vs static budgets", research_question="rq", hypothesis="h", proposed_method="m",
            baselines=["full cache", "static eviction"], datasets=["LongBench"], metrics=["peak memory", "accuracy"],
            ablations=["budget size"], controls=["same model"], failure_conditions=["no memory reduction at matched accuracy"],
            hardware="1 GPU", software_environment="PyTorch", reproducibility_notes="seeds fixed", expected_outcomes="lower memory",
            confounders_addressed=["matched average memory"], related_modification_id="M001",
        )
        calls = 1
    elif action == "ANALYZE_RESULTS":
        plan_id = focus
        a = next(x for x in tk.ws.experiment_analyses() if x.plan_id == plan_id)
        verdict = "SUPPORTED" if a.status == "PASSED" else "INCONCLUSIVE"
        tk.record_hypothesis_evaluation(plan_id=plan_id, verdict=verdict, rationale=f"verification status {a.status}")
        calls = 1
    return calls


class ScriptedRuntime:
    """Stands in for dsh in tests: reads each loop prompt and records what an agent would."""

    name = "scripted"

    def __init__(self, settings: Settings, apis: FakeApis | None = None, skip: set[str] | None = None,
                 fail_action: str | None = None, fail_times: int = 10**6) -> None:
        self.settings, self.apis = settings, apis or FakeApis()
        self.skip = skip or set()
        self.fail_action, self.fail_times = fail_action, fail_times
        self.calls: list[tuple[str, str | None, str | None]] = []  # (action, focus_id, session_id)
        self.prompts: list[str] = []

    @property
    def actions(self) -> list[str]:
        return [a for a, _, _ in self.calls]

    def run_phase(self, ws: Workspace, prompt: str, *, phase: str, session_id: str | None, on_event: EventSink) -> RunOutcome:
        action, focus, focus_id = parse_prompt(prompt)
        self.calls.append((action, focus_id, session_id))
        self.prompts.append(prompt)
        if action == self.fail_action and self.fail_times > 0:
            self.fail_times -= 1
            return RunOutcome(ok=False, session_id=None, error="MISSING_CREDENTIAL: no API key", exit_code=1)
        calls = 0
        if action not in self.skip:
            calls = scripted_action(make_toolkit(ws, self.settings, self.apis), action, focus, focus_id)
            for _ in range(calls):
                on_event("tool_call", {"tool": f"step_{action.lower()}", "input": "{}"})
        return RunOutcome(ok=True, session_id=session_id or "session-test", final_text="done", finish_reason="completed", exit_code=0, tool_calls=calls or 1)


def load_json(path: Path):
    return json.loads(path.read_text())
