import { h, NONE, join, safeUrl, plural, facts, S, data, pendingNote } from "../core.js";

export default async function literature() {
  const [papers, analyses, searches] = await Promise.all([data("papers"), data("analyses"), data("searches")]);
  const out = [h("h2", {}, "Literature")];
  if (!papers.length) { out.push(pendingNote("Retrieved papers")); return out; }
  const byId = Object.fromEntries(analyses.map((a) => [a.paper_id, a]));
  out.push(h("p", { class: "lede" }, `${plural(papers.length, "paper")} from ${plural(searches.length, "search", "searches")}, ordered by a lexical relevance score used only for triage. The relevance tier comes from the agent's own analysis.`));
  const list = h("ol", { class: "papers" });
  const draw = () => {
    const q = S.lit.q.toLowerCase();
    const shown = papers.filter((p) => (S.lit.show === "all" || (S.lit.show === "analyzed") === Boolean(byId[p.id]))
      && (!q || `${p.title} ${(p.authors || []).join(" ")} ${p.venue || ""}`.toLowerCase().includes(q)));
    list.replaceChildren(...(shown.length ? shown.map((p) => paperItem(p, byId[p.id])) : [h("li", { class: "empty" }, "No papers match this filter.")]));
  };
  const seg = h("div", { class: "seg", role: "group", "aria-label": "Show papers" },
    [["all", "All"], ["analyzed", "Analyzed"], ["unanalyzed", "Not analyzed"]].map(([k, label]) =>
      h("button", { type: "button", "aria-pressed": S.lit.show === k ? "true" : "false", onclick: (ev) => {
        S.lit.show = k;
        seg.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === ev.currentTarget)));
        draw();
      } }, label)));
  out.push(h("div", { class: "toolbar" },
    h("input", { type: "search", placeholder: "Filter by title, author or venue", "aria-label": "Filter papers", value: S.lit.q, oninput: (ev) => { S.lit.q = ev.target.value; draw(); } }),
    seg,
    h("a", { class: "button", style: "font-size: 0.75rem; padding: 6px 12px; margin-left: auto;", href: `#/p/${encodeURIComponent(S.project)}/graphs` }, "Open in Similarity Matrix →")));
  draw();
  out.push(list);
  return out;
}

function paperItem(p, a) {
  const url = safeUrl(p.url);
  const authors = (p.authors || []).slice(0, 3).join(", ") + ((p.authors || []).length > 3 ? " et al." : "");
  const meta = [authors, p.venue, p.year].filter(Boolean).join(", ");
  const cites = p.citation_count != null ? `; ${p.citation_count} citations per ${p.citation_count_source}` : "";
  const item = h("li", { class: "paper" },
    h("div", { class: "paper-title" }, url ? h("a", { href: url, target: "_blank", rel: "noopener noreferrer" }, p.title) : p.title,
      a ? h("span", { class: `tier ${a.relevance_tier}` }, ` ${a.relevance_tier.replace("_", " ")} relevance`) : null),
    h("div", { class: "paper-meta" }, `${meta}${cites}. Found via ${p.sources.join(", ")}.`),
    (p.metadata_warnings || []).map((w) => h("div", { class: "paper-warning" }, `Check this record: ${w}.`)));
  if (a) {
    const r = a.relation_to_idea;
    const bar = (label, v) => h("span", {}, label, h("span", { class: "bar", role: "img", "aria-label": `${label} overlap ${v}` }, h("i", { style: `width:${Math.round(v * 100)}%` })));
    item.append(h("details", {}, h("summary", {}, "Show analysis"),
      facts([["Problem", a.problem], ["Method", a.method], ["Contribution", a.main_contribution || NONE],
        ["Datasets and benchmarks", join([...a.datasets, ...a.benchmarks])], ["Baselines", join(a.baselines)], ["Metrics", join(a.metrics)],
        ["Results", a.results || NONE], ["Limitations", join(a.limitations)], ["Code", a.code_availability],
        ["Overlap with the idea", h("span", { class: "overlap" }, bar("Problem", r.problem_overlap), bar("Method", r.method_overlap), bar("Evaluation", r.evaluation_overlap))],
        ["How it differs", r.conceptual_difference], ["Basis for the overlap scores", r.basis || "Not stated"], ["Read from", a.analyzed_from === "full_text" ? "full text" : "abstract only"]])));
  }
  return item;
}
