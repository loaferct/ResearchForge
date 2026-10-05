"""Prompts for the investigation loop's actions.

Each action is one dsh turn. Where an action matches an existing phase, its
instructions are reused from :mod:`researchforge.phases`; the loop adds the
reason for the step, the focus (usually an open uncertainty) and the duty to
update the uncertainty ledger.
"""

from __future__ import annotations

import json

from researchforge import phases
from researchforge.config import Settings
from researchforge.schemas import Decision
from researchforge.workspace import Workspace

# Loop phase shown to the user for each action (UNCERTAINTY when the action serves an open question).
ACTION_PHASE = {
    "INTAKE": "INTAKE", "FORMALIZE": "FORMALIZE", "PLAN": "PLAN", "SEARCH": "INVESTIGATE", "READ": "INVESTIGATE",
    "COMPARE": "INVESTIGATE", "VERIFY": "INVESTIGATE", "CHALLENGE": "CHALLENGE", "INVESTIGATE_GAP": "CHALLENGE",
    "SYNTHESIZE": "SYNTHESIZE", "CRITIQUE": "CRITIQUE",
    "REFINE": "REFINE", "PLAN_EXPERIMENT": "EXPERIMENT_PLAN", "EXPERIMENT": "EXPERIMENT",
    "ANALYZE_RESULTS": "ANALYZE", "FINALIZE": "FINALIZE",
}

# Existing phase records (UI rail, report completeness) that an action contributes to.
ACTION_UI_PHASES = {
    "FORMALIZE": ["formalize"], "PLAN": ["formalize"], "SEARCH": ["literature"], "READ": ["analysis"],
    "COMPARE": ["critique"], "VERIFY": ["critique"], "CHALLENGE": ["critique"], "INVESTIGATE_GAP": ["gaps"],
    "SYNTHESIZE": ["landscape"], "CRITIQUE": ["critique"],
    "REFINE": ["gaps", "modifications"], "PLAN_EXPERIMENT": ["experiments"], "ANALYZE_RESULTS": ["experiments"],
    "EXPERIMENT": ["experiments"], "FINALIZE": ["report"],
}

PLAN = """
Goal: plan the investigation before gathering evidence.

1. Call record_investigation_plan with: the questions this investigation must answer (at least: which existing methods are closest, whether the idea exists under other terminology, which baselines and evaluation methodology apply, whether it is feasible), search topics including alternative terminology, and known methods to compare against.
2. Record 2-5 initial uncertainties with record_uncertainty. For each give: a category (novelty, overlap, validity, confounder, evaluation, feasibility), an importance (high / medium / low) reflecting how much the answer would change the assessment, the preferred next_action and other possible_actions (SEARCH, READ, COMPARE, VERIFY, CHALLENGE, REFINE, PLAN_EXPERIMENT). Do not state a confidence you cannot justify.
"""

SEARCH = """
Goal: gather literature for the focus below.

Run search_papers with the focus topic and with alternative terminology for it. Follow the citation graph (expand_citations) of the most relevant new paper. Prefer finding the closest existing work over collecting loosely related papers.
"""

COMPARE = """
Goal: compare the idea with specific existing work.

For the papers most relevant to the focus (use list_papers / get_paper; fetch_paper_text and search_paper_text for method details), determine concretely how their mechanism, assumptions and evaluation differ from the idea. Record each finding with record_claim: kind "evidence" with a verbatim quote where the paper states it, kind "inference" for your comparison. Say plainly when the difference is only an implementation detail.
"""

VERIFY = """
Goal: verify claims against full text.

Use fetch_paper_text and search_paper_text on the papers involved in the focus. Record what the text actually says as "evidence" claims with verbatim quotes and page locations. If an earlier claim is not supported by the text, record a corrected claim and lower confidence.
"""

DIRECTION = """
Record the direction decision with record_direction. Choose change_type from what the evidence shows:
- KEEP_ORIGINAL: the evidence supports continuing as proposed;
- REFINE_SCOPE: narrow to where a distinction survives;
- MODIFY_METHOD: change the mechanism;
- CHANGE_RESEARCH_QUESTION (give the new research_question) or CHANGE_HYPOTHESIS;
- REJECT_DIRECTION: the idea is already well explored or contradicted.
Give the rationale, the supporting paper ids, the uncertainty ids that motivated it, and a confidence (low / medium / high). Do not call it the best direction; explain why it deserves investigation next. The original idea stays unchanged.
"""

REFINE = phases.GAPS.strip() + "\n\n" + phases.MODIFICATIONS.strip() + "\n" + DIRECTION

REFINE_FOCUSED = """
Goal: decide how the research direction should change in response to the focus below.

Review the evidence behind the focus: the uncertainties in get_research_state and the claims in get_records("claims"). Add or revise modifications with record_modification (pass an id to revise) only if the evidence calls for it.
""" + DIRECTION

