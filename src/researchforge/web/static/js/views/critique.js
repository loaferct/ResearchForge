import { KIND_NAME, h, facts, stmt, section, S, paperRefs, data, pendingNote } from "../core.js";

export default async function critique() {
  const [c, claims] = await Promise.all([data("critique"), data("claims")]);
  const out = [h("h2", {}, "Critique")];
  if (!c) { out.push(pendingNote("The critique")); return out; }
  out.push(h("p", { class: "lede" }, "The case against the idea, argued as seriously as the case for it."));
  out.push(h("div", { class: "versus" },
    h("div", { class: "for" }, h("h3", {}, "Strongest argument for"), h("p", {}, c.strongest_for)),
    h("div", { class: "against" }, h("h3", {}, "Strongest argument against"), h("p", {}, c.strongest_against))));
  out.push(facts([
    ["Most important unresolved question", c.most_important_unresolved_question],
    ["Most dangerous confounder", c.most_dangerous_confounder],
    ["Closest existing work", paperRefs(c.closest_paper_ids)],
  ]));
  out.push(section("Overlap and distinction",
    stmt("inference", c.closest_work_explanation, "Why this is the closest work"),
    stmt("inference", c.overlap_summary, "Overlap"),
    stmt("inference", c.distinction_summary, "Potential distinction"),
    stmt("hypothesis", c.potential_contribution, "Potential contribution")));
  const byId = Object.fromEntries(claims.map((x) => [x.id, x]));
  const points = (title, pts) => (pts.length ? section(title, h("ul", { class: "points" }, pts.map((p) => h("li", {},
    h("div", {}, h("span", { class: "q" }, p.question), " ", h("span", { class: `sev ${p.severity}` }, `${p.severity} severity`)),
    h("div", {}, p.finding),
    p.paper_ids.length ? h("div", { class: "stmt-meta" }, "Papers: ", paperRefs(p.paper_ids)) : null,
    p.claim_ids.length ? h("div", { class: "stmt-meta" }, "Claims: ", p.claim_ids.map((id) => (byId[id] ? `${id} (${KIND_NAME[byId[id].kind].toLowerCase()})` : id)).join(", ")) : null)))) : null);
  out.push(points("Novelty", c.novelty), points("Technical validity", c.technical_validity), points("Experimental validity", c.experimental_validity), points("Practicality", c.practicality));
  out.push(h("div", { style: "margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--hairline);" },
    h("a", { class: "button", href: `#/p/${encodeURIComponent(S.project)}/graphs` }, "View in Novelty & Risk Radar →")));
  return out;
}
