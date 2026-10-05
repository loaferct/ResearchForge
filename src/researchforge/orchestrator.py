"""The ResearchOrchestrator: runs the state-driven investigation loop.

    while not finalizing:
        decision = decide_next_action(state)      # controller.py
        outcome  = run one dsh turn for it        # existing runtime + MCP tools
        state    = update from what the workspace now records
        iteration += 1

Each action is one agent turn in the same DeepSeek Harness session. The
workspace (records written through the MCP tools) and ``research_state.json``
(controller state: phase, iteration, budgets, decisions) hold everything
needed to resume. The final report is generated deterministically from them.
See docs/AGENT_LOOP.md.
"""

from __future__ import annotations

import logging
import threading
import time
from collections.abc import Callable

from researchforge import phases, report
from researchforge.actions import ACTION_UI_PHASES, build_prompt
from researchforge.config import Settings
from researchforge.controller import (
    Snapshot, decide_next_action, information_gain, progress, raise_questions, research_decision, should_finalize, state_changes,
)
from researchforge.runtime import AgentRuntime, RunOutcome
from researchforge.schemas import Decision, PhaseState, ResearchState, Uncertainty, utcnow
from researchforge.toolkit import ResearchToolkit
from researchforge.workspace import Workspace

log = logging.getLogger("researchforge.research")

REPORT_PHASE = "report"


def usage_tokens(usage: dict) -> int:
    """Total tokens from a provider usage report (keys vary by adapter); 0 when not reported."""
    if not usage:
        return 0
    for key in ("totalTokens", "total_tokens"):
        if isinstance(usage.get(key), (int, float)):
            return int(usage[key])
    return int(sum(v for k, v in usage.items() if isinstance(v, (int, float)) and ("input" in k.lower() or "output" in k.lower())))


class InvestigationAborted(RuntimeError):
    pass


def new_state(ws: Workspace, settings: Settings) -> ResearchState:
    return ResearchState(
        project=ws.name,
        idea=ws.raw_idea,
        provider=settings.model.custom.provider_id if settings.model.custom else settings.model.provider,
        model=settings.model.model,
        phases=[PhaseState(name=n) for n in (*phases.PHASE_NAMES, REPORT_PHASE)],
    )


def research_log(msg: str, **fields) -> None:
    """Structured `[RESEARCH] key=value` line; values are kept short."""
    def fmt(k: str, v: object) -> str:
        text = str(v)[:120]
        return f'{k}="{text}"' if " " in text else f"{k}={text}"

    parts = " ".join(fmt(k, v) for k, v in fields.items())
    log.info(f"[RESEARCH] {msg} {parts}".strip(), extra={f"rf_{k}": (v[:300] if isinstance(v, str) else v) for k, v in fields.items()})


