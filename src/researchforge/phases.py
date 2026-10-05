"""Investigation phases: what each phase asks of the agent and how completion is checked.

A phase is complete only when the workspace contains the records its gate
requires. The model's prose is never taken as evidence of completion.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass

from researchforge.config import Settings
from researchforge.workspace import Workspace

TOOL_PREFIX = "mcp__researchforge__"

PERSONA = """You are ResearchForge, an autonomous research investigation agent powered by the {{model}} model.

Your job is not simply to answer the user's research question. Your job is to investigate it. Treat every research idea as a hypothesis that requires evidence, and keep the research state explicit by recording it with the tools.

At every step ask: What do I know? What evidence supports it? What evidence contradicts it? What remains uncertain? Which uncertainty matters most? What action would most usefully reduce it, and at what cost? Is more investigation still worthwhile? Record open questions with record_uncertainty so the investigation can pursue the most important one; ResearchForge chooses each next step from that state and tells you why.

Use tools rather than memory when facts need verification. Search broadly enough to find the relevant existing work, and actively search for contradictory evidence. Do not claim novelty without evidence: say "no directly matching work was found in the searched literature" and state what was searched.

Distinguish clearly between evidence (a verified verbatim quote from a retrieved paper), inference (reasoning from cited evidence), hypothesis (proposed, untested), assumption (taken as given; record it as kind "assumption"), speculation (do not record it as a finding), and experimental results (only from executed, verified runs).

When evidence contradicts the original idea, change the research direction rather than bending the evidence: refine the question, modify the hypothesis, narrow the contribution, or reject the direction (record_direction). You may conclude that the idea is already well explored, that evidence is insufficient, that the hypothesis is unsupported, or that the contribution needs modification. Your objective is not to make the idea look promising; it is the most evidence-supported assessment possible.

Never fabricate papers, citations, quotes, experimental or benchmark results, tool outputs, or claims of novelty.

