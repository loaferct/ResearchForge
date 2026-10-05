"""Tests for the state-driven investigation loop (controller + orchestrator)."""

import pytest

from support import FakeApis, ScriptedRuntime, make_toolkit, scripted_action

from researchforge.controller import decide_next_action, should_finalize
from researchforge.experiments.runner import ExperimentRunner
from researchforge.orchestrator import investigate, new_state

from researchforge.toolkit import ToolError
from researchforge.workspace import Workspace


def no_sleep(_s):
    return None


def decide(ws, settings, state=None):
    return decide_next_action(ws, settings, state or new_state(ws, settings))


# ---------------------------------------------------------------- transitions


def test_intake_formalize_plan_investigate_transitions(ws, settings, apis):
    tk = make_toolkit(ws, settings, apis)
    d = decide(ws, settings)
    assert (d.phase, d.action) == ("FORMALIZE", "FORMALIZE")
    scripted_action(tk, "FORMALIZE", None, None)
    d = decide(ws, settings)
    assert (d.phase, d.action) == ("PLAN", "PLAN")
    scripted_action(tk, "PLAN", None, None)
    d = decide(ws, settings)
    assert (d.phase, d.action) == ("INVESTIGATE", "SEARCH")
    assert d.focus == "kv cache eviction"  # first planned topic
    assert "Literature coverage is insufficient" in d.reason and "0 papers" in d.evidence


def test_search_then_read_then_synthesize_then_critique(ws, settings, apis):
    tk = make_toolkit(ws, settings, apis)
    for action in ("FORMALIZE", "PLAN", "SEARCH"):
        scripted_action(tk, action, "kv cache eviction", None)
    d = decide(ws, settings)
    assert d.action == "SEARCH" and d.focus == "adaptive kv cache budget"  # second distinct query still required
    scripted_action(tk, "SEARCH", d.focus, None)
    assert decide(ws, settings).action == "READ"
    scripted_action(tk, "READ", None, None)
    assert decide(ws, settings).action == "SYNTHESIZE"
    scripted_action(tk, "SYNTHESIZE", None, None)
    assert decide(ws, settings).action == "CRITIQUE"


def test_critique_uncertainty_drives_next_action(ws, settings, apis):
    tk = make_toolkit(ws, settings, apis)
    for action in ("FORMALIZE", "PLAN", "SEARCH", "READ", "SYNTHESIZE"):
        scripted_action(tk, action, "kv cache eviction", None)
    scripted_action(tk, "SEARCH", "adaptive kv cache budget", None)
    scripted_action(tk, "CRITIQUE", None, None)
    d = decide(ws, settings)
    # the best-scoring candidate is chosen, and the decision carries the full ranked alternatives
    assert d.phase == "UNCERTAINTY" and d.focus_id == d.candidates[0].uncertainty_id and d.action == d.candidates[0].action
    assert [c.score for c in d.candidates] == sorted((c.score for c in d.candidates), reverse=True)
    assert "score" in d.reason and "importance" in d.reason and "Next best" in d.reason
    assert d.focus_id == "U001" and d.action == "SEARCH"  # high-importance novelty question with no evidence yet
    for uid in ("U001", "U002", "U003"):
        tk.update_uncertainty(id=uid, status="resolved", resolution="checked")
    assert decide(ws, settings).action == "REFINE"