class ResearchOrchestrator:
    def __init__(
        self,
        ws: Workspace,
        settings: Settings,
        runtime: AgentRuntime,
        *,
        stop: threading.Event | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.ws = ws
        self.settings = settings
        self.runtime = runtime
        self.toolkit = ResearchToolkit(ws, settings)
        self.stop = stop or threading.Event()
        self.sleep = sleep

    # ------------------------------------------------------------ state

    def _state(self) -> ResearchState:
        state = self.ws.state() or new_state(self.ws, self.settings)
        known = {p.name for p in state.phases}
        for name in (*phases.PHASE_NAMES, REPORT_PHASE):
            if name not in known:
                state.phases.append(PhaseState(name=name))
        return state

    def _sync_phases(self, state: ResearchState, running: list[str] | None = None, final: bool = False) -> None:
        """Mirror the loop's progress onto the per-phase records the UI and report read."""
        for spec in phases.PHASES:
            ph = state.phase(spec.name)
            missing = spec.check(self.ws, self.settings)
            ph.missing = missing
            if not missing:
                if ph.status != "complete":
                    ph.status, ph.finished_at = "complete", utcnow()
            elif running and spec.name in running:
                ph.status, ph.started_at = "running", ph.started_at or utcnow()
            elif final and ph.attempts:
                ph.status, ph.finished_at = "incomplete", utcnow()
            else:
                ph.status = "pending"

    # ------------------------------------------------------------ loop

    def run(self) -> ResearchState:
        state = self._state()
        state.status, state.error, state.finalize_reason = "running", None, None
        self.ws.save_state(state)
        self.ws.append_event("info", message="investigation started" if state.budget.iterations == 0 else "investigation resumed",
                             runtime=self.runtime.name, model=f"{state.provider}/{state.model}", iteration=state.budget.iterations)
        if state.loop_phase == "INTAKE":
            self._record(state, Decision(iteration=0, phase="INTAKE", action="INTAKE", reason="Research idea received.",
                                         evidence=f"idea: {self.ws.raw_idea[:200]}", outcome="idea stored in the workspace"), announce=False)
            self.ws.append_event("decision", "INTAKE", **self._decision_event(state.decisions[-1]))
            state.loop_phase = "FORMALIZE"
            self.ws.save_state(state)
        try:
            while True:
                if self.stop.is_set():
                    raise InvestigationAborted("stopped by user")
                for u in raise_questions(self.ws, self.settings, state):
                    self.ws.append_event("info", "UNCERTAINTY", message=f"question raised: {u.id} {u.question[:160]}", uncertainty=u.id, raised_by="controller")
                    research_log("uncertainty_added", uncertainty=u.id, importance=u.importance, category=u.category, raised_by="controller", question=u.question)
                self.ws.save_state(state)
                decision = decide_next_action(self.ws, self.settings, state)
                state.loop_phase, state.current_action = decision.phase, decision.action
                state.current_focus = decision.focus
                research_log("decision", phase=decision.phase, action=decision.action, focus=decision.focus or "", reason=decision.reason,
                             iteration=decision.iteration,
                             open_uncertainties=sum(1 for u in self.ws.uncertainties() if u.status in ("open", "partially_resolved")),
                             candidates="; ".join(f"{c.action}:{c.uncertainty_id}={c.score}" for c in decision.candidates[:4]))
                if decision.closes_investigation:
                    self._close_investigation(state, decision.closes_investigation)
                if decision.action == "FINALIZE":
                    self._record(state, decision.model_copy(update={"outcome": "finalizing"}))
                    state.finalize_reason = decision.reason
                    break
                if decision.action == "EXPERIMENT":
                    pending = [p.strip() for p in (decision.focus or "").split(",") if p.strip()]
                    state.awaiting_approval = sorted(set(state.awaiting_approval) | set(pending))
                    self._record(state, decision.model_copy(update={"outcome": "awaiting human approval; not executed"}))
                    research_log("experiment awaiting approval", plans=",".join(pending))
                    continue
                self._execute(state, decision)
        except InvestigationAborted as exc:
            state.status, state.error = "failed", str(exc)
            self.ws.append_event("error", message=f"investigation stopped: {exc}")
            self._sync_phases(state)
            self.ws.save_state(state)
            self._report(state, final=False)
            return state

        self._sync_phases(state, final=True)
        ready, missing = should_finalize(self.ws, self.settings, state)
        if state.awaiting_approval and not any(r.plan_id in state.awaiting_approval for r in self.ws.runs()):
            state.status = "awaiting_approval"
        else:
            state.status = "complete" if ready else "incomplete"
        state.loop_phase, state.current_action, state.current_focus = "FINALIZE", "FINALIZE", None
        state.research_decision, state.research_decision_basis = research_decision(self.ws, state)
        research_log("research_decision", decision=state.research_decision, basis=state.research_decision_basis)
        self._report(state)
        self.ws.append_event("info", message="investigation finished", status=state.status,
                             missing=missing, reason=state.finalize_reason, iterations=state.budget.iterations)
        research_log("finalized", status=state.status, iterations=state.budget.iterations, reason=state.finalize_reason or "",
                     missing="; ".join(missing), research_decision=state.research_decision or "")
        return state

    def _execute(self, state: ResearchState, decision: Decision) -> None:
        ui_phases = ACTION_UI_PHASES.get(decision.action, [])
        for name in ui_phases:
            state.phase(name).attempts += 1
        self._sync_phases(state, running=ui_phases)
        self.ws.save_state(state)
        self.ws.append_event("decision", decision.phase, **self._decision_event(decision))
        self.ws.append_event("phase_start", ui_phases[0] if ui_phases else None, title=f"{decision.action}: {decision.focus or decision.reason}"[:200],
                             action=decision.action, loop_phase=decision.phase)

        before = Snapshot.take(self.ws)
        before_u = {u.id: u for u in self.ws.uncertainties()}
        before_dirs = len(self.ws.directions())
        tools_used: list[str] = []
        critique_round = state.critiques + 1
        prompt = build_prompt(self.ws, self.settings, decision, self.toolkit.get_research_state(), critique_round)
        outcome = self._run_with_retries(state, decision, prompt, ui_phases[0] if ui_phases else decision.action.lower(), tools_used)
        after = Snapshot.take(self.ws)
        changes = state_changes(before, after)
        gain = information_gain(changes)

        state.budget.iterations += 1
        state.budget.tool_calls += outcome.tool_calls
        state.budget.failed_tool_calls += outcome.failed_tool_calls
        state.budget.seconds += outcome.duration_s
        state.budget.tokens += usage_tokens(outcome.usage)
        for name in ui_phases:
            state.phase(name).tool_calls += outcome.tool_calls
            state.phase(name).failed_tool_calls += outcome.failed_tool_calls
        if decision.action == "CRITIQUE" and after.critique != before.critique:
            state.critiques += 1
            state.papers_at_last_critique = after.papers

        advanced, summary = progress(decision.action, before, after, decision.focus_id)
        key = f"{decision.action}:{decision.focus_id or ''}"
        if advanced:
            state.no_progress.pop(key, None)
        else:
            state.no_progress[key] = state.no_progress.get(key, 0) + 1
            if state.no_progress[key] >= self.settings.investigation.max_action_retries:
                self._block(state, decision, key)
        self._track_uncertainty(decision)
        if outcome.error:
            summary += f"; runtime note: {outcome.error[:200]}"
        self._record(state, decision.model_copy(update={"outcome": summary, "tools_used": sorted(set(tools_used)), "state_changes": changes,
                                                        "info_gain": gain}), announce=False)
        self._log_changes(before_u, before_dirs)
        self._sync_phases(state)
        self.ws.save_state(state)
        self.ws.append_event("phase_end", ui_phases[0] if ui_phases else None, status="complete" if advanced else "no_progress",
                             action=decision.action, outcome=summary, missing=[] if advanced else [f"{decision.action} made no recorded progress"])
        research_log("result", action=decision.action, progressed=advanced, info_gain=gain, tools=",".join(sorted(set(tools_used))), outcome=summary,
                     papers=after.papers, open_uncertainties=sum(1 for _, s in after.uncertainties if s in ("open", "partially_resolved")))
        if outcome.usage:
            self.ws.append_event("info", decision.phase, message="token usage", usage=outcome.usage, duration_s=outcome.duration_s)

    def _run_with_retries(self, state: ResearchState, decision: Decision, prompt: str, phase_label: str,
                          tools_used: list[str] | None = None) -> RunOutcome:
        inv = self.settings.investigation
        outcome = RunOutcome(ok=False, session_id=None, error="not run")
        for attempt in range(inv.runtime_retries + 1):
            outcome = self.runtime.run_phase(
                self.ws, prompt, phase=phase_label, session_id=state.dsh_session_id,
                on_event=lambda kind, data: self._on_event(decision, kind, data, tools_used),
            )
            if outcome.session_id:
                state.dsh_session_id = outcome.session_id
            if outcome.ok or outcome.tool_calls > 0:
                return outcome
            state.budget.runtime_failures += 1
            self.ws.append_event("warning", decision.phase, message=f"agent runtime failed ({outcome.error}); attempt {attempt + 1} of {inv.runtime_retries + 1}")
            research_log("runtime failure", action=decision.action, attempt=attempt + 1, error=outcome.error or "")
            if attempt < inv.runtime_retries:
                self.sleep(inv.runtime_retry_backoff_s * (2 ** attempt))
        state.phase(ACTION_UI_PHASES.get(decision.action, [phases.PHASE_NAMES[0]])[0]).notes.append((outcome.error or "")[:500])
        raise InvestigationAborted(f"agent runtime failed during {decision.action} after {inv.runtime_retries + 1} attempts: {outcome.error}")

    def _on_event(self, decision: Decision, kind: str, data: dict, tools_used: list[str] | None) -> None:
        if kind == "tool_call" and tools_used is not None and data.get("tool"):
            tools_used.append(str(data["tool"]))
            research_log("tool_invocation", action=decision.action, tool=data["tool"])
        self.ws.append_event(kind, decision.phase, **data)

    def _close_investigation(self, state: ResearchState, reason: str) -> None:
        """End uncertainty investigation: remaining open questions are reported as unresolved, with the reason."""
        now = utcnow()
        left = []
        for u in self.ws.uncertainties():
            if u.status in ("open", "partially_resolved") and (state.investigation_closed_at is None or u.created_at > state.investigation_closed_at):
                self.ws.save_uncertainty(u.model_copy(update={"status": "unresolved", "resolution": u.resolution or f"Left open: {reason}."}))
                left.append(u.id)
        state.investigation_closed, state.investigation_closed_at = reason, now
        self.ws.save_state(state)
        self.ws.append_event("warning", "UNCERTAINTY", message=f"investigation closed: {reason}", left_unresolved=left)
        research_log("stopping_decision", scope="investigation", reason=reason, left_unresolved=",".join(left))

    def _log_changes(self, before_u: dict, before_dirs: int) -> None:
        for u in self.ws.uncertainties():
            old = before_u.get(u.id)
            if old is None:
                research_log("uncertainty_added", uncertainty=u.id, importance=u.importance, category=u.category, raised_by=u.source or "model")
                continue
            if old.status != u.status:
                research_log("uncertainty_status", uncertainty=u.id, before=old.status, after=u.status, verdict=u.challenge_verdict or "")
            if old.confidence != u.confidence:
                research_log("confidence_change", uncertainty=u.id, before=old.confidence, after=u.confidence, basis=u.confidence_basis)
        for d in self.ws.directions()[before_dirs:]:
            research_log("direction_change", direction=d.id, change_type=d.change_type, previous=d.previous_direction_id or "original idea",
                         confidence=d.confidence, rationale=d.rationale)
            self.ws.append_event("info", "REFINE", message=f"direction {d.id}: {d.change_type} ({d.confidence} confidence)", direction=d.id)

    def _block(self, state: ResearchState, decision: Decision, key: str) -> None:
        if key in state.blocked_actions:
            return
        state.blocked_actions.append(key)
        what = f"{decision.action}" + (f" for {decision.focus}" if decision.focus else "")
        self.ws.save_uncertainty(Uncertainty(
            question=f"Could not complete {what} after {self.settings.investigation.max_action_retries} attempts without recorded progress.",
            importance="medium", status="unresolved", next_action="SEARCH" if decision.action == "SEARCH" else "VERIFY",
            rationale="Raised by the controller; the step was skipped and the investigation continued with other actions.",
            source="controller",
        ))
        if decision.focus_id:
            u = self.ws.uncertainty(decision.focus_id)
            if u and u.status in ("open", "partially_resolved"):
                self.ws.save_uncertainty(u.model_copy(update={"status": "unresolved", "resolution": u.resolution or "Investigation step made no progress; left unresolved."}))
        self.ws.append_event("warning", decision.phase, message=f"blocked {what}: no progress after repeated attempts; choosing another action")
        research_log("action blocked", action=decision.action, focus=decision.focus or "")

    def _track_uncertainty(self, decision: Decision) -> None:
        if not decision.focus_id:
            return
        u = self.ws.uncertainty(decision.focus_id)
        if u is None:
            return
        u = u.model_copy(update={"attempts": u.attempts + 1})
        if u.status in ("open", "partially_resolved") and u.attempts >= self.settings.investigation.max_uncertainty_attempts:
            u = u.model_copy(update={"status": "unresolved", "resolution": u.resolution or "Not resolved within the investigation's attempt budget."})
            research_log("uncertainty unresolved", uncertainty=u.id)
        self.ws.save_uncertainty(u)

    def _record(self, state: ResearchState, decision: Decision, announce: bool = True) -> None:
        state.decisions.append(decision)
        if announce:
            self.ws.append_event("decision", decision.phase, **self._decision_event(decision))
        self.ws.save_state(state)

    @staticmethod
    def _decision_event(d: Decision) -> dict:
        return {"iteration": d.iteration, "action": d.action, "focus": d.focus, "reason": d.reason,
                "evidence": d.evidence, "expected": d.expected_outcome, "outcome": d.outcome,
                "candidates": [{"action": c.action, "uncertainty": c.uncertainty_id, "score": c.score} for c in d.candidates[:4]]}

    def _report(self, state: ResearchState, final: bool = True) -> None:
        ph = state.phase(REPORT_PHASE)
        ph.status, ph.started_at = "running", utcnow()
        self.ws.save_state(state)
        self.ws.append_event("phase_start", REPORT_PHASE, title="Final report")
        paths = report.write_reports(self.ws, self.settings)
        ph.status = "complete" if final else "incomplete"
        ph.finished_at = utcnow()
        self.ws.save_state(state)
        self.ws.append_event("phase_end", REPORT_PHASE, status=ph.status, files=[str(p) for p in paths])


def investigate(ws: Workspace, settings: Settings, runtime: AgentRuntime, stop: threading.Event | None = None,
                sleep: Callable[[float], None] = time.sleep) -> ResearchState:
    return ResearchOrchestrator(ws, settings, runtime, stop=stop, sleep=sleep).run()
