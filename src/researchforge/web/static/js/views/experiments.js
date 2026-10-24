import { h, NONE, join, api, facts, stmt, S, data, pendingNote, app } from "../core.js";

export default async function experiments() {
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
              app.schedulePoll();
            } catch (e) { out.append(h("p", { class: "error" }, `The experiment did not start: ${e.message}`)); e2.target.disabled = false; }
          } }, plan.status === "failed" ? "Approve and run again" : "Approve and run"));
      } catch (e) { out.replaceChildren(h("p", { class: "error" }, `The commands could not be previewed: ${e.message}`)); ev.target.disabled = false; }
    } }, "Preview commands"),
    out);
}
