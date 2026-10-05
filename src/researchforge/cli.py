"""ResearchForge command line.

    researchforge investigate --idea "..."      start an investigation
    researchforge resume <project>              continue from the first unfinished phase
    researchforge status <project>              phase progress
    researchforge report <project>              regenerate and print the report
    researchforge experiment <project> ...      list / preview / run (with --approve) experiments
    researchforge serve                          web UI
    researchforge eval <project>                 evaluation metrics
    researchforge doctor                         check the installation
    researchforge list                           list projects
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from researchforge import logging_setup
from researchforge.config import Settings, config_path, load_dotenv, load_settings
from researchforge.workspace import Workspace, list_projects

PHASE_TITLES = {
    "formalize": "Phase 1 — Formalizing idea",
    "literature": "Phase 2 — Literature investigation",
    "analysis": "Phase 3 — Paper analysis",
    "landscape": "Phase 4 — Research landscape",
    "critique": "Phase 5 — Critical analysis",
    "gaps": "Phase 6 — Research gaps",
    "modifications": "Phase 7 — Research modification",
    "experiments": "Phase 8 — Experiment design",
    "report": "Final report",
    "experiment": "Experiment",
}


class ProgressPrinter:
    """Tails a workspace's event log and prints human-readable progress."""

    def __init__(self, ws: Workspace, verbose: bool = False, stream=sys.stdout) -> None:
        self.ws, self.verbose, self.stream = ws, verbose, stream
        self.last = max((e.seq for e in ws.events()), default=-1)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        self._thread.join(timeout=2)
        self.flush()

    def _loop(self) -> None:
        while not self._stop.wait(0.5):
            self.flush()

    def flush(self) -> None:
        for e in self.ws.events(self.last):
            self.last = e.seq
            line = self.format(e)
            if line:
                print(line, file=self.stream, flush=True)

    def format(self, e) -> str | None:
        d = e.data
        if e.kind == "decision":
            focus = f" [{d.get('focus')}]" if d.get("focus") else ""
            head = f"\nStep {d.get('iteration')}  {e.phase} → {d.get('action')}{focus}"
            return head + (f"\n  why: {d.get('reason')}" if d.get("reason") else "")
        if e.kind == "phase_start":
            return None if d.get("action") else f"\n{PHASE_TITLES.get(e.phase, e.phase)}"
        if e.kind == "phase_end":
            mark = "✓" if d.get("status") == "complete" else "✗"
            if d.get("action"):
                return f"  {mark} {d.get('outcome', d.get('status'))}"
            extra = f"; missing: {'; '.join(d.get('missing') or [])}" if d.get("missing") else ""
            return f"{mark} {e.phase}: {d.get('status')}{extra}"
        if e.kind == "tool_call":
            return f"  • {d.get('tool')} {d.get('input', '')[:140] if self.verbose else ''}".rstrip()
        if e.kind == "tool_result" and d.get("status") == "error":
            return f"    ! tool error: {str(d.get('result', ''))[:200]}"
        if e.kind in ("warning", "error"):
            return f"  {e.kind.upper()}: {d.get('message', '')}"
        if e.kind == "agent_text" and self.verbose:
            return f"  » {d.get('text', '')[:300]}"
        if e.kind == "info" and d.get("message") in ("investigation started", "investigation finished"):
            return f"{d.get('message')}" + (f" ({d.get('status')})" if d.get("status") else "")
        return None


def _settings(args) -> Settings:
    settings = load_settings(args.config)
    logging_setup.configure(settings.log_level)
    return settings


def _open(settings: Settings, project: str) -> Workspace:
    return Workspace.open(settings.resolved_projects_dir(), project)


def _runtime(settings: Settings, args):
    from researchforge.runtime.dsh import DshHeadlessRuntime

    # Always hand dsh the settings file in effect, so the MCP server (started in the project directory) uses it too.
    path = config_path(args.config)
    return DshHeadlessRuntime(settings, path.resolve() if path else None)


