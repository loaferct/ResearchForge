// ResearchForge web UI. Plain JS, no dependencies. Untrusted text is only ever set via textContent.
"use strict";

// The rail lists result views in investigation order; each view is fed by one or more phases.
const VIEWS = [
  { tab: "overview", title: "Overview", phases: ["formalize"] },
  { tab: "literature", title: "Literature", phases: ["literature", "analysis"] },
  { tab: "map", title: "Research map", phases: ["landscape"] },
  { tab: "critique", title: "Critique", phases: ["critique"] },
  { tab: "gaps", title: "Potential gaps", phases: ["gaps"] },
  { tab: "modifications", title: "Modifications", phases: ["modifications"] },
  { tab: "experiments", title: "Experiments", phases: ["experiments"] },
  { tab: "report", title: "Final report", phases: ["report"] },
];
const PHASE_ACTIVITY = {
  formalize: "Formalizing the idea", literature: "Searching literature", analysis: "Analyzing papers",
  landscape: "Mapping the field", critique: "Critiquing the idea", gaps: "Looking for gaps",
  modifications: "Proposing modifications", experiments: "Designing experiments", report: "Writing the report",
};
const MARK = { complete: "✓", running: "●", incomplete: "✗", failed: "✗", pending: "", skipped: "–" };
const VERDICT = {
  promising_needs_validation: "Promising, but it needs experimental validation",
  substantial_overlap: "Substantial overlap with existing work",
  weak_or_flawed: "Weak or technically flawed as stated",
  insufficient_evidence: "Not enough evidence to judge",
};
const RESEARCH_DECISION = {
  PROMISING: "Promising", NEEDS_MODIFICATION: "Needs modification", ALREADY_WELL_EXPLORED: "Already well explored",
  INSUFFICIENT_EVIDENCE: "Insufficient evidence", EXPERIMENTALLY_SUPPORTED: "Experimentally supported", EXPERIMENTALLY_UNSUPPORTED: "Experimentally unsupported",
};
const KIND_NAME = { evidence: "Evidence", inference: "Inference", hypothesis: "Hypothesis", assumption: "Assumption", experimental: "Experimental result" };

// ---------------------------------------------------------------- helpers

function h(tag, attrs = {}, ...children) {
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
const $ = (id) => document.getElementById(id);
const NONE = "Not recorded";
const join = (items) => (items && items.length ? items.join("; ") : NONE);
const safeUrl = (u) => (typeof u === "string" && /^https?:\/\//i.test(u) ? u : null);
const plural = (n, word, many) => `${n} ${n === 1 ? word : many || `${word}s`}`;

async function api(path, opts = {}) {
  const res = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_) { /* body is not JSON */ }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return (res.headers.get("content-type") || "").includes("json") ? res.json() : res.text();
}

function ago(iso) {
  if (!iso) return "";
  const s = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000);
  if (s < 60) return "just now";
  if (s < 3600) return `${Math.round(s / 60)} min ago`;
  if (s < 86400) return `${Math.round(s / 3600)} h ago`;
  return new Date(iso).toLocaleDateString();
}

function facts(pairs) {
  return h("dl", { class: "facts" }, pairs.filter(([, v]) => v !== undefined).flatMap(([k, v]) => [h("dt", {}, k), h("dd", {}, v ?? NONE)]));
}
// A statement whose epistemic status is shown by its margin rule.
function stmt(kind, text, meta) {
  return h("div", { class: `stmt ${kind}` },
    h("span", { class: `kind ${kind}` }, KIND_NAME[kind] || kind),
    h("span", { class: "stmt-text" }, text),
    meta ? h("div", { class: "stmt-meta" }, meta) : null);
}
function legend() {
  return h("ul", { class: "legend", "aria-label": "How to read statements" },
    h("li", { class: "evidence" }, "Evidence: a verified quote from a retrieved paper"),
    h("li", { class: "inference" }, "Inference: reasoning from cited evidence"),
    h("li", { class: "hypothesis" }, "Hypothesis: proposed, not yet tested"),
    h("li", { class: "assumption" }, "Assumption: taken as given, no evidence"),
    h("li", { class: "experimental" }, "Experimental result: observed in an approved run"));
}
function empty(text) { return h("p", { class: "empty" }, text); }
function section(title, ...children) { return h("section", {}, h("h3", {}, title), ...children); }

