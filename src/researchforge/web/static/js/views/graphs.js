import { h, S, data, pendingNote } from "../core.js";

// Each chart is its own module, fetched the first time its section nears the viewport.
// A module's default export takes its slice of graph_data and returns either a Node (redrawn when the
// slice changes) or a live chart { el, update(slice) } that absorbs new data in place.
const SECTIONS = [
  { key: "novelty", label: "Novelty & Risk Radar", load: () => import("../graphs/novelty.js"), slice: (g) => g.novelty, ready: (g) => g.similarity?.papers?.length },
  { key: "similarity", label: "Paper Similarity Matrix", load: () => import("../graphs/similarity.js"), slice: (g) => g.similarity, ready: (g) => g.similarity?.papers?.length },
  { key: "network", label: "Concept Network", load: () => import("../graphs/network.js"), slice: (g) => g.network, ready: (g) => (g.network?.nodes?.length || 0) > 1 },
  { key: "timeline", label: "Publication Timeline", load: () => import("../graphs/timeline.js"), slice: (g) => g.timeline, ready: (g) => g.timeline?.timeline?.length },
  { key: "epistemic", label: "Evidence Grounding", load: () => import("../graphs/epistemic.js"), slice: (g) => g.epistemic, ready: (g) => g.epistemic?.total_claims },
];

// The view outlives re-renders while a project is open, so live charts keep their layout as data arrives.
let live = null;

function build() {
  const nav = h("div", { class: "graph-nav", role: "tablist", "aria-label": "Graph views" },
    [["all", "All Visualizations"], ...SECTIONS.map((s) => [s.key, s.label])].map(([k, lbl]) => h("button", {
      type: "button",
      "aria-pressed": String(S.graphs.subTab === k),
      onclick: (ev) => {
        S.graphs.subTab = k;
        nav.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === ev.currentTarget)));
        updateVisibility();
      },
    }, lbl)));
  const status = h("p", { class: "graph-live", hidden: true, "aria-live": "polite" });
  const container = h("div", { class: "graphs-container" });
  const slots = SECTIONS.map((s) => ({ ...s, el: h("div", { class: "graph-slot", "data-key": s.key }, h("div", { class: "graph-slot-wait", "aria-hidden": "true" })), mod: null, chart: null, sig: null, loading: false }));
  container.append(...slots.map((s) => s.el));
  const root = [h("h2", {}, "Visual Graphs & Analytics"),
    h("p", { class: "lede" }, "Multi-dimensional analytical mapping of the research idea: quantitative novelty profile, multi-aspect paper similarity matrix, concept network topology, publication trends, and evidence grounding."),
    nav, status, container];

  const observer = "IntersectionObserver" in window
    ? new IntersectionObserver((entries) => entries.forEach((en) => {
      if (!en.isIntersecting) return;
      const slot = slots.find((s) => s.el === en.target);
      if (slot) { observer.unobserve(slot.el); slot.near = true; mount(slot); }
    }), { rootMargin: "400px 0px" })
    : null;
  slots.forEach((s) => (observer ? observer.observe(s.el) : (s.near = true)));

  function updateVisibility() {
    const cur = S.graphs.subTab;
    slots.forEach((s) => {
      s.el.hidden = (cur !== "all" && cur !== s.key) || !s.ready(live.gData);
      if (!s.el.hidden && cur === s.key) { s.near = true; mount(s); }
    });
  }

  async function mount(slot) {
    if (slot.el.hidden || !slot.near || !live?.gData || !slot.ready(live.gData)) return;
    if (!slot.mod) {
      if (slot.loading) return;
      slot.loading = true;
      try { slot.mod = await slot.load(); } catch (e) {
        slot.el.replaceChildren(h("p", { class: "error" }, `This chart could not be loaded: ${e.message}`));
        return;
      } finally { slot.loading = false; }
    }
    slot.chart?.resume?.();
    const slice = slot.slice(live.gData);
    const sig = JSON.stringify(slice);
    if (sig === slot.sig) return;
    slot.sig = sig;
    if (slot.chart?.update) { slot.chart.update(slice); return; }
    const out = slot.mod.default(slice);
    slot.chart = out instanceof Node ? null : out;
    slot.el.replaceChildren(out instanceof Node ? out : out.el);
  }

  return { project: S.project, root, slots, status, gData: null, updateVisibility, mount };
}

export default async function graphs() {
  const gData = await data("graph_data");
  const anyReady = gData && SECTIONS.some((s) => s.ready(gData));
  if (!anyReady) {
    return [h("h2", {}, "Visual Graphs & Analytics"), pendingNote("Visual graphs and similarity metrics")];
  }
  if (!live || live.project !== S.project) live = build();
  live.gData = gData;
  const net = gData.network || {};
  const analyzed = (net.nodes || []).filter((n) => n.type === "paper" && n.analyzed !== false).length;
  live.status.hidden = !S.info?.running;
  live.status.textContent = S.info?.running
    ? `Live: ${analyzed} of ${net.retrieved_total ?? analyzed} retrieved papers analyzed so far. The charts update as the investigation records more.`
    : "";
  live.updateVisibility();
  live.slots.forEach((s) => live.mount(s));
  return live.root;
}
