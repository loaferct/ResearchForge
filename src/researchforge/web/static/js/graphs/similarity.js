import { h, svg, showChartTooltip, hideChartTooltip, downloadSvg, S } from "../core.js";

export default function render(sim) {
  const papers = sim.papers || [];
  const sec = h("section", { class: "graph-section", id: "sec-similarity" });

  const head = h("div", { class: "graph-header" },
    h("div", {},
      h("h3", {}, "2. Multi-Dimensional Paper Similarity Matrix"),
      h("p", {}, "Interactive comparison of the idea against all retrieved literature across Problem Overlap, Method Overlap, and Evaluation Overlap.")),
    h("button", { type: "button", class: "btn-export", onclick: () => downloadSvg(svgScatter, "similarity-matrix.svg") }, "Export SVG"));
  sec.append(head);

  const w = 740, h_dim = 460;
  const padL = 75, padR = 25, padT = 30, padB = 60;
  const plotW = w - padL - padR;
  const plotH = h_dim - padT - padB;

  const svgScatter = svg("svg", { class: "chart-svg", viewBox: `0 0 ${w} ${h_dim}` });

  const midX = padL + plotW / 2;
  const midY = padT + plotH / 2;

  // Quadrants
  svgScatter.append(svg("rect", { x: midX, y: padT, width: plotW / 2, height: plotH / 2, fill: "rgba(163, 51, 31, 0.04)" }));
  svgScatter.append(svg("text", { x: midX + 10, y: padT + 18, class: "quadrant-label" }, "DIRECT OVERLAP (CLOSEST WORK)"));

  svgScatter.append(svg("rect", { x: padL, y: padT, width: plotW / 2, height: plotH / 2, fill: "rgba(58, 90, 126, 0.03)" }));
  svgScatter.append(svg("text", { x: padL + 10, y: padT + 18, class: "quadrant-label" }, "ALTERNATIVE SOLUTIONS (SAME PROBLEM)"));

  svgScatter.append(svg("rect", { x: midX, y: midY, width: plotW / 2, height: plotH / 2, fill: "rgba(31, 122, 77, 0.03)" }));
  svgScatter.append(svg("text", { x: midX + 10, y: midY + 18, class: "quadrant-label" }, "TRANSFERABLE METHODS (DIFFERENT PROBLEM)"));

  svgScatter.append(svg("rect", { x: padL, y: midY, width: plotW / 2, height: plotH / 2, fill: "rgba(15, 20, 25, 0.02)" }));
  svgScatter.append(svg("text", { x: padL + 10, y: midY + 18, class: "quadrant-label" }, "PERIPHERAL LITERATURE"));

  // Grid
  [0, 0.25, 0.5, 0.75, 1.0].forEach((v) => {
    const gx = padL + v * plotW;
    const gy = padT + (1 - v) * plotH;
    svgScatter.append(svg("line", { x1: gx, y1: padT, x2: gx, y2: padT + plotH, class: v === 0.5 ? "grid-line-strong" : "grid-line" }));
    svgScatter.append(svg("line", { x1: padL, y1: gy, x2: padL + plotW, y2: gy, class: v === 0.5 ? "grid-line-strong" : "grid-line" }));
    svgScatter.append(svg("text", { x: gx, y: padT + plotH + 16, class: "axis-text", "text-anchor": "middle" }, `${Math.round(v * 100)}%`));
    svgScatter.append(svg("text", { x: padL - 8, y: gy + 3, class: "axis-text", "text-anchor": "end" }, `${Math.round(v * 100)}%`));
  });

  svgScatter.append(svg("text", { x: padL + plotW / 2, y: h_dim - 18, class: "chart-title", "text-anchor": "middle" }, "Method Overlap → (Technical Similarity)"));
  svgScatter.append(svg("text", {
    x: -(padT + plotH / 2),
    y: 20,
    class: "chart-title",
    "text-anchor": "middle",
    transform: "rotate(-90)",
  }, "Problem Overlap → (Domain & Task Similarity)"));

  // Bubbles
  const bubbleEls = [];
  papers.forEach((p) => {
    const cx = padL + p.method_overlap * plotW;
    const cy = padT + (1 - p.problem_overlap) * plotH;
    const rad = 5 + Math.round(p.evaluation_overlap * 7);
    const color = p.is_closest ? "#b3801f" : (p.relevance_tier === "high" ? "#1f7a4d" : (p.relevance_tier === "medium" ? "#3a5a7e" : "#8c96a4"));

    const circle = svg("circle", {
      cx, cy, r: rad,
      fill: color,
      "fill-opacity": "0.78",
      stroke: p.is_closest ? "var(--warn)" : "#ffffff",
      "stroke-width": p.is_closest ? "2.5" : "1.2",
      class: `scatter-bubble ${p.is_closest ? "closest" : ""}`,
      "data-id": p.id,
      "data-tier": p.relevance_tier,
      "data-quad": p.quadrant,
      "data-title": p.title.toLowerCase(),
    });

    circle.addEventListener("mouseenter", (e) => {
      showChartTooltip([
        h("div", { class: "tt-title" }, p.title),
        h("div", { class: "tt-meta" }, `${p.authors || "Unknown"} (${p.year || "n.d."})${p.citations ? ` • ${p.citations} citations` : ""}`),
        h("div", { class: "tt-row" }, h("span", {}, "Problem Overlap:"), h("b", {}, `${Math.round(p.problem_overlap * 100)}%`)),
        h("div", { class: "tt-row" }, h("span", {}, "Method Overlap:"), h("b", {}, `${Math.round(p.method_overlap * 100)}%`)),
        h("div", { class: "tt-row" }, h("span", {}, "Evaluation Overlap:"), h("b", {}, `${Math.round(p.evaluation_overlap * 100)}%`)),
        h("div", { class: "tt-row" }, h("span", {}, "Composite Similarity:"), h("b", {}, `${Math.round(p.composite_similarity * 100)}%`)),
        p.conceptual_difference ? h("div", { class: "tt-desc" }, `Difference: ${p.conceptual_difference}`) : null,
      ], e.clientX, e.clientY);
    });
    circle.addEventListener("mouseleave", hideChartTooltip);
    circle.addEventListener("click", () => {
      selectPaper(p.id);
    });

    svgScatter.append(circle);
    bubbleEls.push(circle);
  });

  const controls = h("div", { class: "scatter-controls" },
    [["all", `All Papers (${papers.length})`],
     ["high", "High Relevance Only"],
     ["closest", "Closest Work Only"],
     ["direct_overlap", "Direct Overlap Quadrant"]].map(([k, label]) =>
      h("button", {
        type: "button",
        class: "filter-btn",
        "aria-pressed": String(S.graphs.scatterFilter === k),
        onclick: (ev) => {
          S.graphs.scatterFilter = k;
          controls.querySelectorAll(".filter-btn").forEach((b) => b.setAttribute("aria-pressed", String(b === ev.currentTarget)));
          applyFilter();
        }
      }, label)),
    h("input", {
      type: "search",
      placeholder: "Filter / highlight paper by title...",
      "aria-label": "Search papers",
      oninput: (ev) => {
        S.graphs.scatterSearch = ev.target.value.toLowerCase().trim();
        applyFilter();
      }
    }));

  function applyFilter() {
    const f = S.graphs.scatterFilter;
    const q = S.graphs.scatterSearch;
    bubbleEls.forEach((el) => {
      const isClose = el.classList.contains("closest");
      const tier = el.getAttribute("data-tier");
      const quad = el.getAttribute("data-quad");
      const title = el.getAttribute("data-title");

      let match = true;
      if (f === "high") match = tier === "high";
      else if (f === "closest") match = isClose;
      else if (f === "direct_overlap") match = quad === "direct_overlap";

      if (q && !title.includes(q)) match = false;

      el.classList.toggle("dimmed", !match);
      el.classList.toggle("highlighted", Boolean(q && match));
    });
  }

  const inspectorBox = h("div", { class: "inspector-card" });
  function selectPaper(paperId) {
    const p = papers.find((x) => x.id === paperId) || papers[0];
    if (!p) return;
    S.graphs.selectedPaper = p.id;

    inspectorBox.replaceChildren(
      h("div", { style: "display: flex; justify-content: space-between; align-items: baseline; gap: 1rem; flex-wrap: wrap;" },
        h("h4", {}, p.url ? h("a", { href: p.url, target: "_blank", rel: "noopener noreferrer" }, p.title) : p.title),
        h("span", { class: `tier ${p.relevance_tier}` }, `${p.relevance_tier} relevance`)),
      h("div", { class: "meta" }, `${p.authors || "Unknown authors"} • ${p.venue || "Venue not specified"} (${p.year || "n.d."}) • ${p.citations} citations per provider`),
      h("div", { class: "inspector-bars" },
        h("div", { class: "inspector-metric" },
          h("div", { class: "lbl" }, "Problem Overlap"),
          h("div", { class: "val" }, `${Math.round(p.problem_overlap * 100)}%`),
          h("div", { class: "p-bar" }, h("div", { class: "p-fill", style: `width: ${p.problem_overlap * 100}%; background: var(--steel);` }))),
        h("div", { class: "inspector-metric" },
          h("div", { class: "lbl" }, "Method Overlap"),
          h("div", { class: "val" }, `${Math.round(p.method_overlap * 100)}%`),
          h("div", { class: "p-bar" }, h("div", { class: "p-fill", style: `width: ${p.method_overlap * 100}%; background: var(--success);` }))),
        h("div", { class: "inspector-metric" },
          h("div", { class: "lbl" }, "Evaluation Overlap"),
          h("div", { class: "val" }, `${Math.round(p.evaluation_overlap * 100)}%`),
          h("div", { class: "p-bar" }, h("div", { class: "p-fill", style: `width: ${p.evaluation_overlap * 100}%; background: var(--warn);` })))),
      h("div", { class: "diff-text" }, h("b", {}, "How this work differs: "), p.conceptual_difference || "No specific conceptual distinction recorded."),
      p.basis ? h("div", { class: "diff-text", style: "color: var(--ink-60);" }, h("b", {}, "Basis: "), p.basis) : null);
  }

  if (papers.length) selectPaper(papers[0].id);

  const topPapersBox = h("div", { class: "chart-card", style: "margin-top: 20px;" },
    h("h4", { style: "margin: 0 0 12px; font-size: 0.9375rem;" }, "Top Closest Papers: Side-by-Side Multi-Aspect Overlap"),
    h("div", { style: "display: flex; gap: 16px; margin-bottom: 12px; font-size: 0.75rem; font-family: var(--mono); color: var(--ink-60);" },
      h("span", { style: "display: inline-flex; align-items: center; gap: 4px;" }, h("i", { style: "width: 8px; height: 8px; border-radius: 2px; background: var(--steel); display: inline-block;" }), "Problem Overlap"),
      h("span", { style: "display: inline-flex; align-items: center; gap: 4px;" }, h("i", { style: "width: 8px; height: 8px; border-radius: 2px; background: var(--success); display: inline-block;" }), "Method Overlap"),
      h("span", { style: "display: inline-flex; align-items: center; gap: 4px;" }, h("i", { style: "width: 8px; height: 8px; border-radius: 2px; background: var(--warn); display: inline-block;" }), "Evaluation Overlap")),
    h("div", {}, (sim.top_similar || papers.slice(0, 7)).map((tp) =>
      h("div", { class: "bar-chart-row" },
        h("div", { class: "p-title", title: tp.title }, tp.title),
        h("div", { class: "bar-group" },
          h("div", { class: "bar-sub" }, h("span", { class: "b-lbl" }, "Prob"), h("div", { class: "b-track" }, h("div", { class: "b-fill", style: `width: ${tp.problem_overlap * 100}%; background: var(--steel);` })), h("span", { class: "b-val" }, `${Math.round(tp.problem_overlap * 100)}%`)),
          h("div", { class: "bar-sub" }, h("span", { class: "b-lbl" }, "Meth"), h("div", { class: "b-track" }, h("div", { class: "b-fill", style: `width: ${tp.method_overlap * 100}%; background: var(--success);` })), h("span", { class: "b-val" }, `${Math.round(tp.method_overlap * 100)}%`)),
          h("div", { class: "bar-sub" }, h("span", { class: "b-lbl" }, "Eval"), h("div", { class: "b-track" }, h("div", { class: "b-fill", style: `width: ${tp.evaluation_overlap * 100}%; background: var(--warn);` })), h("span", { class: "b-val" }, `${Math.round(tp.evaluation_overlap * 100)}%`)))))));

  sec.append(controls, h("div", { class: "chart-card" }, svgScatter), inspectorBox, topPapersBox);
  return sec;
}
