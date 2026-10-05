"""Detect failed or suspicious experiment results.

Checks: failed or timed-out runs, missing results, missing expected metrics,
non-finite values, inconsistent sample counts between arms, configuration
mismatches between arms on shared keys that are not the variable under test,
and unusually large improvements over the baseline.
"""

from __future__ import annotations

import math

from researchforge.schemas import ExperimentAnalysis, ExperimentPlan, ExperimentRun, MetricComparison, VerificationIssue

# Configuration keys that must match between baseline and method arms when both
# declare them; a mismatch makes the comparison unfair.
CONTROLLED_KEYS = ("model", "model_version", "dataset", "benchmark", "seed", "num_samples", "max_length", "batch_size", "hardware", "precision")


def _num(value) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def analyze(plan: ExperimentPlan, runs: list[ExperimentRun], large_threshold: float) -> ExperimentAnalysis:
    spec = plan.execution
    issues: list[VerificationIssue] = []
    add = lambda sev, code, msg, sug="": issues.append(VerificationIssue(severity=sev, code=code, message=msg, suggestion=sug))  # noqa: E731

    for r in runs:
        if r.status == "timeout":
            add("error", "RUN_TIMEOUT", f"arm {r.arm} exceeded the time limit", "Reduce the workload or raise the timeout.")
        elif r.status != "ok":
            add("error", "RUN_FAILED", f"arm {r.arm} exited with code {r.exit_code}", f"Inspect {r.stderr_path}.")
        if r.error:
            add("error", "RESULTS_INVALID", f"arm {r.arm}: {r.error}", "Make the command write a JSON object of metrics to $RF_RESULTS_FILE.")
    expected = spec.expected_metrics if spec else []
    ok_runs = [r for r in runs if r.status == "ok" and r.results]
    for r in ok_runs:
        missing = [m for m in expected if m not in r.results]
        if missing:
            add("error", "MISSING_METRICS", f"arm {r.arm} did not report {missing}")
        for k, v in r.results.items():
            if isinstance(v, float) and not math.isfinite(v):
                add("error", "NON_FINITE", f"arm {r.arm} reported {k}={v}")

    if spec and spec.sample_count_key:
        counts = {r.arm: r.results.get(spec.sample_count_key) for r in ok_runs}
        if len({c for c in counts.values()}) > 1:
            add("error", "SAMPLE_COUNT_MISMATCH", f"arms evaluated different numbers of samples: {counts}", "Evaluate every arm on the identical sample set.")
        if any(c in (None, 0) for c in counts.values()):
            add("error", "MISSING_SAMPLES", f"sample count missing or zero: {counts}")

    baselines = [r for r in ok_runs if r.role == "baseline"]
    others = [r for r in ok_runs if r.role != "baseline"]
    if not baselines:
        add("error", "NO_BASELINE", "no successful baseline run; results cannot be compared")
    for b in baselines:
        for o in others:
            for key in CONTROLLED_KEYS:
                if key in b.config and key in o.config and b.config[key] != o.config[key]:
                    add("error", "CONFIG_MISMATCH", f"{b.arm} and {o.arm} differ on controlled key {key!r}: {b.config[key]!r} vs {o.config[key]!r}", "Match the configurations or declare the key as the variable under test.")
            if b.git_commit != o.git_commit:
                add("warning", "VERSION_MISMATCH", f"{b.arm} and {o.arm} ran different code versions")

    comparisons: list[MetricComparison] = []
    higher = spec.higher_is_better if spec else {}
    for b in baselines:
        for o in others:
            for metric in sorted(set(b.results) & set(o.results)):
                bv, ov = _num(b.results[metric]), _num(o.results[metric])
                if bv is None or ov is None or metric == (spec.sample_count_key if spec else None):
                    continue
                rel = (ov - bv) / abs(bv) if bv != 0 else None
                comparisons.append(MetricComparison(metric=metric, baseline_arm=b.arm, method_arm=o.arm, baseline_value=bv, method_value=ov, relative_change=rel))
                if rel is not None and metric in higher:
                    improvement = rel if higher[metric] else -rel
                    if improvement > large_threshold:
                        add("warning", "UNUSUALLY_LARGE_IMPROVEMENT", f"{o.arm} improves {metric} by {improvement:.0%} over {b.arm}", "Check for a misconfigured baseline, data leakage, or mismatched budgets before trusting this result.")

    errors = [i for i in issues if i.severity == "error"]
    status = "FAILED" if errors else ("SUSPICIOUS" if issues else "PASSED")
    if status == "FAILED":
        summary = "Experiment status: FAILED. " + " ".join(f"Cause: {i.message}." for i in errors[:3])
    elif status == "SUSPICIOUS":
        summary = "Experiment completed but results need review: " + "; ".join(i.message for i in issues[:3])
    else:
        summary = f"Experiment completed; {len(ok_runs)} arms passed verification."
    return ExperimentAnalysis(plan_id=plan.id, status=status, run_ids=[r.id for r in runs], issues=issues, comparisons=comparisons, summary=summary)
