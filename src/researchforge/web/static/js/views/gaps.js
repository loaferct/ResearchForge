import { h, NONE, facts, stmt, section, paperRefs, sources, data, pendingNote } from "../core.js";

export default async function gaps() {
  const [gaps, noGap] = await Promise.all([data("gaps"), data("no_gap")]);
  const out = [h("h2", {}, "Potential gaps")];
  if (!gaps.length && noGap) {
    out.push(stmt("inference", `No gap is supported by the retrieved evidence. ${noGap.rationale}`, paperRefs(noGap.paper_ids)));
    return out;
  }
  if (!gaps.length) { out.push(pendingNote("Evidence-linked gaps")); return out; }
  out.push(h("p", { class: "lede" }, "Each gap is a hypothesis about what the literature has not yet done, tied to the passages that suggest it."));
  for (const g of gaps) {
    out.push(h("div", { class: "entry" },
      h("h3", {}, g.gap),
      h("p", { class: "stmt-meta" }, `${g.id}, confidence ${g.confidence}`),
      section("Evidence", sources(g.evidence)),
      facts([["Why existing work does not address it", g.why_unaddressed], ["Research question", g.research_question],
        ["Potential experiment", g.potential_experiment], ["Related papers", paperRefs(g.related_paper_ids)],
        ["Still to verify", g.verification_required || NONE]])));
  }
  return out;
}