// ---------------------------------------------------------------- state

const S = { project: null, tab: "overview", lastEvent: -1, papers: {}, timer: null, cache: {}, pollUntil: 0, lastTool: null, lit: { q: "", show: "all" } };

function paperRef(id) {
  const p = S.papers[id];
  if (!p) return h("code", {}, id);
  const url = safeUrl(p.url);
  const text = `${p.title} (${p.year ?? "n.d."})`;
  return url ? h("a", { href: url, target: "_blank", rel: "noopener noreferrer", title: id }, text) : h("span", { title: id }, text);
}
function paperRefs(ids) {
  if (!ids || !ids.length) return NONE;
  const out = h("span");
  ids.forEach((id, i) => { if (i) out.append("; "); out.append(paperRef(id)); });
  return out;
}
function sources(items) {
  if (!items || !items.length) return h("p", { class: "muted" }, "No sources cited.");
  return h("ul", { class: "sources" }, items.map((e) => h("li", {},
    e.paper_id ? paperRef(e.paper_id) : h("span", {}, `Experiment run ${e.experiment_run_id}`),
    h("span", { class: "muted" }, `, ${e.location}, ${e.support} support `),
    e.verified ? h("span", { class: "check ok" }, "✓ quote verified")
      : e.quote ? h("span", { class: "check no" }, "quote not found in the retrieved text")
      : h("span", { class: "check none" }, "no quote given"),
    e.quote ? h("blockquote", { class: "quote" }, `“${e.quote}”`) : null)));
}

// ---------------------------------------------------------------- routing

