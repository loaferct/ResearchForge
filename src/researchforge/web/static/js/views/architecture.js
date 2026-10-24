import { h, svg } from "../core.js";

// Interactive architecture: every box is a part of ResearchForge, every numbered arrow one hop of data,
// in the order an investigation uses them. Hover or tap a box for what it does; Play walks the hops in order.

const W = 170, H = 60;
const GROUPS = {
  you: { name: "You", note: "In your browser or terminal" },
  app: { name: "ResearchForge app", note: "Process 1: the web server, the research loop and the report" },
  agent: { name: "Agent runtime", note: "Process 2: DeepSeek Harness (dsh), started once per research step" },
  tools: { name: "Tool server", note: "Process 3: started by the agent runtime, runs ResearchForge's research tools" },
  outside: { name: "Outside this repo", note: "External services and files on disk" },
};

const NODES = [
  { id: "researcher", x: 30, y: 40, group: "outside", title: "Researcher", sub: "you, with one idea",
    does: "Starts an investigation by typing a research idea on the home page, or with researchforge investigate in a terminal. Later approves or declines any experiment.",
    code: "home page form · cli.py" },
  { id: "webui", x: 30, y: 300, group: "you", title: "Web UI", sub: "rail · views · live graphs",
    does: "The page you are on. It shows the rail of investigation steps, each result view and the live charts. While a run is active it polls the API every 2 seconds and redraws only what changed. Each view's code loads the first time you open it.",
    code: "web/static/js/main.js · views/ · graphs/" },
  { id: "experiments", x: 30, y: 560, group: "app", title: "Experiments", sub: "approved runs only",
    does: "Shows each experiment plan's commands for review. Nothing runs until you press Approve; then it runs locally or in Docker with no network, and the result is checked before the loop re-evaluates the hypothesis.",
    code: "experiments/runner.py · experiments/verify.py" },
  { id: "api", x: 260, y: 40, group: "app", title: "API server", sub: "FastAPI on 127.0.0.1",
    does: "Creates the project folder, starts the investigation in a background thread, and serves the project's state, events, records and graph data as JSON. It binds to localhost and has no login, so it is not for shared networks.",
    code: "web/app.py" },
  { id: "loop", x: 260, y: 170, group: "app", title: "Run loop", sub: "one research step a turn",
    does: "Runs the investigation one research step at a time until the controller decides to finalize. You can stop it after the current step and resume later; finished steps are kept.",
    code: "orchestrator.py · ResearchOrchestrator" },
  { id: "decide", x: 470, y: 170, group: "app", title: "Decide next step", sub: "controller",
    does: "Reads the recorded state (open questions, coverage, critique freshness, budgets) and scores candidate actions such as search, analyze or critique. It picks the best one, or stops when more work would add little.",
    code: "controller.py · decide_next_action()" },
  { id: "prompt", x: 680, y: 170, group: "app", title: "Build prompt", sub: "instructions for the step",
    does: "Turns the chosen action into instructions for the agent, with a compact digest of what the workspace already holds, so a step works even if the agent's own history is lost.",
    code: "actions.py · build_prompt()" },
  { id: "launch", x: 680, y: 300, group: "app", title: "Launch agent", sub: "one dsh turn",
    does: "Starts DeepSeek Harness headless with ResearchForge's overlay (shell, file writes and web search turned off), sends the prompt, streams its JSON events and stops it on timeout.",
    code: "runtime/dsh.py · DshHeadlessRuntime" },
  { id: "agent", x: 900, y: 300, group: "agent", title: "AI agent", sub: "reasons and calls tools",
    does: "The model's loop: it reads the prompt, reasons, calls research tools, reads the results and repeats until the step is done. It cannot write results freely; it must call record tools whose inputs are validated.",
    code: "DeepSeek Harness (external)" },
  { id: "llm", x: 1112, y: 300, group: "outside", title: "LLM", sub: "DeepSeek or compatible",
    does: "The language model the agent talks to over HTTPS: DeepSeek by default, or your own Qwen, Llama or Mistral behind an OpenAI-compatible endpoint.",
    code: "researchforge.toml · [model]" },
  { id: "bridge", x: 900, y: 430, group: "agent", title: "Tool bridge", sub: "MCP client",
    does: "Forwards each tool call from the agent to ResearchForge's tool server as MCP JSON-RPC over stdin and stdout.",
    code: "dsh-mcp-client (external)" },
  { id: "toolserver", x: 900, y: 560, group: "tools", title: "Tool server", sub: "exposes research tools",
    does: "Publishes ResearchForge's research tools over MCP and runs each call the agent makes.",
    code: "mcp_server.py" },
  { id: "tools", x: 680, y: 560, group: "tools", title: "Research tools", sub: "search · read · record",
    does: "Every tool the agent can use: search_papers, expand_citations, fetch_paper_text, and the record_* tools that save analyses, claims, gaps, plans and the critique. Each returns structured data.",
    code: "toolkit.py · ResearchToolkit" },
  { id: "evidence", x: 680, y: 690, group: "tools", title: "Evidence checks", sub: "quotes, word for word",
    does: "Checks every quoted passage against the retrieved abstract or full text and rejects unknown paper ids. An evidence claim with a quote that is not found is flagged, never silently accepted.",
    code: "evidence.py · verify_items()" },
  { id: "search", x: 900, y: 690, group: "tools", title: "Paper search", sub: "merge · dedupe · cache",
    does: "Queries the literature sources with retries and an on-disk cache, then merges duplicates across sources and scores relevance for triage.",
    code: "literature/ · sources.py · merge.py" },
  { id: "papersdb", x: 1112, y: 690, group: "outside", title: "Paper databases", sub: "arXiv · OpenAlex · S2 …",
    does: "Open scholarly APIs: arXiv, OpenAlex, Semantic Scholar and Crossref, plus GitHub for code. No proprietary search service.",
    code: "external HTTP APIs" },
  { id: "storage", x: 470, y: 560, group: "app", title: "Project storage", sub: "save and load state",
    does: "Saves every record atomically and loads it back: papers, analyses, claims, decisions and events. It is the single source of truth that every other part reads.",
    code: "workspace.py · Workspace" },
  { id: "folder", x: 470, y: 690, group: "outside", title: "Project folder", sub: "research_projects/<name>/",
    does: "Plain files you can open, audit or resume from: idea.yaml, papers/, evidence/, hypotheses/, experiments/, events.jsonl and reports/.",
    code: "on disk" },
  { id: "analytics", x: 260, y: 560, group: "app", title: "Graph analytics", sub: "data for the charts",
    does: "Computes the data behind Visual graphs from the saved records: the novelty radar, the similarity matrix, the concept network (including papers not analyzed yet), the timeline and evidence grounding.",
    code: "analytics.py · compute_all_graph_data()" },
  { id: "report", x: 260, y: 430, group: "app", title: "Report", sub: "built from records",
    does: "Writes the final report in Markdown and HTML from the recorded data only. No model writes it, so it cannot cite a paper that was never retrieved.",
    code: "report.py · write_reports()" },
];