Operating rules:
- Use only the research tools (named mcp__researchforge__*). Your text replies are NOT saved; results exist only when recorded with a record_* tool.
- Cite only paper ids returned by search_papers, list_papers or expand_citations.
- Similarity and relevance scores are heuristic signals, not proof of novelty or overlap. Explain their basis.
- If a tool returns an error, read it and correct the call; do not repeat the same failing call.
- Do not repeat searches you have already run; check get_research_state.""".strip()

PERSONA_SUFFIX = "The investigation workspace is {{cwd}}."


@dataclass(frozen=True)
class PhaseSpec:
    name: str
    title: str
    instructions: str
    check: Callable[[Workspace, Settings], list[str]]

    def prompt(self, ws: Workspace, settings: Settings, digest: dict, missing: list[str] | None = None) -> str:
        parts = [f"# ResearchForge phase: {self.title}", ""]
        if missing:
            parts += [
                "This phase is NOT complete yet. The workspace is still missing:",
                *[f"- {m}" for m in missing],
                "Record the missing items now with the record_* tools.",
                "",
            ]
        parts += [
            f"Research idea: {ws.raw_idea}",
            "",
            self.instructions.format(
                min_papers=settings.investigation.min_papers,
                min_queries=settings.investigation.min_queries,
                papers_to_analyze=settings.investigation.papers_to_analyze,
                min_mods=settings.investigation.min_modifications,
                max_mods=settings.investigation.max_modifications,
            ).strip(),
            "",
            "Current investigation state (from the workspace):",
            "```json",
            json.dumps(digest, indent=1, default=str)[:12000],
            "```",
            "",
            "When the phase requirements are recorded, reply with a two-sentence summary of what you recorded.",
        ]
        return "\n".join(parts)


# ---------------------------------------------------------------- gates


def _check_formalize(ws: Workspace, s: Settings) -> list[str]:
    idea = ws.idea_analysis()
    if idea is None:
        return ["idea analysis (call record_idea_analysis)"]
    if len(set(idea.search_queries)) < 2:
        return ["at least two distinct search queries in the idea analysis"]
    return []


def _topical_searches(ws: Workspace) -> set[str]:
    return {r.query.lower() for r in ws.searches() if not r.query.startswith(("references of ", "citations of "))}


def _check_literature(ws: Workspace, s: Settings) -> list[str]:
    missing = []
    n = ws.paper_count()
    if n < s.investigation.min_papers:
        missing.append(f"at least {s.investigation.min_papers} retrieved papers (have {n}); run more search_papers queries")
    q = len(_topical_searches(ws))
    if q < s.investigation.min_queries:
        missing.append(f"at least {s.investigation.min_queries} distinct search queries (have {q})")
    return missing


def _analysis_target(ws: Workspace, s: Settings) -> int:
    return min(s.investigation.papers_to_analyze, ws.paper_count())


def _check_analysis(ws: Workspace, s: Settings) -> list[str]:
    if not ws.paper_count():
        return ["retrieved papers to analyze (none were retrieved; run search_papers)"]
    have, target = ws.analysis_count(), _analysis_target(ws, s)
    if have < target:
        return [f"paper analyses for at least {target} of the most relevant papers (have {have}); call record_paper_analysis"]
    return []


def _check_landscape(ws: Workspace, s: Settings) -> list[str]:
    return [] if ws.landscape() else ["research landscape (call record_landscape)"]


def _check_critique(ws: Workspace, s: Settings) -> list[str]:
    missing = []
    if ws.critique() is None:
        missing.append("critique (call record_critique)")
    claims = [c for c in ws.claims() if c.kind in ("evidence", "inference")]
    if len(claims) < 2:
        missing.append(f"at least 2 evidence or inference claims (have {len(claims)}); call record_claim")
    if not any(i.verified for c in claims for i in c.evidence):
        missing.append("at least one claim backed by a verified quote from a retrieved paper")
    return missing


def _check_gaps(ws: Workspace, s: Settings) -> list[str]:
    if ws.gaps() or ws.no_gap():
        return []
    return ["at least one evidence-linked gap (record_gap), or record_no_gap if the evidence supports none"]


def _check_modifications(ws: Workspace, s: Settings) -> list[str]:
    n = len(ws.modifications())
    if n < s.investigation.min_modifications:
        return [f"at least {s.investigation.min_modifications} modifications (have {n}); call record_modification"]
    return []


def _check_experiments(ws: Workspace, s: Settings) -> list[str]:
    return [] if ws.plans() else ["at least one experiment plan (call record_experiment_plan)"]


# ---------------------------------------------------------------- phase prompts

FORMALIZE = """
Goal: formalize the idea into a testable research question.

1. Decompose the idea into problem, target domain, proposed mechanism, hypothesis, expected contribution, assumptions, and independent/dependent/control variables.
2. List ambiguities (e.g. which metric, workload, model, baseline). Resolve what you reasonably can with a quick search_papers call and mark resolved_by="literature"; otherwise make an explicit assumption (resolved_by="assumption") or leave it "unresolved". Do not ask the user.
3. Write a single testable research_question, keywords, and at least 3 diverse search_queries (synonyms, the mechanism, the problem, the evaluation setting).
4. Call record_idea_analysis.
"""

LITERATURE = """
Goal: retrieve the literature most relevant to the idea.

1. Run search_papers for each planned query and for new formulations suggested by what you find (named methods, alternative terminology). Aim for at least {min_papers} papers from at least {min_queries} distinct queries.
2. For the 2-3 most relevant papers, call expand_citations (direction "citations" for follow-up work, "references" for foundations) to find closely related work that keyword search misses.
3. Prefer finding the CLOSEST existing work over collecting many loosely related papers.
"""

ANALYSIS = """
Goal: analyze the {papers_to_analyze} most relevant retrieved papers (use list_papers with only_unanalyzed=true).

For each paper call record_paper_analysis with: problem, method, key assumptions, contribution, datasets, benchmarks, baselines, metrics, results, limitations, future work, code availability, and relation_to_idea (problem/method/evaluation overlap in [0,1] with the basis for each value, and the conceptual difference).
- Mark relevance_tier honestly; "not_relevant" is allowed.
- For the closest 2-3 papers, call fetch_paper_text and search_paper_text to read the method and limitations, set analyzed_from="full_text", and check implementation evidence with search_github / inspect_repository (pass paper_id).
- Do not fill fields you cannot support from the abstract or text; write "not stated in abstract" instead.
"""

LANDSCAPE = """
Goal: map the research area.