def test_scoring_prefers_important_evidence_poor_cheap_actions(ws, settings, apis):
    from researchforge.controller import score_candidates

    tk = make_toolkit(ws, settings, apis)
    import asyncio

    asyncio.run(tk.search_papers("kv cache eviction"))
    high = tk.record_uncertainty(question="Is the policy already published?", importance="high", category="novelty", next_action="SEARCH")["uncertainty_id"]
    low = tk.record_uncertainty(question="Which plotting style?", importance="low", category="other", next_action="SEARCH")["uncertainty_id"]
    known = tk.record_uncertainty(question="Does TestSnap fix budgets?", importance="high", category="overlap", next_action="VERIFY",
                                  supporting_paper_ids=["arxiv:9999.00003"], contradicting_paper_ids=["arxiv:9999.00001"])["uncertainty_id"]
    cands = score_candidates(ws, settings, new_state(ws, settings))
    by_id = {c.uncertainty_id: c for c in cands}
    assert cands[0].uncertainty_id == high
    assert by_id[high].score > by_id[known].score > by_id[low].score  # evidence on both sides lowers deficiency
    assert by_id[known].deficiency == 0.35 and by_id[high].deficiency == 1.0
    c = by_id[high]
    assert c.score == round(c.importance * c.expected_gain * c.relevance * c.deficiency / c.cost, 3)
    assert "prior" in c.gain_basis


def test_should_finalize_requires_research_conditions(ws, settings):
    ready, missing = should_finalize(ws, settings, new_state(ws, settings))
    assert not ready
    assert "formalized research question" in missing and "investigation plan" in missing and "research direction decision" in missing


def test_full_loop_finalizes_when_sufficient(ws, settings):
    rt = ScriptedRuntime(settings)
    state = investigate(ws, settings, rt, sleep=no_sleep)
    assert state.status == "complete"
    assert state.decisions[-1].action == "FINALIZE" and "criteria met" in state.decisions[-1].reason
    assert rt.actions.index("CRITIQUE") < rt.actions.index("VERIFY") < rt.actions.index("REFINE")
    assert all(u.status == "resolved" for u in ws.uncertainties())
    assert state.decisions[0].phase == "INTAKE"
    assert all(d.reason for d in state.decisions)
    assert [e for e in ws.events() if e.kind == "decision"]


def test_structured_research_logs(ws, settings, caplog):
    import logging

    caplog.set_level(logging.INFO, logger="researchforge.research")
    investigate(ws, settings, ScriptedRuntime(settings), sleep=no_sleep)
    lines = [r.getMessage() for r in caplog.records if r.name == "researchforge.research"]
    assert any(l.startswith("[RESEARCH] decision phase=FORMALIZE action=FORMALIZE") for l in lines)
    assert any("action=SEARCH" in l and "papers=11" in l for l in lines if l.startswith("[RESEARCH] result"))
    assert any(l.startswith("[RESEARCH] finalized status=complete") for l in lines)
    assert all(len(l) < 1200 for l in lines)  # no model output dumped into logs


# ---------------------------------------------------------------- stopping, budgets, attempts


def test_budget_limit_stops_the_loop(ws, settings):
    settings.investigation.max_iterations = 4
    rt = ScriptedRuntime(settings)
    state = investigate(ws, settings, rt, sleep=no_sleep)
    assert len(rt.actions) == 4
    assert state.finalize_reason.startswith("Stopping: iteration budget reached")
    assert state.status == "incomplete"
    assert "Stopped by a safety limit" in ws.report_path("md").read_text()


def test_search_budget_enforced_by_tool(ws, settings, apis):
    settings.investigation.max_searches = 1
    tk = make_toolkit(ws, settings, apis)
    import asyncio

    asyncio.run(tk.search_papers("kv cache eviction"))
    with pytest.raises(ToolError, match="search budget reached"):
        asyncio.run(tk.search_papers("attention sinks"))


class NoUpdateRuntime(ScriptedRuntime):
    """Makes progress on focused steps but never updates the uncertainty itself."""

    def run_phase(self, ws, prompt, *, phase, session_id, on_event):
        from support import parse_prompt

        action, focus, focus_id = parse_prompt(prompt)
        if focus_id:
            self.calls.append((action, focus_id, session_id))
            tk = make_toolkit(ws, self.settings, self.apis)
            tk.record_claim(statement=f"note {len(self.calls)}", kind="inference", confidence="low", evidence=[{"paper_id": "arxiv:9999.00001"}])
            from researchforge.runtime import RunOutcome

            return RunOutcome(ok=True, session_id="s", tool_calls=1)
        return super().run_phase(ws, prompt, phase=phase, session_id=session_id, on_event=on_event)


