// ResearchForge web UI shell: routing, the home page, the project frame and polling.
// Plain JS modules, no dependencies or build step. Each result view is its own module, loaded on first use.
import { VIEWS, PHASE_ACTIVITY, MARK, h, $, plural, api, ago, S, app, data } from "./core.js";

const VIEW_MODULES = {
  overview: () => import("./views/overview.js"),
  literature: () => import("./views/literature.js"),
  map: () => import("./views/map.js"),
  critique: () => import("./views/critique.js"),
  graphs: () => import("./views/graphs.js"),
  gaps: () => import("./views/gaps.js"),
  modifications: () => import("./views/modifications.js"),
  experiments: () => import("./views/experiments.js"),
  evidence: () => import("./views/evidence.js"),
  report: () => import("./views/report.js"),
};
const loadedViews = {};
function loadView(tab) {
  const key = tab in VIEW_MODULES ? tab : "overview";
  loadedViews[key] ||= VIEW_MODULES[key]().catch((e) => { delete loadedViews[key]; throw e; });
  return loadedViews[key];
}

// ---------------------------------------------------------------- routing

function route() {
  clearTimeout(S.timer);
  const m = location.hash.match(/^#\/p\/([^/?]+)(?:\/([a-zA-Z0-9_-]+))?(?:\/([a-zA-Z0-9_-]+))?/);
  const searchMatch = location.hash.match(/[?&]sub=([a-zA-Z0-9_-]+)/);
  document.body.classList.toggle("in-project", Boolean(m));
  if (m) {
    const proj = decodeURIComponent(m[1]);
    const tab = m[2] || "overview";
    const subTab = m[3] || (searchMatch ? searchMatch[1] : null);
    openProject(proj, tab, subTab);
  } else {
    S.project = null;
    $("project").hidden = true;
    $("home").hidden = false;
    document.title = "ResearchForge: check a research idea against the literature";
    loadProjects();
  }
}
window.addEventListener("hashchange", route);
$("home-link").addEventListener("click", (e) => { e.preventDefault(); location.hash = ""; window.scrollTo(0, 0); });
// "Start an investigation" links: bring the form into view and put the cursor in it.
document.querySelectorAll("[data-focus-idea]").forEach((a) => a.addEventListener("click", (e) => {
  e.preventDefault();
  if (S.project) location.hash = "";
  const smooth = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  $("start").scrollIntoView({ behavior: smooth ? "smooth" : "auto", block: "start" });
  $("idea").focus({ preventScroll: true });
}));
// Mark the landing-page nav link for the section in the middle of the viewport.
const navLinks = [...document.querySelectorAll('.site-nav a[href^="#"]:not(.nav-cta)')];
if ("IntersectionObserver" in window) {
  const spy = new IntersectionObserver((entries) => entries.forEach((en) => {
    const link = navLinks.find((a) => a.getAttribute("href") === "#" + en.target.id);
    if (en.isIntersecting) navLinks.forEach((a) => (a === link ? a.setAttribute("aria-current", "true") : a.removeAttribute("aria-current")));
    else if (link) link.removeAttribute("aria-current");
  }), { rootMargin: "-45% 0px -50% 0px" });
  navLinks.forEach((a) => { const el = document.querySelector(a.getAttribute("href")); if (el) spy.observe(el); });
}

// ---------------------------------------------------------------- home

async function loadProjects() {
  const list = $("project-list");
  try {
    const projects = await api("/api/projects");
    $("past").hidden = !projects.length;
    if (!projects.length) return;
    list.replaceChildren(...projects.map((p) => {
      const state = p.running ? "running" : p.status;
      const label = { running: "running", complete: "complete", incomplete: "incomplete", failed: "stopped", created: "not started" }[state] || state;
      return h("li", {}, h("a", { href: `#/p/${encodeURIComponent(p.name)}` },
        h("span", { class: "p-idea" }, p.idea),
        h("span", { class: "p-meta" }, h("span", { class: `status ${state}` }, label), p.updated_at ? `, ${ago(p.updated_at)}` : "")));
    }));
  } catch (e) {
    $("past").hidden = false;
    list.replaceChildren(h("li", { class: "empty-row error" }, `Could not load investigations: ${e.message}`));
  }
}

$("new-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const err = $("new-error");
  const field = $("idea");
  err.hidden = true;
  field.removeAttribute("aria-invalid");
  if (field.value.trim().length < 10) {
    err.textContent = "Describe the idea in at least one full sentence (10 characters or more).";
    err.hidden = false;
    field.setAttribute("aria-invalid", "true");
    field.focus();
    return;
  }
  const btn = e.submitter || e.target.querySelector("button[type=submit]");
  btn.disabled = true;
  btn.textContent = "Starting…";
  try {
    const res = await api("/api/projects", { method: "POST", body: JSON.stringify({ idea: field.value.trim() }) });
    location.hash = `#/p/${encodeURIComponent(res.project)}`;
  } catch (ex) {
    err.textContent = `The investigation did not start: ${ex.message}`;
    err.hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = "Investigate research idea";
  }
});

