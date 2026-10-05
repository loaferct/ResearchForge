"""End-to-end: real DeepSeek Harness + real ResearchForge MCP server + scripted model.

Runs the actual orchestrator with the actual ``dsh --profile headless`` runtime.
The model is replaced by a scripted OpenAI-compatible server configured as a
custom ``llm-pi-ai`` endpoint, exactly as a self-hosted open model would be.
This verifies the integration path: overlay composition, MCP server launch by
dsh, tool naming, argument transport, error propagation back to the model,
session resumption across phases, and workspace persistence.

Opt in with:  pytest -m e2e
Requires Node.js >= 22.19 (npx downloads dsh on first use) or RF_E2E_DSH_COMMAND.
"""

from __future__ import annotations

import json
import os
import shutil

import pytest

from support import ABSTRACTS, TITLES
from e2e.scripted_llm import ScriptedLLM

from researchforge.config import DEFAULT_DSH_VERSION, Settings
from researchforge.orchestrator import investigate
from researchforge.runtime.dsh import DshHeadlessRuntime
from researchforge.schemas import Paper, SearchRecord, SourceStatus
from researchforge.workspace import Workspace

pytestmark = pytest.mark.e2e

IDS = [f"arxiv:{i}" for i in TITLES]
OVERLAP = {"problem_overlap": 0.8, "method_overlap": 0.5, "evaluation_overlap": 0.6, "conceptual_difference": "static budget vs per-request budget", "basis": "abstract"}
MOD = {"description": "d", "why_differs": "w", "technical_mechanism": "t", "expected_benefit": "b", "potential_novelty": "possible, needs verification",
       "implementation_difficulty_basis": "needs a predictor", "experimental_difficulty": "low", "experimental_difficulty_basis": "public benchmarks",
       "main_risk": "predictor overhead", "required_baselines": ["static eviction"], "related_paper_ids": [IDS[0]]}

RESOLVE = ("update_uncertainty", {"id": "__FOCUS__", "status": "resolved", "resolution": "The full text confirms the budget is fixed per layer.", "paper_ids": [IDS[2]]})
FIXED_BUDGET_CLAIM = ("record_claim", {"statement": "The closest work shares one budget across requests", "kind": "evidence", "confidence": "medium",
                                       "evidence": [{"paper_id": IDS[2], "quote": "The cache budget is fixed per layer and shared by every request", "support": "direct"}]})