def test_uncertainty_left_unresolved_after_attempt_budget(ws, settings):
    rt = NoUpdateRuntime(settings)
    state = investigate(ws, settings, rt, sleep=no_sleep)
    focused = [f for _, f, _ in rt.calls if f]
    assert focused.count("U001") == settings.investigation.max_uncertainty_attempts
    u = ws.uncertainty("U001")
    assert u.status == "unresolved" and "attempt budget" in u.resolution
    assert state.decisions[-1].action == "FINALIZE"
    assert "U001" in ws.report_path("md").read_text()


def test_recritique_after_new_evidence(ws, settings):
    state = investigate(ws, settings, ScriptedRuntime(settings), sleep=no_sleep)
    assert state.critiques == 1
    assert decide_next_action(ws, settings, state).action == "FINALIZE"
    # papers retrieved after the critique was recorded make it stale
    later = ws.critique().recorded_at
    from datetime import timedelta

    for p in ws.papers()[: settings.investigation.recritique_after_papers]:
        ws.save_paper(p.model_copy(update={"retrieved_at": later + timedelta(minutes=5)}))
    d = decide_next_action(ws, settings, state)
    assert d.action == "CRITIQUE" and "arrived since the last critique" in d.reason
    state.critiques = settings.investigation.max_critiques
    assert decide_next_action(ws, settings, state).action == "FINALIZE"


# ---------------------------------------------------------------- experiment feedback


BENCH = """
import json, os, sys
cfg = json.loads(os.environ["RF_ARM_CONFIG"])
json.dump({"accuracy": cfg.get("acc", 0.8), "mem": cfg.get("mem", 10.0), "n": 100}, open(os.environ["RF_RESULTS_FILE"], "w"))
"""


def executable_plan(ws, settings):
    tk = make_toolkit(ws, settings, FakeApis())
    arms = [{"name": "base", "role": "baseline", "command": "python3 bench.py", "config": {"mem": 10.0, "model": "m"}},
            {"name": "method", "role": "method", "command": "python3 bench.py", "config": {"mem": 8.0, "model": "m"}}]
    res = tk.record_experiment_plan(title="Runnable check", research_question="q", hypothesis="h", proposed_method="m",
                                    baselines=["static"], metrics=["mem"],
                                    execution={"arms": arms, "expected_metrics": ["mem", "accuracy"], "higher_is_better": {"mem": False}, "sample_count_key": "n"})
    (ws.experiment_dir(res["plan_id"]) / "bench.py").write_text(BENCH)
    return res


def test_experiment_waits_for_approval_then_analysis_reevaluates(ws, settings):
    investigate(ws, settings, ScriptedRuntime(settings), sleep=no_sleep)
    assert executable_plan(ws, settings)["plan_id"] == "E002"

    rt = ScriptedRuntime(settings)
    state = investigate(Workspace(ws.root), settings, rt, sleep=no_sleep)
    assert state.status == "awaiting_approval" and state.awaiting_approval == ["E002"]
    assert "EXPERIMENT" in [d.action for d in state.decisions]
    assert ws.runs() == []  # nothing ran without approval
    assert "Awaiting human approval to run: E002" in ws.report_path("md").read_text()

    analysis = ExperimentRunner(ws, settings).run("E002", approved=True)
    assert analysis.status == "PASSED"
    rt = ScriptedRuntime(settings)
    state = investigate(Workspace(ws.root), settings, rt, sleep=no_sleep)
    assert rt.actions == ["ANALYZE_RESULTS"]
    assert ws.evaluations()[0].verdict == "SUPPORTED"
    assert state.status == "complete"
    md = ws.report_path("md").read_text()
    assert "Hypothesis re-evaluation for E002:** **[Experimental result]** SUPPORTED" in md


