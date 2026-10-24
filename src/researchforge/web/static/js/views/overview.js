import { VERDICT, RESEARCH_DECISION, h, NONE, join, plural, facts, stmt, section, S, paperRefs, data, pendingNote } from "../core.js";

export default async function overview() {
  const [idea, critique] = await Promise.all([data("idea"), data("critique")]);
  const c = S.info.counts;
  const out = [];
  if (critique) {
    out.push(h("div", { class: `verdict ${critique.overall_status}` },
      h("p", { class: "verdict-kicker" }, "Assessment"),
      h("h2", {}, VERDICT[critique.overall_status] || critique.overall_status),
      h("p", {}, critique.status_rationale)));
  } else {
    out.push(h("h2", {}, "Overview"), h("p", { class: "lede" }, S.info.running ? "The assessment appears after the critique phase." : "No assessment was recorded."));
  }
  const rd = S.info.state?.research_decision;
  if (rd) {
    out.push(h("p", { class: "decision" }, h("b", {}, `Research decision: ${RESEARCH_DECISION[rd] || rd}.`),
      ` ${S.info.state.research_decision_basis || ""}. This describes the state of the evidence, not the worth of the idea.`));
  }
  out.push(h("p", { class: "tally" },
    `${plural(c.papers, "paper")} retrieved in ${plural(c.searches, "search", "searches")}; ${c.analyses} analyzed; ${plural(c.claims, "claim")}, ${plural(c.gaps, "gap")}, ${plural(c.modifications, "modification")} and ${plural(c.plans, "experiment plan")} recorded.`));
  out.push(h("div", { class: "stat-box", style: "margin: 16px 0 24px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; border-left: 3px solid var(--steel);" },
    h("div", {},
      h("p", { style: "margin: 0; font-weight: 600; font-size: 0.9375rem;" }, "Visual Graphs & Analytics"),
      h("p", { style: "margin: 2px 0 0; font-size: 0.8125rem; color: var(--ink-60);" }, "Multi-dimensional Novelty Radar, Paper Similarity Matrix, and Landscape Concept Network are available.")),
    h("a", { class: "button", href: `#/p/${encodeURIComponent(S.project)}/graphs` }, "Explore Visual Graphs →")));
  if (critique) {
    out.push(section("The case in brief",
      facts([["Closest existing work", paperRefs(critique.closest_paper_ids)]]),
      stmt("inference", critique.overlap_summary, "Overlap"),
      stmt("inference", critique.distinction_summary, "Potential distinction"),
      stmt("inference", critique.strongest_against, "Major risk")));
  }
  if (!idea) { out.push(pendingNote("The formalized research question")); return out; }
  const [uncertainties, directions] = await Promise.all([data("uncertainties"), data("directions")]);
  out.push(section("Research question", h("p", { class: "prose" }, idea.research_question),
    stmt("hypothesis", idea.hypothesis, directions.length ? "Original hypothesis, kept unchanged" : null)));
  if (directions.length) {
    const d = directions[directions.length - 1];
    out.push(section("Current direction", stmt("hypothesis", d.direction, `Hypothesis: ${d.hypothesis}`),
      h("p", { class: "lede" }, `Why it deserves investigation: ${d.rationale}`)));
  }
  if (uncertainties.length) {
    const order = { open: 0, partially_resolved: 1, unresolved: 2, resolved: 3 };
    const sorted = [...uncertainties].sort((a, b) => order[a.status] - order[b.status] || a.id.localeCompare(b.id));
    out.push(section("Open questions", h("ul", { class: "points" }, sorted.map((u) => h("li", {},
      h("div", {}, h("span", { class: "q" }, u.question), h("span", { class: `u-status ${u.status}` }, u.status.replace("_", " "))),
      h("div", { class: "stmt-meta" }, [`${u.id}, ${u.category}, ${u.importance} importance`,
        u.challenge_verdict ? `challenge verdict: ${u.challenge_verdict}` : null,
        u.confidence != null ? `confidence ${u.confidence} (${u.confidence_basis})` : null,
        u.status === "resolved" ? null : `next: ${u.next_action.toLowerCase().replace("_", " ")}`,
        `investigated ${plural(u.attempts, "time")}`, u.source === "controller" ? "raised by ResearchForge" : null].filter(Boolean).join(", ")),
      u.resolution ? h("div", {}, u.resolution) : null)))));
  }
  const decisions = (S.info.state?.decisions || []).slice().reverse();
  if (decisions.length) {
    const item = (d) => h("li", {}, h("span", { class: "n" }, d.iteration),
      h("div", { class: "act" }, d.action.toLowerCase().replace("_", " "), d.focus ? h("span", {}, ` on ${d.focus}`) : null),
      h("div", { class: "why" }, d.reason),
      d.candidates && d.candidates.length > 1 ? h("div", { class: "why" }, `Also considered: ${d.candidates.slice(1, 3).map((c) => `${c.action.toLowerCase()} on ${c.uncertainty_id} (${c.score})`).join("; ")}`) : null,
      d.outcome ? h("div", { class: "got" }, d.outcome + (d.info_gain != null ? `. Information gain ${d.info_gain}` : "")) : null);
    out.push(section("Investigation log",
      h("p", { class: "lede" }, "Each step was chosen by the controller from what the investigation had recorded so far. Most recent first."),
      h("ol", { class: "log" }, decisions.slice(0, 8).map(item)),
      decisions.length > 8 ? h("details", {}, h("summary", {}, `Show all ${decisions.length} log entries`), h("ol", { class: "log" }, decisions.slice(8).map(item))) : null));
  }
  out.push(section("Formalization", facts([
    ["Problem", idea.problem], ["Proposed method", idea.proposed_method], ["Target domain", idea.target_domain],
    ["Target system", idea.target_system || NONE], ["Expected contribution", idea.expected_contribution],
    ["Independent variables", join(idea.variables.independent)], ["Dependent variables", join(idea.variables.dependent)],
    ["Controls", join(idea.variables.controls)], ["Assumptions", join(idea.assumptions)],
    ["Expected benefits", join(idea.expected_benefits)], ["Potential risks", join(idea.potential_risks)],
  ])));
  if (idea.ambiguities.length) {
    out.push(section("Ambiguities", facts(idea.ambiguities.map((a) => [a.question,
      h("span", {}, a.resolution || "Unresolved", h("span", { class: "muted" }, a.resolved_by === "unresolved" ? "" : ` (resolved by ${a.resolved_by})`))]))));
  }
  return out;
}