def _run(ws: Workspace, settings: Settings, args) -> int:
    from researchforge.orchestrator import investigate

    print(f"RESEARCHFORGE\n\nProject: {ws.root}\nModel: {settings.model.custom.provider_id if settings.model.custom else settings.model.provider}/{settings.model.model}")
    with ProgressPrinter(ws, verbose=args.verbose):
        state = investigate(ws, settings, _runtime(settings, args))
    print(f"\nStatus: {state.status}" + (f": {state.error}" if state.error else ""))
    if state.finalize_reason:
        print(f"Finished because: {state.finalize_reason}")
    if state.status == "awaiting_approval":
        print(f"Experiment {', '.join(state.awaiting_approval)} needs approval: researchforge experiment {ws.name} --run <id> --approve, then researchforge resume {ws.name}")
    print(f"Report: {ws.report_path('md')}\n        {ws.report_path('html')}")
    return 0 if state.status in ("complete", "awaiting_approval") else 1


def cmd_investigate(args) -> int:
    settings = _settings(args)
    idea = args.idea or (sys.stdin.read() if not sys.stdin.isatty() else "")
    if not idea.strip():
        print("error: provide --idea or pipe the idea on stdin", file=sys.stderr)
        return 2
    ws = Workspace.create(settings.resolved_projects_dir(), idea.strip(), args.name)
    return _run(ws, settings, args)


def cmd_resume(args) -> int:
    settings = _settings(args)
    return _run(_open(settings, args.project), settings, args)


def cmd_status(args) -> int:
    settings = _settings(args)
    ws = _open(settings, args.project)
    state = ws.state()
    print(f"{ws.name}: {ws.raw_idea}")
    if not state:
        print("not started")
        return 0
    print(f"status: {state.status}  dsh session: {state.dsh_session_id}  model: {state.provider}/{state.model}")
    for p in state.phases:
        mark = {"complete": "✓", "running": "●", "incomplete": "✗", "failed": "✗"}.get(p.status, "○")
        print(f"  {mark} {PHASE_TITLES.get(p.name, p.name):38} {p.status:10} attempts={p.attempts} tools={p.tool_calls}" + (f"  missing: {'; '.join(p.missing)}" if p.missing else ""))
    b = state.budget
    print(f"loop: phase={state.loop_phase} steps={b.iterations}/{settings.investigation.max_iterations} tool_calls={b.tool_calls} "
          f"runtime_failures={b.runtime_failures} time={int(b.seconds)}s")
    if state.finalize_reason:
        print(f"  finished because: {state.finalize_reason}")
    for u in ws.uncertainties():
        print(f"  {u.id} [{u.importance}, {u.status}] {u.question}")
    if state.awaiting_approval:
        print(f"  awaiting approval: {', '.join(state.awaiting_approval)} (researchforge experiment {ws.name} --run <id> --approve, then resume)")
    return 0


def cmd_report(args) -> int:
    from researchforge.report import write_reports

    settings = _settings(args)
    ws = _open(settings, args.project)
    md_path, html_path = write_reports(ws, settings)
    if args.format == "md":
        print(md_path.read_text(encoding="utf-8"))
    elif args.format == "path":
        print(f"{md_path}\n{html_path}")
    else:
        print(html_path)
    return 0


def cmd_list(args) -> int:
    settings = _settings(args)
    for ws in list_projects(settings.resolved_projects_dir()):
        state = ws.state()
        print(f"{ws.name:50} {state.status if state else 'created':11} {ws.raw_idea[:70]}")
    return 0


