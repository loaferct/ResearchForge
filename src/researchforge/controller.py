"""The research controller: choose the next action from the research state.

Selection happens in two tiers.

1. **Coverage prerequisites.** Formalize, plan, reach minimum literature, read,
   map the field and critique once. Nothing can be judged before these exist;
   a prerequisite that is already satisfied is skipped.
2. **Uncertainty-driven investigation.** Every open uncertainty contributes one
   candidate per action that could reduce it. Candidates are scored with

       score = importance * expected_gain * relevance * deficiency / cost

   and the best one is executed. The terms come from recorded state or explicit
   configuration, never from invented numbers:

   * importance: the uncertainty's recorded importance (high 3, medium 2, low 1);
   * relevance: fixed weight of its category (novelty, overlap and contradiction
     questions bear most directly on the research assessment);
   * deficiency: how much evidence is still missing (no linked evidence 1.0,
     one-sided evidence 0.6, both supporting and contradicting evidence 0.35;
     x0.7 when partially resolved);
   * expected_gain: a documented prior per action, blended with the information
     gain that action type actually produced earlier in this investigation, and
     halved for each earlier attempt of the same action on the same question;
   * cost: the configured relative cost of the action.

   Investigation stops when returns diminish (``diminishing_window`` steps with
   no observed information gain) or the best candidate scores below
   ``min_action_score``; the remaining questions are then reported as
   unresolved. Refinement, experiment design and analysis follow, and new
   questions they raise (for example a contradicted conclusion or a failed
   experiment) reopen investigation.

The controller also creates questions of its own: it challenges the critique,
each gap and each new direction with a contradictory-evidence search, and turns
weakened conclusions and unsupported experiments into refinement questions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from researchforge import phases
from researchforge.actions import ACTION_PHASE
from researchforge.config import Settings
from researchforge.literature.sources import query_terms
from researchforge.schemas import Candidate, Decision, ResearchState, Uncertainty, utcnow
from researchforge.workspace import Workspace

IMPORTANCE_RANK = {"high": 0, "medium": 1, "low": 2}
IMPORTANCE_WEIGHT = {"high": 3.0, "medium": 2.0, "low": 1.0}
BLOCKING_IMPORTANCE = ("high", "medium")
CATEGORY_RELEVANCE = {
    "novelty": 1.0, "overlap": 1.0, "contradiction": 1.0, "validity": 0.9, "confounder": 0.9,
    "direction": 0.9, "evaluation": 0.8, "feasibility": 0.7, "other": 0.6,
}
# Prior expected information gain per action (0-1), used until this investigation has observed the action.
PRIOR_GAIN = {
    "SEARCH": 0.6, "READ": 0.5, "COMPARE": 0.6, "VERIFY": 0.6, "CHALLENGE": 0.7, "INVESTIGATE_GAP": 0.7,
    "REFINE": 0.5, "PLAN_EXPERIMENT": 0.4,
}
INVESTIGATION_ACTIONS = tuple(PRIOR_GAIN)
RELEVANT_PAPER = 0.2  # heuristic relevance at or above which a new paper counts toward information gain


# ---------------------------------------------------------------- observation


@dataclass(frozen=True)
class Snapshot:
    papers: int
    relevant_papers: int
    searches: int
    analyses: int
    claims: int
    verified_claims: int
    landscape: str | None
    critique: str | None
    gaps: int
    no_gap: bool
    modifications: int
    directions: int
    plans: int
    evaluations: int
    idea: bool
    plan: bool
    uncertainties: tuple  # (id, status) per uncertainty
    contradicted: int  # uncertainties with contradicting evidence or a weakened/refuted challenge verdict

    @classmethod
    def take(cls, ws: Workspace) -> "Snapshot":
        lan, cri = ws.landscape(), ws.critique()
        papers, claims, us = ws.papers(), ws.claims(), ws.uncertainties()
        return cls(
            papers=len(papers), relevant_papers=sum(1 for p in papers if p.relevance >= RELEVANT_PAPER),
            searches=len(ws.searches()), analyses=len(ws.analyses()),
            claims=len(claims), verified_claims=sum(1 for c in claims if any(i.verified for i in c.evidence)),
            landscape=lan.recorded_at.isoformat() if lan else None, critique=cri.recorded_at.isoformat() if cri else None,
            gaps=len(ws.gaps()), no_gap=ws.no_gap() is not None, modifications=len(ws.modifications()),
            directions=len(ws.directions()), plans=len(ws.plans()), evaluations=len(ws.evaluations()),
            idea=ws.idea_analysis() is not None, plan=ws.investigation_plan() is not None,
            uncertainties=tuple((u.id, u.status) for u in us),
            contradicted=sum(1 for u in us if u.contradicting_paper_ids or u.challenge_verdict in ("weakened", "refuted")),
        )


def summarize(s: Snapshot) -> str:
    return (f"{s.papers} papers from {s.searches} searches, {s.analyses} analyzed, {s.claims} claims ({s.verified_claims} verified), "
            f"{sum(1 for _, st in s.uncertainties if st in ('open', 'partially_resolved'))} open uncertainties")


def state_changes(before: Snapshot, after: Snapshot) -> dict[str, int]:
    fields = ("papers", "relevant_papers", "searches", "analyses", "claims", "verified_claims", "gaps", "modifications",
              "directions", "plans", "evaluations", "contradicted")
    out = {f: getattr(after, f) - getattr(before, f) for f in fields if getattr(after, f) != getattr(before, f)}
    before_status = dict(before.uncertainties)
    new_u = [uid for uid, _ in after.uncertainties if uid not in before_status]
    resolved = [uid for uid, st in after.uncertainties if st == "resolved" and before_status.get(uid) != "resolved"]
    if new_u:
        out["uncertainties_created"] = len(new_u)
    if resolved:
        out["uncertainties_resolved"] = len(resolved)
    for flag in ("landscape", "critique"):
        if getattr(after, flag) != getattr(before, flag):
            out[f"{flag}_recorded"] = 1
    if after.idea and not before.idea:
        out["idea_formalized"] = 1
    if after.plan and not before.plan:
        out["plan_recorded"] = 1
    return out


def information_gain(changes: dict[str, int]) -> float:
    """Observed information gain of a step.

    0.5 per new relevant paper (at most 2.0), 0.5 per new analysis, 1 per newly
    verified claim, 2 per resolved uncertainty, 2 per newly contradicted
    conclusion, 1 per new structural record (idea, plan, landscape, critique,
    direction, experiment plan, hypothesis evaluation). Unverified claims and
    irrelevant papers count for nothing.
    """
    g = min(2.0, 0.5 * max(0, changes.get("relevant_papers", 0)))
    g += 0.5 * max(0, changes.get("analyses", 0))
    g += 1.0 * max(0, changes.get("verified_claims", 0))
    g += 2.0 * changes.get("uncertainties_resolved", 0)
    g += 2.0 * max(0, changes.get("contradicted", 0))
    for k in ("idea_formalized", "plan_recorded", "landscape_recorded", "critique_recorded", "directions", "plans", "evaluations"):
        g += 1.0 * max(0, min(1, changes.get(k, 0)))
    return round(g, 2)


def progress(action: str, before: Snapshot, after: Snapshot, focus_id: str | None) -> tuple[bool, str]:
    """Did the action change the state in the way it is supposed to? Returns (progressed, outcome text)."""
    ch = state_changes(before, after)
    labels = {"papers": "papers", "searches": "searches", "analyses": "analyses", "claims": "claims", "verified_claims": "verified claims",
              "gaps": "gaps", "modifications": "modifications", "directions": "directions", "plans": "experiment plans",
              "evaluations": "hypothesis evaluations", "contradicted": "contradicted conclusions", "uncertainties_created": "uncertainties",
              "uncertainties_resolved": "resolved uncertainties"}
    parts = [f"+{ch[k]} {v}" for k, v in labels.items() if ch.get(k, 0) > 0]
    parts += [t for k, t in (("landscape_recorded", "landscape recorded"), ("critique_recorded", "critique recorded"),
                             ("idea_formalized", "idea formalized"), ("plan_recorded", "investigation plan recorded")) if ch.get(k)]
    before_status = dict(before.uncertainties)
    changed_u = [uid for uid, st in after.uncertainties if uid in before_status and before_status[uid] != st]
    if changed_u:
        parts.append(f"uncertainties updated: {', '.join(changed_u)}")
    expected = {
        "FORMALIZE": after.idea and not before.idea,
        "PLAN": after.plan and not before.plan,
        "SEARCH": after.searches > before.searches or after.papers > before.papers,
        "READ": after.analyses > before.analyses,
        "SYNTHESIZE": after.landscape != before.landscape,
        "CRITIQUE": after.critique != before.critique,
        "COMPARE": after.claims > before.claims or bool(changed_u),
        "VERIFY": after.claims > before.claims or bool(changed_u),
        "CHALLENGE": after.searches > before.searches or after.claims > before.claims or bool(changed_u),
        "INVESTIGATE_GAP": after.searches > before.searches or after.claims > before.claims or bool(changed_u),
        "REFINE": (after.gaps > before.gaps or after.no_gap != before.no_gap or after.modifications > before.modifications
                   or after.directions > before.directions or bool(changed_u)),
        "PLAN_EXPERIMENT": after.plans > before.plans,
        "ANALYZE_RESULTS": after.evaluations > before.evaluations,
    }.get(action, bool(parts))
    if focus_id and (focus_id in changed_u or after.claims > before.claims or after.papers > before.papers):
        # Working on an open question: new evidence or an update to the question counts as progress.
        expected = True
    return bool(expected), ("; ".join(parts) if parts else "no recorded change")


# ---------------------------------------------------------------- budgets and uncertainty helpers


def budget_exhausted(state: ResearchState, settings: Settings, ws: Workspace) -> str | None:
    inv, b = settings.investigation, state.budget
    if b.iterations >= inv.max_iterations:
        return f"iteration budget reached ({inv.max_iterations})"
    if b.tool_calls >= inv.max_tool_calls:
        return f"tool-call budget reached ({inv.max_tool_calls})"
    if b.seconds >= inv.time_limit_s:
        return f"time budget reached ({int(inv.time_limit_s)} s)"
    if inv.max_tokens and b.tokens >= inv.max_tokens:
        return f"token budget reached ({inv.max_tokens})"
    return None


def eligible(u: Uncertainty, state: ResearchState) -> bool:
    """Open, and not closed out by an earlier end of investigation."""
    if u.status not in ("open", "partially_resolved"):
        return False
    return state.investigation_closed_at is None or u.created_at > state.investigation_closed_at


def open_uncertainties(ws: Workspace, blocking_only: bool = True) -> list[Uncertainty]:
    items = [u for u in ws.uncertainties() if u.status in ("open", "partially_resolved")]
    if blocking_only:
        items = [u for u in items if u.importance in BLOCKING_IMPORTANCE]
    return sorted(items, key=lambda u: (IMPORTANCE_RANK[u.importance], u.attempts, u.id))


def papers_since_critique(ws: Workspace) -> int:
    """Papers first retrieved after the current critique was recorded (derived from records, so it survives resume)."""
    critique = ws.critique()
    if critique is None:
        return 0
    return sum(1 for p in ws.papers() if p.retrieved_at > critique.recorded_at)


def next_search_topic(ws: Workspace) -> str | None:
    searched = {" ".join(sorted(query_terms(s.query))) for s in ws.searches()}
    plan, idea = ws.investigation_plan(), ws.idea_analysis()
    topics = (plan.search_topics if plan else []) + (idea.search_queries if idea else [])
    return next((t for t in topics if " ".join(sorted(query_terms(t))) not in searched), None)


# ---------------------------------------------------------------- controller-raised questions


def raise_questions(ws: Workspace, settings: Settings, state: ResearchState) -> list[Uncertainty]:
    """Create the questions the controller itself insists on. Returns the new ones.

    * challenge the critique's assessment, each gap and each new direction with a
      contradictory-evidence search (once per record);
    * a weakened or refuted conclusion becomes a refinement question;
    * an experiment that did not support the hypothesis, or was inconclusive,
      becomes a follow-up question.
    """
    created: list[Uncertainty] = []
    if settings.investigation.controller_mode == "pipeline":
        return created  # the fixed-pipeline baseline raises no questions of its own
    existing_refs = {u.target_ref for u in ws.uncertainties() if u.target_ref}

    def add(ref: str, **fields) -> None:
        if ref in existing_refs:
            return
        u = ws.save_uncertainty(Uncertainty(source="controller", target_ref=ref, **fields))
        existing_refs.add(ref)
        created.append(u)

    if settings.investigation.challenge_conclusions:
        critique = ws.critique()
        if critique and "critique" not in state.challenged_refs:
            state.challenged_refs.append("critique")
            add("critique", question=f"Does published work contradict the current assessment: {critique.distinction_summary}?",
                description=f"Assessment: {critique.overall_status}. {critique.status_rationale}", category="contradiction",
                importance="high", next_action="CHALLENGE",
                rationale="The assessment was formed from work found around the initial idea; look for work that would invalidate it.")
        for g in ws.gaps():
            if g.id not in state.challenged_refs:
                state.challenged_refs.append(g.id)
                add(g.id, question=f"Has gap {g.id} already been addressed: {g.gap}?", category="novelty", importance="high",
                    next_action="INVESTIGATE_GAP",
                    rationale="A gap is only a hypothesis until a targeted search fails to find work that closes it.")
        directions = ws.directions()
        if directions:
            d = directions[-1]
            if d.id not in state.challenged_refs and d.change_type != "REJECT_DIRECTION":
                state.challenged_refs.append(d.id)
                add(d.id, question=f"Is direction {d.id} already explored or contradicted: {d.direction}?", category="contradiction",
                    importance="high", next_action="CHALLENGE",
                    rationale="A refined direction must be checked against existing work before it is recommended.")

    for u in ws.uncertainties():
        if u.challenge_verdict in ("weakened", "refuted"):
            add(f"refine:{u.id}", question=f"The conclusion behind {u.id} was {u.challenge_verdict} by contradicting work; how should the direction change?",
                description=u.resolution, category="direction", importance="high", next_action="REFINE",
                paper_ids=u.contradicting_paper_ids, rationale="Evidence contradicts the current direction; refine it instead of forcing the evidence to fit.")

    runs = len({r.id for r in ws.runs()})
    for e in ws.evaluations():
        if e.verdict == "NOT_SUPPORTED":
            add(e.plan_id, question=f"Why did experiment {e.plan_id} not support the hypothesis, and what should change?",
                description=e.rationale, category="direction", importance="high", next_action="REFINE", possible_actions=["SEARCH"],
                rationale="An unsupported hypothesis must be revised or rejected, not reported as promising.")
        elif e.verdict == "INCONCLUSIVE":
            actions = ["PLAN_EXPERIMENT"] if runs < settings.investigation.max_experiment_runs else []
            add(e.plan_id, question=f"What would resolve the inconclusive result of experiment {e.plan_id}?", description=e.rationale,
                category="evaluation", importance="medium", next_action="VERIFY", possible_actions=actions,
                rationale="An inconclusive experiment leaves the hypothesis untested.")
    return created


# ---------------------------------------------------------------- scoring


def deficiency(u: Uncertainty) -> float:
    sides = bool(u.supporting_paper_ids) + bool(u.contradicting_paper_ids)
    linked = bool(u.paper_ids or u.claim_ids)
    d = 1.0 if not (sides or linked) else (0.35 if sides == 2 else 0.6)
    return round(d * (0.7 if u.status == "partially_resolved" else 1.0), 3)


def observed_gain(state: ResearchState, action: str) -> list[float]:
    return [min(1.0, d.info_gain / 3.0) for d in state.decisions if d.action == action and d.info_gain is not None]


def expected_gain(action: str, u: Uncertainty, state: ResearchState, ws_papers: int) -> tuple[float, str]:
    prior = PRIOR_GAIN.get(action, 0.4)
    seen = observed_gain(state, action)
    base = (prior + sum(seen)) / (1 + len(seen))
    basis = f"prior {prior}" + (f", observed mean over {len(seen)} earlier {action} steps" if seen else "")
    tried = sum(1 for d in state.decisions if d.focus_id == u.id and d.action == action and d.info_gain is not None)
    if tried:
        base *= 0.5 ** tried
        basis += f", halved for {tried} earlier attempt{'s' if tried > 1 else ''} on {u.id}"
    if action in ("VERIFY", "COMPARE") and not (u.paper_ids or u.supporting_paper_ids or u.contradicting_paper_ids) and ws_papers == 0:
        base *= 0.5
        basis += ", no papers to check yet"
    return round(base, 3), basis


def score_candidates(ws: Workspace, settings: Settings, state: ResearchState) -> list[Candidate]:
    inv = settings.investigation
    blocked = set(state.blocked_actions)
    n_papers, n_searches = len(ws.papers()), len(ws.searches())
    out: list[Candidate] = []
    for u in ws.uncertainties():
        if not eligible(u, state) or u.attempts >= inv.max_uncertainty_attempts:
            continue
        for action in u.actions():
            if f"{action}:{u.id}" in blocked:
                continue
            if action in ("SEARCH", "CHALLENGE", "INVESTIGATE_GAP") and (n_searches >= inv.max_searches or n_papers >= inv.max_papers):
                continue
            if action == "PLAN_EXPERIMENT" and len({r.plan_id for r in ws.runs()}) >= inv.max_experiment_runs:
                continue
            gain, basis = expected_gain(action, u, state, n_papers)
            imp, rel, dfc = IMPORTANCE_WEIGHT[u.importance], CATEGORY_RELEVANCE.get(u.category, 0.6), deficiency(u)
            cost = inv.action_costs.get(action, 1.0)
            out.append(Candidate(action=action, uncertainty_id=u.id, target=u.question, importance=imp, expected_gain=gain,
                                 gain_basis=basis, relevance=rel, deficiency=dfc, cost=cost,
                                 score=round(imp * gain * rel * dfc / cost, 3)))
    # Deterministic order: best score, then higher importance, then lower cost, then older question.
    return sorted(out, key=lambda c: (-c.score, -c.importance, c.cost, c.uncertainty_id or ""))


def explain(c: Candidate) -> str:
    return (f"score {c.score} = importance {c.importance:g} x expected gain {c.expected_gain:g} x relevance {c.relevance:g} "
            f"x evidence deficiency {c.deficiency:g} / cost {c.cost:g}")


def diminishing_returns(state: ResearchState, settings: Settings) -> str | None:
    """No observed information gain over the last ``diminishing_window`` investigation steps."""
    inv = settings.investigation
    steps = [d for d in state.decisions if d.action in INVESTIGATION_ACTIONS and d.focus_id and d.info_gain is not None]
    if state.investigation_closed_at:
        steps = [d for d in steps if d.at > state.investigation_closed_at]
    window = steps[-inv.diminishing_window:]
    if len(window) < inv.diminishing_window:
        return None
    total = sum(d.info_gain or 0 for d in window)
    if total <= inv.diminishing_threshold:
        return f"diminishing returns: the last {len(window)} investigation steps produced {total:g} information gain"
    return None


# ---------------------------------------------------------------- stopping and the research decision


def should_finalize(ws: Workspace, settings: Settings, state: ResearchState) -> tuple[bool, list[str]]:
    """The research stopping condition. Returns (ready, what is still missing)."""
    missing: list[str] = []
    if ws.idea_analysis() is None:
        missing.append("formalized research question")
    if ws.investigation_plan() is None:
        missing.append("investigation plan")
    for name in ("literature", "analysis", "landscape", "critique"):
        missing += phases.get(name).check(ws, settings)
    blocking = [u for u in open_uncertainties(ws) if eligible(u, state)]
    if blocking:
        missing.append(f"{len(blocking)} important open uncertainties ({', '.join(u.id for u in blocking)})")
    if not (ws.gaps() or ws.no_gap()):
        missing.append("evidence-linked gap or no-gap finding")
    if len(ws.modifications()) < settings.investigation.min_modifications:
        missing.append("modifications")
    if not ws.directions():
        missing.append("research direction decision")
    if not ws.plans():
        missing.append("experiment plan")
    evaluated = {e.plan_id for e in ws.evaluations()}
    unevaluated = [a.plan_id for a in ws.experiment_analyses() if a.plan_id not in evaluated]
    if unevaluated:
        missing.append(f"hypothesis evaluation for executed experiments {unevaluated}")
    return (not missing), missing


def research_decision(ws: Workspace, state: ResearchState) -> tuple[str, str]:
    """Describe the state of the evidence (not the absolute worth of the idea).

    Precedence: an experimental verdict; then a rejected direction or a critique
    of substantial overlap; then a changed direction; then missing evidence;
    otherwise the critique's promising assessment.
    """
    evaluations = ws.evaluations()
    if evaluations:
        latest = max(evaluations, key=lambda e: e.recorded_at)
        if latest.verdict == "SUPPORTED":
            return "EXPERIMENTALLY_SUPPORTED", f"experiment {latest.plan_id} passed verification and supported the hypothesis"
        if latest.verdict == "NOT_SUPPORTED":
            return "EXPERIMENTALLY_UNSUPPORTED", f"experiment {latest.plan_id} did not support the hypothesis"
    critique, directions = ws.critique(), ws.directions()
    latest_dir = directions[-1] if directions else None
    if (latest_dir and latest_dir.change_type == "REJECT_DIRECTION") or (critique and critique.overall_status == "substantial_overlap"):
        return "ALREADY_WELL_EXPLORED", "the direction was rejected or the critique found substantial overlap with existing work"
    unresolved_high = [u.id for u in ws.uncertainties() if u.importance == "high" and u.status in ("open", "partially_resolved", "unresolved")]
    if critique is None or critique.overall_status == "insufficient_evidence" or unresolved_high:
        why = "no critique was recorded" if critique is None else (
            "the critique found insufficient evidence" if critique.overall_status == "insufficient_evidence"
            else f"high-importance questions remain unresolved ({', '.join(unresolved_high)})")
        return "INSUFFICIENT_EVIDENCE", why
    if latest_dir and latest_dir.change_type not in ("KEEP_ORIGINAL",):
        return "NEEDS_MODIFICATION", f"evidence led to direction change {latest_dir.change_type} ({latest_dir.id})"
    if critique.overall_status == "weak_or_flawed":
        return "NEEDS_MODIFICATION", "the critique judged the idea weak or flawed as stated"
    return "PROMISING", "the critique judged the idea promising and no contradicting evidence overturned it; still untested experimentally"


# ---------------------------------------------------------------- decision


def _key(action: str, focus_id: str | None = None) -> str:
    return f"{action}:{focus_id or ''}"


def decide_next_action(ws: Workspace, settings: Settings, state: ResearchState) -> Decision:
    """Pick the most useful next action from the current state."""
    inv = settings.investigation
    it = state.budget.iterations + 1
    snap = Snapshot.take(ws)
    ev = summarize(snap)
    blocked = set(state.blocked_actions)

    def make(action: str, reason: str, expected: str = "", focus: str | None = None, focus_id: str | None = None,
             phase: str | None = None, **extra: Any) -> Decision:
        return Decision(iteration=it, phase=phase or ACTION_PHASE[action], action=action, focus=focus, focus_id=focus_id,
                        reason=reason, evidence=ev, expected_outcome=expected, **extra)

    def ok(action: str, focus_id: str | None = None) -> bool:
        return _key(action, focus_id) not in blocked

    exhausted = budget_exhausted(state, settings, ws)
    if exhausted:
        return make("FINALIZE", f"Stopping: {exhausted}.", "Report what was established and what remains open.")

    # ---- tier 1: coverage prerequisites
    if not snap.idea and ok("FORMALIZE"):
        return make("FORMALIZE", "The idea has not been formalized into a testable research question.",
                    "Problem, hypothesis, variables, assumptions and search queries recorded.")
    if not snap.plan and ok("PLAN"):
        return make("PLAN", "No investigation plan exists yet, so it is unclear what must be determined.",
                    "Questions to answer, search topics and initial uncertainties recorded.")
    lit_missing = phases.get("literature").check(ws, settings)
    if lit_missing and ok("SEARCH") and snap.searches < inv.max_searches and snap.papers < inv.max_papers:
        topic = next_search_topic(ws)
        return make("SEARCH", f"Literature coverage is insufficient: {lit_missing[0]}.",
                    "Retrieve the work closest to the idea.", focus=topic or "new terminology for the core mechanism")
    if phases.get("analysis").check(ws, settings) and ok("READ"):
        return make("READ", "Retrieved papers have not been analyzed enough to judge overlap.",
                    "Structured analyses of the most relevant papers.")
    if snap.landscape is None and ok("SYNTHESIZE"):
        return make("SYNTHESIZE", "Analyses exist but the field has not been mapped.", "A landscape placing the idea among approaches.")
    if snap.critique is None and ok("CRITIQUE"):
        return make("CRITIQUE", "The idea has not been challenged yet.", "Strongest objections recorded as critique and uncertainties.")

    if inv.controller_mode == "pipeline":
        return _pipeline_tail(ws, settings, state, snap, make, ok)

    # ---- a critique written before contradicting evidence arrived is stale: revise the assessment first
    critique = ws.critique()
    if critique and inv.recritique_on_contradiction and max(state.critiques, 1) < inv.max_critiques and ok("CRITIQUE"):
        contradicted = [u for u in ws.uncertainties()
                        if u.challenge_verdict in ("weakened", "refuted") and u.updated_at > critique.recorded_at]
        if contradicted:
            what = ", ".join(f"{u.id} {u.challenge_verdict}" for u in contradicted)
            return make("CRITIQUE", f"The current critique predates contradicting evidence ({what}); the assessment must be revised before continuing.",
                        "A critique that accounts for the contradicting work.", focus="; ".join(u.question for u in contradicted)[:300])

    # ---- the first assessment is challenged before budget goes anywhere else (docs/paper/research_plan.md §10)
    if inv.challenge_conclusions and ok("CHALLENGE"):
        first = next((u for u in ws.uncertainties() if u.source == "controller" and u.target_ref == "critique"
                      and u.status in ("open", "partially_resolved") and u.attempts == 0), None)
        if first is not None and ok("CHALLENGE", first.id):
            return make("CHALLENGE", f"The critique's assessment has not been challenged yet ({first.id}); look for published work that "
                        "contradicts it before investing in anything that builds on it.",
                        f"Evidence that confirms, weakens or refutes the assessment ({first.id}).", focus=f"{first.id}: {first.question}",
                        focus_id=first.id, phase="CHALLENGE")

    # ---- tier 2: uncertainty-driven investigation
    closing: str | None = None
    candidates = score_candidates(ws, settings, state)
    if candidates:
        dim = diminishing_returns(state, settings)
        best = candidates[0]
        if dim:
            closing = dim
        elif best.score < inv.min_action_score:
            closing = f"further investigation judged not worthwhile: best candidate {best.action} on {best.uncertainty_id} scores {best.score} < {inv.min_action_score}"
        else:
            u = ws.uncertainty(best.uncertainty_id or "")
            assert u is not None  # candidates are built from recorded uncertainties
            runner_up = f" Next best: {candidates[1].action} on {candidates[1].uncertainty_id} ({candidates[1].score})." if len(candidates) > 1 else ""
            return make(best.action,
                        f"Most valuable next step for {u.importance}-importance {u.category} question {u.id}: {explain(best)}.{runner_up}",
                        f"Evidence that resolves or narrows {u.id}.", focus=f"{u.id}: {u.question}", focus_id=u.id,
                        phase="CHALLENGE" if best.action in ("CHALLENGE", "INVESTIGATE_GAP") else "UNCERTAINTY",
                        candidates=candidates[:6], expected_gain=best.expected_gain, estimated_cost=best.cost)

    extra: dict[str, Any] = {"closes_investigation": closing, "candidates": candidates[:6]} if closing else {}
    closed_note = f" Investigation closed ({closing})." if closing else ""

    if (max(state.critiques, 1) < inv.max_critiques and papers_since_critique(ws) >= inv.recritique_after_papers and ok("CRITIQUE")):
        return make("CRITIQUE", f"{papers_since_critique(ws)} papers arrived since the last critique.{closed_note}",
                    "Critique revised against the new evidence.", **extra)

    # ---- after investigation: refine, design, analyze
    if (not (snap.gaps or snap.no_gap) or snap.modifications < inv.min_modifications or snap.directions == 0) and ok("REFINE"):
        return make("REFINE", f"The findings have not yet been turned into gaps, modifications and a direction decision.{closed_note}",
                    "Evidence-linked gaps, 2-5 modifications and a recorded direction decision.", **extra)
    if snap.plans == 0 and ok("PLAN_EXPERIMENT"):
        return make("PLAN_EXPERIMENT", f"A research direction exists but no experiment would test it.{closed_note}",
                    "An experiment plan with baselines, metrics, controls and falsifying outcomes.", **extra)

    evaluated = {e.plan_id for e in ws.evaluations()}
    for a in ws.experiment_analyses():
        if a.plan_id not in evaluated and ok("ANALYZE_RESULTS", a.plan_id):
            return make("ANALYZE_RESULTS", f"Experiment {a.plan_id} finished ({a.status}) but the hypothesis has not been re-evaluated.{closed_note}",
                        "SUPPORTED, NOT_SUPPORTED or INCONCLUSIVE with rationale.", focus=a.plan_id, focus_id=a.plan_id, **extra)

    ran = {r.plan_id for r in ws.runs()}
    pending = [p.id for p in ws.plans() if p.execution is not None and p.status == "awaiting_approval" and p.id not in ran]
    new_pending = [p for p in pending if p not in state.awaiting_approval]
    if new_pending and len(ran) < inv.max_experiment_runs:
        return make("EXPERIMENT", f"Executable experiment {', '.join(new_pending)} requires human approval before it can run.{closed_note}",
                    "Investigation pauses the experiment until approved; the report states it was not performed.",
                    focus=", ".join(new_pending), **extra)

    ready, missing = should_finalize(ws, settings, state)
    if ready or closing:
        reason = ("Finalization criteria met: question formalized, literature investigated, overlap and contradicting work checked, "
                  "important uncertainties investigated, idea critiqued, direction and experiment plan recorded.") if ready and not closing else (
                  f"Stopping investigation: {closing}." + (f" Still missing: {'; '.join(missing)}." if missing else ""))
        return make("FINALIZE", reason, "Final report from the research state.", **extra)
    return make("FINALIZE", f"No further useful action is available within the limits; still missing: {'; '.join(missing)}.",
                "Report marks what could not be established.", **extra)


PIPELINE_EXTRA = "Fixed pipeline: extra search round"


def _pipeline_tail(ws: Workspace, settings: Settings, state: ResearchState, snap: Snapshot, make, ok) -> Decision:
    """The fixed-pipeline baseline after the coverage tier (docs/paper/research_plan.md §5.1, S-pipe / S-pipe+).

    Optional extra search-and-read rounds, one re-critique if they ran, then refine, plan and finalize.
    No uncertainty-driven investigation and no self-challenge. The research decision uses the same rule
    as the adaptive loop, so verdicts are comparable.
    """
    inv = settings.investigation
    extra = [d for d in state.decisions if d.action == "SEARCH" and d.reason.startswith(PIPELINE_EXTRA)]
    last = state.decisions[-1] if state.decisions else None
    if last is not None and last in extra and ok("READ"):
        return make("READ", "Fixed pipeline: read the papers retrieved by the extra search round.", "Analyses of the newly retrieved papers.")
    searches_left = snap.searches < inv.max_searches and snap.papers < inv.max_papers
    if len(extra) < inv.pipeline_extra_searches and searches_left and ok("SEARCH"):
        return make("SEARCH", f"{PIPELINE_EXTRA} {len(extra) + 1} of {inv.pipeline_extra_searches}.",
                    "More work related to the idea.", focus=next_search_topic(ws) or "related work not yet retrieved")
    if extra and state.critiques < 2 and ok("CRITIQUE"):
        return make("CRITIQUE", "Fixed pipeline: critique once more after the extra search rounds.", "Critique revised against the new evidence.")
    if (not (snap.gaps or snap.no_gap) or snap.modifications < inv.min_modifications or snap.directions == 0) and ok("REFINE"):
        return make("REFINE", "Fixed pipeline: turn the findings into gaps, modifications and a direction decision.",
                    "Evidence-linked gaps, 2-5 modifications and a recorded direction decision.")
    if snap.plans == 0 and ok("PLAN_EXPERIMENT"):
        return make("PLAN_EXPERIMENT", "Fixed pipeline: design an experiment for the direction.", "An experiment plan.")
    return make("FINALIZE", "Fixed pipeline complete.", "Final report from the research state.")


__all__ = [
    "Snapshot", "summarize", "state_changes", "information_gain", "progress", "budget_exhausted", "open_uncertainties",
    "papers_since_critique", "next_search_topic", "raise_questions", "score_candidates", "diminishing_returns",
    "should_finalize", "research_decision", "decide_next_action", "utcnow",
]
