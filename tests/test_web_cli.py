import time

import pytest
from fastapi.testclient import TestClient

from support import ScriptedRuntime

from researchforge import cli
from researchforge.orchestrator import investigate
from researchforge.web.app import create_app


@pytest.fixture
def client(settings):
    app = create_app(settings, runtime_factory=lambda: ScriptedRuntime(settings))
    return TestClient(app)


def wait_done(client, project, timeout=20):
    deadline = time.time() + timeout
    while time.time() < deadline:
        info = client.get(f"/api/projects/{project}").json()
        if not info["running"] and info["state"] and info["state"]["status"] != "running":
            return info
        time.sleep(0.1)
    raise AssertionError("investigation did not finish")


def test_web_investigation_lifecycle(client):
    assert client.get("/").status_code == 200
    assert "Investigate research idea" in client.get("/").text
    assert client.get("/static/app.js").status_code == 200
    assert client.post("/api/projects", json={"idea": "short"}).status_code == 422

    res = client.post("/api/projects", json={"idea": "Can request-aware dynamic KV-cache management reduce memory?"})
    assert res.status_code == 201
    project = res.json()["project"]
    info = wait_done(client, project)
    assert info["state"]["status"] == "complete"
    assert info["counts"]["papers"] > 0 and info["overall_status"] == "promising_needs_validation"

    events = client.get(f"/api/projects/{project}/events").json()
    assert events[0]["seq"] == 0 and any(e["kind"] == "phase_start" for e in events)
    later = client.get(f"/api/projects/{project}/events", params={"after": events[-2]["seq"]}).json()
    assert len(later) == 1

    for kind in ("idea", "papers", "analyses", "landscape", "critique", "claims", "gaps", "modifications", "plans", "searches", "runs"):
        assert client.get(f"/api/projects/{project}/data/{kind}").status_code == 200, kind
    assert client.get(f"/api/projects/{project}/data/secrets").status_code == 404
    html = client.get(f"/api/projects/{project}/report.html")
    assert html.status_code == 200 and "Executive Summary" in html.text
    assert "## 1. Executive Summary" in client.get(f"/api/projects/{project}/report.md").text

    ev = client.get(f"/api/projects/{project}/eval", params={"ground_truth": "kv-cache"}).json()
    assert ev["retrieval"]["relevant_in_ground_truth"] == 11
    assert client.get(f"/api/projects/{project}/eval", params={"ground_truth": "../../etc/passwd"}).status_code == 400

    assert client.post(f"/api/projects/{project}/experiments/E001/run", json={"approve": False}).status_code == 403
    assert client.get(f"/api/projects/{project}/experiments/E001/preview").status_code == 400  # design-only plan
    assert client.post(f"/api/projects/{project}/stop").status_code == 409


def test_web_rejects_path_traversal(client):
    assert client.get("/api/projects/..%2F..%2Fetc").status_code == 404
    assert client.get("/api/projects/nonexistent").status_code == 404


def test_cli_status_report_list_and_experiment_preview(ws, settings, tmp_path, capsys, monkeypatch):
    investigate(ws, settings, ScriptedRuntime(settings))
    cfg = tmp_path / "rf.toml"
    cfg.write_text(f'projects_dir = "{settings.projects_dir}"\nlog_level = "WARNING"\n')
    assert cli.main(["--config", str(cfg), "status", ws.name]) == 0
    out = capsys.readouterr().out
    assert "✓ Phase 1 — Formalizing idea" in out and "complete" in out
    assert cli.main(["--config", str(cfg), "list"]) == 0
    assert ws.name in capsys.readouterr().out
    assert cli.main(["--config", str(cfg), "report", ws.name]) == 0
    assert "## 15. References" in capsys.readouterr().out
    assert cli.main(["--config", str(cfg), "experiment", ws.name]) == 0
    assert "E001" in capsys.readouterr().out
    assert cli.main(["--config", str(cfg), "experiment", ws.name, "--run", "E001"]) == 2  # design only
    assert cli.main(["--config", str(cfg), "status", "missing-project"]) == 2
    assert cli.main(["--config", str(cfg), "eval", ws.name, "--ground-truth", "kv-cache", "--k", "5"]) == 0
    assert '"precision"' in capsys.readouterr().out


def test_cli_experiment_requires_approve_flag(ws, settings, tmp_path, capsys):
    from test_experiments_eval import arm, make_plan

    make_plan(ws, [arm("base", "baseline")])
    cfg = tmp_path / "rf.toml"
    cfg.write_text(f'projects_dir = "{settings.projects_dir}"\nlog_level = "WARNING"\n')
    assert cli.main(["--config", str(cfg), "experiment", ws.name, "--run", "E001"]) == 3
    assert "Nothing was executed" in capsys.readouterr().out
    assert ws.runs() == []
    assert cli.main(["--config", str(cfg), "experiment", ws.name, "--run", "E001", "--approve"]) == 0
    assert "Experiment status: PASSED" in capsys.readouterr().out
    assert len(ws.runs()) == 1
