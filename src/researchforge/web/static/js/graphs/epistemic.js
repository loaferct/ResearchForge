import { h, facts, svg, showChartTooltip, hideChartTooltip, downloadSvg } from "../core.js";

export default function render(ep) {
  const sec = h("section", { class: "graph-section", id: "sec-epistemic" });
  const head = h("div", { class: "graph-header" },
    h("div", {},
      h("h3", {}, "5. Epistemic Evidence Grounding & Verification Rate"),
      h("p", {}, "Distribution of claims by epistemic status and strict quote verification against source literature.")),
    h("button", { type: "button", class: "btn-export", onclick: () => downloadSvg(svgDonut, "epistemic-donut.svg") }, "Export SVG"));
  sec.append(head);

  const kinds = [
    { key: "evidence", label: "Evidence", count: ep.kinds.evidence || 0, color: "var(--success)" },
    { key: "inference", label: "Inference", count: ep.kinds.inference || 0, color: "var(--steel)" },
    { key: "hypothesis", label: "Hypothesis", count: ep.kinds.hypothesis || 0, color: "var(--warn)" },
    { key: "assumption", label: "Assumption", count: ep.kinds.assumption || 0, color: "#8c96a4" },
    { key: "experimental", label: "Experimental", count: ep.kinds.experimental || 0, color: "var(--ink)" },
  ];
  const total = ep.total_claims || kinds.reduce((s, k) => s + k.count, 0) || 1;

  const w = 320, h_dim = 260, cx = 160, cy = 130, rOuter = 95, rInner = 60;
  const svgDonut = svg("svg", { class: "chart-svg", viewBox: `0 0 ${w} ${h_dim}` });

  let cumAngle = -Math.PI / 2;
  kinds.forEach((k) => {
    if (k.count <= 0) return;
    const sliceAngle = (k.count / total) * Math.PI * 2;
    const startA = cumAngle;
    const endA = cumAngle + sliceAngle;
    cumAngle = endA;

    const x1 = cx + Math.cos(startA) * rOuter;
    const y1 = cy + Math.sin(startA) * rOuter;
    const x2 = cx + Math.cos(endA) * rOuter;
    const y2 = cy + Math.sin(endA) * rOuter;
    const x3 = cx + Math.cos(endA) * rInner;
    const y3 = cy + Math.sin(endA) * rInner;
    const x4 = cx + Math.cos(startA) * rInner;
    const y4 = cy + Math.sin(startA) * rInner;

    const largeArc = sliceAngle > Math.PI ? 1 : 0;
    const d = `M ${x1} ${y1} A ${rOuter} ${rOuter} 0 ${largeArc} 1 ${x2} ${y2} L ${x3} ${y3} A ${rInner} ${rInner} 0 ${largeArc} 0 ${x4} ${y4} Z`;

    const path = svg("path", { d, fill: k.color, class: "donut-slice" });
    path.addEventListener("mouseenter", (e) => {
      showChartTooltip([
        h("div", { class: "tt-title" }, `${k.label}: ${k.count} claims`),
        h("div", { class: "tt-row" }, h("span", {}, "Percentage:"), h("b", {}, `${Math.round((k.count / total) * 100)}%`)),
      ], e.clientX, e.clientY);
    });
    path.addEventListener("mouseleave", hideChartTooltip);
    svgDonut.append(path);
  });

  const donutWrap = h("div", { class: "donut-wrap" },
    svgDonut,
    h("div", { class: "donut-center" },
      h("div", { class: "donut-center-val" }, String(ep.total_claims)),
      h("div", { class: "donut-center-lbl" }, "Total Claims")));

  const evStats = ep.evidence_verification || {};
  const vRate = Math.round((evStats.verification_rate || 0) * 100);

  const panel = h("div", { class: "stats-panel" },
    h("div", { class: "stat-box" },
      h("div", { class: "stat-box-lbl" }, "Quote Verification Rate"),
      h("div", { class: "stat-box-num" }, `${vRate}%`,
        h("small", { class: `check ${vRate >= 70 ? "ok" : "no"}` }, vRate >= 70 ? "High Grounding" : "Unverified Quotes Present")),
      h("p", { class: "stat-box-desc" }, "Passages verified word-for-word against retrieved abstracts or full text before acceptance.")),
    h("div", { class: "stat-box" },
      h("div", { class: "stat-box-lbl" }, "Evidence Citations Breakdown"),
      facts([
        ["Verified quotes", `${evStats.verified_quotes || 0} citations checked word-for-word`],
        ["Unverified quotes", `${evStats.unverified_quotes || 0} passages not found in text`],
        ["Citations without quote", `${evStats.no_quotes || 0} indirect mentions`],
      ])),
    h("div", { class: "stat-box" },
      h("div", { class: "stat-box-lbl" }, "Epistemic Claim Kinds"),
      h("ul", { class: "donut-legend" }, kinds.map((k) =>
        h("li", {},
          h("span", {}, h("i", { style: `background: ${k.color};` }), k.label),
          h("b", {}, `${k.count} (${Math.round((k.count / total) * 100)}%)`))))));

  const grid = h("div", { class: "chart-grid-2" },
    h("div", { class: "chart-card" }, donutWrap),
    panel);
  sec.append(grid);
  return sec;
}
