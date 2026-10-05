"""Run an approved experiment plan and record everything needed to reproduce it.

Safety rules:

* Nothing runs without explicit approval (``approved=True`` from the CLI's
  ``--approve`` flag or the web UI's Approve button). The research agent can
  only *propose* an execution spec.
* Commands are split with ``shlex`` and executed as argv without a shell, so
  pipes, redirects, ``;`` and ``&&`` are not interpreted.
* Commands run inside ``<project>/experiments/<plan>/`` with a scrubbed
  environment (only allow-listed variables pass through) and a timeout.
* The Docker backend additionally runs each command in a container with the
  experiment directory as the only mount and ``--network none`` by default.

Each arm must write a JSON object of metrics to the path in ``$RF_RESULTS_FILE``.
"""

from __future__ import annotations

import json
import os
import platform
import shlex
import shutil
import subprocess
import time
from pathlib import Path

from researchforge.config import Settings
from researchforge.experiments.verify import analyze
from researchforge.schemas import ExperimentAnalysis, ExperimentPlan, ExperimentRun, VerificationIssue, utcnow
from researchforge.workspace import Workspace, safe_name

FORBIDDEN_TOKENS = {"|", "||", "&&", ";", ">", ">>", "<", "&", "`"}
BLOCKED_PROGRAMS = {"rm", "sudo", "su", "dd", "mkfs", "shutdown", "reboot", "chmod", "chown", "curl", "wget", "ssh", "scp"}


class ApprovalRequired(PermissionError):
    pass


class UnsafeCommand(ValueError):
    pass


def parse_command(command: str) -> list[str]:
    argv = shlex.split(command)
    if not argv:
        raise UnsafeCommand("empty command")
    bad = [t for t in argv if t in FORBIDDEN_TOKENS or "$(" in t or "`" in t]
    if bad:
        raise UnsafeCommand(f"shell syntax is not supported (commands run without a shell): {bad}")
    program = Path(argv[0]).name
    if program in BLOCKED_PROGRAMS:
        raise UnsafeCommand(f"program {program!r} is not allowed in experiments")
    if program in ("sh", "bash", "zsh") and len(argv) > 1 and argv[1] == "-c":
        raise UnsafeCommand("inline shell scripts (sh -c) are not allowed; put commands in a script file inside the repository")
    return argv


def hardware_info() -> dict[str, str]:
    info = {
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "python": platform.python_version(),
        "cpu_count": str(os.cpu_count() or "unknown"),
    }
    if shutil.which("nvidia-smi"):
        try:
            gpus = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"],
                capture_output=True, text=True, timeout=10,
            ).stdout.strip()
            info["gpus"] = gpus or "none reported"
        except (OSError, subprocess.SubprocessError) as exc:
            info["gpus"] = f"nvidia-smi failed: {exc}"
    return info


def git_commit(path: Path) -> str | None:
    if not (path / ".git").exists():
        return None
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


