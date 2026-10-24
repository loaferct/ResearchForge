// Shared helpers, labels and state for the ResearchForge UI. Untrusted text is only ever set via textContent.

// The rail lists result views in investigation order; each view is fed by one or more phases.
export const VIEWS = [
  { tab: "overview", title: "Overview", phases: ["formalize"] },
  { tab: "literature", title: "Literature", phases: ["literature", "analysis"] },
  { tab: "map", title: "Research map", phases: ["landscape"] },
  { tab: "critique", title: "Critique", phases: ["critique"] },
  { tab: "graphs", title: "Visual graphs", phases: ["analysis", "landscape", "critique"] },
  { tab: "gaps", title: "Potential gaps", phases: ["gaps"] },
  { tab: "modifications", title: "Modifications", phases: ["modifications"] },
  { tab: "experiments", title: "Experiments", phases: ["experiments"] },
  { tab: "report", title: "Final report", phases: ["report"] },
];
export const PHASE_ACTIVITY = {
  formalize: "Formalizing the idea", literature: "Searching literature", analysis: "Analyzing papers",
  landscape: "Mapping the field", critique: "Critiquing the idea", gaps: "Looking for gaps",
  modifications: "Proposing modifications", experiments: "Designing experiments", report: "Writing the report",
};
export const MARK = { complete: "✓", running: "●", incomplete: "✗", failed: "✗", pending: "", skipped: "–" };
export const VERDICT = {
  promising_needs_validation: "Promising, but it needs experimental validation",
  substantial_overlap: "Substantial overlap with existing work",
  weak_or_flawed: "Weak or technically flawed as stated",
  insufficient_evidence: "Not enough evidence to judge",
};
export const RESEARCH_DECISION = {
  PROMISING: "Promising", NEEDS_MODIFICATION: "Needs modification", ALREADY_WELL_EXPLORED: "Already well explored",
  INSUFFICIENT_EVIDENCE: "Insufficient evidence", EXPERIMENTALLY_SUPPORTED: "Experimentally supported", EXPERIMENTALLY_UNSUPPORTED: "Experimentally unsupported",
};
export const KIND_NAME = { evidence: "Evidence", inference: "Inference", hypothesis: "Hypothesis", assumption: "Assumption", experimental: "Experimental result" };

// ---------------------------------------------------------------- helpers

export function h(tag, attrs = {}, ...children) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}
export const $ = (id) => document.getElementById(id);
export const NONE = "Not recorded";
export const join = (items) => (items && items.length ? items.join("; ") : NONE);
export const safeUrl = (u) => (typeof u === "string" && /^https?:\/\//i.test(u) ? u : null);
export const plural = (n, word, many) => `${n} ${n === 1 ? word : many || `${word}s`}`;

export async function api(path, opts = {}) {
  const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_) { /* body is not JSON */ }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return (res.headers.get("content-type") || "").includes("json") ? res.json() : res.text();
}

