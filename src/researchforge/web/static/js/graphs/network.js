import { h, plural, showChartTooltip, hideChartTooltip, downloadCanvas } from "../core.js";

// Concept network on a canvas with a continuous force layout. New papers grow out of their category (or the
// idea) and the layout relaxes around them, so the graph fills in while the investigation is still running.

const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const HEIGHT = 520;

// Rest length and stiffness of each relation; similarity links shorten as overlap grows.
const LINK = {
  idea_category: { len: () => 200, k: 0.06 },
  category_paper: { len: () => 70, k: 0.1 },
  similarity: { len: (e) => 95 + (1 - (e.similarity ?? 0.3)) * 190, k: 0.025 },
  retrieved: { len: () => 330, k: 0.012 },
};

function radiusOf(d) {
  if (d.type === "idea") return 18;
  if (d.type === "category") return 10;
  if (d.analyzed === false) return 3.5;
  if (d.is_closest) return 9;
  return d.group === "high" ? 7 : 5.5;
}

// Theme colors come from the CSS tokens and are re-read when the theme changes. Tokens may be color-mix()
// expressions, so each is resolved through a probe element's computed color rather than parsed directly.
function readPalette() {
  const probe = document.createElement("span");
  probe.style.display = "none";
  document.body.append(probe);
  const tok = (name, fallback) => {
    probe.style.color = fallback;
    probe.style.color = `var(${name}, ${fallback})`;
    const v = getComputedStyle(probe).color;
    const nums = (v.match(/-?[\d.]+/g) || ["0", "0", "0"]).slice(0, 3).map(Number);
    return v.startsWith("color(") ? nums.map((c) => Math.round(c * 255)) : nums;
  };
  const out = {
    idea: tok("--success", "#1f7a4d"), category: tok("--steel", "#3a5a7e"), closest: tok("--warn", "#b3801f"),
    paper: tok("--steel", "#3a5a7e"), muted: tok("--ink-60", "#5a626c"), ink: tok("--ink", "#0f1419"), card: tok("--card", "#ffffff"),
    font: getComputedStyle(document.documentElement).getPropertyValue("--sans").trim() || "sans-serif",
  };
  probe.remove();
  return out;
}
const rgba = ([r, g, b], a) => `rgba(${r}, ${g}, ${b}, ${Math.max(0, Math.min(1, a))})`;
const ease = (cur, target, rate) => cur + (target - cur) * rate;

