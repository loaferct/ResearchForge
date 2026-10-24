import { h, join, facts, stmt, section, S, paperRefs, data, pendingNote } from "../core.js";

export default async function map() {
  const l = await data("landscape");
  const out = [h("h2", {}, "Research map")];
  if (!l) { out.push(pendingNote("The research landscape")); return out; }
  out.push(h("p", { class: "lede" }, l.field_name));
  out.push(h("div", { style: "margin-bottom: 20px;" },
    h("a", { class: "button", style: "font-size: 0.75rem; padding: 6px 14px;", href: `#/p/${encodeURIComponent(S.project)}/graphs/network` }, "Open Interactive Concept Network →")));
  const children = {};
  l.categories.forEach((c) => (children[c.parent || ""] ||= []).push(c));
  const here = (l.idea_position || "").toLowerCase();
  const branch = (parent) => {
    const nodes = children[parent] || [];
    if (!nodes.length) return null;
    return h("ul", { class: parent ? null : "tree" }, nodes.map((c) => h("li", {},
      h("span", { class: `node${here.includes(c.name.toLowerCase()) ? " here" : ""}` }, c.name),
      c.description ? h("div", { class: "node-papers" }, c.description) : null,
      c.paper_ids.length ? h("div", { class: "node-papers" }, paperRefs(c.paper_ids)) : null,
      branch(c.name))));
  };
  out.push(section("Approaches", branch("")));
  out.push(section("Where the idea fits", stmt("inference", l.idea_position)));
  out.push(section("What the field shares", facts([
    ["Dominant approaches", join(l.dominant_approaches)], ["Common assumptions", join(l.common_assumptions)],
    ["Datasets", join(l.common_datasets)], ["Benchmarks", join(l.common_benchmarks)], ["Metrics", join(l.common_metrics)],
  ])));
  const linked = (items) => items.length ? items.map((f) => stmt("inference", f.description, paperRefs(f.paper_ids))) : [h("p", { class: "muted" }, "None recorded.")];
  out.push(section("Limitations repeated across papers", ...linked(l.repeated_limitations)));
  out.push(section("Contradictions between papers", ...linked(l.contradictions)));
  if (l.underexplored_combinations.length) out.push(section("Underexplored combinations", ...l.underexplored_combinations.map((x) => stmt("hypothesis", x))));
  return out;
}
