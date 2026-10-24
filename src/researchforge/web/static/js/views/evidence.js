import { KIND_NAME, h, legend, section, sources, data, pendingNote } from "../core.js";

export default async function evidence() {
  const [claims, searches] = await Promise.all([data("claims"), data("searches")]);
  const out = [h("h2", {}, "Evidence ledger"), h("p", { class: "lede" }, "Every claim the investigation recorded, with its sources. Quotes are checked word for word against the retrieved abstract or full text."), legend()];
  const kinds = ["evidence", "inference", "hypothesis", "assumption", "experimental"].map((k) => [k, claims.filter((c) => c.kind === k)]).filter(([, g]) => g.length);
  if (!kinds.length) out.push(pendingNote("Claims"));
  for (const [k, group] of kinds) {
    out.push(section(`${KIND_NAME[k]} (${group.length})`, ...group.map((c) =>
      h("div", { class: `stmt ${c.kind}` }, h("span", { class: "stmt-text" }, c.statement),
        h("div", { class: "stmt-meta" }, `${c.id}, confidence ${c.confidence}${c.phase ? `, recorded during ${c.phase}` : ""}`),
        sources(c.evidence)))));
  }
  out.push(section("Search log", searches.length ? h("div", { class: "table-wrap" }, h("table", { class: "results" },
    h("tr", {}, h("th", {}, "Query"), h("th", {}, "Sources"), h("th", {}, "Papers")),
    searches.map((s) => h("tr", {}, h("td", {}, s.query),
      h("td", {}, s.sources.map((x) => `${x.source}: ${x.status === "ok" ? x.count : x.status}`).join(", ")),
      h("td", {}, s.paper_ids.length))))) : h("p", { class: "muted" }, "No searches yet.")));
  return out;
}
