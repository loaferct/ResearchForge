"""Uncertainty-driven adaptive loop: challenges, refinement, diminishing returns, budgets, feedback, failures."""

import asyncio

import pytest

import support
from support import FakeApis, ScriptedRuntime, make_toolkit, parse_prompt, scripted_action

from researchforge.controller import decide_next_action, raise_questions, research_decision
from researchforge.evaluation.metrics import loop_metrics
from researchforge.experiments.runner import ExperimentRunner
from researchforge.orchestrator import investigate, new_state
from researchforge.runtime import RunOutcome
from researchforge.toolkit import ToolError


def no_sleep(_s):
    return None


@pytest.fixture(autouse=True)
def reset_verdicts():
    support.CHALLENGE_VERDICTS.clear()
    yield
    support.CHALLENGE_VERDICTS.clear()


def build_until_critique(ws, settings, apis):
    tk = make_toolkit(ws, settings, apis)
    for action in ("FORMALIZE", "PLAN", "SEARCH", "READ", "SYNTHESIZE"):
        scripted_action(tk, action, "kv cache eviction", None)
    scripted_action(tk, "SEARCH", "adaptive kv cache budget", None)
    scripted_action(tk, "CRITIQUE", None, None)
    return tk


# ---------------------------------------------------------------- test 1: uncertainty tracking


def test_controller_raises_challenge_questions_for_conclusions(ws, settings, apis):
    tk = build_until_critique(ws, settings, apis)
    state = new_state(ws, settings)
    created = raise_questions(ws, settings, state)
    assert [u.target_ref for u in created] == ["critique"]
    u = created[0]
    assert (u.source, u.category, u.importance, u.next_action) == ("controller", "contradiction", "high", "CHALLENGE")
    assert raise_questions(ws, settings, state) == []  # once per conclusion
    scripted_action(tk, "REFINE", None, None)
    refs = [u.target_ref for u in raise_questions(ws, settings, state)]
    assert refs == ["G001", "D001"]  # the new gap and the new direction are challenged too


def test_uncertainty_confidence_requires_basis_and_fields_round_trip(ws, settings, apis):
    tk = build_until_critique(ws, settings, apis)
    with pytest.raises(ToolError, match="confidence_basis"):
        tk.record_uncertainty(question="Q?", importance="high", confidence=0.4)
    uid = tk.record_uncertainty(question="Has the policy been evaluated?", importance="high", category="novelty",
                                possible_actions=["SEARCH", "VERIFY"], confidence=0.45, confidence_basis="two partial matches",
                                supporting_paper_ids=["arxiv:9999.00003"], contradicting_paper_ids=["arxiv:9999.00006"])["uncertainty_id"]
    u = ws.uncertainty(uid)
    assert u.actions() == ["SEARCH", "VERIFY"] and u.confidence == 0.45
    assert tk.get_research_state()["uncertainties"][-1]["contradicting"] == ["arxiv:9999.00006"]


# ---------------------------------------------------------------- tests 3 and 4: contradiction and refinement


def test_contradicting_evidence_weakens_conclusion_and_triggers_refinement(ws, settings):
    support.CHALLENGE_VERDICTS["critique"] = "weakened"
    rt = ScriptedRuntime(settings)
    state = investigate(ws, settings, rt, sleep=no_sleep)
    challenged = next(u for u in ws.uncertainties() if u.target_ref == "critique")
    assert challenged.challenge_verdict == "weakened" and challenged.contradicting_paper_ids == ["arxiv:9999.00006"]
    follow = next(u for u in ws.uncertainties() if u.target_ref == f"refine:{challenged.id}")
    assert follow.status == "resolved" and follow.next_action == "REFINE"
    # the refinement was driven by that question, and the direction change records why
    refine_steps = [d for d in state.decisions if d.action == "REFINE" and d.focus_id == follow.id]
    assert refine_steps
    changed = next(d for d in ws.directions() if follow.id in d.uncertainty_ids)
    assert changed.change_type == "REFINE_SCOPE" and changed.paper_ids == ["arxiv:9999.00006"]
    # it departs from the original idea (no earlier direction), which stays untouched
    assert changed.previous_direction_id is None
    assert ws.idea_analysis().hypothesis.startswith("Per-request budgets reduce memory")
    # the order shows the contradiction drove the refinement, and the new direction was itself challenged
    actions = [(d.action, d.focus_id) for d in state.decisions]
    assert actions.index(("CHALLENGE", challenged.id)) < actions.index(("REFINE", follow.id)) < actions.index(("CHALLENGE", next(u.id for u in ws.uncertainties() if u.target_ref == changed.id)))
    assert state.research_decision == "NEEDS_MODIFICATION"
    m = loop_metrics(ws)
    assert m["contradictory_evidence_found"] >= 1 and m["direction_changes"] >= 1 and m["challenges"] >= 2


