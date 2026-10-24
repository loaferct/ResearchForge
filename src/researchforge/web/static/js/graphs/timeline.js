import { h, svg, showChartTooltip, hideChartTooltip, downloadSvg } from "../core.js";

export default function render(tl) {
  const points = tl.timeline || [];
  const sec = h("section", { class: "graph-section", id: "sec-timeline" });
  const head = h("div", { class: "graph-header" },
    h("div", {},
      h("h3", {}, "4. Literature Publication Timeline & Citation Momentum"),
      h("p", {}, "Historical progression and recent publication velocity of relevant literature in this field.")),
    h("button", { type: "button", class: "btn-export", onclick: () => downloadSvg(svgTl, "publication-timeline.svg") }, "Export SVG"));
  sec.append(head);

  const w = 740, h_dim = 300, padL = 60, padR = 25, padT = 30, padB = 45;
  const plotW = w - padL - padR;
  const plotH = h_dim - padT - padB;
  const svgTl = svg("svg", { class: "chart-svg", viewBox: `0 0 ${w} ${h_dim}` });

  if (!points.length) {
    sec.append(h("p", { class: "empty" }, "No publication dates recorded for retrieved papers."));
    return sec;
  }

  const maxCount = Math.max(...points.map((p) => p.count), 5);
  const barW = Math.min(48, Math.max(14, (plotW / points.length) * 0.65));
  const step = plotW / points.length;

  [0, 0.25, 0.5, 0.75, 1.0].forEach((v) => {
    const gy = padT + (1 - v) * plotH;
    svgTl.append(svg("line", { x1: padL, y1: gy, x2: padL + plotW, y2: gy, class: "grid-line" }));
    svgTl.append(svg("text", { x: padL - 8, y: gy + 3, class: "axis-text", "text-anchor": "end" }, String(Math.round(v * maxCount))));
  });

  const linePts = [];
  points.forEach((p, i) => {
    const bx = padL + i * step + (step - barW) / 2;
    const bHeight = (p.count / maxCount) * plotH;
    const by = padT + plotH - bHeight;

    const bar = svg("rect", {
      x: bx, y: by, width: barW, height: bHeight,
      fill: "var(--steel)", "fill-opacity": "0.85", rx: "3",
      style: "cursor: pointer; transition: fill 150ms ease;",
    });

    bar.addEventListener("mouseenter", (e) => {
      bar.setAttribute("fill", "var(--success)");
      showChartTooltip([
        h("div", { class: "tt-title" }, `Year ${p.year}`),
        h("div", { class: "tt-row" }, h("span", {}, "Retrieved Papers:"), h("b", {}, String(p.count))),
        h("div", { class: "tt-row" }, h("span", {}, "Analyzed In-Depth:"), h("b", {}, String(p.analyzed_count))),
        h("div", { class: "tt-row" }, h("span", {}, "Total Citations:"), h("b", {}, String(p.total_citations))),
        p.papers?.length ? h("div", { class: "tt-desc" }, `Key work: ${p.papers[0].title}`) : null,
      ], e.clientX, e.clientY);
    });
    bar.addEventListener("mouseleave", () => {
      bar.setAttribute("fill", "var(--steel)");
      hideChartTooltip();
    });

    svgTl.append(bar);
    svgTl.append(svg("text", { x: bx + barW / 2, y: padT + plotH + 18, class: "axis-text", "text-anchor": "middle" }, String(p.year)));
    linePts.push(`${bx + barW / 2},${by}`);
  });

  if (linePts.length > 1) {
    svgTl.append(svg("polyline", { points: linePts.join(" "), fill: "none", stroke: "var(--success)", "stroke-width": "2", "stroke-dasharray": "3 3" }));
  }

  sec.append(h("div", { class: "chart-card" }, svgTl));
  return sec;
}
