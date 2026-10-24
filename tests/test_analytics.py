from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from support import ScriptedRuntime
from researchforge.analytics import (
    compute_all_graph_data,
    compute_epistemic_grounding,
    compute_landscape_network,
    compute_novelty_profile,
    compute_similarity_matrix,
    compute_timeline_trends,
)
from researchforge.orchestrator import investigate
from researchforge.web.app import create_app
from researchforge.workspace import Workspace


@pytest.fixture
def investigated_ws(ws, settings):
    investigate(ws, settings, ScriptedRuntime(settings))
    return ws


def test_analytics_computation(investigated_ws):
    data = compute_all_graph_data(investigated_ws)
    assert data["project"] == investigated_ws.name
    assert "novelty" in data
    assert "similarity" in data
    assert "network" in data
    assert "timeline" in data
    assert "epistemic" in data

    # Novelty profile
    novelty = data["novelty"]
    assert 0 <= novelty["composite_novelty_score"] <= 100
    assert len(novelty["dimensions"]) == 6
    assert any(d["axis"] == "Problem Novelty" for d in novelty["dimensions"])
    assert any(d["axis"] == "Method Distinction" for d in novelty["dimensions"])

    # Similarity matrix
    sim = data["similarity"]
    assert sim["total_analyzed"] >= 0
    assert "quadrant_counts" in sim
    for p in sim["papers"]:
        assert 0.0 <= p["problem_overlap"] <= 1.0
        assert 0.0 <= p["method_overlap"] <= 1.0
        assert 0.0 <= p["evaluation_overlap"] <= 1.0
        assert 0.0 <= p["composite_similarity"] <= 1.0
        assert p["quadrant"] in ("direct_overlap", "alternative_solutions", "transferable_methods", "peripheral")

    # Network topology
    net = data["network"]
    assert any(n["id"] == "idea" for n in net["nodes"])
    assert len(net["nodes"]) >= 1

    # Timeline
    tl = data["timeline"]
    assert "timeline" in tl

    # Epistemic
    ep = data["epistemic"]
    assert "kinds" in ep
    assert "evidence_verification" in ep


def test_web_graph_data_endpoint(investigated_ws, settings):
    app = create_app(settings)
    client = TestClient(app)

    res = client.get(f"/api/projects/{investigated_ws.name}/graph_data")
    assert res.status_code == 200
    body = res.json()
    assert body["project"] == investigated_ws.name
    assert "novelty" in body
    assert "similarity" in body

    res2 = client.get(f"/api/projects/{investigated_ws.name}/data/graph_data")
    assert res2.status_code == 200
    assert res2.json()["project"] == investigated_ws.name