def test_evaluation_rules_prevent_fake_results(ws, settings, apis):
    tk = make_toolkit(ws, settings, apis)
    with pytest.raises(ToolError, match="no executed and analyzed experiment"):
        tk.record_hypothesis_evaluation(plan_id="E001", verdict="SUPPORTED", rationale="looks good")
    pid = executable_plan(ws, settings)["plan_id"]
    ExperimentRunner(ws, settings).run(pid, approved=True)
    a = ws.experiment_analyses()[0]
    ws.save_experiment_analysis(a.model_copy(update={"status": "FAILED"}))
    with pytest.raises(ToolError, match="cannot support the hypothesis"):
        tk.record_hypothesis_evaluation(plan_id=pid, verdict="SUPPORTED", rationale="x")
    assert tk.record_hypothesis_evaluation(plan_id=pid, verdict="INCONCLUSIVE", rationale="verification failed")["verdict"] == "INCONCLUSIVE"


def test_not_supported_opens_refinement(ws, settings, apis):
    investigate(ws, settings, ScriptedRuntime(settings), sleep=no_sleep)
    executable_plan(ws, settings)
    ExperimentRunner(ws, settings).run("E002", approved=True)
    tk = make_toolkit(ws, settings, apis)
    tk.record_hypothesis_evaluation(plan_id="E002", verdict="NOT_SUPPORTED", rationale="no memory saving at matched accuracy")
    tk.record_uncertainty(question="Which modification addresses the failed hypothesis?", importance="high", next_action="REFINE")
    state = ws.state()
    d = decide_next_action(ws, settings, state)
    assert d.action == "REFINE" and d.phase == "UNCERTAINTY" and "Which modification" in d.focus


# ---------------------------------------------------------------- records and resume


def test_direction_preserves_original_idea(ws, settings, apis):
    tk = make_toolkit(ws, settings, apis)
    scripted_action(tk, "FORMALIZE", None, None)
    original = ws.idea_analysis().hypothesis
    tk.record_direction(direction="request-aware allocation", hypothesis="new", rationale="overlap found")
    tk.record_direction(direction="heterogeneous workloads", hypothesis="newer", rationale="narrower")
    assert ws.idea_analysis().hypothesis == original
    assert [d.id for d in ws.directions()] == ["D001", "D002"]
    assert tk.get_research_state()["current_direction"]["direction"] == "heterogeneous workloads"


def test_uncertainty_tools_validate(ws, settings, apis):
    tk = make_toolkit(ws, settings, apis)
    first = tk.record_uncertainty(question="Is X known?", importance="high")
    assert tk.record_uncertainty(question="is  x known?", importance="low")["uncertainty_id"] == first["uncertainty_id"]  # deduplicated
    with pytest.raises(ToolError, match="explain the resolution"):
        tk.update_uncertainty(id=first["uncertainty_id"], status="resolved")
    with pytest.raises(ToolError, match="unknown uncertainty"):
        tk.update_uncertainty(id="U999", status="open")
    with pytest.raises(ToolError, match="never retrieved"):
        tk.record_uncertainty(question="Y?", importance="low", paper_ids=["arxiv:nope"])


def test_resume_restores_loop_state(ws, settings):
    settings.investigation.max_iterations = 5
    investigate(ws, settings, ScriptedRuntime(settings), sleep=no_sleep)
    saved = ws.state()
    assert saved.budget.iterations == 5 and len(saved.decisions) >= 6
    settings.investigation.max_iterations = 40
    rt = ScriptedRuntime(settings)
    state = investigate(Workspace(ws.root), settings, rt, sleep=no_sleep)
    assert "FORMALIZE" not in rt.actions and "PLAN" not in rt.actions
    assert state.budget.iterations > 5 and state.status == "complete"
    assert state.decisions[: len(saved.decisions)] == saved.decisions