export function ago(iso) {
  if (!iso) return "";
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.round(s / 60)} min ago`;
  if (s < 86400) return `${Math.round(s / 3600)} h ago`;
  return new Date(iso).toLocaleDateString();
}

export function facts(pairs) {
  return h("dl", { class: "facts" }, pairs.filter(([, v]) => v !== undefined).flatMap(([k, v]) => [h("dt", {}, k), h("dd", {}, v ?? NONE)]));
}
// A statement whose epistemic status is shown by its margin rule.
export function stmt(kind, text, meta) {
  return h("div", { class: `stmt ${kind}` },
    h("span", { class: `kind ${kind}` }, KIND_NAME[kind] || kind),
    h("span", { class: "stmt-text" }, text),
    meta ? h("div", { class: "stmt-meta" }, meta) : null);
}
export function legend() {
  return h("ul", { class: "legend", "aria-label": "How to read statements" },
    h("li", { class: "evidence" }, "Evidence: a verified quote from a retrieved paper"),
    h("li", { class: "inference" }, "Inference: reasoning from cited evidence"),
    h("li", { class: "hypothesis" }, "Hypothesis: proposed, not yet tested"),
    h("li", { class: "assumption" }, "Assumption: taken as given, no evidence"),
    h("li", { class: "experimental" }, "Experimental result: observed in an approved run"));
}
export function empty(text) { return h("p", { class: "empty" }, text); }
export function section(title, ...children) { return h("section", {}, h("h3", {}, title), ...children); }

export const SVG_NS = "http://www.w3.org/2000/svg";
export function svg(tag, attrs = {}, ...children) {
  const el = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.setAttribute("class", v);
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat()) {
    if (c === null || c === undefined || c === false) continue;
    el.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return el;
}

let tooltipEl = null;
function getTooltip() {
  if (!tooltipEl) {
    tooltipEl = h("div", { class: "chart-tooltip" });
    document.body.appendChild(tooltipEl);
  }
  return tooltipEl;
}

export function showChartTooltip(items, clientX, clientY) {
  const tt = getTooltip();
  tt.replaceChildren(...(Array.isArray(items) ? items : [items]));
  tt.classList.add("visible");
  const x = Math.min(window.innerWidth - 180, Math.max(160, clientX));
  const y = Math.max(70, clientY);
  tt.style.left = `${x}px`;
  tt.style.top = `${y}px`;
}

export function hideChartTooltip() {
  if (tooltipEl) tooltipEl.classList.remove("visible");
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function downloadSvg(svgEl, filename) {
  const clone = svgEl.cloneNode(true);
  clone.setAttribute("xmlns", SVG_NS);
  const serializer = new XMLSerializer();
  const source = '<?xml version="1.0" standalone="no"?>\r\n' + serializer.serializeToString(clone);
  downloadBlob(new Blob([source], { type: "image/svg+xml;charset=utf-8" }), filename || "chart.svg");
}

export function downloadCanvas(canvas, filename) {
  canvas.toBlob((blob) => blob && downloadBlob(blob, filename || "chart.png"), "image/png");
}

// ---------------------------------------------------------------- state

export const S = {
  project: null,
  tab: "overview",
  lastEvent: -1,
  papers: {},
  timer: null,
  cache: {},
  pollUntil: 0,
  lastTool: null,
  lit: { q: "", show: "all" },
  graphs: { subTab: "all", scatterFilter: "all", scatterSearch: "", selectedPaper: null },
};

// Hooks the app shell fills in, so views can ask for polling without importing the shell.
export const app = { schedulePoll() {} };

export async function data(kind) {
  if (!(kind in S.cache)) S.cache[kind] = await api(`/api/projects/${encodeURIComponent(S.project)}/data/${kind}`);
  return S.cache[kind];
}

export function pendingNote(what) {
  return empty(S.info?.running ? `${what} will appear here when that phase finishes.` : `${what} was not recorded. Resume the investigation to retry that phase.`);
}

export function paperRef(id) {
  const p = S.papers[id];
  if (!p) return h("code", {}, id);
  const url = safeUrl(p.url);
  const text = `${p.title} (${p.year ?? "n.d."})`;
  return url ? h("a", { href: url, target: "_blank", rel: "noopener noreferrer", title: id }, text) : h("span", { title: id }, text);
}
export function paperRefs(ids) {
  if (!ids || !ids.length) return NONE;
  const out = h("span");
  ids.forEach((id, i) => { if (i) out.append("; "); out.append(paperRef(id)); });
  return out;
}
export function sources(items) {
  if (!items || !items.length) return h("p", { class: "muted" }, "No sources cited.");
  return h("ul", { class: "sources" }, items.map((e) => h("li", {},
    e.paper_id ? paperRef(e.paper_id) : h("span", {}, `Experiment run ${e.experiment_run_id}`),
    h("span", { class: "muted" }, `, ${e.location}, ${e.support} support `),
    e.verified ? h("span", { class: "check ok" }, "✓ quote verified")
      : e.quote ? h("span", { class: "check no" }, "quote not found in the retrieved text")
      : h("span", { class: "check none" }, "no quote given"),
    e.quote ? h("blockquote", { class: "quote" }, `“${e.quote}”`) : null)));
}