Call record_landscape with: a taxonomy of categories (with parent links for sub-categories) that reference analyzed paper ids, where the proposed idea sits, dominant approaches, common assumptions, datasets, benchmarks and metrics, limitations repeated across papers (with paper ids), underexplored combinations, and contradictions between papers (with paper ids). Use get_records("analyses") to review analyses.
"""

CRITIQUE = """
Goal: try to disprove or weaken the idea.

1. Record the key findings as claims with record_claim: kind "evidence" for statements supported by a verbatim quote (support "direct"), kind "inference" for your conclusions drawn from cited papers. Record at least: the closest existing work and how it overlaps; the main technical risk; the main experimental confounder.
2. Answer the novelty, technical-validity, experimental-validity and practicality questions (e.g. has essentially the same idea been proposed? is the difference only implementation-level? what confounders could produce the claimed result? are baselines strong and budgets matched? is it feasible?). Link each point to claim ids and paper ids.
3. Call record_critique with: strongest argument for, strongest argument against, most important unresolved question, most dangerous confounder, closest paper ids with explanation, potential contribution, overlap and distinction summaries, and overall_status (promising_needs_validation | substantial_overlap | weak_or_flawed | insufficient_evidence) with its rationale.
"""

GAPS = """
Goal: identify research gaps that are supported by evidence.

For each gap call record_gap with: the gap, evidence items citing retrieved papers (quote where possible), related paper ids, why existing work does not address it, a research question, a potential experiment, confidence, and what verification is still required (e.g. searching more recent literature). Do not invent gaps without evidence. If the evidence supports no gap, call record_no_gap with the rationale and papers.
"""

MODIFICATIONS = """
Goal: propose {min_mods}-{max_mods} concrete modifications that would make the idea stronger or more distinct, especially where it overlaps with existing work.

For each call record_modification with: title, description, why it differs from the closest work, technical mechanism, expected benefit, potential novelty (hedged), implementation and experimental difficulty (low/moderate/high) each with the basis for the rating, main risk, required baselines, related paper ids and gap ids. Mark the strongest direction recommended=true. Do not use numeric scores.
"""

EXPERIMENTS = """
Goal: design an experiment plan for the most promising direction.

Call record_experiment_plan with: research question, hypothesis, proposed method, baselines (strong and budget-matched), datasets, workloads, hardware, software environment, metrics, ablations, controls, confounders addressed, expected outcomes, failure conditions (what result would falsify the hypothesis), reproducibility notes, related modification id and paper ids.
Only if an open implementation exists and a small, safe experiment is feasible, add an `execution` spec (repo_url, setup commands, arms with role baseline/method/ablation whose command writes JSON metrics to $RF_RESULTS_FILE, expected_metrics, higher_is_better, sample_count_key). Execution never runs without human approval.
"""


PHASES: tuple[PhaseSpec, ...] = (
    PhaseSpec("formalize", "Formalizing the idea", FORMALIZE, _check_formalize),
    PhaseSpec("literature", "Literature investigation", LITERATURE, _check_literature),
    PhaseSpec("analysis", "Paper analysis", ANALYSIS, _check_analysis),
    PhaseSpec("landscape", "Research landscape", LANDSCAPE, _check_landscape),
    PhaseSpec("critique", "Critical analysis", CRITIQUE, _check_critique),
    PhaseSpec("gaps", "Research gap discovery", GAPS, _check_gaps),
    PhaseSpec("modifications", "Research modification", MODIFICATIONS, _check_modifications),
    PhaseSpec("experiments", "Experiment design", EXPERIMENTS, _check_experiments),
)
PHASE_NAMES = tuple(p.name for p in PHASES)


def get(name: str) -> PhaseSpec:
    for p in PHASES:
        if p.name == name:
            return p
    raise KeyError(name)
