import { h, facts, svg, showChartTooltip, hideChartTooltip, downloadSvg } from "../core.js";

export default function render(nov) {
  const dims = nov.dimensions || [];
  const sec = h("section", { class: "graph-section", id: "sec-novelty" });

  const head = h("div", { class: "graph-header" },
    h("div", {},
      h("h3", {}, "1. Multi-Dimensional Idea Novelty & Risk Profile"),
      h("p", {}, "Quantitative radar evaluating research uniqueness, methodological distinction, evidence backing, and feasibility.")),
    h("button", { type: "button", class: "btn-export", onclick: () => downloadSvg(svgRadar, "novelty-radar.svg") }, "Export SVG"));
  sec.append(head);

  const w = 480, h_dim = 360, cx = 240, cy = 180, r = 120;
  const n = dims.length || 6;
  const svgRadar = svg("svg", { class: "chart-svg", viewBox: `0 0 ${w} ${h_dim}` });

  // Concentric polygon grids (20%, 40%, 60%, 80%, 100%)
  [0.2, 0.4, 0.6, 0.8, 1.0].forEach((lvl) => {
    const pts = [];
    for (let i = 0; i < n; i++) {
      const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
      pts.push(`${cx + Math.cos(angle) * r * lvl},${cy + Math.sin(angle) * r * lvl}`);
    }
    svgRadar.append(svg("polygon", { points: pts.join(" "), class: "radar-grid" }));
    svgRadar.append(svg("text", { x: cx + 4, y: cy - r * lvl - 2, class: "axis-text" }, `${Math.round(lvl * 100)}%`));
  });

  // Radial axis lines
  for (let i = 0; i < n; i++) {
    const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
    const x2 = cx + Math.cos(angle) * r;
    const y2 = cy + Math.sin(angle) * r;
    svgRadar.append(svg("line", { x1: cx, y1: cy, x2, y2, class: "radar-axis" }));
  }

  // Baseline literature polygon
  const baselinePts = [];
  for (let i = 0; i < n; i++) {
    const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
    const bScore = [40, 50, 45, 50, 60, 45][i] || 50;
    baselinePts.push(`${cx + Math.cos(angle) * r * (bScore / 100)},${cy + Math.sin(angle) * r * (bScore / 100)}`);
  }
  svgRadar.append(svg("polygon", { points: baselinePts.join(" "), class: "radar-baseline" }));

  // Idea Novelty Polygon
  const ideaPts = [];
  dims.forEach((d, i) => {
    const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
    const rad = (Math.min(100, Math.max(0, d.score)) / 100) * r;
    ideaPts.push(`${cx + Math.cos(angle) * rad},${cy + Math.sin(angle) * rad}`);
  });
  svgRadar.append(svg("polygon", { points: ideaPts.join(" "), class: "radar-polygon" }));

  // Vertices and Labels
  dims.forEach((d, i) => {
    const angle = (Math.PI * 2 / n) * i - Math.PI / 2;
    const rad = (Math.min(100, Math.max(0, d.score)) / 100) * r;
    const px = cx + Math.cos(angle) * rad;
    const py = cy + Math.sin(angle) * rad;

    const dot = svg("circle", { cx: px, cy: py, r: 4.5, class: "radar-point" });
    dot.addEventListener("mouseenter", (e) => {
      showChartTooltip([
        h("div", { class: "tt-title" }, d.axis),
        h("div", { class: "tt-row" }, h("span", {}, "Score:"), h("b", {}, `${d.score}%`)),
        h("div", { class: "tt-desc" }, d.description),
      ], e.clientX, e.clientY);
    });
    dot.addEventListener("mouseleave", hideChartTooltip);
    svgRadar.append(dot);

    const lx = cx + Math.cos(angle) * (r + 22);
    const ly = cy + Math.sin(angle) * (r + 14);
    const anchor = Math.abs(Math.cos(angle)) < 0.2 ? "middle" : (Math.cos(angle) > 0 ? "start" : "end");
    const lbl = svg("text", { x: lx, y: ly, class: "radar-label", "text-anchor": anchor }, d.axis);
    const sc = svg("tspan", { class: "radar-score", dx: "4" }, `${d.score}%`);
    lbl.append(sc);
    svgRadar.append(lbl);
  });

  // Right Side Metrics Panel
  const panel = h("div", { class: "stats-panel" },
    h("div", { class: "stat-box" },
      h("div", { class: "stat-box-lbl" }, "Overall Novelty & Independence Index"),
      h("div", { class: "stat-box-num" }, `${nov.composite_novelty_score}%`,
        h("small", { class: `tier ${nov.composite_novelty_score >= 60 ? "high" : "medium"}` },
          nov.composite_novelty_score >= 65 ? "Distinct Idea" : (nov.composite_novelty_score >= 45 ? "Moderate Overlap" : "Substantial Overlap"))),
      h("p", { class: "stat-box-desc" }, nov.status_rationale || "Derived from maximum literature overlap, claim grounding, and critique analysis.")),
    h("div", { class: "stat-box" },
      h("div", { class: "stat-box-lbl" }, "Peak Literature Overlap Signals"),
      facts([
        ["Max Problem Overlap", `${Math.round(nov.max_problem_overlap * 100)}% (closest literature setting)`],
        ["Max Method Overlap", `${Math.round(nov.max_method_overlap * 100)}% (closest technical approach)`],
        ["Max Evaluation Overlap", `${Math.round(nov.max_eval_overlap * 100)}% (benchmarks & metrics)`],
      ])),
    h("div", { class: "stat-box" },
      h("div", { class: "stat-box-lbl" }, "Critique Severity Distribution"),
      h("div", { class: "critique-bars" },
        [["High Severity", nov.critique_severities.high || 0, "var(--error)"],
         ["Moderate", nov.critique_severities.moderate || 0, "var(--warn)"],
         ["Low Severity", nov.critique_severities.low || 0, "var(--success)"]].map(([name, val, col]) =>
          h("div", { class: "critique-bar-row" },
            h("span", { class: "c-name" }, name),
            h("div", { class: "c-track" }, h("div", { class: "c-fill", style: `width: ${Math.min(100, val * 25)}%; background: ${col};` })),
            h("span", { class: "c-val" }, String(val)))))));

  const grid = h("div", { class: "chart-grid-2" },
    h("div", { class: "chart-card" }, svgRadar),
    panel);
  sec.append(grid);
  return sec;
}