SCRIPT = {
    "FORMALIZE": [
        ("get_research_state", {}),
        ("record_idea_analysis", {
            "problem": "KV cache memory limits long-context inference", "target_domain": "LLM inference",
            "proposed_method": "request-aware dynamic KV cache budgets", "hypothesis": "per-request budgets cut memory at equal accuracy",
            "research_question": "Does request-aware budgeting reduce peak KV memory at matched accuracy versus static budgets?",
            "expected_contribution": "adaptive budgeting policy", "keywords": ["kv", "cache", "budget"],
            "variables": {"independent": ["budget policy"], "dependent": ["peak memory", "accuracy"], "controls": ["model"]},
            "search_queries": ["kv cache eviction", "adaptive kv cache budget"],
        }),
    ],
    "PLAN": [
        ("record_investigation_plan", {"questions": ["Which methods are closest?", "Is per-request budgeting known under other names?"],
                                       "search_topics": ["kv cache eviction", "adaptive kv cache budget"], "comparison_targets": ["static-budget eviction"]}),
        ("record_uncertainty", {"question": "Does the closest work already vary the budget per request?", "importance": "high", "next_action": "COMPARE"}),
    ],
    "COMPARE": [FIXED_BUDGET_CLAIM, RESOLVE],
    "VERIFY": [FIXED_BUDGET_CLAIM, RESOLVE],
    "CHALLENGE": [("record_challenge_result", {"uncertainty_id": "__FOCUS__", "verdict": "holds", "rationale": "Searched follow-up work and alternative formulations; none contradicts it.",
                                               "supporting_paper_ids": [IDS[2]]})],
    "INVESTIGATE_GAP": [("record_challenge_result", {"uncertainty_id": "__FOCUS__", "verdict": "holds", "rationale": "No retrieved work varies the budget per request.",
                                                     "supporting_paper_ids": [IDS[0], IDS[2]]})],
    "READ": [("record_paper_analysis", {"paper_id": pid, "relevance_tier": "high", "problem": "KV memory", "method": "eviction", "relation_to_idea": OVERLAP}) for pid in IDS[:3]],
    "SYNTHESIZE": [("record_landscape", {"field_name": "KV cache optimization", "idea_position": "request-aware budgets under Eviction",
                                        "categories": [{"name": "Eviction", "paper_ids": IDS[:2]}, {"name": "Budgets", "parent": "Eviction", "paper_ids": [IDS[2]]}]})],
    "CRITIQUE": [
        ("record_claim", {"statement": "Closest work fixes the budget across requests", "kind": "evidence", "confidence": "medium",
                          "evidence": [{"paper_id": IDS[2], "quote": "The cache budget is fixed per layer and shared by every request", "support": "direct"}]}),
        ("record_claim", {"statement": "Request-level adaptation is untested in the closest work", "kind": "inference", "confidence": "low",
                          "evidence": [{"paper_id": IDS[0], "support": "indirect"}]}),
        ("record_critique", {"strongest_for": "requests differ", "strongest_against": "gains may vanish at matched compute",
                             "most_important_unresolved_question": "predictor cost", "most_dangerous_confounder": "unmatched budgets",
                             "closest_paper_ids": [IDS[0], IDS[2]], "closest_work_explanation": "same eviction mechanism",
                             "potential_contribution": "request-level adaptation", "overlap_summary": "eviction overlaps",
                             "distinction_summary": "budget varies per request", "overall_status": "promising_needs_validation",
                             "status_rationale": "testable distinction", "novelty": [{"question": "already proposed?", "finding": "not in searched literature", "severity": "moderate", "claim_ids": ["C001"]}]}),
        ("record_uncertainty", {"question": "Could the gain come from unmatched memory budgets?", "importance": "high", "next_action": "VERIFY"}),
    ],
    "REFINE": [
        ("record_gap", {"gap": "static budgets across heterogeneous requests", "why_unaddressed": "budgets fixed",
                        "research_question": "does per-request budgeting help?", "potential_experiment": "matched-memory comparison", "confidence": "medium",
                        "evidence": [{"paper_id": IDS[0], "quote": "under a static cache budget", "support": "direct"}]}),
        ("record_modification", {"title": "invalid first attempt", "implementation_difficulty": "extreme", **MOD}),  # rejected by schema
        ("record_modification", {"title": "Budget predictor", "implementation_difficulty": "moderate", "recommended": True, **MOD}),
        ("record_modification", {"title": "Rate-matched evaluation", "implementation_difficulty": "low", **MOD}),
        ("record_direction", {"direction": "Request-aware budget allocation under heterogeneous workloads", "hypothesis": "per-request budgets beat static ones at matched memory",
                              "rationale": "eviction overlaps; the budget policy is the remaining distinction", "modification_id": "M001"}),
    ],
    "PLAN_EXPERIMENT": [("record_experiment_plan", {"title": "Request-aware vs static budgets", "research_question": "rq", "hypothesis": "h", "proposed_method": "m",
                                                "baselines": ["full cache", "static eviction"], "metrics": ["peak memory", "accuracy"], "controls": ["same model"],
                                                "failure_conditions": ["no reduction at matched accuracy"]})],
}


def seed(ws: Workspace) -> None:
    for i, title in TITLES.items():
        ws.save_paper(Paper(id=f"arxiv:{i}", title=title, abstract=ABSTRACTS[i], year=2024, source="arxiv", sources=["arxiv"], arxiv_id=i, url=f"https://arxiv.org/abs/{i}"))
    for q in ("kv cache eviction", "adaptive kv cache budget"):
        ws.append_search(SearchRecord(query=q, sources=[SourceStatus(source="arxiv", status="ok", count=len(TITLES))], paper_ids=IDS))


@pytest.fixture
def dsh_command():
    cmd = os.environ.get("RF_E2E_DSH_COMMAND")
    if cmd:
        return cmd.split()
    if not shutil.which("npx"):
        pytest.skip("npx not available")
    return ["npx", "-y", f"@deepseek-ai/dsh@{DEFAULT_DSH_VERSION}"]


