"""Deterministic report generation from recorded investigation data.

No model call happens here. Every section is rendered from validated records,
references are drawn only from retrieved paper records, and each statement is
labelled with its epistemic status:

* **[Evidence]** a claim with a verified quote from a retrieved source
* **[Inference]** reasoning derived from cited evidence
* **[Hypothesis]** a proposal not yet validated
* **[Experimental result]** observed in an executed, verified experiment
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import markdown as md

from researchforge.config import Settings
from researchforge.evidence import grounding
from researchforge.schemas import Claim, CritiquePoint, EvidenceItem, Paper
from researchforge.workspace import Workspace, atomic_write_text

STATUS_TEXT = {
    "promising_needs_validation": "Promising but requires experimental validation",
    "substantial_overlap": "Substantial overlap with existing work",
    "weak_or_flawed": "Weak or technically flawed as currently stated",
    "insufficient_evidence": "Insufficient evidence to assess",
}
KIND_LABEL = {
    "evidence": "[Evidence]",
    "inference": "[Inference]",
    "hypothesis": "[Hypothesis]",
    "assumption": "[Assumption]",
    "experimental": "[Experimental result]",
}
DECISION_TEXT = {
    "PROMISING": "Promising (evidence so far supports pursuing it)",
    "NEEDS_MODIFICATION": "Needs modification",
    "ALREADY_WELL_EXPLORED": "Already well explored",
    "INSUFFICIENT_EVIDENCE": "Insufficient evidence",
    "EXPERIMENTALLY_SUPPORTED": "Experimentally supported",
    "EXPERIMENTALLY_UNSUPPORTED": "Experimentally unsupported",
}
NOT_RECORDED = "_Not recorded: this phase did not produce the required records._"


def esc(text: str | None) -> str:
    return (text or "").replace("|", "\\|").replace("\n", " ").strip()


class Citer:
    """Assigns reference numbers in order of first citation."""

    def __init__(self, papers: dict[str, Paper]) -> None:
        self.papers = papers
        self.order: list[str] = []

    def __call__(self, paper_id: str | None) -> str:
        if not paper_id:
            return ""
        if paper_id not in self.papers:
            return f"[unknown paper {paper_id}]"
        if paper_id not in self.order:
            self.order.append(paper_id)
        return f"[{self.order.index(paper_id) + 1}]"

    def many(self, ids: list[str]) -> str:
        return ", ".join(self(i) for i in dict.fromkeys(ids)) if ids else ""

    def title(self, paper_id: str) -> str:
        p = self.papers.get(paper_id)
        return f"{p.title} ({p.year or 'n.d.'}) {self(paper_id)}" if p else paper_id


def fmt_reference(n: int, p: Paper) -> str:
    authors = ", ".join(p.authors[:3]) + (" et al." if len(p.authors) > 3 else "") if p.authors else "Unknown authors"
    parts = [f"{n}. {authors}. **{p.title}**."]
    if p.venue:
        parts.append(f"_{p.venue}_,")
    parts.append(f"{p.year or 'n.d.'}.")
    if p.url:
        parts.append(f"<{p.url}>")
    if p.doi and (not p.url or p.doi not in p.url):
        parts.append(f"doi:{p.doi}")
    meta = f"id `{p.id}`; retrieved from {', '.join(p.sources)}"
    if p.citation_count is not None:
        meta += f"; {p.citation_count} citations per {p.citation_count_source}"
    return " ".join(parts) + f" ({meta})"


def fmt_evidence(item: EvidenceItem, cite: Citer) -> str:
    src = cite(item.paper_id) if item.paper_id else f"experiment run `{item.experiment_run_id}`"
    status = "verified" if item.verified else "unverified"
    quote = f' "{esc(item.quote)}"' if item.quote else ""
    return f"{src}, {item.location} ({item.support} support, {status}){quote}"


def fmt_claim(c: Claim, cite: Citer) -> str:
    lines = [f"- **{KIND_LABEL[c.kind]}** {c.statement} _(claim {c.id}, confidence: {c.confidence})_"]
    for item in c.evidence:
        lines.append(f"  - {fmt_evidence(item, cite)}")
    return "\n".join(lines)


def _bullets(items: list[str], empty: str = "_None recorded._") -> str:
    return "\n".join(f"- {i}" for i in items) if items else empty


def build_report(ws: Workspace, settings: Settings) -> str:
    papers = {p.id: p for p in ws.papers()}
    cite = Citer(papers)
    idea = ws.idea_analysis()
    analyses = sorted(ws.analyses(), key=lambda a: ["high", "medium", "low", "not_relevant"].index(a.relevance_tier))
    analysis_by = {a.paper_id: a for a in analyses}
    landscape, critique = ws.landscape(), ws.critique()
    claims, gaps, mods, plans = ws.claims(), ws.gaps(), ws.modifications(), ws.plans()
    claims_by = {c.id: c for c in claims}
    no_gap = ws.no_gap()
    searches = ws.searches()
    state = ws.state()
    exp_analyses = ws.experiment_analyses()
    runs = ws.runs()
    grounded = grounding(claims)
    uncertainties = ws.uncertainties()
    directions = ws.directions()
    evaluations = {e.plan_id: e for e in ws.evaluations()}
    decisions = state.decisions if state else []
    high = [a for a in analyses if a.relevance_tier == "high"]
    incomplete = [p.name for p in state.phases if p.status in ("incomplete", "failed", "pending")] if state else []
    incomplete = [p for p in incomplete if p != "report"]
    source_counter = Counter(s for p in papers.values() for s in p.sources)
    failed_sources = sorted({f"{s.source} ({(s.detail or '')[:80]})" for r in searches for s in r.sources if s.status == "error"})
    recommended = next((m for m in mods if m.recommended), mods[0] if mods else None)

    out: list[str] = []
    w = out.append
    w("# ResearchForge Investigation Report")
    w("")
    w(f"Project `{ws.name}`" + (f" · model `{state.provider}/{state.model}`" if state else "") + (f" · status **{state.status}**" if state else ""))
    w("")
    w("> Labels: **[Evidence]** directly supported by a verified quote from a retrieved source; **[Inference]** reasoning derived from cited evidence; **[Hypothesis]** proposed, not validated; **[Assumption]** taken as given without evidence; **[Experimental result]** observed in an executed experiment.")
    w("")

    # 1 ------------------------------------------------------------------
    w("## 1. Executive Summary")
    w("")
    w(f"**Investigated:** {esc(ws.raw_idea)}")
    w("")
    if idea:
        w(f"**Research question:** {esc(idea.research_question)}")
        w("")
    w(
        f"**Literature investigated:** {len(papers)} papers retrieved from {len(searches)} searches "
        f"({', '.join(f'{k}: {v}' for k, v in source_counter.most_common()) or 'no sources'}); "
        f"{len(analyses)} analyzed; {len(high)} rated highly relevant."
    )
    w("")
    if critique:
        w(f"**Assessment:** {STATUS_TEXT[critique.overall_status]}. **[Inference]** {esc(critique.status_rationale)}")
        w("")
        w(f"**Closest existing work:** {'; '.join(cite.title(pid) for pid in critique.closest_paper_ids)}")
        w("")
        w(f"**Potential overlap:** {esc(critique.overlap_summary)}")
        w("")
        w(f"**Potential distinction:** {esc(critique.distinction_summary)}")
        w("")
        w(f"**Major risk:** {esc(critique.strongest_against)}")
        w("")
    else:
        w("**Assessment:** not available. The critique phase did not record a critique.")
        w("")
    if gaps:
        g = gaps[0]
        w(f"**Potential gap:** **[Hypothesis]** {esc(g.gap)} (confidence: {g.confidence}; {len(gaps)} gap(s) recorded)")
        w("")
    elif no_gap:
        w(f"**Potential gap:** none supported by the retrieved evidence. {esc(no_gap.rationale)}")
        w("")
    if recommended:
        w(f"**Recommended modification:** **[Hypothesis]** {esc(recommended.title)}: {esc(recommended.description)}")
        w("")
    if plans:
        w(f"**Recommended experiment:** {esc(plans[0].title)} ({plans[0].id})")
        w("")
    if state and state.research_decision:
        w(f"**Research decision:** {DECISION_TEXT.get(state.research_decision, state.research_decision)}. **[Inference]** Basis: {esc(state.research_decision_basis)}. This describes the state of the evidence, not the absolute value of the idea.")
        w("")
    if directions:
        d0 = directions[-1]
        w(f"**Current research direction ({d0.change_type.replace('_', ' ').lower()}, {d0.confidence} confidence):** **[Hypothesis]** {esc(d0.direction)} (the original idea is kept in Section 2)")
        w("")
    if state and state.investigation_closed:
        w(f"**Investigation closed early:** {esc(state.investigation_closed)}. Questions still open at that point are listed as unresolved in Section 13.")
        w("")
    if decisions:
        resolved = sum(1 for u in uncertainties if u.status == "resolved")
        unresolved = sum(1 for u in uncertainties if u.status in ("open", "partially_resolved", "unresolved"))
        w(f"**Investigation:** {state.budget.iterations} steps chosen from the research state; {len(uncertainties)} uncertainties raised, {resolved} resolved, {unresolved} still open or unresolved (Section 13, Appendix C).")
        w("")
    if state and state.finalize_reason and state.finalize_reason.startswith("Stopping"):
        w(f"**Stopped by a safety limit:** {esc(state.finalize_reason)} Conclusions below cover only what was recorded before the limit.")
        w("")
    w(f"**Claim grounding:** {grounded.grounded}/{grounded.total} evidence and inference claims have at least one verified source.")
    w("")
    if incomplete:
        w(f"**Incomplete phases:** {', '.join(incomplete)}. Sections that depend on them are marked as not recorded.")
        w("")
    w("This report does not declare the idea novel. Absence of a matching paper in these searches does not establish novelty; see Section 13.")
    w("")

    # 2 ------------------------------------------------------------------
    w("## 2. Original Research Idea")
    w("")
    w(f"> {esc(ws.raw_idea)}")
    w("")

    # 3 ------------------------------------------------------------------
    w("## 3. Formalized Research Question")
    w("")
    if idea:
        w(f"**Research question:** {esc(idea.research_question)}")
        w("")
        w(f"**Hypothesis:** **[Hypothesis]** {esc(idea.hypothesis)}")
        w("")
        if directions:
            d = directions[-1]
            w(f"**Refined direction ({d.id}, {d.change_type}):** **[Hypothesis]** {esc(d.direction)}. Hypothesis: {esc(d.hypothesis)}. Why it deserves investigation: {esc(d.rationale)}")
            if d.research_question:
                w("")
                w(f"**Reformulated research question:** {esc(d.research_question)}")
            w("")
            if len(directions) > 1:
                w("Direction history: " + "; ".join(
                    f"{x.id} ({x.change_type}{', from ' + x.previous_direction_id if x.previous_direction_id else ', from the original idea'}): {esc(x.direction)}"
                    for x in directions))
                w("")
        rows = [
            ("Problem", idea.problem), ("Target domain", idea.target_domain), ("Proposed method", idea.proposed_method),
            ("Target system", idea.target_system), ("Expected contribution", idea.expected_contribution),
            ("Independent variables", ", ".join(idea.variables.independent)),
            ("Dependent variables", ", ".join(idea.variables.dependent)),
            ("Controls", ", ".join(idea.variables.controls)),
        ]
        w("| Aspect | Formalization |")
        w("|---|---|")
        for k, v in rows:
            w(f"| {k} | {esc(v) or 'Not recorded'} |")
        w("")
        w("**Assumptions**")
        w("")
        w(_bullets([esc(a) for a in idea.assumptions]))
        w("")
        w("**Expected benefits / potential risks**")
        w("")
        w(_bullets([f"Benefit: {esc(b)}" for b in idea.expected_benefits] + [f"Risk: {esc(r)}" for r in idea.potential_risks]))
        w("")
        if idea.ambiguities:
            w("**Ambiguities**")
            w("")
            w("| Question | Resolution | Resolved by |")
            w("|---|---|---|")
            for a in idea.ambiguities:
                w(f"| {esc(a.question)} | {esc(a.resolution) or 'Not recorded'} | {a.resolved_by} |")
            w("")
    else:
        w(NOT_RECORDED)
        w("")

    # 4 ------------------------------------------------------------------
    w("## 4. Existing Research")
    w("")
    if analyses:
        w("Overlap values are heuristic signals assigned during analysis, not measurements of novelty.")
        w("")
        w("| Paper | Relevance | Method | Problem / method / evaluation overlap | Read from |")
        w("|---|---|---|---|---|")
        for a in analyses:
            r = a.relation_to_idea
            w(f"| {esc(cite.title(a.paper_id))} | {a.relevance_tier} | {esc(a.method)[:300]} | {r.problem_overlap:.1f} / {r.method_overlap:.1f} / {r.evaluation_overlap:.1f} | {a.analyzed_from} |")
        w("")
        w("<details><summary>Full paper analyses</summary>")
        w("")
        for a in analyses:
            w(f"#### {esc(cite.title(a.paper_id))}")
            w("")
            w(f"- **Problem:** {esc(a.problem)}")
            w(f"- **Method:** {esc(a.method)}")
            w(f"- **Main contribution:** {esc(a.main_contribution) or 'Not recorded'}")
            w(f"- **Key assumptions:** {esc('; '.join(a.key_assumptions)) or 'Not recorded'}")
            w(f"- **Datasets / benchmarks:** {esc(', '.join(a.datasets + a.benchmarks)) or 'Not recorded'}")
            w(f"- **Baselines:** {esc(', '.join(a.baselines)) or 'Not recorded'}")
            w(f"- **Metrics:** {esc(', '.join(a.metrics)) or 'Not recorded'}")
            w(f"- **Results:** {esc(a.results) or 'Not recorded'}")
            w(f"- **Limitations:** {esc('; '.join(a.limitations)) or 'Not recorded'}")
            w(f"- **Future work:** {esc('; '.join(a.future_work)) or 'Not recorded'}")
            w(f"- **Code availability:** {esc(a.code_availability)}")
            w(f"- **Relation to idea:** {esc(a.relation_to_idea.conceptual_difference)} _(basis: {esc(a.relation_to_idea.basis) or 'not stated'})_")
            w("")
        w("</details>")
        w("")
    else:
        w(NOT_RECORDED)
        w("")

    # 5 ------------------------------------------------------------------
    w("## 5. Research Landscape")
    w("")
    if landscape:
        w("```text")
        w(landscape.field_name)
        children: dict[str | None, list] = {}
        for c in landscape.categories:
            children.setdefault(c.parent, []).append(c)

        def tree(parent: str | None, prefix: str) -> None:
            nodes = children.get(parent, [])
            for i, c in enumerate(nodes):
                last = i == len(nodes) - 1
                refs = " ".join(cite(pid) for pid in c.paper_ids)
                w(f"{prefix}{'└── ' if last else '├── '}{c.name}{('  ' + refs) if refs else ''}")
                tree(c.name, prefix + ("    " if last else "│   "))

        tree(None, "")
        w("```")
        w("")
        w(f"**Where the idea fits:** **[Inference]** {esc(landscape.idea_position)}")
        w("")
        for label, items in (
            ("Dominant approaches", landscape.dominant_approaches),
            ("Common assumptions", landscape.common_assumptions),
            ("Common datasets", landscape.common_datasets),
            ("Common benchmarks", landscape.common_benchmarks),
            ("Common metrics", landscape.common_metrics),
            ("Underexplored combinations", [f"**[Hypothesis]** {x}" for x in landscape.underexplored_combinations]),
        ):
            w(f"**{label}**")
            w("")
            w(_bullets([esc(x) for x in items]))
            w("")
        w("**Limitations repeated across papers**")
        w("")
        w(_bullets([f"{esc(f.description)} {cite.many(f.paper_ids)}" for f in landscape.repeated_limitations]))
        w("")
        w("**Contradictions between papers**")
        w("")
        w(_bullets([f"{esc(f.description)} {cite.many(f.paper_ids)}" for f in landscape.contradictions]))
        w("")
    else:
        w(NOT_RECORDED)
        w("")

    # 6 ------------------------------------------------------------------
    w("## 6. Closest Existing Work")
    w("")
    if critique:
        w(f"**[Inference]** {esc(critique.closest_work_explanation)}")
        w("")
        for pid in critique.closest_paper_ids:
            a = analysis_by.get(pid)
            detail = f": {esc(a.relation_to_idea.conceptual_difference)}" if a else " (not analyzed in detail)"
            w(f"- {esc(cite.title(pid))}{detail}")
        w("")
    else:
        w(NOT_RECORDED)
        w("")

    # 7 ------------------------------------------------------------------
    w("## 7. Potential Overlap")
    w("")
    if critique:
        w(f"**Overlap:** **[Inference]** {esc(critique.overlap_summary)}")
        w("")
        w(f"**Potential distinction:** **[Inference]** {esc(critique.distinction_summary)}")
        w("")
        _points(w, "Novelty questions", critique.novelty, cite, claims_by)
    else:
        w(NOT_RECORDED)
        w("")

    # 8 ------------------------------------------------------------------
    w("## 8. Potential Research Gap")
    w("")
    if gaps:
        for g in gaps:
            w(f"### {g.id}: {esc(g.gap)}")
            w("")
            w("- **Status:** **[Hypothesis]** a potential gap, derived from the evidence below")
            w("- **Evidence:**")
            for item in g.evidence:
                w(f"  - {fmt_evidence(item, cite)}")
            if g.related_paper_ids:
                w(f"- **Related papers:** {cite.many(g.related_paper_ids)}")
            w(f"- **Why existing work does not address it:** **[Inference]** {esc(g.why_unaddressed)}")
            w(f"- **Research question:** {esc(g.research_question)}")
            w(f"- **Potential experiment:** {esc(g.potential_experiment)}")
            w(f"- **Confidence:** {g.confidence}")
            w(f"- **Verification required:** {esc(g.verification_required) or 'not stated'}")
            w("")
    elif no_gap:
        w(f"**[Inference]** No research gap is supported by the retrieved evidence. {esc(no_gap.rationale)} {cite.many(no_gap.paper_ids)}")
        w("")
    else:
        w(NOT_RECORDED)
        w("")

    # 9 ------------------------------------------------------------------
    w("## 9. Critique")
    w("")
    if critique:
        w("| | |")
        w("|---|---|")
        w(f"| Strongest argument FOR | {esc(critique.strongest_for)} |")
        w(f"| Strongest argument AGAINST | {esc(critique.strongest_against)} |")
        w(f"| Most important unresolved question | {esc(critique.most_important_unresolved_question)} |")
        w(f"| Most dangerous experimental confounder | {esc(critique.most_dangerous_confounder)} |")
        w(f"| Closest existing work | {cite.many(critique.closest_paper_ids)} |")
        w(f"| Potential contribution | **[Hypothesis]** {esc(critique.potential_contribution)} |")
        w("")
        _points(w, "Technical validity", critique.technical_validity, cite, claims_by)
        _points(w, "Experimental validity", critique.experimental_validity, cite, claims_by)
        _points(w, "Practicality", critique.practicality, cite, claims_by)
    else:
        w(NOT_RECORDED)
        w("")

    # 10 -----------------------------------------------------------------
    w("## 10. Proposed Modifications")
    w("")
    if mods:
        w("Difficulty ratings are qualitative (low / moderate / high) with the stated basis; no numeric scoring is used.")
        w("")
        for m in mods:
            w(f"### {m.id}: {esc(m.title)}{' (recommended)' if m.recommended else ''}")
            w("")
            w(f"**[Hypothesis]** {esc(m.description)}")
            w("")
            w("| | |")
            w("|---|---|")
            w(f"| Why it differs | {esc(m.why_differs)} |")
            w(f"| Technical mechanism | {esc(m.technical_mechanism)} |")
            w(f"| Expected benefit | {esc(m.expected_benefit)} |")
            w(f"| Potential novelty | {esc(m.potential_novelty)} |")
            w(f"| Implementation difficulty | {m.implementation_difficulty}, because {esc(m.implementation_difficulty_basis)} |")
            w(f"| Experimental difficulty | {m.experimental_difficulty}, because {esc(m.experimental_difficulty_basis)} |")
            w(f"| Main risk | {esc(m.main_risk)} |")
            w(f"| Required baselines | {esc(', '.join(m.required_baselines)) or 'Not recorded'} |")
            w(f"| Related work | {cite.many(m.related_paper_ids) or 'Not recorded'} |")
            w(f"| Addresses gaps | {', '.join(m.addresses_gap_ids) or 'Not recorded'} |")
            w("")
    else:
        w(NOT_RECORDED)
        w("")

    # 11 -----------------------------------------------------------------
    w("## 11. Recommended Experimental Design")
    w("")
    if plans:
        for p in plans:
            w(f"### {p.id}: {esc(p.title)}")
            w("")
            w(f"- **Research question:** {esc(p.research_question)}")
            w(f"- **Hypothesis:** **[Hypothesis]** {esc(p.hypothesis)}")
            w(f"- **Proposed method:** {esc(p.proposed_method)}")
            w(f"- **Baselines:** {esc(', '.join(p.baselines))}")
            w(f"- **Datasets:** {esc(', '.join(p.datasets)) or 'Not recorded'}")
            w(f"- **Workloads:** {esc(', '.join(p.workloads)) or 'Not recorded'}")
            w(f"- **Hardware:** {esc(p.hardware) or 'Not recorded'}")
            w(f"- **Software environment:** {esc(p.software_environment) or 'Not recorded'}")
            w(f"- **Metrics:** {esc(', '.join(p.metrics))}")
            w(f"- **Ablations:** {esc('; '.join(p.ablations)) or 'Not recorded'}")
            w(f"- **Controls:** {esc('; '.join(p.controls)) or 'Not recorded'}")
            w(f"- **Confounders addressed:** {esc('; '.join(p.confounders_addressed)) or 'Not recorded'}")
            w(f"- **Expected outcomes:** {esc(p.expected_outcomes) or 'Not recorded'}")
            w(f"- **Failure conditions:** {esc('; '.join(p.failure_conditions)) or 'Not recorded'}")
            w(f"- **Reproducibility:** {esc(p.reproducibility_notes) or 'Not recorded'}")
            if p.related_paper_ids:
                w(f"- **Related work:** {cite.many(p.related_paper_ids)}")
            if p.execution:
                arms = ", ".join(f"{a.name} ({a.role})" for a in p.execution.arms)
                w(f"- **Executable spec:** {arms}; status `{p.status}`; runs only after explicit approval")
            w("")
    else:
        w(NOT_RECORDED)
        w("")

    # 12 -----------------------------------------------------------------
    w("## 12. Experimental Results")
    w("")
    if exp_analyses:
        for ea in exp_analyses:
            w(f"### Experiment {ea.plan_id}: {ea.status}")
            w("")
            w(ea.summary or "")
            w("")
            if ea.comparisons:
                w("| Metric | Baseline | Method | Baseline value | Method value | Relative change |")
                w("|---|---|---|---|---|---|")
                for c in ea.comparisons:
                    rel = f"{c.relative_change:+.1%}" if c.relative_change is not None else "n/a"
                    w(f"| {c.metric} | {c.baseline_arm} | {c.method_arm} | {c.baseline_value:g} | {c.method_value:g} | {rel} |")
                w("")
                if ea.status == "PASSED":
                    w("**[Experimental result]** The values above were observed in the executed runs listed below.")
                else:
                    w("These values come from runs that failed verification; they are not reported as experimental results.")
                w("")
            for issue in ea.issues:
                w(f"- **{issue.severity.upper()} {issue.code}:** {esc(issue.message)} {('Suggestion: ' + esc(issue.suggestion)) if issue.suggestion else ''}")
            w("")
            for r in [r for r in runs if r.id in ea.run_ids]:
                w(f"- Run `{r.id}` ({r.arm}, {r.status}, exit {r.exit_code}, {r.duration_s:.1f}s, commit {r.git_commit or 'n/a'}): `{esc(' '.join(r.argv))[:200]}`")
            w("")
    else:
        w("Experiment not performed. The designs in Section 11 are untested.")
        w("")
    for pid, e in evaluations.items():
        label = "[Experimental result]" if e.verdict == "SUPPORTED" else "[Inference]"
        w(f"**Hypothesis re-evaluation for {pid}:** **{label}** {e.verdict}. {esc(e.rationale)}" + (f" Next step: {esc(e.next_step)}" if e.next_step else ""))
        w("")
    if state and state.awaiting_approval:
        pending = [p for p in state.awaiting_approval if not any(r.plan_id == p for r in runs)]
        if pending:
            w(f"Awaiting human approval to run: {', '.join(pending)}. Approve with `researchforge experiment <project> --run <id> --approve`, then resume to re-evaluate the hypothesis.")
            w("")

    # 13 -----------------------------------------------------------------
    w("## 13. Remaining Uncertainty")
    w("")
    uncertain: list[str] = []
    queries = [s.query for s in searches]
    uncertain.append(
        f"Literature coverage: searched {len(queries)} queries over {', '.join(sorted({s.source for r in searches for s in r.sources})) or 'no sources'}. "
        "Work outside these queries and sources, very recent preprints, and non-English work may be missing; the absence of matching work here does not establish novelty."
    )
    if failed_sources:
        uncertain.append(f"Some source requests failed and their results are missing: {'; '.join(failed_sources[:6])}.")
    flagged = [p for p in papers.values() if p.metadata_warnings]
    for p in flagged[:8]:
        uncertain.append(f"Metadata warning for {cite.title(p.id)}: {esc(p.metadata_warnings[0])}. Its abstract was not accepted as direct evidence.")
    abstract_only = [a.paper_id for a in analyses if a.analyzed_from == "abstract"]
    if abstract_only:
        uncertain.append(f"{len(abstract_only)} of {len(analyses)} analyses are based on abstracts only.")
    if critique:
        uncertain.append(f"Unresolved question: {esc(critique.most_important_unresolved_question)}")
    if idea:
        for a in idea.ambiguities:
            if a.resolved_by in ("unresolved", "assumption"):
                uncertain.append(f"Ambiguity ({a.resolved_by}): {esc(a.question)}" + (f"; assumed: {esc(a.resolution)}" if a.resolution else ""))
    for g in gaps:
        if g.verification_required:
            uncertain.append(f"Gap {g.id} requires verification: {esc(g.verification_required)}")
    if grounded.ungrounded_ids:
        uncertain.append(f"Claims without a verified source: {', '.join(grounded.ungrounded_ids)}.")
    if incomplete:
        uncertain.append(f"Phases that did not complete: {', '.join(incomplete)}.")
    if not exp_analyses:
        uncertain.append("No hypothesis in this report has been tested experimentally.")
    w(_bullets(uncertain))
    if uncertainties:
        w("")
        w("**Uncertainty ledger**")
        w("")
        w("| Id | Question | Category | Importance | Status | Evidence for / against | Resolution |")
        w("|---|---|---|---|---|---|---|")
        for u in sorted(uncertainties, key=lambda u: (u.status == "resolved", {"high": 0, "medium": 1, "low": 2}[u.importance], u.id)):
            status = u.status.replace("_", " ") + (f" ({u.challenge_verdict})" if u.challenge_verdict else "")
            sides = f"{cite.many(u.supporting_paper_ids) or 'none'} / {cite.many(u.contradicting_paper_ids) or 'none'}"
            raised = " (raised by ResearchForge)" if u.source == "controller" else ""
            w(f"| {u.id} | {esc(u.question)}{raised} | {u.category} | {u.importance} | {status} | {sides} | {esc(u.resolution) or 'Not recorded'} |")
    w("")

    # 14 -----------------------------------------------------------------
    w("## 14. Suggested Next Steps")
    w("")
    steps: list[str] = []
    if plans and not exp_analyses:
        steps.append(f"Run the recommended experiment {plans[0].id} ({esc(plans[0].title)}) with budget-matched baselines.")
    if critique:
        steps.append(f"Resolve: {esc(critique.most_important_unresolved_question)}")
        steps.append(f"Design a control for the confounder: {esc(critique.most_dangerous_confounder)}")
    for g in gaps:
        if g.verification_required:
            steps.append(f"Verify gap {g.id}: {esc(g.verification_required)}")
    closest_abstract_only = [pid for pid in (critique.closest_paper_ids if critique else []) if pid in abstract_only]
    if closest_abstract_only:
        steps.append(f"Read the full text of the closest work analyzed only from abstracts: {cite.many(closest_abstract_only)}.")
    years = [p.year for p in papers.values() if p.year]
    if years:
        steps.append(f"Search for work newer than the most recent retrieved paper ({max(years)}) before claiming a distinction.")
    if recommended:
        steps.append(f"Prototype the recommended modification {recommended.id} ({esc(recommended.title)}).")
    w("\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)) if steps else "_No next steps could be derived from the recorded data._")
    w("")

    # Appendix A: evidence ledger (renders before references so citations are numbered)
    appendix: list[str] = ["## Appendix A. Evidence Ledger", ""]
    if claims:
        for kind in ("evidence", "inference", "hypothesis", "assumption", "experimental"):
            group = [c for c in claims if c.kind == kind]
            if group:
                appendix.append(f"### {KIND_LABEL[kind]} claims ({len(group)})")
                appendix.append("")
                appendix.extend(fmt_claim(c, cite) for c in group)
                appendix.append("")
    else:
        appendix.append("_No claims recorded._")
        appendix.append("")
    appendix += ["## Appendix B. Search Log", "", "| Query | Sources (status: results) | Papers |", "|---|---|---|"]
    for s in searches:
        srcs = ", ".join(f"{x.source} ({x.status}: {x.count})" for x in s.sources)
        appendix.append(f"| {esc(s.query)} | {srcs} | {len(s.paper_ids)} |")
    appendix.append("")
    if decisions:
        appendix += ["## Appendix C. Investigation Log", "",
                     "Each step was chosen by the ResearchForge controller from the recorded research state.", "",
                     "| Step | Phase | Action | Why | Alternatives considered | Outcome | Information gain |", "|---|---|---|---|---|---|---|"]
        for d in decisions:
            focus = f" ({esc(d.focus)[:80]})" if d.focus else ""
            alts = "; ".join(f"{c.action} {c.uncertainty_id} ({c.score:g})" for c in d.candidates[1:3]) or "none"
            gain = f"{d.info_gain:g}" if d.info_gain is not None else "n/a"
            appendix.append(f"| {d.iteration} | {d.phase} | {d.action}{focus} | {esc(d.reason)[:260]} | {alts} | {esc(d.outcome)[:200]} | {gain} |")
        appendix.append("")

    # 15 -----------------------------------------------------------------
    refs = ["## 15. References", ""]
    if cite.order:
        refs += [fmt_reference(i, papers[pid]) for i, pid in enumerate(cite.order, 1)]
    else:
        refs.append("_No papers were cited._")
    refs.append("")
    uncited = [p for p in sorted(papers.values(), key=lambda p: -p.relevance) if p.id not in cite.order]
    if uncited:
        refs += ["<details><summary>Other retrieved papers (not cited in this report)</summary>", ""]
        refs += [f"- {esc(p.title)} ({p.year or 'n.d.'}) <{p.url}> `{p.id}`" if p.url else f"- {esc(p.title)} ({p.year or 'n.d.'}) `{p.id}`" for p in uncited]
        refs += ["", "</details>", ""]

    return "\n".join(out + refs + appendix)


def _points(w, title: str, points: list[CritiquePoint], cite: Citer, claims_by: dict[str, Claim]) -> None:
    w(f"**{title}**")
    w("")
    if not points:
        w("_None recorded._")
        w("")
        return
    for p in points:
        links = []
        if p.paper_ids:
            links.append(cite.many(p.paper_ids))
        for cid in p.claim_ids:
            c = claims_by.get(cid)
            if c:
                links.append(f"{KIND_LABEL[c.kind]} claim {cid}")
        w(f"- **{esc(p.question)}** ({p.severity} severity): {esc(p.finding)}" + (f" _({'; '.join(links)})_" if links else ""))
    w("")


HTML_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ResearchForge report: {title}</title>
<style>
:root{{--surface:#f1f3f6;--card:#ffffff;--header:#e6e9ed;--ink:#0f1419;--soft:#5a626c;--rule:rgba(15,20,25,.08);--tint:rgba(15,20,25,.06)}}
@font-face{{font-family:"Inter";src:url("/static/fonts/inter.woff2") format("woff2");font-weight:100 900}}
@font-face{{font-family:"Inter";src:url("/static/fonts/inter-italic.woff2") format("woff2");font-weight:100 900;font-style:italic}}
@font-face{{font-family:"IBM Plex Mono";src:url("/static/fonts/ibm-plex-mono-400.woff2") format("woff2");font-weight:400}}
body{{font:16px/1.6 Inter,"Segoe UI",Arial,sans-serif;max-width:72ch;margin:2.5rem auto;padding:0 16px;color:var(--ink);background:var(--card)}}
h1,h2,h3{{letter-spacing:-.018em;line-height:1.2;font-weight:600}} h1{{font-size:1.875rem;font-weight:700;letter-spacing:-.025em}} h2{{font-size:1.25rem;letter-spacing:-.012em;border-top:1px solid var(--rule);padding-top:1.2rem;margin-top:2.4rem}}
a{{color:var(--ink);text-decoration-color:rgba(15,20,25,.3);text-underline-offset:.2em}} a:hover{{text-decoration-color:currentColor}} strong{{font-weight:600}}
table{{border-collapse:collapse;width:100%;margin:1rem 0;font-size:14px;line-height:1.45;display:block;overflow-x:auto;border:1px solid var(--rule)}}
td,th{{border-bottom:1px solid var(--rule);padding:.5rem .75rem;vertical-align:top;text-align:left}} th{{background:var(--header);color:var(--soft);font:500 11px/1.3 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.06em;text-transform:uppercase}}
code,pre{{font-family:"IBM Plex Mono",ui-monospace,monospace;background:var(--tint);border-radius:3px;font-size:.85em}} pre{{padding:.8rem;overflow:auto;line-height:1.4;border-radius:5px}}
blockquote{{border-left:3px solid rgba(15,20,25,.6);margin:1rem 0;padding:.5em 0 .5em 1.25em;color:var(--soft);font-style:italic}}
details{{margin:1rem 0}} summary{{cursor:pointer;font-weight:600}}
</style></head><body>
{body}
</body></html>"""


def render_html(markdown_text: str, title: str) -> str:
    body = md.markdown(markdown_text, extensions=["tables", "fenced_code", "md_in_html"])
    return HTML_TEMPLATE.format(title=title.replace("<", "&lt;"), body=body)


def write_reports(ws: Workspace, settings: Settings) -> list[Path]:
    text = build_report(ws, settings)
    md_path, html_path = ws.report_path("md"), ws.report_path("html")
    atomic_write_text(md_path, text)
    atomic_write_text(html_path, render_html(text, ws.name))
    return [md_path, html_path]