CHALLENGE = """
Goal: try to disprove the conclusion in the focus below. Do not look for support; look for what would invalidate it.

Search (search_papers, expand_citations with direction "citations") for: papers that claim to solve the problem, closely related methods under other names, alternative formulations, negative or contradicting experimental results, and recent work. Read the decisive passages (fetch_paper_text / search_paper_text) and record what they say with record_claim.
Then call record_challenge_result for the focused uncertainty with verdict holds / weakened / refuted, the supporting and contradicting paper ids, and what you searched. "weakened" and "refuted" require contradicting papers that were actually retrieved.
"""

INVESTIGATE_GAP = """
Goal: check whether the gap in the focus below has already been addressed.

Search specifically for work that closes this gap (the exact problem, synonyms, recent preprints, follow-up work of the papers cited as evidence for the gap). Record what you find with record_claim.
Then call record_challenge_result for the focused uncertainty: holds (no work closes the gap in what was searched), weakened (partially addressed) or refuted (already addressed), with the paper ids.
"""

ANALYZE_RESULTS = """
Goal: evaluate the hypothesis against the executed experiment.

The experiment results are in get_research_state (experiment_results) and get_records("experiment_plans"). Call record_hypothesis_evaluation for the plan: SUPPORTED only if verification passed and the result matches the hypothesis, NOT_SUPPORTED if it contradicts it, INCONCLUSIVE otherwise. State the next step.
ResearchForge then raises the follow-up question itself (NOT_SUPPORTED leads to a refinement, INCONCLUSIVE to a further check). Add uncertainties only for other issues the results reveal, for example an unexpected metric.
Never report numbers that are not in the recorded results.
"""

CRITIQUE_LOOP = """

This is critique round {round}. If a critique already exists, revise it with the evidence gathered since (record_critique replaces it).
Record every concern that could change the assessment as an uncertainty with record_uncertainty (category, importance, next action and possible actions). Record what you are taking as given without evidence as claims of kind "assumption". Mark questions that the evidence now answers with update_uncertainty, citing supporting and contradicting papers.
"""

INSTRUCTIONS = {
    "FORMALIZE": phases.FORMALIZE,
    "PLAN": PLAN,
    "SEARCH": SEARCH,
    "READ": phases.ANALYSIS,
    "SYNTHESIZE": phases.LANDSCAPE,
    "COMPARE": COMPARE,
    "VERIFY": VERIFY,
    "CHALLENGE": CHALLENGE,
    "INVESTIGATE_GAP": INVESTIGATE_GAP,
    "CRITIQUE": phases.CRITIQUE,
    "REFINE": REFINE,
    "PLAN_EXPERIMENT": phases.EXPERIMENTS,
    "ANALYZE_RESULTS": ANALYZE_RESULTS,
}


def build_prompt(ws: Workspace, settings: Settings, decision: Decision, digest: dict, critique_round: int = 1) -> str:
    inv = settings.investigation
    template = INSTRUCTIONS[decision.action]
    if decision.action == "REFINE" and decision.focus_id and ws.gaps() and len(ws.modifications()) >= settings.investigation.min_modifications:
        template = REFINE_FOCUSED  # gaps and modifications exist; the question is how the direction should change
    body = template.format(
        min_papers=inv.min_papers, min_queries=inv.min_queries, papers_to_analyze=inv.papers_to_analyze,
        min_mods=inv.min_modifications, max_mods=inv.max_modifications,
    ).strip()
    if decision.action == "CRITIQUE":
        body += CRITIQUE_LOOP.format(round=critique_round)
    parts = [
        f"# ResearchForge step: {decision.action}",
        "",
        f"Research idea: {ws.raw_idea}",
        f"Iteration {decision.iteration} of at most {inv.max_iterations}. Loop phase: {decision.phase}.",
        f"Why this step: {decision.reason}",
    ]
    if decision.expected_outcome:
        parts.append(f"Expected outcome: {decision.expected_outcome}")
    if decision.focus:
        parts += ["", f"Focus: {decision.focus}"]
        if decision.focus_id:
            parts.append(
                f"This step investigates uncertainty {decision.focus_id}. When done, call update_uncertainty(id=\"{decision.focus_id}\", ...) "
                "with what the evidence shows (resolved / partially_resolved with a resolution, or open with a better next_action)."
            )
    parts += [
        "",
        body,
        "",
        "Throughout: record new questions that could change the assessment with record_uncertainty. Do not repeat searches already in the state.",
        "",
        "Current investigation state (from the workspace):",
        "```json",
        json.dumps(digest, indent=1, default=str)[:14000],
        "```",
        "",
        "When the step's records are saved, reply with a two-sentence summary of what you recorded.",
    ]
    return "\n".join(parts)