def cmd_experiment(args) -> int:
    from researchforge.experiments.runner import ApprovalRequired, ExperimentRunner, UnsafeCommand

    settings = _settings(args)
    ws = _open(settings, args.project)
    runner = ExperimentRunner(ws, settings)
    if not args.run:
        plans = ws.plans()
        if not plans:
            print("No experiment plans recorded.")
        for p in plans:
            kind = "executable" if p.execution else "design only"
            print(f"{p.id}  [{p.status}]  {kind:11}  {p.title}")
        return 0
    plan = ws.plan(args.run)
    if plan is None:
        print(f"error: unknown plan {args.run}", file=sys.stderr)
        return 2
    try:
        preview = runner.preview(plan)
    except (ValueError, UnsafeCommand) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print("Experiment preview (local computation):")
    print(json.dumps(preview, indent=2))
    if not args.approve:
        print("\nNothing was executed. Re-run with --approve to execute these commands.")
        return 3
    try:
        analysis = runner.run(args.run, approved=True)
    except (ApprovalRequired, UnsafeCommand, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(f"\nExperiment status: {analysis.status}\n{analysis.summary}")
    for i in analysis.issues:
        print(f"  {i.severity.upper()} {i.code}: {i.message}" + (f"\n    suggestion: {i.suggestion}" if i.suggestion else ""))
    from researchforge.report import write_reports

    write_reports(ws, settings)
    return 0 if analysis.status != "FAILED" else 1


def cmd_serve(args) -> int:
    import uvicorn

    from researchforge.web.app import create_app

    settings = _settings(args)
    path = config_path(args.config)
    app = create_app(settings, path.resolve() if path else None)
    print(f"ResearchForge UI on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="warning")
    return 0


def cmd_bench(args) -> int:
    from researchforge.evaluation.bench import BenchSpec, run_bench, score_bench
    from researchforge.runtime.dsh import DshHeadlessRuntime

    settings = _settings(args)
    spec = BenchSpec.load(args.spec)
    if args.action == "score":
        print(json.dumps(score_bench(spec), indent=2))
        return 0
    rows = run_bench(spec, settings, lambda s, cfg: DshHeadlessRuntime(s, cfg), workers=args.workers)
    failed = [r["key"] for r in rows if r["error"]]
    print(f"finished {len(rows)} runs" + (f"; {len(failed)} crashed: {failed}" if failed else ""))
    return 1 if failed else 0


def cmd_eval(args) -> int:
    from researchforge.evaluation.metrics import GroundTruth, evaluate, gap_review_sheet, parse_ks

    settings = _settings(args)
    ws = _open(settings, args.project)
    truth = GroundTruth.load(args.ground_truth) if args.ground_truth else None
    result = evaluate(ws, truth, parse_ks(args.k))
    if args.gap_sheet:
        result["gap_review_sheet"] = gap_review_sheet(ws)
    print(json.dumps(result, indent=2, default=str))
    return 0


def cmd_doctor(args) -> int:
    from researchforge.runtime.dsh import dump_config

    settings = _settings(args)
    ok = True

    def check(label: str, passed: bool, detail: str = "") -> None:
        nonlocal ok
        ok &= passed
        print(f"{'✓' if passed else '✗'} {label}" + (f": {detail}" if detail else ""))

    check("Python >= 3.10", sys.version_info >= (3, 10), sys.version.split()[0])
    cmd = settings.dsh.resolved_command()
    launcher = shutil.which(cmd[0])
    check(f"dsh launcher `{cmd[0]}` on PATH", launcher is not None, launcher or "install Node.js >= 22.19 and `npm i -g @deepseek-ai/dsh`")
    if shutil.which("node"):
        version = subprocess.run(["node", "--version"], capture_output=True, text=True).stdout.strip()
        parts = tuple(int(x) for x in version.lstrip("v").split(".")[:2] if x.isdigit())
        check("Node.js >= 22.19", parts >= (22, 19), version)
    else:
        check("Node.js", False, "not found")
    model = settings.model
    if model.custom:
        env_name = model.custom.api_key_env
        check(f"custom model endpoint {model.custom.provider_id}", True, f"{model.custom.base_url} models={model.custom.models}")
        if env_name:
            check(f"credential ${env_name}", bool(os.environ.get(env_name)), "set" if os.environ.get(env_name) else "not set")
    elif model.provider == "deepseek-official":
        check("credential $DEEPSEEK_API_KEY", bool(os.environ.get("DEEPSEEK_API_KEY")), "set" if os.environ.get("DEEPSEEK_API_KEY") else "not set (or save the key in dsh's Settings → Models)")
    if launcher and not args.skip_dsh:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Workspace.create(Path(tmp), "doctor check")
            print("… composing dsh configuration with the ResearchForge overlay (first npx run downloads dsh)")
            try:
                result = dump_config(settings, ws, Path(args.config).resolve() if args.config else None)
                composed = result.returncode == 0 and "mcp-researchforge" in result.stdout
                warnings = [l for l in result.stderr.splitlines() if "not found" in l]
                check("dsh composes the ResearchForge overlay", composed and not warnings, "; ".join(warnings) or result.stderr.strip()[-300:] if not composed or warnings else "")
            except subprocess.TimeoutExpired:
                check("dsh composes the ResearchForge overlay", False, "timed out")
    projects = settings.resolved_projects_dir()
    check("projects directory", True, str(projects))
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="researchforge", description="Turn a research idea into an evidence-backed investigation.")
    p.add_argument("--config", help="settings TOML (default: $RESEARCHFORGE_CONFIG or ./researchforge.toml)")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("investigate", help="start a new investigation")
    s.add_argument("--idea", help="the research idea (or pipe it on stdin)")
    s.add_argument("--name", help="project directory name")
    s.add_argument("-v", "--verbose", action="store_true", help="show tool inputs and agent text")
    s.set_defaults(fn=cmd_investigate)

    s = sub.add_parser("resume", help="continue an investigation")
    s.add_argument("project")
    s.add_argument("-v", "--verbose", action="store_true")
    s.set_defaults(fn=cmd_resume)

    s = sub.add_parser("status", help="show phase progress")
    s.add_argument("project")
    s.set_defaults(fn=cmd_status)

    s = sub.add_parser("report", help="regenerate the report from recorded data")
    s.add_argument("project")
    s.add_argument("--format", choices=["md", "html", "path"], default="md")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("list", help="list investigations")
    s.set_defaults(fn=cmd_list)

    s = sub.add_parser("experiment", help="list, preview or run (with --approve) experiment plans")
    s.add_argument("project")
    s.add_argument("--run", metavar="PLAN_ID", help="preview (and with --approve, execute) this plan")
    s.add_argument("--approve", action="store_true", help="explicitly approve executing the previewed commands")
    s.set_defaults(fn=cmd_experiment)

    s = sub.add_parser("serve", help="start the web UI")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=8765)
    s.set_defaults(fn=cmd_serve)

    s = sub.add_parser("eval", help="evaluation metrics for a project")
    s.add_argument("project")
    s.add_argument("--ground-truth", help="curated relevant-paper set: a YAML path or a bundled name such as kv-cache")
    s.add_argument("--k", default="5,10,20")
    s.add_argument("--gap-sheet", action="store_true", help="include a sheet for expert rating of gaps")
    s.set_defaults(fn=cmd_eval)

    s = sub.add_parser("bench", help="run or score the temporal prior-art benchmark (docs/paper/research_plan.md)")
    s.add_argument("action", choices=["run", "score"])
    s.add_argument("spec", help="benchmark spec YAML")
    s.add_argument("--workers", type=int, default=1, help="investigations to run in parallel")
    s.set_defaults(fn=cmd_bench)

    s = sub.add_parser("doctor", help="check the installation")
    s.add_argument("--skip-dsh", action="store_true", help="do not launch dsh")
    s.set_defaults(fn=cmd_doctor)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv()  # ./.env, if present; existing environment variables win
    try:
        return args.fn(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("\ninterrupted; resume with `researchforge resume <project>`", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