def test_challenge_verdict_needs_contradicting_papers(ws, settings, apis):
    tk = build_until_critique(ws, settings, apis)
    raise_questions(ws, settings, new_state(ws, settings))
    uid = next(u.id for u in ws.uncertainties() if u.target_ref == "critique")
    with pytest.raises(ToolError, match="contradicting_paper_ids"):
        tk.record_challenge_result(uncertainty_id=uid, verdict="refuted", rationale="looked")
    with pytest.raises(ToolError, match="never retrieved"):
        tk.record_challenge_result(uncertainty_id=uid, verdict="refuted", rationale="looked", contradicting_paper_ids=["arxiv:0000.0"])
    assert tk.record_challenge_result(uncertainty_id=uid, verdict="holds", rationale="searched follow-up work")["verdict"] == "holds"


def test_rejected_direction_is_not_challenged_and_reads_as_well_explored(ws, settings, apis):
    tk = build_until_critique(ws, settings, apis)
    tk.record_direction(direction="Drop it", hypothesis="n/a", rationale="identical method exists", change_type="REJECT_DIRECTION",
                        paper_ids=["arxiv:9999.00001"])
    state = new_state(ws, settings)
    assert "D001" not in [u.target_ref for u in raise_questions(ws, settings, state)]
    assert research_decision(ws, state)[0] == "ALREADY_WELL_EXPLORED"
    with pytest.raises(ToolError, match="research_question"):
        tk.record_direction(direction="x", hypothesis="y", rationale="z", change_type="CHANGE_RESEARCH_QUESTION")


# ---------------------------------------------------------------- test 5: stopping


class StalledRuntime(ScriptedRuntime):
    """Coverage steps work; focused investigation steps find nothing new."""

    def run_phase(self, ws, prompt, *, phase, session_id, on_event):
        action, _focus, focus_id = parse_prompt(prompt)
        if focus_id and action != "REFINE":
            self.calls.append((action, focus_id, session_id))
            make_toolkit(ws, self.settings, self.apis).update_uncertainty(id=focus_id, status="partially_resolved", resolution="nothing conclusive found")
            return RunOutcome(ok=True, session_id="s", tool_calls=1)
        return super().run_phase(ws, prompt, phase=phase, session_id=session_id, on_event=on_event)


def test_diminishing_returns_closes_investigation_and_finalizes(ws, settings):
    settings.investigation.diminishing_window = 2
    state = investigate(ws, settings, StalledRuntime(settings), sleep=no_sleep)
    assert state.investigation_closed and state.investigation_closed.startswith("diminishing returns")
    first_close = next(i for i, d in enumerate(state.decisions) if d.closes_investigation)
    investigated = [d for d in state.decisions[:first_close] if d.focus_id and d.action not in ("REFINE", "ANALYZE_RESULTS")]
    assert len(investigated) == 2 and all(d.info_gain == 0 for d in investigated)
    assert state.decisions[first_close].closes_investigation.startswith("diminishing returns")
    left = [u for u in ws.uncertainties() if u.resolution.startswith("Left open: diminishing returns")]
    assert left and all(u.status == "unresolved" for u in left)
    assert state.decisions[-1].action == "FINALIZE"
    assert "Investigation closed early" in ws.report_path("md").read_text()


def test_low_value_candidates_are_not_pursued(ws, settings):
    settings.investigation.min_action_score = 100.0
    rt = ScriptedRuntime(settings)
    state = investigate(ws, settings, rt, sleep=no_sleep)
    assert "not worthwhile" in state.investigation_closed
    # Only the mandatory first challenge of the critique runs; nothing is pursued on score.
    challenged = [d for d in state.decisions if d.phase == "CHALLENGE"]
    assert len(challenged) == 1 and "has not been challenged yet" in challenged[0].reason
    assert not any(d.phase == "UNCERTAINTY" for d in state.decisions)
    closing = next(d for d in state.decisions if d.closes_investigation)
    assert closing.candidates and closing.candidates[0].score < 100


def test_closed_investigation_reopens_for_new_questions(ws, settings):
    settings.investigation.diminishing_window = 2
    state = investigate(ws, settings, StalledRuntime(settings), sleep=no_sleep)
    # questions raised after the first closure (the gap and direction challenges) are still investigated
    first_close = next(i for i, d in enumerate(state.decisions) if d.closes_investigation)
    after = [d for d in state.decisions[first_close + 1:] if d.focus_id and d.phase == "CHALLENGE"]
    assert after, [(d.action, d.focus_id) for d in state.decisions]


# ---------------------------------------------------------------- test 6: budgets


class TokenRuntime(ScriptedRuntime):
    def run_phase(self, ws, prompt, **kw):
        out = super().run_phase(ws, prompt, **kw)
        out.usage = {"inputTokens": 3000, "outputTokens": 1000, "totalTokens": 4000}
        return out