function route() {
  clearTimeout(S.timer);
  const m = location.hash.match(/^#\/p\/([^/]+)(?:\/(\w+))?/);
  document.body.classList.toggle("in-project", Boolean(m));
  if (m) {
    openProject(decodeURIComponent(m[1]), m[2] || "overview");
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

async function openProject(name, tab) {
  const switched = S.project !== name;
  if (switched) {
    Object.assign(S, { project: name, lastEvent: -1, cache: {}, lastTool: null, lit: { q: "", show: "all" } });
    $("activity").replaceChildren();
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
  if (force || (events.length && S.tab !== "report")) {
    if (events.length) S.cache = {};
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
    gaps: plural(counts.gaps, "gap"),
    modifications: plural(counts.modifications, "direction"),
    experiments: plural(counts.plans, "plan"),
  }[view.tab] || "";
}

function renderRail(info) {
  const byName = Object.fromEntries((info.state?.phases || []).map((p) => [p.name, p]));
  $("rail-steps").replaceChildren(...VIEWS.map((v) => {
    const status = viewStatus(v, byName);
    const note = viewNote(v, status, byName, info.counts);
    return h("li", {}, h("a", { href: `#/p/${encodeURIComponent(S.project)}/${v.tab}`, "aria-current": S.tab === v.tab ? "page" : null },
      h("span", {}, v.title),
      h("span", { class: `step-mark ${status}`, "aria-label": status === "pending" ? "not started" : status }, MARK[status] || ""),
      note ? h("span", { class: `step-note ${status}` }, note) : null));
  }));
  document.querySelectorAll(".rail-link").forEach((a) => {
    a.href = `#/p/${encodeURIComponent(S.project)}/${a.dataset.tab}`;
    if (S.tab === a.dataset.tab) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
}

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

async function data(kind) {
  if (!(kind in S.cache)) S.cache[kind] = await api(`/api/projects/${encodeURIComponent(S.project)}/data/${kind}`);
  return S.cache[kind];
}

function skeleton() { return h("div", { class: "skeleton", "aria-hidden": "true" }, h("i"), h("i"), h("i"), h("i")); }

async function renderTab() {
  const body = $("tab-body");
  if (!body.childElementCount || body.dataset.tab !== S.tab) body.replaceChildren(skeleton());
  body.dataset.tab = S.tab;
  try {
    const papers = await data("papers");
    S.papers = Object.fromEntries(papers.map((p) => [p.id, p]));
    const render = TABS[S.tab] || TABS.overview;
    body.replaceChildren(...[await render()].flat().filter(Boolean));
  } catch (e) {
    body.replaceChildren(h("p", { class: "error" }, `This section could not be loaded: ${e.message}`));
  }
}

function pendingNote(what) {
  return empty(S.info?.running ? `${what} will appear here when that phase finishes.` : `${what} was not recorded. Resume the investigation to retry that phase.`);
}

// ---------------------------------------------------------------- views

const TABS = {
  async overview() {
    const [idea, critique] = await Promise.all([data("idea"), data("critique")]);
    const c = S.info.counts;
    const out = [];
    if (critique) {
      out.push(h("div", { class: `verdict ${critique.overall_status}` },
        h("p", { class: "verdict-kicker" }, "Assessment"),
        h("h2", {}, VERDICT[critique.overall_status] || critique.overall_status),
        h("p", {}, critique.status_rationale)));
    } else {
      out.push(h("h2", {}, "Overview"), h("p", { class: "lede" }, S.info.running ? "The assessment appears after the critique phase." : "No assessment was recorded."));
    }
    const rd = S.info.state?.research_decision;
    if (rd) {
      out.push(h("p", { class: "decision" }, h("b", {}, `Research decision: ${RESEARCH_DECISION[rd] || rd}.`),
        ` ${S.info.state.research_decision_basis || ""}. This describes the state of the evidence, not the worth of the idea.`));
    }
    out.push(h("p", { class: "tally" },
      `${plural(c.papers, "paper")} retrieved in ${plural(c.searches, "search", "searches")}; ${c.analyses} analyzed; ${plural(c.claims, "claim")}, ${plural(c.gaps, "gap")}, ${plural(c.modifications, "modification")} and ${plural(c.plans, "experiment plan")} recorded.`));
    if (critique) {
      out.push(section("The case in brief",
        facts([["Closest existing work", paperRefs(critique.closest_paper_ids)]]),
        stmt("inference", critique.overlap_summary, "Overlap"),
        stmt("inference", critique.distinction_summary, "Potential distinction"),
        stmt("inference", critique.strongest_against, "Major risk")));
    }
    if (!idea) { out.push(pendingNote("The formalized research question")); return out; }
    const [uncertainties, directions] = await Promise.all([data("uncertainties"), data("directions")]);
    out.push(section("Research question", h("p", { class: "prose" }, idea.research_question),
      stmt("hypothesis", idea.hypothesis, directions.length ? "Original hypothesis, kept unchanged" : null)));
    if (directions.length) {
      const d = directions[directions.length - 1];
      out.push(section("Current direction", stmt("hypothesis", d.direction, `Hypothesis: ${d.hypothesis}`),
        h("p", { class: "lede" }, `Why it deserves investigation: ${d.rationale}`)));
    }
    if (uncertainties.length) {
      const order = { open: 0, partially_resolved: 1, unresolved: 2, resolved: 3 };
      const sorted = [...uncertainties].sort((a, b) => order[a.status] - order[b.status] || a.id.localeCompare(b.id));
      out.push(section("Open questions", h("ul", { class: "points" }, sorted.map((u) => h("li", {},
        h("div", {}, h("span", { class: "q" }, u.question), h("span", { class: `u-status ${u.status}` }, u.status.replace("_", " "))),
        h("div", { class: "stmt-meta" }, [`${u.id}, ${u.category}, ${u.importance} importance`,
          u.challenge_verdict ? `challenge verdict: ${u.challenge_verdict}` : null,
          u.confidence != null ? `confidence ${u.confidence} (${u.confidence_basis})` : null,
          u.status === "resolved" ? null : `next: ${u.next_action.toLowerCase().replace("_", " ")}`,
          `investigated ${plural(u.attempts, "time")}`, u.source === "controller" ? "raised by ResearchForge" : null].filter(Boolean).join(", ")),
        u.resolution ? h("div", {}, u.resolution) : null)))));
    }
    const decisions = (S.info.state?.decisions || []).slice().reverse();
    if (decisions.length) {
      const item = (d) => h("li", {}, h("span", { class: "n" }, d.iteration),
        h("div", { class: "act" }, d.action.toLowerCase().replace("_", " "), d.focus ? h("span", {}, ` on ${d.focus}`) : null),
        h("div", { class: "why" }, d.reason),
        d.candidates && d.candidates.length > 1 ? h("div", { class: "why" }, `Also considered: ${d.candidates.slice(1, 3).map((c) => `${c.action.toLowerCase()} on ${c.uncertainty_id} (${c.score})`).join("; ")}`) : null,
        d.outcome ? h("div", { class: "got" }, d.outcome + (d.info_gain != null ? `. Information gain ${d.info_gain}` : "")) : null);
      out.push(section("Investigation log",
        h("p", { class: "lede" }, "Each step was chosen by the controller from what the investigation had recorded so far. Most recent first."),
        h("ol", { class: "log" }, decisions.slice(0, 8).map(item)),
        decisions.length > 8 ? h("details", {}, h("summary", {}, `Show all ${decisions.length} log entries`), h("ol", { class: "log" }, decisions.slice(8).map(item))) : null));
    }
    out.push(section("Formalization", facts([
      ["Problem", idea.problem], ["Proposed method", idea.proposed_method], ["Target domain", idea.target_domain],
      ["Target system", idea.target_system || NONE], ["Expected contribution", idea.expected_contribution],
      ["Independent variables", join(idea.variables.independent)], ["Dependent variables", join(idea.variables.dependent)],
      ["Controls", join(idea.variables.controls)], ["Assumptions", join(idea.assumptions)],
      ["Expected benefits", join(idea.expected_benefits)], ["Potential risks", join(idea.potential_risks)],
    ])));
    if (idea.ambiguities.length) {
      out.push(section("Ambiguities", facts(idea.ambiguities.map((a) => [a.question,
        h("span", {}, a.resolution || "Unresolved", h("span", { class: "muted" }, a.resolved_by === "unresolved" ? "" : ` (resolved by ${a.resolved_by})`))]))));
    }
    return out;
  },

  async literature() {
    const [papers, analyses, searches] = await Promise.all([data("papers"), data("analyses"), data("searches")]);
    const out = [h("h2", {}, "Literature")];
    if (!papers.length) { out.push(pendingNote("Retrieved papers")); return out; }
    const byId = Object.fromEntries(analyses.map((a) => [a.paper_id, a]));
    out.push(h("p", { class: "lede" }, `${plural(papers.length, "paper")} from ${plural(searches.length, "search", "searches")}, ordered by a lexical relevance score used only for triage. The relevance tier comes from the agent's own analysis.`));
    const list = h("ol", { class: "papers" });
    const draw = () => {
      const q = S.lit.q.toLowerCase();
      const shown = papers.filter((p) => (S.lit.show === "all" || (S.lit.show === "analyzed") === Boolean(byId[p.id]))
        && (!q || `${p.title} ${(p.authors || []).join(" ")} ${p.venue || ""}`.toLowerCase().includes(q)));
      list.replaceChildren(...(shown.length ? shown.map((p) => paperItem(p, byId[p.id])) : [h("li", { class: "empty" }, "No papers match this filter.")]));
    };
    const seg = h("div", { class: "seg", role: "group", "aria-label": "Show papers" },
      [["all", "All"], ["analyzed", "Analyzed"], ["unanalyzed", "Not analyzed"]].map(([k, label]) =>
        h("button", { type: "button", "aria-pressed": S.lit.show === k ? "true" : "false", onclick: (ev) => {
          S.lit.show = k;
          seg.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b === ev.currentTarget)));
          draw();
        } }, label)));
    out.push(h("div", { class: "toolbar" },
      h("input", { type: "search", placeholder: "Filter by title, author or venue", "aria-label": "Filter papers", value: S.lit.q, oninput: (ev) => { S.lit.q = ev.target.value; draw(); } }),
      seg));
    draw();
    out.push(list);
    return out;
  },

  async map() {
    const l = await data("landscape");
    const out = [h("h2", {}, "Research map")];
    if (!l) { out.push(pendingNote("The research landscape")); return out; }
    out.push(h("p", { class: "lede" }, l.field_name));
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
  },

  async critique() {
    const [c, claims] = await Promise.all([data("critique"), data("claims")]);
    const out = [h("h2", {}, "Critique")];
    if (!c) { out.push(pendingNote("The critique")); return out; }
    out.push(h("p", { class: "lede" }, "The case against the idea, argued as seriously as the case for it."));
    out.push(h("div", { class: "versus" },
      h("div", { class: "for" }, h("h3", {}, "Strongest argument for"), h("p", {}, c.strongest_for)),
      h("div", { class: "against" }, h("h3", {}, "Strongest argument against"), h("p", {}, c.strongest_against))));
    out.push(facts([
      ["Most important unresolved question", c.most_important_unresolved_question],
      ["Most dangerous confounder", c.most_dangerous_confounder],
      ["Closest existing work", paperRefs(c.closest_paper_ids)],
    ]));
    out.push(section("Overlap and distinction",
      stmt("inference", c.closest_work_explanation, "Why this is the closest work"),
      stmt("inference", c.overlap_summary, "Overlap"),
      stmt("inference", c.distinction_summary, "Potential distinction"),
      stmt("hypothesis", c.potential_contribution, "Potential contribution")));
    const byId = Object.fromEntries(claims.map((x) => [x.id, x]));
    const points = (title, pts) => (pts.length ? section(title, h("ul", { class: "points" }, pts.map((p) => h("li", {},
      h("div", {}, h("span", { class: "q" }, p.question), " ", h("span", { class: `sev ${p.severity}` }, `${p.severity} severity`)),
      h("div", {}, p.finding),
      p.paper_ids.length ? h("div", { class: "stmt-meta" }, "Papers: ", paperRefs(p.paper_ids)) : null,
      p.claim_ids.length ? h("div", { class: "stmt-meta" }, "Claims: ", p.claim_ids.map((id) => (byId[id] ? `${id} (${KIND_NAME[byId[id].kind].toLowerCase()})` : id)).join(", ")) : null)))) : null);
    out.push(points("Novelty", c.novelty), points("Technical validity", c.technical_validity), points("Experimental validity", c.experimental_validity), points("Practicality", c.practicality));
    return out;
  },

  async gaps() {
    const [gaps, noGap] = await Promise.all([data("gaps"), data("no_gap")]);
    const out = [h("h2", {}, "Potential gaps")];
    if (!gaps.length && noGap) {
      out.push(stmt("inference", `No gap is supported by the retrieved evidence. ${noGap.rationale}`, paperRefs(noGap.paper_ids)));
      return out;
    }
    if (!gaps.length) { out.push(pendingNote("Evidence-linked gaps")); return out; }
    out.push(h("p", { class: "lede" }, "Each gap is a hypothesis about what the literature has not yet done, tied to the passages that suggest it."));
    for (const g of gaps) {
      out.push(h("div", { class: "entry" },
        h("h3", {}, g.gap),
        h("p", { class: "stmt-meta" }, `${g.id}, confidence ${g.confidence}`),
        section("Evidence", sources(g.evidence)),
        facts([["Why existing work does not address it", g.why_unaddressed], ["Research question", g.research_question],
          ["Potential experiment", g.potential_experiment], ["Related papers", paperRefs(g.related_paper_ids)],
          ["Still to verify", g.verification_required || NONE]])));
    }
    return out;
  },

  async modifications() {
    const mods = await data("modifications");
    const out = [h("h2", {}, "Modifications")];
    if (!mods.length) { out.push(pendingNote("Proposed modifications")); return out; }
    out.push(h("p", { class: "lede" }, "Ways to make the idea stronger or more distinct. Difficulty is rated low, moderate or high with the reason; there are no numeric scores."));
    for (const m of mods) {
      out.push(h("div", { class: "entry" },
        h("h3", {}, m.title, m.recommended ? h("span", { class: "rec" }, "Recommended") : null),
        stmt("hypothesis", m.description),
        facts([["Why it differs", m.why_differs], ["Mechanism", m.technical_mechanism], ["Expected benefit", m.expected_benefit],
          ["Potential novelty", m.potential_novelty], ["Implementation difficulty", `${m.implementation_difficulty}, because ${m.implementation_difficulty_basis}`],
          ["Experimental difficulty", `${m.experimental_difficulty}, because ${m.experimental_difficulty_basis}`], ["Main risk", m.main_risk],
          ["Required baselines", join(m.required_baselines)], ["Related work", paperRefs(m.related_paper_ids)], ["Addresses gaps", join(m.addresses_gap_ids)]])));
    }
    return out;
  },

  async experiments() {
    const [plans, analyses] = await Promise.all([data("plans"), data("experiment_analyses")]);
    const out = [h("h2", {}, "Experiments")];
    if (!plans.length) { out.push(pendingNote("Experiment plans")); return out; }
    out.push(h("p", { class: "lede" }, "Plans are designs until you approve a run. Nothing executes without your approval."));
    const byPlan = Object.fromEntries(analyses.map((a) => [a.plan_id, a]));
    for (const p of plans) {
      const a = byPlan[p.id];
      const box = h("div", { class: "entry" },
        h("h3", {}, p.title),
        h("p", { class: "stmt-meta" }, `${p.id}, ${p.execution ? "executable" : "design only"}, ${p.status.replace("_", " ")}`),
        h("p", { class: "prose" }, p.research_question),
        stmt("hypothesis", p.hypothesis),
        facts([["Proposed method", p.proposed_method], ["Baselines", join(p.baselines)], ["Datasets", join(p.datasets)], ["Workloads", join(p.workloads)],
          ["Metrics", join(p.metrics)], ["Ablations", join(p.ablations)], ["Controls", join(p.controls)], ["Confounders addressed", join(p.confounders_addressed)],
          ["Would falsify the hypothesis", join(p.failure_conditions)], ["Expected outcomes", p.expected_outcomes || NONE],
          ["Hardware", p.hardware || NONE], ["Software", p.software_environment || NONE], ["Reproducibility", p.reproducibility_notes || NONE]]));
      if (a) box.append(resultBlock(a));
      if (p.execution) box.append(approvalPanel(p));
      out.push(box);
    }
    return out;
  },

  async evidence() {
    const [claims, searches] = await Promise.all([data("claims"), data("searches")]);
    const out = [h("h2", {}, "Evidence ledger"), h("p", { class: "lede" }, "Every claim the investigation recorded, with its sources. Quotes are checked word for word against the retrieved abstract or full text."), legend()];
    const kinds = ["evidence", "inference", "hypothesis", "assumption", "experimental"].map((k) => [k, claims.filter((c) => c.kind === k)]).filter(([, g]) => g.length);
    if (!kinds.length) out.push(pendingNote("Claims"));
    for (const [k, group] of kinds) {
      out.push(section(`${KIND_NAME[k]} (${group.length})`, ...group.map((c) =>
        h("div", { class: `stmt ${c.kind}` }, h("span", { class: "stmt-text" }, c.statement),
          h("div", { class: "stmt-meta" }, `${c.id}, confidence ${c.confidence}${c.phase ? `, recorded during ${c.phase}` : ""}`),
          sources(c.evidence)))));
    }
    out.push(section("Search log", searches.length ? h("div", { class: "table-wrap" }, h("table", { class: "results" },
      h("tr", {}, h("th", {}, "Query"), h("th", {}, "Sources"), h("th", {}, "Papers")),
      searches.map((s) => h("tr", {}, h("td", {}, s.query),
        h("td", {}, s.sources.map((x) => `${x.source}: ${x.status === "ok" ? x.count : x.status}`).join(", ")),
        h("td", {}, s.paper_ids.length))))) : h("p", { class: "muted" }, "No searches yet.")));
    return out;
  },

  async report() {
    const name = encodeURIComponent(S.project);
    return [h("h2", {}, "Final report"),
      h("p", { class: "lede" }, "Generated from the recorded data only; no model writes it. ",
        h("a", { href: `/api/projects/${name}/report.html?refresh=true`, target: "_blank" }, "Open in a new tab"), " or download the ",
        h("a", { href: `/api/projects/${name}/report.md?refresh=true`, download: `${S.project}-report.md` }, "Markdown version"), "."),
      h("iframe", { class: "report", src: `/api/projects/${name}/report.html?refresh=true`, sandbox: "", title: "Final report" })];
  },
};

function paperItem(p, a) {
  const url = safeUrl(p.url);
  const authors = (p.authors || []).slice(0, 3).join(", ") + ((p.authors || []).length > 3 ? " et al." : "");
  const meta = [authors, p.venue, p.year].filter(Boolean).join(", ");
  const cites = p.citation_count != null ? `; ${p.citation_count} citations per ${p.citation_count_source}` : "";
  const item = h("li", { class: "paper" },
    h("div", { class: "paper-title" }, url ? h("a", { href: url, target: "_blank", rel: "noopener noreferrer" }, p.title) : p.title,
      a ? h("span", { class: `tier ${a.relevance_tier}` }, ` ${a.relevance_tier.replace("_", " ")} relevance`) : null),
    h("div", { class: "paper-meta" }, `${meta}${cites}. Found via ${p.sources.join(", ")}.`),
    (p.metadata_warnings || []).map((w) => h("div", { class: "paper-warning" }, `Check this record: ${w}.`)));
  if (a) {
    const r = a.relation_to_idea;
    const bar = (label, v) => h("span", {}, label, h("span", { class: "bar", role: "img", "aria-label": `${label} overlap ${v}` }, h("i", { style: `width:${Math.round(v * 100)}%` })));
    item.append(h("details", {}, h("summary", {}, "Show analysis"),
      facts([["Problem", a.problem], ["Method", a.method], ["Contribution", a.main_contribution || NONE],
        ["Datasets and benchmarks", join([...a.datasets, ...a.benchmarks])], ["Baselines", join(a.baselines)], ["Metrics", join(a.metrics)],
        ["Results", a.results || NONE], ["Limitations", join(a.limitations)], ["Code", a.code_availability],
        ["Overlap with the idea", h("span", { class: "overlap" }, bar("Problem", r.problem_overlap), bar("Method", r.method_overlap), bar("Evaluation", r.evaluation_overlap))],
        ["How it differs", r.conceptual_difference], ["Basis for the overlap scores", r.basis || "Not stated"], ["Read from", a.analyzed_from === "full_text" ? "full text" : "abstract only"]])));
  }
  return item;
}

function resultBlock(a) {
  const label = { PASSED: "Passed verification", SUSPICIOUS: "Completed, needs review", FAILED: "Failed" }[a.status] || a.status;
  const box = h("div", {}, h("h3", {}, `Result: ${label}`), stmt(a.status === "PASSED" ? "experimental" : "inference", a.summary));
  if (a.issues.length) box.append(h("ul", { class: "points" }, a.issues.map((i) => h("li", {},
    h("span", { class: `sev ${i.severity === "error" ? "high" : ""}` }, i.severity === "error" ? "Problem" : "Warning"), ` ${i.message}`,
    i.suggestion ? h("div", { class: "stmt-meta" }, i.suggestion) : null))));
  if (a.comparisons.length) box.append(h("div", { class: "table-wrap" }, h("table", { class: "results" },
    h("tr", {}, ["Metric", "Baseline", "Method", "Baseline value", "Method value", "Change"].map((t) => h("th", {}, t))),
    a.comparisons.map((c) => h("tr", {}, h("td", {}, c.metric), h("td", {}, c.baseline_arm), h("td", {}, c.method_arm), h("td", {}, c.baseline_value), h("td", {}, c.method_value),
      h("td", {}, c.relative_change == null ? "n/a" : `${c.relative_change > 0 ? "+" : ""}${(c.relative_change * 100).toFixed(1)}%`))))));
  return box;
}

function approvalPanel(plan) {
  const out = h("div");
  return h("div", { class: "approve" },
    h("p", {}, "This plan includes commands that would run on this computer. Review them before approving."),
    h("button", { type: "button", onclick: async (ev) => {
      ev.target.disabled = true;
      try {
        const p = await api(`/api/projects/${encodeURIComponent(S.project)}/experiments/${encodeURIComponent(plan.id)}/preview`);
        out.replaceChildren(
          h("p", {}, `Runs in ${p.workdir} with the ${p.backend} backend (network: ${p.network}), time limit ${Math.round(p.timeout_s / 60)} min.`),
          h("pre", { class: "preview" }, JSON.stringify({ repo: p.repo, setup: p.setup, arms: p.arms }, null, 2)),
          h("button", { class: "primary", type: "button", onclick: async (e2) => {
            e2.target.disabled = true;
            try {
              await api(`/api/projects/${encodeURIComponent(S.project)}/experiments/${encodeURIComponent(plan.id)}/run`, { method: "POST", body: JSON.stringify({ approve: true }) });
              out.replaceChildren(h("p", {}, "Experiment started. Its result appears above when the run finishes."));
              S.pollUntil = Date.now() + 10 * 60 * 1000;
              schedulePoll();
            } catch (e) { out.append(h("p", { class: "error" }, `The experiment did not start: ${e.message}`)); e2.target.disabled = false; }
          } }, plan.status === "failed" ? "Approve and run again" : "Approve and run"));
      } catch (e) { out.replaceChildren(h("p", { class: "error" }, `The commands could not be previewed: ${e.message}`)); ev.target.disabled = false; }
    } }, "Preview commands"),
    out);
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