export default function render(net) {
  const sec = h("section", { class: "graph-section", id: "sec-network" });
  const fitBtn = h("button", { type: "button", class: "btn-export", onclick: () => fit(true) }, "Fit view");
  const exportBtn = h("button", { type: "button", class: "btn-export", onclick: () => downloadCanvas(canvas, "concept-network.png") }, "Export PNG");
  sec.append(h("div", { class: "graph-header" },
    h("div", {},
      h("h3", {}, "3. Interactive Concept & Citation Network"),
      h("p", {}, "Your idea at the center, the field's categories around it, and the papers linked to them. Closer and thicker links mean more overlap. Drag nodes, scroll to zoom, click to inspect.")),
    h("div", { style: "display: flex; gap: 8px;" }, fitBtn, exportBtn)));

  // ------------------------------------------------------------ controls
  let filter = "all";
  let query = "";
  const pills = [["all", "All nodes"], ["categories", "Idea & categories"], ["closest", "Closest work"], ["high_sim", "High similarity ≥40%"], ["analyzed", "Analyzed only"]];
  const pillEls = new Map();
  const pillGroup = h("div", { class: "network-pill-group", role: "group", "aria-label": "Show nodes" },
    pills.map(([key, label]) => {
      const b = h("button", { type: "button", class: "network-pill", "aria-pressed": String(filter === key), onclick: () => {
        filter = key;
        pillEls.forEach((el, k) => el.setAttribute("aria-pressed", String(k === key)));
        applyFilters();
      } }, label);
      pillEls.set(key, b);
      return b;
    }));
  const search = h("input", { type: "search", class: "network-search", placeholder: "Find a paper or category…", "aria-label": "Find a node",
    oninput: (ev) => { query = ev.target.value.toLowerCase().trim(); applyFilters(); },
    onkeydown: (ev) => {
      if (ev.key !== "Enter") return;
      const hit = [...nodes.values()].find((n) => n.match && n.at > 0 && n.d.type !== "idea");
      if (hit) { select(hit); focusOn(hit); }
    } });
  sec.append(h("div", { class: "network-controls" }, pillGroup, search));

  // ------------------------------------------------------------ canvas
  const canvas = h("canvas", { class: "network-canvas", tabindex: "0", role: "img" });
  const ctx = canvas.getContext("2d");
  const toast = h("div", { class: "network-toast", "aria-hidden": "true" });
  const wrap = h("div", { class: "network-wrapper" },
    h("div", { class: "network-toolbar" },
      h("button", { type: "button", title: "Zoom in", "aria-label": "Zoom in", onclick: () => zoomBy(1.25) }, "+"),
      h("button", { type: "button", title: "Zoom out", "aria-label": "Zoom out", onclick: () => zoomBy(0.8) }, "−"),
      h("button", { type: "button", title: "Fit view", "aria-label": "Fit view", onclick: () => fit(true) }, "⟲")),
    h("div", { class: "network-legend" },
      h("span", {}, h("i", { class: "lg-idea" }), "Your idea"),
      h("span", {}, h("i", { class: "lg-category" }), "Category"),
      h("span", {}, h("i", { class: "lg-paper" }), "Analyzed paper"),
      h("span", {}, h("i", { class: "lg-closest" }), "Closest work"),
      h("span", {}, h("i", { class: "lg-retrieved" }), "Retrieved, not analyzed yet")),
    canvas, toast);
  sec.append(wrap);
  const inspector = h("div", { class: "inspector-card", style: "margin-top: 14px;" });
  sec.append(inspector);

  let pal = readPalette();
  const themeWatch = new MutationObserver(() => { pal = readPalette(); kick(); });
  themeWatch.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

  let width = 940, dpr = 1;
  function resize() {
    width = Math.max(280, wrap.clientWidth || 940);
    dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.round(width * dpr);
    canvas.height = Math.round(HEIGHT * dpr);
    canvas.style.height = `${HEIGHT}px`;
    kick();
  }
  if ("ResizeObserver" in window) new ResizeObserver(resize).observe(wrap);

  // ------------------------------------------------------------ simulation state
  const nodes = new Map(); // id -> { d, x, y, vx, vy, r, rt, a, at, dim, born, match }
  let edges = [];
  let heat = 1;
  let hover = null, selected = null, drag = null;
  const cam = { x: 0, y: 0, k: 1 }, camGoal = { x: 0, y: 0, k: 1 };
  let userMoved = false;
  let raf = null;
  let toastTimer = null;

  function place(d, idx) {
    if (d.type === "idea") return { x: 0, y: 0 };
    if (d.type === "category") {
      const cats = net.nodes.filter((n) => n.type === "category");
      const angle = (cats.indexOf(d) / Math.max(1, cats.length)) * Math.PI * 2 - Math.PI / 2;
      return { x: Math.cos(angle) * 200, y: Math.sin(angle) * 150 };
    }
    // New papers start beside their category, or beside the idea, and drift into place.
    const parent = nodes.get(d.category_id) || nodes.get("idea");
    const angle = Math.random() * Math.PI * 2;
    const spread = parent && parent.d.type === "category" ? 26 : 60 + (idx % 7) * 12;
    return { x: (parent?.x || 0) + Math.cos(angle) * spread, y: (parent?.y || 0) + Math.sin(angle) * spread };
  }

  function update(next) {
    net = next || { nodes: [], edges: [] };
    const seen = new Set();
    let added = 0, grown = 0;
    const now = performance.now();
    // Categories first, so papers placed in this pass can start next to theirs.
    const ordered = [...net.nodes].sort((a, b) => (a.type === "paper") - (b.type === "paper"));
    ordered.forEach((d, idx) => {
      seen.add(d.id);
      const n = nodes.get(d.id);
      if (n) {
        if (n.d.analyzed === false && d.analyzed !== false) { grown++; n.born = now; }
        n.d = d;
        n.gone = false;
        n.rt = radiusOf(d);
        if (n.at === 0 && !n.filtered) n.at = 1;
        return;
      }
      const p = place(d, idx);
      nodes.set(d.id, { d, ...p, vx: 0, vy: 0, r: REDUCED ? radiusOf(d) : 0.5, rt: radiusOf(d), a: REDUCED ? 1 : 0, at: 1, dim: 1, born: now, match: true });
      if (d.type === "paper") added++;
    });
    nodes.forEach((n, id) => { if (!seen.has(id)) { n.at = 0; n.gone = true; } });
    edges = (net.edges || []).map((e) => ({ ...e, s: nodes.get(e.source), t: nodes.get(e.target) })).filter((e) => e.s && e.t);
    const idea = nodes.get("idea");
    if (idea) { idea.fx = 0; idea.fy = 0; }

    if (added || grown) {
      heat = Math.max(heat, added > 10 ? 1 : 0.6);
      if (nodes.size > added + 1) flash(added ? `+${plural(added, "paper")}` : `${plural(grown, "paper")} analyzed`);
    }
    if (REDUCED) { for (let i = 0; i < 300; i++) tick(); heat = 0; }
    applyFilters();
    describe();
    if (selected && nodes.has(selected.d.id)) renderInspector(); else select(defaultSelection());
    kick();
  }

  function flash(text) {
    toast.textContent = text;
    toast.classList.add("visible");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove("visible"), 2600);
  }

  function describe() {
    const papers = [...nodes.values()].filter((n) => n.d.type === "paper" && !n.gone);
    const analyzed = papers.filter((n) => n.d.analyzed !== false).length;
    const cats = [...nodes.values()].filter((n) => n.d.type === "category" && !n.gone).length;
    canvas.setAttribute("aria-label", `Concept network: your idea, ${plural(cats, "category", "categories")} and ${plural(papers.length, "paper")}, ${analyzed} of them analyzed. Use the arrow keys to step through papers.`);
    const counts = {
      all: nodes.size, categories: 1 + cats,
      closest: papers.filter((n) => n.d.is_closest).length,
      high_sim: papers.filter((n) => (n.d.similarity || 0) >= 0.4).length,
      analyzed,
    };
    pills.forEach(([key, label]) => { pillEls.get(key).textContent = `${label} (${counts[key]})`; });
  }

  function passes(n) {
    const d = n.d;
    if (d.type === "idea") return true;
    if (filter === "categories") return d.type === "category";
    if (filter === "closest") return d.is_closest;
    if (filter === "high_sim") return (d.similarity || 0) >= 0.4;
    if (filter === "analyzed") return d.type === "category" || d.analyzed !== false;
    return true;
  }
  function applyFilters() {
    nodes.forEach((n) => {
      const text = `${n.d.full_title || ""} ${n.d.label || ""} ${n.d.authors || ""} ${n.d.category_name || ""}`.toLowerCase();
      n.match = !query || text.includes(query);
      n.filtered = !passes(n) || n.gone;
      n.at = n.filtered ? 0 : 1;
    });
    kick();
  }

  // ------------------------------------------------------------ physics

  function tick() {
    const list = [...nodes.values()].filter((n) => n.at > 0 || n.a > 0.02);
    const alpha = heat;
    for (let i = 0; i < list.length; i++) {
      const a = list[i];
      a.vx -= a.x * 0.0018 * alpha;
      a.vy -= a.y * 0.0024 * alpha;
      for (let j = i + 1; j < list.length; j++) {
        const b = list[j];
        let dx = b.x - a.x, dy = b.y - a.y;
        let d2 = dx * dx + dy * dy;
        if (d2 < 0.01) { dx = Math.random() - 0.5; dy = Math.random() - 0.5; d2 = dx * dx + dy * dy; }
        if (d2 > 90000) continue;
        const dist = Math.sqrt(d2);
        const charge = (a.d.type === "paper" ? 1 : 2.4) * (b.d.type === "paper" ? 1 : 2.4);
        let f = (520 * charge * alpha) / Math.max(d2, 120);
        const minGap = a.rt + b.rt + 8;
        if (dist < minGap) f += (minGap - dist) * 0.25; // collision
        const fx = (dx / dist) * f, fy = (dy / dist) * f;
        a.vx -= fx; a.vy -= fy;
        b.vx += fx; b.vy += fy;
      }
    }
    for (const e of edges) {
      const spec = LINK[e.type] || LINK.similarity;
      const dx = e.t.x - e.s.x, dy = e.t.y - e.s.y;
      const dist = Math.max(1, Math.hypot(dx, dy));
      const f = ((dist - spec.len(e)) / dist) * spec.k * alpha;
      e.s.vx += dx * f; e.s.vy += dy * f;
      e.t.vx -= dx * f; e.t.vy -= dy * f;
    }
    for (const n of list) {
      if (n.fx != null) { n.x = n.fx; n.y = n.fy; n.vx = n.vy = 0; continue; }
      n.vx *= 0.62; n.vy *= 0.62;
      n.x += Math.max(-14, Math.min(14, n.vx));
      n.y += Math.max(-14, Math.min(14, n.vy));
    }
    heat = ease(heat, drag ? 0.25 : 0, 0.018);
  }

  // ------------------------------------------------------------ camera

  function bounds() {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    nodes.forEach((n) => {
      if (n.at === 0) return;
      x0 = Math.min(x0, n.x - n.rt); x1 = Math.max(x1, n.x + n.rt);
      y0 = Math.min(y0, n.y - n.rt); y1 = Math.max(y1, n.y + n.rt);
    });
    return x0 === Infinity ? { x0: -100, y0: -100, x1: 100, y1: 100 } : { x0, y0, x1, y1 };
  }
  function fitGoal() {
    const b = bounds();
    const k = Math.max(0.3, Math.min(1.5, Math.min((width - 80) / (b.x1 - b.x0 + 60), (HEIGHT - 90) / (b.y1 - b.y0 + 60))));
    camGoal.k = k; camGoal.x = -(b.x0 + b.x1) / 2; camGoal.y = -(b.y0 + b.y1) / 2;
  }
  function fit(byUser) {
    if (byUser) userMoved = false;
    fitGoal();
    if (REDUCED) Object.assign(cam, camGoal);
    kick();
  }
  function zoomBy(f, sx = width / 2, sy = HEIGHT / 2) {
    const before = toWorld(sx, sy);
    cam.k = Math.max(0.25, Math.min(4, cam.k * f));
    const after = toWorld(sx, sy);
    cam.x += after.x - before.x; cam.y += after.y - before.y;
    Object.assign(camGoal, cam);
    userMoved = true;
    kick();
  }
  function focusOn(n) {
    camGoal.x = -n.x; camGoal.y = -n.y; camGoal.k = Math.max(cam.k, 1.2);
    userMoved = true;
    if (REDUCED) Object.assign(cam, camGoal);
    kick();
  }
  const toWorld = (sx, sy) => ({ x: (sx - width / 2) / cam.k - cam.x, y: (sy - HEIGHT / 2) / cam.k - cam.y });

  // ------------------------------------------------------------ drawing

  function colorOf(d) {
    if (d.type === "idea") return pal.idea;
    if (d.type === "category") return pal.category;
    if (d.analyzed === false) return pal.muted;
    if (d.is_closest) return pal.closest;
    return d.group === "high" ? pal.paper : pal.muted;
  }

  function draw(now) {
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, HEIGHT);
    ctx.setTransform(dpr * cam.k, 0, 0, dpr * cam.k, dpr * (width / 2 + cam.x * cam.k), dpr * (HEIGHT / 2 + cam.y * cam.k));
    const px = 1 / cam.k; // one screen pixel in world units

    // A soft glow under the idea anchors the eye.
    const idea = nodes.get("idea");
    if (idea) {
      const g = ctx.createRadialGradient(idea.x, idea.y, 0, idea.x, idea.y, 240);
      g.addColorStop(0, rgba(pal.idea, 0.10));
      g.addColorStop(1, rgba(pal.idea, 0));
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(idea.x, idea.y, 240, 0, Math.PI * 2); ctx.fill();
    }

    // Edges: gentle curves, faint unless they touch the hovered node.
    ctx.lineCap = "round";
    for (const e of edges) {
      const vis = Math.min(e.s.a, e.t.a) * Math.min(e.s.dim, e.t.dim);
      if (vis < 0.02) continue;
      const lit = hover && (e.s === hover || e.t === hover);
      let col = pal.category, alpha = 0.2, w = 1;
      if (e.type === "idea_category") { alpha = 0.26; w = 1.4; }
      else if (e.type === "category_paper") { alpha = 0.14; w = 0.9; }
      else if (e.type === "similarity") {
        const sim = e.similarity ?? 0.3;
        col = (e.t.d.is_closest || e.s.d.is_closest) ? pal.closest : pal.idea;
        alpha = 0.05 + sim * 0.2; w = 0.6 + sim * 1.6;
      } else if (e.type === "retrieved") { col = pal.muted; alpha = 0.05; w = 0.6; }
      if (lit) alpha = Math.max(0.65, alpha * 2.5);
      const mx = (e.s.x + e.t.x) / 2, my = (e.s.y + e.t.y) / 2;
      const bend = 0.12;
      ctx.strokeStyle = rgba(col, alpha * vis);
      ctx.lineWidth = w * px * (lit ? 1.6 : 1);
      ctx.setLineDash(e.type === "retrieved" ? [2 * px, 5 * px] : []);
      ctx.beginPath();
      ctx.moveTo(e.s.x, e.s.y);
      ctx.quadraticCurveTo(mx - (e.t.y - e.s.y) * bend, my + (e.t.x - e.s.x) * bend, e.t.x, e.t.y);
      ctx.stroke();
    }
    ctx.setLineDash([]);

    // Nodes: soft-shadowed discs with a light center; new ones bloom in with a fading ring.
    const layer = (n) => (n.d.type === "idea" ? 2 : n.d.type === "category" ? 1 : 0);
    for (const n of [...nodes.values()].sort((a, b) => layer(a) - layer(b) || a.rt - b.rt)) {
      const vis = n.a * n.dim;
      if (vis < 0.02 || n.r < 0.3) continue;
      const col = colorOf(n.d);
      const pending = n.d.type === "paper" && n.d.analyzed === false;
      const age = (now - n.born) / 1400;
      if (age < 1 && !REDUCED && n.d.type !== "idea") {
        ctx.strokeStyle = rgba(col, (1 - age) * 0.45 * vis);
        ctx.lineWidth = 1.5 * px;
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 4 + age * 16, 0, Math.PI * 2); ctx.stroke();
      }
      if (n.d.type === "idea") {
        const pulse = REDUCED ? 0 : Math.sin(now / 900) * 2.5;
        ctx.fillStyle = rgba(pal.idea, 0.14 * vis);
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 9 + pulse, 0, Math.PI * 2); ctx.fill();
      }
      ctx.save();
      ctx.shadowColor = rgba(col, pending ? 0 : 0.35 * vis);
      ctx.shadowBlur = pending ? 0 : 10;
      ctx.shadowOffsetY = pending ? 0 : 2;
      if (pending) {
        ctx.fillStyle = rgba(col, 0.22 * vis);
      } else {
        const g = ctx.createRadialGradient(n.x - n.r * 0.35, n.y - n.r * 0.35, n.r * 0.1, n.x, n.y, n.r);
        g.addColorStop(0, rgba(col.map((c) => c + (255 - c) * 0.35), 0.95 * vis));
        g.addColorStop(1, rgba(col, 0.9 * vis));
        ctx.fillStyle = g;
      }
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2); ctx.fill();
      ctx.restore();
      ctx.lineWidth = (pending ? 1 : 1.5) * px;
      ctx.strokeStyle = pending ? rgba(col, 0.55 * vis) : rgba(pal.card, 0.9 * vis);
      ctx.stroke();
      if (n === selected || (query && n.match && n.d.type !== "idea")) {
        ctx.strokeStyle = rgba(n === selected ? pal.ink : pal.closest, 0.8 * vis);
        ctx.lineWidth = 1.8 * px;
        ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 4 * px + 2, 0, Math.PI * 2); ctx.stroke();
      }
    }

    // Labels: the idea, categories and closest work, then others when hovered, selected or zoomed in.
    // Higher-priority labels claim their space first; a label that would overlap one already drawn is skipped.
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    ctx.lineJoin = "round";
    const rank = (n) => (n === hover ? 0 : n === selected ? 1 : n.d.type === "idea" ? 2 : n.d.is_closest ? 3 : n.d.type === "category" ? 4 : 5);
    const placed = [];
    for (const n of [...nodes.values()].sort((a, b) => rank(a) - rank(b))) {
      const vis = n.a * n.dim;
      if (vis < 0.3) continue;
      const d = n.d;
      const always = d.type !== "paper" || d.is_closest;
      if (!always && n !== hover && n !== selected && !(cam.k > 1.6 && d.analyzed !== false && vis > 0.6)) continue;
      let text = d.type === "idea" ? "Your idea" : d.label || "";
      const max = d.type === "category" ? 26 : 30;
      if (text.length > max && n !== hover && n !== selected) text = text.slice(0, max - 1) + "…";
      const size = d.type === "idea" ? 12.5 : d.type === "category" ? 11 : 10;
      ctx.font = `${d.type === "paper" && !d.is_closest ? 500 : 600} ${size * px}px ${pal.font}`;
      const y = n.y + n.r + 5 * px;
      const half = ctx.measureText(text).width / 2 + 3 * px;
      const box = { x0: n.x - half, x1: n.x + half, y0: y - px, y1: y + (size + 2) * px };
      if (rank(n) > 1 && placed.some((b) => box.x0 < b.x1 && box.x1 > b.x0 && box.y0 < b.y1 && box.y1 > b.y0)) continue;
      placed.push(box);
      ctx.strokeStyle = rgba(pal.card, 0.85 * vis);
      ctx.lineWidth = 3.5 * px;
      ctx.strokeText(text, n.x, y);
      ctx.fillStyle = rgba(d.type === "category" ? pal.category : pal.ink, (d.type === "paper" && !d.is_closest ? 0.8 : 0.95) * vis);
      ctx.fillText(text, n.x, y);
    }
  }

  // ------------------------------------------------------------ loop

  function kick() {
    if (!raf && canvas.isConnected) raf = requestAnimationFrame(frame);
  }
  function frame(now) {
    raf = null;
    if (!canvas.isConnected) return; // resumes when the view is shown again
    if (heat > 0.004) { tick(); if (heat > 0.5) tick(); }
    let busy = heat > 0.004 || Boolean(drag);
    const near = hover ? neighbors(hover) : null;
    nodes.forEach((n, id) => {
      const dimTo = near && !near.has(n) ? 0.18 : 1;
      const rate = REDUCED ? 1 : 0.14;
      n.a = ease(n.a, n.at, rate); n.r = ease(n.r, n.at ? n.rt : 0, rate); n.dim = ease(n.dim, dimTo, rate);
      if (Math.abs(n.a - n.at) > 0.01 || Math.abs(n.r - n.rt * n.at) > 0.05 || Math.abs(n.dim - dimTo) > 0.01 || now - n.born < 1400) busy = true;
      if (n.gone && n.a < 0.02) nodes.delete(id);
    });
    if (!userMoved && heat > 0.004) fitGoal();
    const rate = REDUCED ? 1 : 0.08;
    cam.x = ease(cam.x, camGoal.x, rate); cam.y = ease(cam.y, camGoal.y, rate); cam.k = ease(cam.k, camGoal.k, rate);
    if (Math.abs(cam.x - camGoal.x) > 0.3 || Math.abs(cam.y - camGoal.y) > 0.3 || Math.abs(cam.k - camGoal.k) > 0.002) busy = true;
    draw(now);
    if (busy) raf = requestAnimationFrame(frame);
  }

  function neighbors(n) {
    const set = new Set([n]);
    for (const e of edges) { if (e.s === n) set.add(e.t); else if (e.t === n) set.add(e.s); }
    return set;
  }

  // ------------------------------------------------------------ interaction

  function hit(sx, sy) {
    const p = toWorld(sx, sy);
    let best = null, bestD = Infinity;
    nodes.forEach((n) => {
      if (n.at === 0 || n.a < 0.3) return;
      const d = Math.hypot(n.x - p.x, n.y - p.y);
      if (d < n.rt + 5 / cam.k && d < bestD) { best = n; bestD = d; }
    });
    return best;
  }
  const local = (ev) => { const r = canvas.getBoundingClientRect(); return { sx: ev.clientX - r.left, sy: ev.clientY - r.top }; };

  canvas.addEventListener("pointerdown", (ev) => {
    if (ev.button !== 0) return;
    const { sx, sy } = local(ev);
    const n = hit(sx, sy);
    try { canvas.setPointerCapture(ev.pointerId); } catch (_) { /* pointer already released */ }
    drag = { n, sx, sy, cx: cam.x, cy: cam.y, moved: false };
    canvas.classList.add("dragging");
    hideChartTooltip();
  });
  canvas.addEventListener("pointermove", (ev) => {
    const { sx, sy } = local(ev);
    if (drag) {
      if (Math.hypot(sx - drag.sx, sy - drag.sy) > 3) drag.moved = true;
      if (!drag.moved) return;
      if (drag.n && drag.n.d.type !== "idea") {
        const p = toWorld(sx, sy);
        drag.n.fx = p.x; drag.n.fy = p.y;
        heat = Math.max(heat, 0.25);
      } else if (!drag.n || drag.n.d.type === "idea") {
        cam.x = drag.cx + (sx - drag.sx) / cam.k; cam.y = drag.cy + (sy - drag.sy) / cam.k;
        Object.assign(camGoal, cam);
        userMoved = true;
      }
      kick();
      return;
    }
    const n = hit(sx, sy);
    if (n !== hover) { hover = n; canvas.style.cursor = n ? "pointer" : "grab"; kick(); }
    if (n) showChartTooltip(tooltip(n), ev.clientX, ev.clientY); else hideChartTooltip();
  });
  const release = (ev) => {
    if (!drag) return;
    try { canvas.releasePointerCapture(ev.pointerId); } catch (_) { /* pointer already released */ }
    if (drag.n && drag.n.d.type !== "idea") { drag.n.fx = null; drag.n.fy = null; }
    if (!drag.moved && drag.n) select(drag.n);
    drag = null;
    canvas.classList.remove("dragging");
    kick();
  };
  canvas.addEventListener("pointerup", release);
  canvas.addEventListener("pointercancel", release);
  canvas.addEventListener("pointerleave", () => { if (!drag && hover) { hover = null; hideChartTooltip(); kick(); } });
  canvas.addEventListener("dblclick", () => fit(true));
  canvas.addEventListener("wheel", (ev) => {
    ev.preventDefault();
    const { sx, sy } = local(ev);
    zoomBy(Math.exp(-ev.deltaY * 0.0015), sx, sy);
  }, { passive: false });
  canvas.addEventListener("keydown", (ev) => {
    const papers = [...nodes.values()].filter((n) => n.d.type === "paper" && n.at > 0).sort((a, b) => (b.d.similarity ?? -1) - (a.d.similarity ?? -1));
    if (!papers.length) return;
    if (ev.key === "ArrowRight" || ev.key === "ArrowLeft") {
      ev.preventDefault();
      const i = papers.indexOf(selected);
      const step = ev.key === "ArrowRight" ? 1 : -1;
      const next = i < 0 ? papers[0] : papers[(i + step + papers.length) % papers.length];
      select(next);
      focusOn(next);
    } else if (ev.key === "+" || ev.key === "=") zoomBy(1.2);
    else if (ev.key === "-") zoomBy(0.83);
    else if (ev.key === "0") fit(true);
  });

  function tooltip(n) {
    const d = n.d;
    const out = [h("div", { class: "tt-title" }, d.type === "idea" ? "Your idea" : d.full_title || d.label)];
    if (d.type === "paper") {
      out.push(h("div", { class: "tt-meta" }, `${d.authors || "Authors not listed"}${d.year ? ` (${d.year})` : ""}${d.citations ? ` • ${d.citations} citations` : ""}`));
      if (d.analyzed === false) out.push(h("div", { class: "tt-desc" }, "Retrieved, not analyzed yet."));
      else if (d.similarity != null) out.push(h("div", { class: "tt-row" }, h("span", {}, "Similarity to idea:"), h("b", {}, `${Math.round(d.similarity * 100)}%`)));
      if (d.category_name) out.push(h("div", { class: "tt-row" }, h("span", {}, "Category:"), h("span", {}, d.category_name)));
      if (d.is_closest) out.push(h("div", { class: "tt-desc" }, "Closest existing work, per the critique."));
    } else if (d.type === "category") {
      out.push(h("div", { class: "tt-meta" }, `Category • ${plural(papersIn(d.id).length, "paper")}`));
    } else {
      out.push(h("div", { class: "tt-desc" }, d.full_title));
    }
    return out;
  }
  const papersIn = (cid) => [...nodes.values()].filter((p) => p.d.type === "paper" && p.d.category_id === cid && !p.gone);

  // ------------------------------------------------------------ inspector

  function defaultSelection() {
    const all = [...nodes.values()].filter((n) => !n.gone);
    return all.find((n) => n.d.is_closest) || all.find((n) => n.d.type === "paper" && n.d.analyzed !== false) || nodes.get("idea") || null;
  }
  function select(n) {
    selected = n;
    renderInspector();
    kick();
  }
  const bar = (label, v, color) => h("div", { class: "inspector-metric" },
    h("div", { class: "lbl" }, label),
    h("div", { class: "val" }, `${Math.round((v || 0) * 100)}%`),
    h("div", { class: "p-bar" }, h("div", { class: "p-fill", style: `width: ${(v || 0) * 100}%; background: ${color};` })));

  function renderInspector() {
    const n = selected;
    if (!n) {
      inspector.replaceChildren(h("h4", {}, "Node inspector"), h("p", { class: "meta" }, "Click a paper, a category or your idea to see how it relates."));
      return;
    }
    const d = n.d;
    if (d.type === "idea") {
      inspector.replaceChildren(h("h4", {}, "Your research idea"), h("p", { class: "diff-text", style: "font-size: 0.9375rem; line-height: 1.6;" }, d.full_title || d.label));
      return;
    }
    if (d.type === "category") {
      const members = papersIn(d.id);
      inspector.replaceChildren(
        h("h4", {}, `Category: ${d.label}`),
        h("p", { class: "meta" }, plural(members.length, "paper")),
        d.full_title && d.full_title !== d.label ? h("p", { class: "diff-text" }, d.full_title) : null,
        h("div", { style: "display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px;" },
          members.slice(0, 12).map((m) => h("button", { type: "button", class: "network-pill", onclick: () => { select(m); focusOn(m); } }, m.d.label))));
      return;
    }
    const url = typeof d.url === "string" && /^https?:\/\//i.test(d.url) ? d.url : null;
    inspector.replaceChildren(
      h("h4", {}, url ? h("a", { href: url, target: "_blank", rel: "noopener noreferrer" }, d.full_title || d.label) : d.full_title || d.label),
      h("p", { class: "meta" }, `${d.authors || "Authors not recorded"}${d.year ? ` • ${d.year}` : ""}${d.citations ? ` • ${d.citations} citations` : ""}`),
      h("div", { style: "display: flex; gap: 6px; margin: 6px 0 12px; flex-wrap: wrap;" },
        h("span", { class: `status ${d.analyzed === false ? "pending" : d.group === "high" ? "complete" : "running"}` }, d.analyzed === false ? "Not analyzed yet" : `Relevance: ${d.group}`),
        d.category_name ? h("span", { class: "status pending" }, `Category: ${d.category_name}`) : null,
        d.is_closest ? h("span", { class: "closest-badge" }, "Closest work") : null),
      d.analyzed === false
        ? h("p", { class: "diff-text" }, "This paper was retrieved but not analyzed yet. Overlap scores appear once the agent reads it.")
        : h("div", { class: "inspector-bars" }, bar("Problem overlap", d.problem_overlap, "var(--steel)"), bar("Method overlap", d.method_overlap, "var(--success)"), bar("Evaluation overlap", d.evaluation_overlap, "var(--warn)")),
      d.conceptual_difference ? h("p", { class: "diff-text" }, h("b", {}, "How it differs: "), d.conceptual_difference) : null,
      d.basis ? h("p", { class: "diff-text", style: "color: var(--ink-60);" }, h("b", {}, "Basis: "), d.basis) : null);
  }

  update(net);
  resize();
  fit(false);
  Object.assign(cam, camGoal);
  return { el: sec, update, resume: () => { resize(); } };
}
