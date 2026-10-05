import json
import textwrap

import pytest

from support import ScriptedRuntime

from researchforge.evaluation.metrics import GroundTruth, evaluate, plan_completeness, precision_recall_at_k
from researchforge.experiments.runner import ApprovalRequired, ExperimentRunner, UnsafeCommand, parse_command
from researchforge.orchestrator import investigate
from researchforge.schemas import ExecutionSpec, ExperimentPlan, Paper
from researchforge.report import build_report

BENCH = textwrap.dedent(
    """
    import json, os, sys
    cfg = json.loads(os.environ["RF_ARM_CONFIG"])
    arm = sys.argv[1]
    if arm == "crash":
        sys.exit(3)
    metrics = {"accuracy": cfg.get("acc", 0.8), "peak_memory_gb": cfg.get("mem", 10.0), "n": cfg.get("n", 100)}
    json.dump(metrics, open(os.environ["RF_RESULTS_FILE"], "w"))
    """
)


def make_plan(ws, arms, **spec):
    (ws.experiment_dir("E001") / "bench.py").write_text(BENCH)
    plan = ExperimentPlan(
        title="t", research_question="q", hypothesis="h", proposed_method="m", baselines=["static"], metrics=["accuracy"],
        execution=ExecutionSpec(arms=arms, expected_metrics=["accuracy", "peak_memory_gb"], higher_is_better={"accuracy": True, "peak_memory_gb": False}, sample_count_key="n", **spec),
    )
    return ws.save_plan(plan)


def arm(name, role, **config):
    return {"name": name, "role": role, "command": f"python3 bench.py {name}", "config": config}


def test_command_parsing_rejects_shell_and_dangerous_programs():
    assert parse_command("python3 run.py --n 5") == ["python3", "run.py", "--n", "5"]
    for bad in ("python3 a.py | tee x", "rm -rf /", "bash -c 'echo hi'", "python3 a.py && echo", "echo $(whoami)", "curl http://x"):
        with pytest.raises(UnsafeCommand):
            parse_command(bad)


def test_run_requires_approval(ws, settings):
    make_plan(ws, [arm("base", "baseline")])
    with pytest.raises(ApprovalRequired):
        ExperimentRunner(ws, settings).run("E001", approved=False)
    assert ws.runs() == []


def test_successful_run_records_reproducibility_data(ws, settings):
    make_plan(ws, [arm("base", "baseline", acc=0.80, mem=10.0, model="m1"), arm("method", "method", acc=0.79, mem=7.0, model="m1")])
    analysis = ExperimentRunner(ws, settings).run("E001", approved=True)
    assert analysis.status == "PASSED", analysis.issues
    runs = ws.runs("E001")
    assert {r.arm for r in runs} == {"base", "method"}
    r = runs[0]
    assert r.argv[0] == "python3" and r.hardware["platform"] and r.exit_code == 0 and r.results["n"] == 100
    assert "RF_RESULTS_FILE" in r.env and "HOME" not in r.env
    mem = next(c for c in analysis.comparisons if c.metric == "peak_memory_gb")
    assert mem.relative_change == pytest.approx(-0.3)
    assert ws.plan("E001").status == "completed"
    md = build_report(ws, settings)
    assert "[Experimental result]" in md and "Experiment E001: PASSED" in md


def test_verification_flags_mismatches_failures_and_large_gains(ws, settings):
    make_plan(ws, [arm("base", "baseline", n=100, model="m1", mem=10.0), arm("method", "method", n=80, model="m2", mem=1.0)])
    analysis = ExperimentRunner(ws, settings).run("E001", approved=True)
    codes = {i.code for i in analysis.issues}
    assert analysis.status == "FAILED"
    assert {"SAMPLE_COUNT_MISMATCH", "CONFIG_MISMATCH", "UNUSUALLY_LARGE_IMPROVEMENT"} <= codes
    assert analysis.summary.startswith("Experiment status: FAILED")
    md = build_report(ws, settings)
    assert "not reported as experimental results" in md


def test_crashing_arm_fails_with_cause(ws, settings):
    make_plan(ws, [arm("base", "baseline"), arm("crash", "method")])
    analysis = ExperimentRunner(ws, settings).run("E001", approved=True)
    assert analysis.status == "FAILED"
    assert any(i.code == "RUN_FAILED" and "crash" in i.message for i in analysis.issues)
    assert ws.plan("E001").status == "failed"


def test_setup_failure_is_reported(ws, settings):
    make_plan(ws, [arm("base", "baseline")], setup=["python3 missing_setup.py"])
    analysis = ExperimentRunner(ws, settings).run("E001", approved=True)
    assert analysis.status == "FAILED" and analysis.issues[0].code == "SETUP_FAILED"


def test_bundled_ground_truth_and_retrieval_metrics(ws):
    truth = GroundTruth.load("kv-cache")
    assert len(truth.relevant) == 11
    ranked = [
        Paper(id="arxiv:2306.14048", arxiv_id="2306.14048", title="H2O", source="arxiv"),
        Paper(id="doi:x", title="Unrelated", source="crossref"),
        Paper(id="openalex:W1", title=truth.relevant[1]["title"], source="openalex"),
    ]
    m = precision_recall_at_k(ranked, truth, 2)
    assert (m["hits"], m["precision"]) == (1, 0.5)
    assert precision_recall_at_k(ranked, truth, 3)["hits"] == 2


def test_evaluate_full_run(ws, settings):
    investigate(ws, settings, ScriptedRuntime(settings))
    result = evaluate(ws, GroundTruth.load("kv-cache"))
    assert result["claim_grounding"]["grounded"] >= 1
    assert result["records"]["plans"] == 1
    assert result["experiment_plans"][0]["score"] == 1.0
    assert result["efficiency"]["tool_calls_total"] > 0
    assert result["retrieval"]["retrieved_papers"] == len(ws.papers())
    assert result["retrieval"]["overall_recall"] == 0.0  # synthetic papers are not in the curated set


def test_plan_completeness_lists_missing_items():
    plan = ExperimentPlan(title="t", research_question="q", hypothesis="h", proposed_method="m", baselines=["one"], metrics=["m"])
    res = plan_completeness(plan)
    assert "baselines (>=2)" in res["missing"] and "failure conditions" in res["missing"] and res["score"] < 0.3
