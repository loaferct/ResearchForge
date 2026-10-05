"""FastAPI backend for the ResearchForge web UI.

Investigations run in background threads using the same orchestrator and dsh
runtime as the CLI; the browser polls workspace state and events. The server
binds to 127.0.0.1 by default and has no authentication, so do not expose it
on a shared network.
"""

from __future__ import annotations

import json
import re
import threading
from collections.abc import Callable
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from researchforge.config import Settings
from researchforge.experiments.runner import ApprovalRequired, ExperimentRunner, UnsafeCommand
from researchforge.orchestrator import investigate
from researchforge.report import write_reports
from researchforge.runtime import AgentRuntime
from researchforge.workspace import Workspace, list_projects

STATIC = Path(__file__).parent / "static"


class NewInvestigation(BaseModel):
    idea: str = Field(min_length=10, max_length=4000)
    name: str | None = Field(default=None, max_length=60)


class RunApproval(BaseModel):
    approve: bool = False


def _dump(records) -> list:
    return [json.loads(r.model_dump_json()) for r in records]


def create_app(
    settings: Settings,
    config_path: Path | None = None,
    runtime_factory: Callable[[], AgentRuntime] | None = None,
) -> FastAPI:
    app = FastAPI(title="ResearchForge", docs_url="/api/docs")
    projects_dir = settings.resolved_projects_dir()
    projects_dir.mkdir(parents=True, exist_ok=True)
    jobs: dict[str, tuple[threading.Thread, threading.Event]] = {}
    lock = threading.Lock()

    def make_runtime() -> AgentRuntime:
        if runtime_factory is not None:
            return runtime_factory()
        from researchforge.runtime.dsh import DshHeadlessRuntime

        return DshHeadlessRuntime(settings, config_path)

    def ws_for(project: str) -> Workspace:
        path = (projects_dir / project).resolve()
        if path.parent != projects_dir or not (path / "idea.yaml").exists():
            raise HTTPException(404, f"no project {project!r}")
        return Workspace(path)

    def running(project: str) -> bool:
        job = jobs.get(project)
        return bool(job and job[0].is_alive())

    def start(ws: Workspace) -> None:
        with lock:
            if running(ws.name):
                raise HTTPException(409, "investigation already running")
            stop = threading.Event()

            def target() -> None:
                try:
                    investigate(ws, settings, make_runtime(), stop=stop)
                except Exception as exc:  # surface crashes in the UI instead of losing them in a thread
                    ws.append_event("error", message=f"investigation crashed: {type(exc).__name__}: {exc}")
                    state = ws.state()
                    if state:
                        state.status, state.error = "failed", str(exc)
                        ws.save_state(state)

            thread = threading.Thread(target=target, name=f"investigation-{ws.name}", daemon=True)
            jobs[ws.name] = (thread, stop)
            thread.start()

    @app.get("/", response_class=HTMLResponse)
    def index():
        return FileResponse(STATIC / "index.html")

    @app.get("/api/config")
    def config():
        m = settings.model
        return {
            "provider": m.custom.provider_id if m.custom else m.provider,
            "model": m.model,
            "custom_endpoint": m.custom.base_url if m.custom else None,
            "sources": settings.literature.sources,
            "experiment_backend": settings.experiments.backend,
        }

    @app.get("/api/projects")
    def projects():
        out = []
        for ws in reversed(list_projects(projects_dir)):
            state = ws.state()
            out.append({
                "name": ws.name,
                "idea": ws.raw_idea,
                "status": state.status if state else "created",
                "updated_at": state.updated_at if state else None,
                "running": running(ws.name),
            })
        return out

    @app.post("/api/projects", status_code=201)
    def create(body: NewInvestigation):
        ws = Workspace.create(projects_dir, body.idea.strip(), body.name)
        start(ws)
        return {"project": ws.name}

    @app.post("/api/projects/{project}/resume")
    def resume(project: str):
        start(ws_for(project))
        return {"project": project, "running": True}

    @app.post("/api/projects/{project}/stop")
    def stop(project: str):
        ws_for(project)
        job = jobs.get(project)
        if not job or not job[0].is_alive():
            raise HTTPException(409, "not running")
        job[1].set()
        return {"project": project, "stopping": True, "note": "stops after the current phase turn finishes"}

    @app.get("/api/projects/{project}")
    def project_state(project: str):
        ws = ws_for(project)
        state = ws.state()
        critique = ws.critique()
        return {
            "name": ws.name,
            "idea": ws.raw_idea,
            "running": running(project),
            "state": json.loads(state.model_dump_json()) if state else None,
            "counts": {
                "papers": len(ws.papers()),
                "analyses": len(ws.analyses()),
                "claims": len(ws.claims()),
                "gaps": len(ws.gaps()),
                "modifications": len(ws.modifications()),
                "plans": len(ws.plans()),
                "searches": len(ws.searches()),
            },
            "overall_status": critique.overall_status if critique else None,
            "report_ready": ws.report_path("md").exists(),
        }

    @app.get("/api/projects/{project}/events")
    def events(project: str, after: int = -1, limit: int = 400):
        evs = ws_for(project).events(after)
        return [json.loads(e.model_dump_json()) for e in evs[:limit]]

    @app.get("/api/projects/{project}/data/{kind}")
    def data(project: str, kind: str):
        ws = ws_for(project)
        single = {
            "idea": ws.idea_analysis,
            "landscape": ws.landscape,
            "critique": ws.critique,
            "no_gap": ws.no_gap,
            "investigation_plan": ws.investigation_plan,
        }
        many = {
            "papers": lambda: sorted(ws.papers(), key=lambda p: -p.relevance),
            "analyses": ws.analyses,
            "claims": ws.claims,
            "gaps": ws.gaps,
            "modifications": ws.modifications,
            "plans": ws.plans,
            "runs": ws.runs,
            "experiment_analyses": ws.experiment_analyses,
            "searches": ws.searches,
            "uncertainties": ws.uncertainties,
            "directions": ws.directions,
            "evaluations": ws.evaluations,
        }
        if kind in single:
            record = single[kind]()
            return json.loads(record.model_dump_json()) if record else None
        if kind in many:
            return _dump(many[kind]())
        raise HTTPException(404, f"unknown data kind {kind!r}")

    @app.get("/api/projects/{project}/report.{fmt}")
    def report(project: str, fmt: str, refresh: bool = False):
        ws = ws_for(project)
        if fmt not in ("md", "html"):
            raise HTTPException(404)
        if refresh or not ws.report_path(fmt).exists():
            write_reports(ws, settings)
        text = ws.report_path(fmt).read_text(encoding="utf-8")
        return HTMLResponse(text) if fmt == "html" else PlainTextResponse(text)

    @app.get("/api/projects/{project}/experiments/{plan_id}/preview")
    def preview(project: str, plan_id: str):
        ws = ws_for(project)
        plan = ws.plan(plan_id)
        if plan is None:
            raise HTTPException(404, "unknown plan")
        try:
            return ExperimentRunner(ws, settings).preview(plan)
        except (ValueError, UnsafeCommand) as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post("/api/projects/{project}/experiments/{plan_id}/run")
    def run_experiment(project: str, plan_id: str, body: RunApproval):
        ws = ws_for(project)
        key = f"{project}:experiment:{plan_id}"
        if not body.approve:
            raise HTTPException(403, "experiment execution requires explicit approval")
        with lock:
            if running(key):
                raise HTTPException(409, "experiment already running")

            def target() -> None:
                try:
                    ExperimentRunner(ws, settings).run(plan_id, approved=True)
                    write_reports(ws, settings)
                except (ApprovalRequired, UnsafeCommand, ValueError) as exc:
                    ws.append_event("error", "experiment", message=f"experiment {plan_id} not run: {exc}")
                    return
                state = ws.state()
                if state and state.status == "awaiting_approval":
                    # The loop paused for this approval: continue so it analyzes the result and re-evaluates the hypothesis.
                    ws.append_event("info", "experiment", message=f"experiment {plan_id} finished; resuming the investigation to analyze it")
                    try:
                        start(ws)
                    except HTTPException:
                        ws.append_event("warning", "experiment", message="investigation already running; resume it later to analyze the result")

            thread = threading.Thread(target=target, daemon=True)
            jobs[key] = (thread, threading.Event())
            thread.start()
        return {"plan_id": plan_id, "started": True}

    @app.get("/api/projects/{project}/eval")
    def evaluation(project: str, ground_truth: str | None = None):
        from researchforge.evaluation.metrics import DATASETS_DIR, GroundTruth, evaluate

        ws = ws_for(project)
        truth = None
        if ground_truth:
            # Only bundled datasets are selectable from the browser, never arbitrary paths.
            path = DATASETS_DIR / f"{ground_truth}.yaml"
            if not re.fullmatch(r"[a-z0-9-]{1,40}", ground_truth) or not path.exists():
                raise HTTPException(400, f"unknown bundled ground-truth dataset {ground_truth!r}")
            truth = GroundTruth.load(path)
        return evaluate(ws, truth)

    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    return app