// Anchor on a side of a node: side is l, r, t or b; f is the position along that side (0..1).
function at(id, side, f = 0.5) {
  const n = NODES.find((x) => x.id === id);
  if (side === "l") return [n.x, n.y + H * f];
  if (side === "r") return [n.x + W, n.y + H * f];
  if (side === "t") return [n.x + W * f, n.y];
  return [n.x + W * f, n.y + H];
}

const STEPS = [
  { from: "researcher", to: "webui", a: at("researcher", "b"), b: at("webui", "t"), label: "Your idea",
    text: "You type a research idea, ideally a question, on the home page and press Investigate research idea." },
  { from: "webui", to: "api", a: at("webui", "r", 0.25), via: [[245, 315], [245, 70]], b: at("api", "l"), label: "POST /api/projects",
    text: "The page sends the idea to the local API server." },
  { from: "api", to: "loop", a: at("api", "b"), b: at("loop", "t"), label: "Start the run",
    text: "The server creates the project folder (idea.yaml) and starts the investigation in a background thread, then the page opens the project view." },
  { from: "loop", to: "decide", a: at("loop", "r"), b: at("decide", "l"), label: "Which step next?",
    text: "Each iteration starts by asking the controller what to do next." },
  { from: "decide", to: "prompt", a: at("decide", "r"), b: at("prompt", "l"), label: "Chosen action",
    text: "The controller picks one action, such as searching for a topic, analyzing papers or critiquing the idea, and says why." },
  { from: "prompt", to: "launch", a: at("prompt", "b"), b: at("launch", "t"), label: "Step prompt",
    text: "The action becomes a prompt with a digest of the current state." },
  { from: "launch", to: "agent", a: at("launch", "r", 0.3), b: at("agent", "l", 0.3), label: "stdin: prompt",
    text: "ResearchForge starts one headless agent turn and sends the prompt on stdin." },
  { from: "agent", to: "llm", a: at("agent", "r"), b: at("llm", "l"), both: true, label: "HTTPS",
    text: "The agent sends the conversation to the language model and gets back reasoning and tool calls. This repeats inside the turn." },
  { from: "agent", to: "bridge", a: at("agent", "b"), b: at("bridge", "t"), label: "Tool call",
    text: "When the model calls a research tool, the agent hands the call to its MCP client." },
  { from: "bridge", to: "toolserver", a: at("bridge", "b"), b: at("toolserver", "t"), both: true, label: "MCP JSON-RPC",
    text: "The call travels as JSON-RPC over stdin and stdout to ResearchForge's tool server, and the result comes back the same way." },
  { from: "toolserver", to: "tools", a: at("toolserver", "l", 0.3), b: at("tools", "r", 0.3), label: "Run the tool",
    text: "The tool server runs the matching research tool." },
  { from: "tools", to: "search", a: at("tools", "r", 0.8), via: [[875, 608], [875, 720]], b: at("search", "l"), label: "Search",
    text: "Search tools hand the query to the literature layer." },
  { from: "search", to: "papersdb", a: at("search", "r"), b: at("papersdb", "l"), both: true, label: "HTTP",
    text: "Paper search queries arXiv, OpenAlex, Semantic Scholar and Crossref, caching responses and merging duplicates." },
  { from: "tools", to: "evidence", a: at("tools", "b"), b: at("evidence", "t"), label: "Verify",
    text: "Before a claim, gap or analysis is saved, every quote is checked word for word against the paper's text." },
  { from: "tools", to: "storage", a: at("tools", "l", 0.5), b: at("storage", "r", 0.5), label: "Save records",
    text: "Validated records are saved to the project: papers, analyses, claims, gaps, plans, the critique." },
  { from: "storage", to: "folder", a: at("storage", "b"), b: at("folder", "t"), label: "Write files",
    text: "Each record is written atomically as a plain file in the project folder." },
  { from: "agent", to: "launch", a: at("agent", "l", 0.75), b: at("launch", "r", 0.75), label: "stdout: events",
    text: "While it works, the agent streams JSON events on stdout; its exit code says the turn is finished." },
  { from: "launch", to: "storage", a: at("launch", "l", 0.7), via: [[606, 342]], b: at("storage", "t", 0.8), label: "events.jsonl",
    text: "Tool calls, decisions and errors are appended to events.jsonl, which feeds the activity log." },
  { from: "storage", to: "decide", a: at("storage", "t", 0.3), b: at("decide", "b", 0.3), label: "Next iteration",
    text: "The next iteration reads the new state, and the loop repeats from step 4 until the controller decides to finalize." },
  { from: "storage", to: "analytics", a: at("storage", "l", 0.5), b: at("analytics", "r", 0.5), label: "Read records",
    text: "When the page asks for graph data, analytics computes it from the saved records." },
  { from: "analytics", to: "webui", a: at("analytics", "l", 0.3), via: [[230, 578], [230, 395], [166, 395]], b: at("webui", "b", 0.8), label: "Polled every 2 s",
    text: "Through the API, the page polls state, events and graph data while the run is active. Views and charts update in place; the concept network grows as papers are found and analyzed." },
  { from: "loop", to: "report", a: at("loop", "b"), b: at("report", "t"), label: "Finalize",
    text: "When the controller finalizes, the report is assembled from the recorded data." },
  { from: "webui", to: "experiments", a: at("webui", "b", 0.3), b: at("experiments", "t", 0.3), label: "Approve",
    text: "If an experiment plan is executable, you review its commands and approve it. After the run, the investigation resumes and re-evaluates the hypothesis." },
];
STEPS.forEach((s, i) => { s.n = i + 1; s.points = [s.a, ...(s.via || []), s.b]; });