// ---------------------------------------------------------------- project view

async function openProject(name, tab, subTab) {
  const switched = S.project !== name;
  if (switched) {
    Object.assign(S, {
      project: name,
      lastEvent: -1,
      cache: {},
      lastTool: null,
      lit: { q: "", show: "all" },
      graphs: { subTab: subTab || "all", scatterFilter: "all", scatterSearch: "", selectedPaper: null },
    });
    $("activity").replaceChildren();
  } else if (subTab && S.graphs) {
    S.graphs.subTab = subTab;
  }
  const tabChanged = S.tab !== tab;
  S.tab = tab;
  $("home").hidden = true;
  $("project").hidden = false;
  await refresh(true);
  if (tabChanged && !switched) $("tab-body").focus({ preventScroll: true });
  schedulePoll();
}

// Poll only while an investigation or experiment is running; a finished project is static.
function schedulePoll() {
  clearTimeout(S.timer);
  if (!S.project || !S.info || !(S.info.running || S.pollUntil > Date.now())) return;
  S.timer = setTimeout(async () => { await refresh(false); schedulePoll(); }, 2000);
}
app.schedulePoll = schedulePoll;

$("btn-resume").addEventListener("click", async (ev) => {
  ev.target.disabled = true;
  try { await api(`/api/projects/${encodeURIComponent(S.project)}/resume`, { method: "POST" }); await refresh(true); schedulePoll(); }
  catch (e) { showBanner([`Could not resume: ${e.message}`]); }
  finally { ev.target.disabled = false; }
});
$("btn-stop").addEventListener("click", async (ev) => {
  ev.target.disabled = true;
  try { await api(`/api/projects/${encodeURIComponent(S.project)}/stop`, { method: "POST" }); ev.target.textContent = "Stopping after this phase…"; }
  catch (e) { showBanner([`Could not stop: ${e.message}`]); ev.target.disabled = false; }
});

function showBanner(lines) {
  const b = $("p-banner");
  if (!lines) { b.hidden = true; return; }
  b.replaceChildren(...lines.map((l) => h("p", {}, l)));
  b.hidden = false;
}

async function refresh(force) {
  if (!S.project) return;
  const name = encodeURIComponent(S.project);
  let info;
  try { info = await api(`/api/projects/${name}`); } catch (e) { $("tab-body").replaceChildren(h("p", { class: "error" }, `This investigation could not be loaded: ${e.message}`)); return; }
  const finished = Boolean(S.info?.running) && !info.running; // the last poll of a run may bring no new events
  S.info = info;
  document.title = `${info.idea.slice(0, 60)} | ResearchForge`;
  $("p-idea").textContent = info.idea;
  const status = info.running ? "running" : (info.state?.status || "created");
  const st = $("p-status");
  st.textContent = { running: "Investigating", complete: "Investigation complete", incomplete: "Finished with incomplete phases", failed: "Stopped", created: "Not started", awaiting_approval: "Waiting for experiment approval" }[status] || status;
  st.className = `status ${status}`;
  renderNow(info, status);
  $("btn-resume").hidden = info.running || status === "complete";
  $("btn-stop").hidden = !info.running;
  if (!info.running) { $("btn-stop").disabled = false; $("btn-stop").textContent = "Stop after this phase"; }
  if (status === "failed" && info.state?.error) {
    const hint = /credential|api key|MISSING_CREDENTIAL|INVALID_CREDENTIAL/i.test(info.state.error)
      ? "Set DEEPSEEK_API_KEY (or your custom endpoint's key) in the terminal that runs researchforge serve, restart it, then resume."
      : "Fix the cause, then resume. Completed phases are kept.";
    showBanner([`The investigation stopped: ${info.state.error}`, hint]);
  } else if (status === "incomplete") {
    showBanner(["Some phases could not record everything they need; their sections say what is missing. Resume to retry them."]);
  } else if (status === "awaiting_approval") {
    const plans = (info.state?.awaiting_approval || []).join(", ");
    showBanner([`Experiment ${plans} needs your approval before it can run. Review the commands under Experiments; after the run, the investigation resumes and re-evaluates the hypothesis.`]);
  } else {
    showBanner(null);
  }

  const events = await api(`/api/projects/${name}/events?after=${S.lastEvent}`);
  if (events.length) {
    S.lastEvent = events[events.length - 1].seq;
    appendActivity(events);
  }
  renderRail(info);
  if (force || finished || (events.length && S.tab !== "report")) {
    if (events.length || finished) S.cache = {};
    await renderTab();
  }
}