class ExperimentRunner:
    def __init__(self, ws: Workspace, settings: Settings) -> None:
        self.ws = ws
        self.settings = settings.experiments

    def preview(self, plan: ExperimentPlan) -> dict:
        """Everything the human must see before approving."""
        if plan.execution is None:
            raise ValueError(f"plan {plan.id} has no executable spec")
        spec = plan.execution
        return {
            "plan_id": plan.id,
            "title": plan.title,
            "backend": self.settings.backend,
            "docker_image": spec.docker_image or self.settings.docker_image if self.settings.backend == "docker" else None,
            "network": self.settings.docker_network if self.settings.backend == "docker" else "host network (local backend)",
            "workdir": str(self.ws.root / "experiments" / safe_name(plan.id)),
            "repo": f"{spec.repo_url}@{spec.repo_ref or 'default branch'}" if spec.repo_url else None,
            "setup": [parse_command(c) for c in spec.setup],
            "arms": [{"name": a.name, "role": a.role, "argv": parse_command(a.command), "config": a.config} for a in spec.arms],
            "timeout_s": spec.timeout_s or self.settings.timeout_s,
        }

    def _env(self, results_file: str, arm_config: dict) -> dict[str, str]:
        env = {k: os.environ[k] for k in self.settings.env_passthrough if k in os.environ}
        env["RF_RESULTS_FILE"] = results_file
        env["RF_ARM_CONFIG"] = json.dumps(arm_config)
        return env

    def _wrap(self, argv: list[str], workdir: Path, env: dict[str, str], image: str | None) -> tuple[list[str], dict[str, str], str]:
        if self.settings.backend != "docker":
            return argv, env, str(workdir)
        docker = ["docker", "run", "--rm", "--network", self.settings.docker_network, "-v", f"{workdir}:/work", "-w", "/work/src" if (workdir / "src").exists() else "/work"]
        for k, v in env.items():
            if k not in ("PATH", "HOME"):
                docker += ["-e", f"{k}={v.replace(str(workdir), '/work')}"]
        return docker + [image or self.settings.docker_image] + argv, {k: v for k, v in os.environ.items() if k in ("PATH", "HOME", "DOCKER_HOST")}, str(workdir)

    def _exec(self, argv: list[str], cwd: Path, env: dict[str, str], timeout: float, log_prefix: Path) -> tuple[int | None, str, float]:
        stdout_path, stderr_path = log_prefix.with_suffix(".stdout.log"), log_prefix.with_suffix(".stderr.log")
        start = time.monotonic()
        with open(stdout_path, "w") as out, open(stderr_path, "w") as err:
            try:
                proc = subprocess.run(argv, cwd=cwd, env=env, stdout=out, stderr=err, timeout=timeout, stdin=subprocess.DEVNULL)
                return proc.returncode, "ok" if proc.returncode == 0 else "failed", time.monotonic() - start
            except subprocess.TimeoutExpired:
                return None, "timeout", time.monotonic() - start
            except OSError as exc:
                err.write(f"could not start {argv[0]}: {exc}\n")
                return None, "failed", time.monotonic() - start

    def run(self, plan_id: str, *, approved: bool) -> ExperimentAnalysis:
        plan = self.ws.plan(plan_id)
        if plan is None:
            raise ValueError(f"unknown experiment plan {plan_id!r}")
        if plan.execution is None:
            raise ValueError(f"plan {plan_id} has no executable spec; it is a design only")
        if not approved:
            raise ApprovalRequired(f"running experiment {plan_id} executes local commands and requires explicit approval")
        preview = self.preview(plan)  # validates every command before anything runs
        spec = plan.execution
        workdir = self.ws.experiment_dir(plan.id)
        logs = workdir / "logs"
        logs.mkdir(exist_ok=True)
        timeout = preview["timeout_s"]
        image = spec.docker_image
        self.ws.append_event("info", "experiment", message=f"experiment {plan.id} approved and starting", preview=preview)
        base_env = self._env("", {})
        stamp = time.strftime("%Y%m%d-%H%M%S")
        runs: list[ExperimentRun] = []

        code_dir = workdir
        if spec.repo_url:
            code_dir = workdir / "src"
            if not code_dir.exists():
                argv = ["git", "clone", "--depth", "50", spec.repo_url, str(code_dir)]
                rc, status, dur = self._exec(argv, workdir, {k: v for k, v in os.environ.items() if k in ("PATH", "HOME")}, timeout, logs / f"{stamp}-clone")
                if status != "ok":
                    return self._fail(plan, runs, "SETUP_FAILED", f"git clone failed (see {logs}/{stamp}-clone.stderr.log)")
            if spec.repo_ref:
                rc, status, _ = self._exec(["git", "-C", str(code_dir), "checkout", spec.repo_ref], workdir, {k: v for k, v in os.environ.items() if k in ("PATH", "HOME")}, 120, logs / f"{stamp}-checkout")
                if status != "ok":
                    return self._fail(plan, runs, "SETUP_FAILED", f"git checkout {spec.repo_ref} failed")

        for i, command in enumerate(spec.setup):
            argv, env, _ = self._wrap(parse_command(command), workdir, base_env, image)
            rc, status, _ = self._exec(argv, code_dir, env, timeout, logs / f"{stamp}-setup{i}")
            if status != "ok":
                return self._fail(plan, runs, "SETUP_FAILED", f"setup command {command!r} {status} (exit {rc}); see {logs}/{stamp}-setup{i}.stderr.log")

        commit = git_commit(code_dir)
        hw = hardware_info()
        for arm in spec.arms:
            run_id = f"{plan.id}-{arm.name}-{stamp}"
            results_file = workdir / "results" / f"{arm.name}-{stamp}.json"
            results_file.parent.mkdir(exist_ok=True)
            env = self._env(str(results_file), arm.config)
            argv, exec_env, _ = self._wrap(parse_command(arm.command), workdir, env, image)
            started = utcnow()
            rc, status, dur = self._exec(argv, code_dir, exec_env, timeout, logs / run_id)
            results, error = None, None
            if results_file.exists():
                try:
                    results = json.loads(results_file.read_text())
                    if not isinstance(results, dict):
                        error, results = "results file is not a JSON object", None
                except json.JSONDecodeError as exc:
                    error = f"results file is not valid JSON: {exc}"
            elif status == "ok":
                error = "command succeeded but wrote no results file ($RF_RESULTS_FILE)"
            run = ExperimentRun(
                id=run_id, plan_id=plan.id, arm=arm.name, role=arm.role, status=status,
                argv=argv, cwd=str(code_dir), backend=self.settings.backend,
                env={k: v for k, v in env.items() if k not in ("PATH", "HOME")},
                config=arm.config, git_commit=commit, hardware=hw,
                started_at=started, finished_at=utcnow(), duration_s=round(dur, 3), exit_code=rc,
                stdout_path=str(logs / f"{run_id}.stdout.log"), stderr_path=str(logs / f"{run_id}.stderr.log"),
                results=results, error=error,
            )
            self.ws.save_run(run)
            runs.append(run)
            self.ws.append_event("info", "experiment", message=f"arm {arm.name} finished: {status}", run_id=run_id, exit_code=rc)

        analysis = analyze(plan, runs, self.settings.large_improvement_threshold)
        return self._finish(plan, analysis)

    def _fail(self, plan: ExperimentPlan, runs: list[ExperimentRun], code: str, message: str) -> ExperimentAnalysis:
        analysis = ExperimentAnalysis(
            plan_id=plan.id,
            status="FAILED",
            run_ids=[r.id for r in runs],
            issues=[VerificationIssue(severity="error", code=code, message=message, suggestion="Fix the setup and re-run with approval.")],
            summary=f"Experiment status: FAILED. Cause: {message}",
        )
        return self._finish(plan, analysis)

    def _finish(self, plan: ExperimentPlan, analysis: ExperimentAnalysis) -> ExperimentAnalysis:
        self.ws.save_experiment_analysis(analysis)
        self.ws.save_plan(plan.model_copy(update={"status": "failed" if analysis.status == "FAILED" else "completed"}))
        self.ws.append_event("error" if analysis.status == "FAILED" else "info", "experiment", message=analysis.summary, status=analysis.status)
        return analysis
