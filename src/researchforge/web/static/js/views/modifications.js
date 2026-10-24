import { h, join, facts, stmt, paperRefs, data, pendingNote } from "../core.js";

export default async function modifications() {
  const mods = await data("modifications");
  const out = [h("h2", {}, "Modifications")];
  if (!mods.length) { out.push(pendingNote("Proposed modifications")); return out; }
  out.push(h("p", { class: "lede" }, "Ways to make the idea stronger or more distinct. Difficulty is rated low, moderate or high with the reason; there are no numeric scores."));
  for (const m of mods) {
    out.push(h("div", { class: "entry" },
      h("h3", {}, m.title, m.recommended ? h("span", { class: "rec" }, "Recommended") : null),
      stmt("hypothesis", m.description),
      facts([["Why it differs", m.why_differs], ["Mechanism", m.technical_mechanism], ["Expected benefit", m.expected_benefit],
        ["Potential novelty", m.potential_novelty], ["Implementation difficulty", `${m.implementation_difficulty}, because ${m.implementation_difficulty_basis}`],
        ["Experimental difficulty", `${m.experimental_difficulty}, because ${m.experimental_difficulty_basis}`], ["Main risk", m.main_risk],
        ["Required baselines", join(m.required_baselines)], ["Related work", paperRefs(m.related_paper_ids)], ["Addresses gaps", join(m.addresses_gap_ids)]])));
  }
  return out;
}