// What the loop is doing now, from the controller state (phase, action, focus, step).
const LOOP_PHASE_TEXT = {
  INTAKE: "Receiving the idea", FORMALIZE: "Formalizing the idea", PLAN: "Planning the investigation",
  INVESTIGATE: "Gathering evidence", SYNTHESIZE: "Mapping the field", CRITIQUE: "Critiquing the idea",
  UNCERTAINTY: "Investigating an open question", REFINE: "Refining the direction", EXPERIMENT_PLAN: "Designing an experiment",
  EXPERIMENT: "Experiment", ANALYZE: "Analyzing experiment results", FINALIZE: "Writing the report",
};
function renderNow(info, status) {
  const el = $("p-now");
  const s = info.state;
  if (!s) { el.replaceChildren(); return; }
  const steps = s.budget?.iterations ?? 0;
  if (status === "running") {
    el.replaceChildren(h("b", {}, `Step ${steps + 1}. `), `${LOOP_PHASE_TEXT[s.loop_phase] || s.loop_phase}`,
      s.current_action && s.current_action !== "FINALIZE" ? `, action ${s.current_action.toLowerCase().replace("_", " ")}` : "",
      s.current_focus ? `: ${s.current_focus}` : ".");
  } else if (steps) {
    const reason = s.finalize_reason ? ` ${s.finalize_reason}` : "";
    el.replaceChildren(h("b", {}, `${plural(steps, "step")} taken.`), reason);
  } else {
    el.replaceChildren();
  }
}

function viewStatus(view, byName) {
  const sts = view.phases.map((p) => (byName[p] || { status: "pending" }).status);
  if (sts.includes("running")) return "running";
  if (sts.every((s) => s === "complete")) return "complete";
  if (sts.some((s) => s === "incomplete" || s === "failed")) return "incomplete";
  if (sts.some((s) => s === "complete")) return S.info?.running ? "running" : "incomplete";
  return "pending";
}

function viewNote(view, status, byName, counts) {
  if (status === "running") {
    const running = view.phases.find((p) => byName[p]?.status === "running") || view.phases[0];
    return S.info.running ? `${PHASE_ACTIVITY[running]}${S.lastTool ? `: ${S.lastTool}` : "…"}` : "";
  }
  if (status === "incomplete") {
    const missing = view.phases.flatMap((p) => byName[p]?.missing || []);
    return missing.length ? `Missing ${missing[0].replace(/\s*\(.*$/, "")}` : "Incomplete";
  }
  if (status !== "complete") return "";
  return {
    literature: `${plural(counts.papers, "paper")}, ${counts.analyses} analyzed`,
    critique: plural(counts.claims, "claim"),
    graphs: `${counts.analyses} analyzed, 5 models`,
    gaps: plural(counts.gaps, "gap"),
    modifications: plural(counts.modifications, "direction"),
    experiments: plural(counts.plans, "plan"),
  }[view.tab] || "";
}

// Fetch a view's code when the reader points at its link, so opening it feels instant.
const prefetch = (tab) => { loadView(tab).catch(() => { /* retried when the view opens */ }); };