const PHASES = [
  { title: "Start", from: 1, to: 3 },
  { title: "One research step (repeats)", from: 4, to: 19 },
  { title: "Showing results", from: 20, to: 23 },
];

function polyLength(pts) {
  let len = 0;
  for (let i = 1; i < pts.length; i++) len += Math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1]);
  return len;
}
function pointAt(pts, t) {
  let left = polyLength(pts) * t;
  for (let i = 1; i < pts.length; i++) {
    const [x0, y0] = pts[i - 1], [x1, y1] = pts[i];
    const seg = Math.hypot(x1 - x0, y1 - y0);
    if (left <= seg || i === pts.length - 1) {
      const f = seg ? Math.min(1, left / seg) : 0;
      return [x0 + (x1 - x0) * f, y0 + (y1 - y0) * f];
    }
    left -= seg;
  }
  return pts[0];
}

export default function render() {
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  let pinned = null; // { type: "node" | "step", id }
  let playing = false, playTimer = null, dotRaf = null;
  let current = 0; // step number shown by Play / Next / Prev, 0 = none

  // ------------------------------------------------------------ diagram
  const root = svg("svg", { class: "arch-svg", viewBox: "0 0 1290 770", role: "group", "aria-label": "ResearchForge architecture: data flow in 23 steps" });
  root.append(svg("defs", {},
    svg("marker", { id: "arch-arrow", viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" },
      svg("path", { d: "M0,0 L10,5 L0,10 z", class: "arch-arrowhead" })),
    svg("marker", { id: "arch-arrow-on", viewBox: "0 0 10 10", refX: "9", refY: "5", markerWidth: "7", markerHeight: "7", orient: "auto-start-reverse" },
      svg("path", { d: "M0,0 L10,5 L0,10 z", class: "arch-arrowhead on" }))));

  const edgeLayer = svg("g", {});
  const nodeLayer = svg("g", {});
  const badgeLayer = svg("g", {});
  const dot = svg("circle", { r: "6", class: "arch-dot", visibility: "hidden" });
  root.append(edgeLayer, nodeLayer, badgeLayer, dot);

  const edgeEls = new Map();
  for (const s of STEPS) {
    const d = "M" + s.points.map((p) => p.join(",")).join(" L");
    const line = svg("path", { d, class: "arch-edge", "marker-end": "url(#arch-arrow)", "marker-start": s.both ? "url(#arch-arrow)" : null });
    const hit = svg("path", { d, class: "arch-edge-hit" });
    const [bx, by] = pointAt(s.points, 0.5);
    const badge = svg("g", { class: "arch-badge", tabindex: "0", role: "button", "aria-label": `Step ${s.n}: ${s.label}` },
      svg("circle", { cx: bx, cy: by, r: "10" }),
      svg("text", { x: bx, y: by + 3.5, "text-anchor": "middle" }, String(s.n)));
    edgeLayer.append(line, hit);
    badgeLayer.append(badge);
    for (const el of [hit, badge]) {
      el.addEventListener("pointerenter", () => preview({ type: "step", id: s.n }));
      el.addEventListener("pointerleave", () => preview(null));
      el.addEventListener("click", () => pin({ type: "step", id: s.n }));
    }
    badge.addEventListener("focus", () => preview({ type: "step", id: s.n }));
    badge.addEventListener("blur", () => preview(null));
    badge.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); pin({ type: "step", id: s.n }); } });
    edgeEls.set(s.n, { line, badge, step: s });
  }

  const nodeEls = new Map();
  for (const n of NODES) {
    const g = svg("g", { class: `arch-node g-${n.group}`, tabindex: "0", role: "button", "aria-label": `${n.title}: ${n.sub}` },
      svg("rect", { x: n.x, y: n.y, width: W, height: H, rx: "6" }),
      svg("rect", { x: n.x, y: n.y, width: "4", height: H, rx: "2", class: "arch-node-rule" }),
      svg("text", { x: n.x + W / 2, y: n.y + 26, "text-anchor": "middle", class: "arch-node-title" }, n.title),
      svg("text", { x: n.x + W / 2, y: n.y + 43, "text-anchor": "middle", class: "arch-node-sub" }, n.sub));
    g.addEventListener("pointerenter", () => preview({ type: "node", id: n.id }));
    g.addEventListener("pointerleave", () => preview(null));
    g.addEventListener("focus", () => preview({ type: "node", id: n.id }));
    g.addEventListener("blur", () => preview(null));
    g.addEventListener("click", () => pin({ type: "node", id: n.id }));
    g.addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); pin({ type: "node", id: n.id }); } });
    nodeLayer.append(g);
    nodeEls.set(n.id, g);
  }
  root.addEventListener("click", (ev) => { if (ev.target === root) pin(null); });

  // ------------------------------------------------------------ pan and zoom
  // The view is the SVG viewBox. Drag anywhere to pan (a drag never counts as a click on a box);
  // Ctrl/⌘ + wheel or a pinch zooms around the pointer, so plain scrolling still scrolls the page.
  const FULL = { x: 0, y: 0, w: 1290, h: 770 };
  const view = { ...FULL };
  let animRaf = null;
  const applyView = () => root.setAttribute("viewBox", `${view.x} ${view.y} ${view.w} ${view.h}`);
  const zoomLevel = () => FULL.w / view.w;
  function toSvg(clientX, clientY) {
    const r = root.getBoundingClientRect();
    return { x: view.x + ((clientX - r.left) / r.width) * view.w, y: view.y + ((clientY - r.top) / r.height) * view.h };
  }
  function clampView() {
    view.w = Math.max(FULL.w / 5, Math.min(FULL.w * 1.25, view.w));
    view.h = view.w * (FULL.h / FULL.w);
    // Keep at least a quarter of the diagram on screen.
    view.x = Math.max(-view.w * 0.75, Math.min(FULL.w - view.w * 0.25, view.x));
    view.y = Math.max(-view.h * 0.75, Math.min(FULL.h - view.h * 0.25, view.y));
  }
  function zoomAt(factor, cx, cy) {
    cancelAnimationFrame(animRaf);
    const w = Math.max(FULL.w / 5, Math.min(FULL.w * 1.25, view.w / factor));
    const f = w / view.w;
    view.x = cx - (cx - view.x) * f;
    view.y = cy - (cy - view.y) * f;
    view.w = w;
    clampView();
    applyView();
    zoomReadout.textContent = `${Math.round(zoomLevel() * 100)}%`;
  }
  function animateTo(target) {
    cancelAnimationFrame(animRaf);
    if (reduced) { Object.assign(view, target); applyView(); zoomReadout.textContent = `${Math.round(zoomLevel() * 100)}%`; return; }
    const from = { ...view }, t0 = performance.now();
    const frame = (now) => {
      const t = Math.min(1, (now - t0) / 260), e = 1 - Math.pow(1 - t, 3);
      for (const k of ["x", "y", "w", "h"]) view[k] = from[k] + (target[k] - from[k]) * e;
      applyView();
      zoomReadout.textContent = `${Math.round(zoomLevel() * 100)}%`;
      if (t < 1) animRaf = requestAnimationFrame(frame);
    };
    animRaf = requestAnimationFrame(frame);
  }
  function zoomButton(factor) {
    const cx = view.x + view.w / 2, cy = view.y + view.h / 2;
    const w = Math.max(FULL.w / 5, Math.min(FULL.w * 1.25, view.w / factor));
    const target = { w, h: w * (FULL.h / FULL.w), x: cx - w / 2, y: cy - (w * (FULL.h / FULL.w)) / 2 };
    animateTo(target);
  }
  const resetView = () => animateTo({ ...FULL });

  root.addEventListener("wheel", (ev) => {
    if (!ev.ctrlKey && !ev.metaKey) return; // plain wheel scrolls the page
    ev.preventDefault();
    const p = toSvg(ev.clientX, ev.clientY);
    zoomAt(Math.exp(-ev.deltaY * 0.0022), p.x, p.y);
  }, { passive: false });

  const pointers = new Map();
  let pan = null, pinch = null, suppressClick = false;
  root.addEventListener("pointerdown", (ev) => {
    if (ev.button !== 0) return;
    pointers.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
    if (pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      pinch = { dist: Math.hypot(a.x - b.x, a.y - b.y), w: view.w };
      pan = null;
    } else {
      pan = { x: ev.clientX, y: ev.clientY, vx: view.x, vy: view.y, moved: false, id: ev.pointerId };
    }
  });
  root.addEventListener("pointermove", (ev) => {
    if (!pointers.has(ev.pointerId)) return;
    pointers.set(ev.pointerId, { x: ev.clientX, y: ev.clientY });
    if (pinch && pointers.size === 2) {
      const [a, b] = [...pointers.values()];
      const mid = toSvg((a.x + b.x) / 2, (a.y + b.y) / 2);
      zoomAt(view.w / (pinch.w * pinch.dist / Math.max(1, Math.hypot(a.x - b.x, a.y - b.y))), mid.x, mid.y);
      suppressClick = true;
      return;
    }
    if (!pan || pan.id !== ev.pointerId) return;
    const dx = ev.clientX - pan.x, dy = ev.clientY - pan.y;
    if (!pan.moved && Math.hypot(dx, dy) < 4) return;
    if (!pan.moved) {
      pan.moved = true;
      // Capture only once it is a real drag, so a plain click still reaches the box under the pointer.
      try { root.setPointerCapture(ev.pointerId); } catch (_) { /* pointer already released */ }
      root.classList.add("panning");
      cancelAnimationFrame(animRaf);
    }
    const r = root.getBoundingClientRect();
    view.x = pan.vx - (dx / r.width) * view.w;
    view.y = pan.vy - (dy / r.height) * view.h;
    clampView();
    applyView();
  });
  const endPointer = (ev) => {
    pointers.delete(ev.pointerId);
    if (pointers.size < 2) pinch = null;
    if (pan && pan.id === ev.pointerId) {
      if (pan.moved) suppressClick = true;
      pan = null;
      root.classList.remove("panning");
    }
  };
  root.addEventListener("pointerup", endPointer);
  root.addEventListener("pointercancel", endPointer);
  // A drag or pinch ends with a click event; swallow it before it selects a box.
  root.addEventListener("click", (ev) => {
    if (!suppressClick) return;
    suppressClick = false;
    ev.stopPropagation();
    ev.preventDefault();
  }, true);
  root.addEventListener("dblclick", (ev) => { if (ev.target === root) resetView(); });

  const zoomReadout = h("span", { class: "arch-zoom-level", "aria-live": "polite" }, "100%");
  const zoomBar = h("div", { class: "arch-zoom", role: "group", "aria-label": "Zoom" },
    h("button", { type: "button", title: "Zoom in", "aria-label": "Zoom in", onclick: () => zoomButton(1.35) }, "+"),
    zoomReadout,
    h("button", { type: "button", title: "Zoom out", "aria-label": "Zoom out", onclick: () => zoomButton(1 / 1.35) }, "−"),
    h("button", { type: "button", title: "Reset view", "aria-label": "Reset view", onclick: resetView }, "⟲"));

  // ------------------------------------------------------------ detail card and step list
  const card = h("aside", { class: "arch-card", "aria-live": "polite" });
  const stepItems = new Map();
  const steps = h("div", { class: "arch-steps" }, PHASES.map((ph) => h("section", {},
    h("h3", {}, `${ph.title}`, h("span", { class: "arch-range" }, ` steps ${ph.from}–${ph.to}`)),
    h("ol", { start: String(ph.from) }, STEPS.filter((s) => s.n >= ph.from && s.n <= ph.to).map((s) => {
      const btn = h("button", { type: "button", class: "arch-step",
        onclick: () => { stop(); go(s.n); },
        onpointerenter: () => preview({ type: "step", id: s.n }), onpointerleave: () => preview(null) },
        h("span", { class: "arch-step-n" }, String(s.n)),
        h("span", {}, h("b", {}, s.label), " ", s.text));
      stepItems.set(s.n, btn);
      return h("li", {}, btn);
    })))));

  function nodeById(id) { return NODES.find((n) => n.id === id); }
  function groupChip(group) { return h("span", { class: `arch-chip g-${group}` }, GROUPS[group].name); }

  function intro() {
    card.replaceChildren(
      h("p", { class: "arch-kicker" }, "How to read this"),
      h("h2", {}, "Hover or tap any box"),
      h("p", {}, "Each box is a part of ResearchForge; each numbered arrow is one hop of data, in the order an investigation uses them. Press Play to follow the flow from your idea to the final report."),
      h("ul", { class: "arch-legend" }, Object.entries(GROUPS).map(([k, g]) => h("li", {}, groupChip(k), h("span", {}, g.note)))));
  }

  function showNode(n) {
    const touching = STEPS.filter((s) => s.from === n.id || s.to === n.id);
    card.replaceChildren(
      h("p", { class: "arch-kicker" }, groupChip(n.group)),
      h("h2", {}, n.title),
      h("p", { class: "arch-sub" }, n.sub),
      h("h3", {}, "What it does"),
      h("p", {}, n.does),
      h("h3", {}, "In the code"),
      h("p", {}, h("code", {}, n.code)),
      touching.length ? h("h3", {}, "Steps it takes part in") : null,
      touching.length ? h("div", { class: "arch-chips" }, touching.map((s) =>
        h("button", { type: "button", class: "arch-step-chip", onclick: () => { stop(); go(s.n); } }, `${s.n}. ${s.label}`))) : null);
  }

  function showStep(s) {
    const a = nodeById(s.from), b = nodeById(s.to);
    card.replaceChildren(
      h("p", { class: "arch-kicker" }, `Step ${s.n} of ${STEPS.length}`),
      h("h2", {}, s.label),
      h("p", { class: "arch-route" }, h("span", {}, a.title), s.both ? " ⇄ " : " → ", h("span", {}, b.title)),
      h("p", {}, s.text),
      h("div", { class: "arch-chips" },
        h("button", { type: "button", class: "arch-step-chip", onclick: () => pin({ type: "node", id: a.id }) }, `About ${a.title}`),
        h("button", { type: "button", class: "arch-step-chip", onclick: () => pin({ type: "node", id: b.id }) }, `About ${b.title}`)));
  }

  // ------------------------------------------------------------ highlighting
  function highlight(sel) {
    const litNodes = new Set(), litSteps = new Set();
    if (sel?.type === "node") {
      litNodes.add(sel.id);
      STEPS.forEach((s) => { if (s.from === sel.id || s.to === sel.id) { litSteps.add(s.n); litNodes.add(s.from); litNodes.add(s.to); } });
    } else if (sel?.type === "step") {
      const s = STEPS[sel.id - 1];
      litSteps.add(s.n); litNodes.add(s.from); litNodes.add(s.to);
    }
    root.classList.toggle("has-focus", Boolean(sel));
    nodeEls.forEach((g, id) => {
      g.classList.toggle("on", litNodes.has(id));
      g.classList.toggle("selected", pinned?.type === "node" && pinned.id === id);
    });
    edgeEls.forEach(({ line, badge, step }, n) => {
      const on = litSteps.has(n);
      line.classList.toggle("on", on);
      badge.classList.toggle("on", on);
      line.setAttribute("marker-end", on ? "url(#arch-arrow-on)" : "url(#arch-arrow)");
      if (step.both) line.setAttribute("marker-start", on ? "url(#arch-arrow-on)" : "url(#arch-arrow)");
    });
    stepItems.forEach((btn, n) => btn.classList.toggle("on", sel?.type === "step" && sel.id === n));
    if (!sel) intro();
    else if (sel.type === "node") showNode(nodeById(sel.id));
    else showStep(STEPS[sel.id - 1]);
  }
  const preview = (sel) => highlight(sel || pinned);
  function pin(sel) {
    stop();
    pinned = sel;
    if (sel?.type === "step") current = sel.id;
    highlight(sel);
    if (sel?.type === "step") travel(STEPS[sel.id - 1]);
  }

  // ------------------------------------------------------------ playback
  function travel(s) {
    cancelAnimationFrame(dotRaf);
    if (reduced) { dot.setAttribute("visibility", "hidden"); return; }
    const t0 = performance.now(), dur = 1100;
    dot.setAttribute("visibility", "visible");
    const frame = (now) => {
      const t = Math.min(1, (now - t0) / dur);
      const eased = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;
      const [x, y] = pointAt(s.points, eased);
      dot.setAttribute("cx", x); dot.setAttribute("cy", y);
      if (t < 1) dotRaf = requestAnimationFrame(frame);
    };
    dotRaf = requestAnimationFrame(frame);
  }
  function go(n) {
    current = Math.max(1, Math.min(STEPS.length, n));
    pinned = { type: "step", id: current };
    highlight(pinned);
    travel(STEPS[current - 1]);
    counter.textContent = `${current} / ${STEPS.length}`;
  }
  function tick() {
    if (!playing) return;
    if (current >= STEPS.length) { stop(); return; }
    go(current + 1);
    playTimer = setTimeout(tick, 2600);
  }
  function play() {
    if (current >= STEPS.length) current = 0;
    playing = true;
    playBtn.textContent = "Pause";
    playBtn.setAttribute("aria-pressed", "true");
    tick();
  }
  function stop() {
    playing = false;
    clearTimeout(playTimer);
    playBtn.textContent = current >= STEPS.length ? "Play again" : current ? "Resume" : "Play the flow";
    playBtn.setAttribute("aria-pressed", "false");
  }
  const playBtn = h("button", { type: "button", class: "primary", "aria-pressed": "false", onclick: () => (playing ? stop() : play()) }, "Play the flow");
  const counter = h("span", { class: "arch-counter" }, `0 / ${STEPS.length}`);
  const controls = h("div", { class: "arch-controls" },
    playBtn,
    h("button", { type: "button", "aria-label": "Previous step", onclick: () => { stop(); go(current - 1); } }, "← Prev"),
    h("button", { type: "button", "aria-label": "Next step", onclick: () => { stop(); go(current + 1); } }, "Next →"),
    counter,
    h("button", { type: "button", class: "arch-reset", onclick: () => { stop(); current = 0; pinned = null; counter.textContent = `0 / ${STEPS.length}`; dot.setAttribute("visibility", "hidden"); highlight(null); stop(); } }, "Reset"));

  intro();
  return h("div", { class: "arch" },
    h("header", { class: "arch-head" },
      h("p", { class: "arch-kicker" }, "Architecture"),
      h("h1", {}, "How an investigation moves through ResearchForge"),
      h("p", { class: "lede" }, "Follow the data from your idea to the final report in 23 steps. Hover or tap a box to see what it does in the app and where it lives in the code.")),
    controls,
    h("div", { class: "arch-grid" },
      h("div", { class: "arch-canvas" }, zoomBar, root,
        h("p", { class: "arch-hint" }, "Drag to move · Ctrl + scroll or pinch to zoom · double-click to reset")),
      card),
    steps);
}