def test_token_budget_stops_safely(ws, settings):
    settings.investigation.max_tokens = 10_000
    rt = TokenRuntime(settings)
    state = investigate(ws, settings, rt, sleep=no_sleep)
    assert len(rt.actions) == 3 and state.budget.tokens == 12_000
    assert state.finalize_reason == "Stopping: token budget reached (10000)."
    assert state.status == "incomplete" and ws.report_path("md").exists()


# ---------------------------------------------------------------- test 7: experiment feedback


BENCH = "import json, os\njson.dump({'mem': 10.0, 'n': 5}, open(os.environ['RF_RESULTS_FILE'], 'w'))\n"


def test_unsupported_experiment_raises_refinement_without_model_help(ws, settings, apis):
    investigate(ws, settings, ScriptedRuntime(settings), sleep=no_sleep)
    tk = make_toolkit(ws, settings, apis)
    pid = tk.record_experiment_plan(title="t", research_question="q", hypothesis="h", proposed_method="m", baselines=["b"], metrics=["mem"],
                                    execution={"arms": [{"name": "b", "role": "baseline", "command": "python3 bench.py"},
                                                        {"name": "m", "role": "method", "command": "python3 bench.py"}]})["plan_id"]
    (ws.experiment_dir(pid) / "bench.py").write_text(BENCH)
    ExperimentRunner(ws, settings).run(pid, approved=True)
    tk.record_hypothesis_evaluation(plan_id=pid, verdict="NOT_SUPPORTED", rationale="memory unchanged at matched accuracy")
    state = ws.state()
    created = raise_questions(ws, settings, state)
    assert [u.target_ref for u in created] == [pid] and created[0].next_action == "REFINE"
    d = decide_next_action(ws, settings, state)
    # either refine directly or first search for explanations of the failure; both target the new question
    assert d.focus_id == created[0].id and d.action in ("REFINE", "SEARCH")
    assert any(c.action == "REFINE" and c.uncertainty_id == created[0].id for c in d.candidates)
    assert research_decision(ws, state)[0] == "EXPERIMENTALLY_UNSUPPORTED"


# ---------------------------------------------------------------- test 8: tool failure


class FlakyRuntime(ScriptedRuntime):
    """The first CHALLENGE call fails outright (no tool calls); tool errors inside other steps are reported."""

    def __init__(self, settings):
        super().__init__(settings)
        self.failed_once = False

    def run_phase(self, ws, prompt, **kw):
        action, _, _ = parse_prompt(prompt)
        if action == "CHALLENGE" and not self.failed_once:
            self.failed_once = True
            self.calls.append((action, None, None))
            return RunOutcome(ok=False, session_id=None, error="upstream 503", exit_code=1)
        out = super().run_phase(ws, prompt, **kw)
        if action == "SEARCH":
            out.failed_tool_calls = 1  # e.g. one literature source failed inside the step
        return out


def test_failed_invocation_is_retried_and_recorded_without_aborting(ws, settings):
    slept = []
    rt = FlakyRuntime(settings)
    state = investigate(ws, settings, rt, sleep=slept.append)
    assert rt.actions.count("CHALLENGE") >= 2 and slept  # retried after backoff
    assert state.budget.runtime_failures == 1 and state.budget.failed_tool_calls >= 1
    assert state.status == "complete"
    warnings = [e.data["message"] for e in ws.events() if e.kind == "warning"]
    assert any("upstream 503" in w for w in warnings)


# ---------------------------------------------------------------- decision trace and metrics


def test_decision_trace_is_built_from_state(ws, settings):
    state = investigate(ws, settings, ScriptedRuntime(settings), sleep=no_sleep)
    traced = [d for d in state.decisions if d.candidates]
    assert traced
    d = traced[0]
    best = d.candidates[0]
    assert d.focus_id == best.uncertainty_id and d.expected_gain == best.expected_gain and d.estimated_cost == best.cost
    assert f"score {best.score}" in d.reason
    steps = [x for x in state.decisions if x.action not in ("INTAKE", "FINALIZE")]
    assert all(x.info_gain is not None for x in steps)
    assert any(x.tools_used for x in steps) and any(x.state_changes for x in steps)
    m = loop_metrics(ws)
    assert m["iterations"] == state.budget.iterations and m["uncertainties_created_by_controller"] >= 1
    assert m["finalization_reason"] == state.finalize_reason and m["research_decision"] == state.research_decision


def test_search_budget_blocks_search_candidates(ws, settings, apis):
    build_until_critique(ws, settings, apis)
    settings.investigation.max_searches = len(ws.searches())
    from researchforge.controller import score_candidates

    raise_questions(ws, settings, new_state(ws, settings))
    assert all(c.action not in ("SEARCH", "CHALLENGE", "INVESTIGATE_GAP") for c in score_candidates(ws, settings, new_state(ws, settings)))
    with pytest.raises(ToolError, match="search budget"):
        asyncio.run(make_toolkit(ws, settings, FakeApis()).search_papers("anything new"))