function renderRail(info) {
  const byName = Object.fromEntries((info.state?.phases || []).map((p) => [p.name, p]));
  $("rail-steps").replaceChildren(...VIEWS.map((v) => {
    const status = viewStatus(v, byName);
    const note = viewNote(v, status, byName, info.counts);
    return h("li", {}, h("a", { href: `#/p/${encodeURIComponent(S.project)}/${v.tab}`, "aria-current": S.tab === v.tab ? "page" : null,
      onpointerenter: () => prefetch(v.tab), onfocus: () => prefetch(v.tab) },
      h("span", {}, v.title),
      h("span", { class: `step-mark ${status}`, "aria-label": status === "pending" ? "not started" : status }, MARK[status] || ""),
      note ? h("span", { class: `step-note ${status}` }, note) : null));
  }));
  document.querySelectorAll(".rail-link").forEach((a) => {
    a.href = `#/p/${encodeURIComponent(S.project)}/${a.dataset.tab}`;
    if (S.tab === a.dataset.tab) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
}
document.querySelectorAll(".rail-link").forEach((a) => {
  a.addEventListener("pointerenter", () => prefetch(a.dataset.tab));
  a.addEventListener("focus", () => prefetch(a.dataset.tab));
});

function appendActivity(events) {
  const list = $("activity");
  for (const e of events) {
    let text = null;
    const d = e.data || {};
    if (e.kind === "tool_call") { text = d.tool; S.lastTool = d.tool; }
    else if (e.kind === "tool_result" && d.status === "error") text = `Tool error: ${String(d.result || "").slice(0, 160)}`;
    else if (e.kind === "decision") { text = `Step ${d.iteration}: ${d.action}${d.focus ? ` (${String(d.focus).slice(0, 70)})` : ""}. ${d.reason || ""}`; S.lastTool = null; }
    else if (e.kind === "phase_start") { if (!d.action) text = `Started: ${d.title || e.phase}`; S.lastTool = null; }
    else if (e.kind === "phase_end") text = d.action ? `${d.action}: ${d.outcome || d.status}` : `${d.status === "complete" ? "Finished" : "Incomplete"}: ${e.phase}`;
    else if (e.kind === "warning" || e.kind === "error") text = d.message || e.kind;
    else if (e.kind === "info" && d.message && d.message !== "token usage" && d.message !== "starting dsh") text = d.message;
    if (text) list.prepend(h("li", { class: e.kind }, text));
  }
  while (list.children.length > 300) list.lastChild.remove();
}

function skeleton() { return h("div", { class: "skeleton", "aria-hidden": "true" }, h("i"), h("i"), h("i"), h("i")); }

async function renderTab() {
  const body = $("tab-body");
  const tab = S.tab;
  if (!body.childElementCount || body.dataset.tab !== tab) body.replaceChildren(skeleton());
  body.dataset.tab = tab;
  try {
    const [view, papers] = await Promise.all([loadView(tab), data("papers")]);
    S.papers = Object.fromEntries(papers.map((p) => [p.id, p]));
    const nodes = [await view.default()].flat().filter(Boolean);
    if (S.tab !== tab) return; // the reader moved on while this view loaded
    // Live views (the graphs) return the nodes already on screen; leave them in place.
    const same = nodes.length === body.children.length && nodes.every((n, i) => body.children[i] === n);
    if (!same) body.replaceChildren(...nodes);
  } catch (e) {
    body.replaceChildren(h("p", { class: "error" }, `This section could not be loaded: ${e.message}`));
  }
}

// ---------------------------------------------------------------- theme (light by default)

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const btn = $("theme-toggle");
  btn.textContent = theme === "dark" ? "Light mode" : "Dark mode";
  btn.setAttribute("aria-pressed", String(theme === "dark"));
}
$("theme-toggle").addEventListener("click", () => {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  applyTheme(next);
  try { localStorage.setItem("rf-theme", next); } catch (_) { /* storage unavailable: the choice lasts for this visit */ }
});
applyTheme(document.documentElement.dataset.theme === "dark" ? "dark" : "light");

// ---------------------------------------------------------------- boot

api("/api/config").then((c) => { $("model-info").textContent = `Model: ${c.provider}/${c.model}`; }).catch(() => {});
route();