def test_investigation_through_real_dsh(tmp_path, dsh_command, monkeypatch):
    with ScriptedLLM(SCRIPT) as llm:
        cfg = tmp_path / "researchforge.toml"
        cfg.write_text(
            f'projects_dir = "{tmp_path / "projects"}"\nlog_level = "WARNING"\n'
            '[investigation]\nmin_papers = 5\nmin_queries = 2\npapers_to_analyze = 3\nmax_phase_attempts = 1\n'
            f'[model]\nmodel = "scripted-model"\n[model.custom]\nprovider_id = "scripted-llm"\nbase_url = "{llm.base_url}"\n'
            'api_key_env = "SCRIPTED_LLM_KEY"\nmodels = ["scripted-model"]\n'
            f'[dsh]\nhome = "{tmp_path / "dshhome"}"\nphase_timeout_s = 600\n'
        )
        monkeypatch.setenv("SCRIPTED_LLM_KEY", "not-a-real-key")
        from researchforge.config import load_settings

        settings: Settings = load_settings(cfg, env={})
        ws = Workspace.create(settings.resolved_projects_dir(), "Can request-aware dynamic KV-cache management reduce LLM inference memory?")
        seed(ws)
        runtime = DshHeadlessRuntime(settings, config_path=cfg, command=dsh_command)
        state = investigate(ws, settings, runtime)

        detail = [(p.name, p.status, p.missing, p.notes[-1:] if p.notes else []) for p in state.phases]
        assert state.status == "complete", detail

        # dsh exposed the ResearchForge tools under the MCP namespace, and not the disabled shell tool
        assert f"mcp__researchforge__record_claim" in llm.tool_names_seen
        assert not any(n in ("bash", "write", "edit") for n in llm.tool_names_seen)
        # the research persona reached the model
        system = next(m for m in llm.requests[-1]["messages"] if m.get("role") == "system")
        assert "ResearchForge" in (system["content"] if isinstance(system["content"], str) else json.dumps(system["content"]))

        # records written by the MCP server that dsh launched
        assert ws.idea_analysis().research_question.startswith("Does request-aware")
        assert len(ws.analyses()) == 3 and ws.landscape() and ws.critique()
        claims = ws.claims()
        assert claims[0].evidence[0].verified is True
        assert [m.title for m in ws.modifications()] == ["Budget predictor", "Rate-matched evaluation"]
        assert ws.plans()[0].id == "E001"

        # the schema error for the invalid modification went back to the model as a tool error
        tool_errors = [e for e in ws.events() if e.kind == "tool_result" and e.data.get("status") == "error"]
        assert any("implementation_difficulty" in e.data.get("result", "") for e in tool_errors)

        # one dsh session was carried across phases
        assert state.dsh_session_id
        starts = [e.data for e in ws.events() if e.kind == "info" and e.data.get("message") == "starting dsh"]
        assert starts[0]["session_id"] is None and all(s["session_id"] == state.dsh_session_id for s in starts[1:])

        # the controller chose the steps from the state: literature was already sufficient (seeded), and the
        # uncertainties recorded by the model drove COMPARE and VERIFY detours before refinement
        assert llm.actions[:5] == ["FORMALIZE", "PLAN", "READ", "SYNTHESIZE", "CRITIQUE"]
        assert "SEARCH" not in llm.actions
        assert {"COMPARE", "VERIFY", "CHALLENGE", "INVESTIGATE_GAP"} <= set(llm.actions)
        assert llm.actions.index("REFINE") < llm.actions.index("INVESTIGATE_GAP")  # the gap is challenged after it is recorded
        assert all(u.status == "resolved" for u in ws.uncertainties())
        assert {u.challenge_verdict for u in ws.uncertainties() if u.source == "controller"} == {"holds"}
        assert ws.directions()[0].direction.startswith("Request-aware budget allocation")
        scored = [d for d in state.decisions if d.candidates]
        assert scored and all(f"score {d.candidates[0].score}" in d.reason for d in scored)
        assert state.decisions[-1].action == "FINALIZE" and state.research_decision == "NEEDS_MODIFICATION"

        md = ws.report_path("md").read_text()
        assert "## 15. References" in md and "Promising but requires experimental validation" in md
        assert "Refined direction (D001, REFINE_SCOPE)" in md and "## Appendix C. Investigation Log" in md
        assert "**Research decision:** Needs modification" in md
