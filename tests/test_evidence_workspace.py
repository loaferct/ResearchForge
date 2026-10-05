import pytest

from researchforge.config import load_settings
from researchforge.evidence import EvidenceError, grounding, normalize, quote_in, validate_claim
from researchforge.schemas import Claim, EvidenceItem, Paper
from researchforge.workspace import Workspace, slugify


def add_paper(ws, pid="arxiv:9999.00001", abstract="We reduce KV cache memory by 5x while preserving accuracy on long-context tasks."):
    ws.save_paper(Paper(id=pid, title="T", source="arxiv", sources=["arxiv"], abstract=abstract))


def test_normalize_handles_pdf_artifacts():
    assert normalize("mem-\nory  “cache” — fast") == 'memory "cache" - fast'
    assert quote_in("reduce KV cache memory by 5x", "We reduce KV cache\nmemory by 5x while")
    assert quote_in("We reduce KV cache ... preserving accuracy on long-context", "We reduce KV cache memory by 5x while preserving accuracy on long-context tasks.")
    assert not quote_in("short", "short text")  # below minimum quote length
    assert not quote_in("reduce KV cache memory by 10x", "We reduce KV cache memory by 5x")


def test_direct_support_requires_verified_quote(ws):
    add_paper(ws)
    bad = Claim(statement="s", kind="evidence", confidence="high", evidence=[EvidenceItem(paper_id="arxiv:9999.00001", quote="reduces memory by 10x on every task", support="direct")])
    with pytest.raises(EvidenceError, match="could not be verified"):
        validate_claim(ws, bad)
    good = bad.model_copy(update={"evidence": [EvidenceItem(paper_id="arxiv:9999.00001", quote="reduce KV cache memory by 5x", support="direct")]})
    claim, warnings = validate_claim(ws, good)
    assert claim.evidence[0].verified and not warnings


def test_unknown_paper_and_kind_rules(ws):
    add_paper(ws)
    with pytest.raises(EvidenceError, match="never retrieved"):
        validate_claim(ws, Claim(statement="s", kind="inference", confidence="low", evidence=[EvidenceItem(paper_id="arxiv:0000.00000")]))
    with pytest.raises(EvidenceError, match="needs at least one verified quote"):
        validate_claim(ws, Claim(statement="s", kind="evidence", confidence="low", evidence=[EvidenceItem(paper_id="arxiv:9999.00001", support="indirect")]))
    with pytest.raises(EvidenceError, match="must list the evidence"):
        validate_claim(ws, Claim(statement="s", kind="inference", confidence="low"))
    claim, _ = validate_claim(ws, Claim(statement="s", kind="hypothesis", confidence="low"))
    assert claim.evidence == []


def test_unverified_indirect_quote_is_kept_with_warning(ws):
    add_paper(ws)
    claim, warnings = validate_claim(ws, Claim(statement="s", kind="inference", confidence="low", evidence=[EvidenceItem(paper_id="arxiv:9999.00001", quote="a paraphrase that is not in the text", support="indirect")]))
    assert not claim.evidence[0].verified and warnings


def test_grounding_excludes_hypotheses():
    claims = [
        Claim(id="C1", statement="a", kind="evidence", confidence="high", evidence=[EvidenceItem(paper_id="p", verified=True)]),
        Claim(id="C2", statement="b", kind="inference", confidence="low", evidence=[EvidenceItem(paper_id="p")]),
        Claim(id="C3", statement="c", kind="hypothesis", confidence="low", evidence=[EvidenceItem(paper_id="p", verified=True)]),
    ]
    g = grounding(claims)
    assert (g.grounded, g.total, g.ungrounded_ids) == (1, 2, ["C2"])


def test_workspace_layout_ids_events_and_reopen(settings):
    projects = settings.resolved_projects_dir()
    ws = Workspace.create(projects, "An idea about caches", name="My Project!")
    assert ws.name == "my-project"
    for sub in ("papers/text", "evidence/claims", "experiments/plans", "reports", "cache/http"):
        assert (ws.root / sub).is_dir()
    again = Workspace.create(projects, "Another", name="My Project!")
    assert again.root != ws.root
    assert ws.allocate_id(ws.root / "evidence" / "claims", "C") == "C001"
    assert ws.allocate_id(ws.root / "evidence" / "claims", "C") == "C002"
    assert ws.claims() == []  # placeholders are not records
    e1 = ws.append_event("info", message="a")
    e2 = ws.append_event("tool_call", "literature", tool="search_papers")
    assert (e1.seq, e2.seq) == (0, 1)
    assert [e.seq for e in ws.events(after=0)] == [1]
    assert Workspace.open(projects, "my-project").raw_idea == "An idea about caches"
    with pytest.raises(FileNotFoundError):
        Workspace.open(projects, "missing")
    assert slugify("  Hello, World!  ") == "hello-world"


def test_settings_file_and_env(tmp_path):
    cfg = tmp_path / "rf.toml"
    cfg.write_text('[model]\nprovider = "p"\nmodel = "m"\n[model.custom]\nprovider_id = "local-vllm"\nbase_url = "http://localhost:8000/v1"\nmodels = ["Qwen/Qwen3-32B"]\napi_key_env = "LOCAL_KEY"\n[literature]\nmax_results_per_source = 5\n')
    s = load_settings(cfg, env={"RF_MODEL": "Qwen/Qwen3-32B", "RF_DSH_COMMAND": "node /x/dsh.js"})
    assert s.model.model == "Qwen/Qwen3-32B" and s.model.provider == "p"
    assert s.model.custom.provider_id == "local-vllm"
    assert s.literature.max_results_per_source == 5
    assert s.dsh.resolved_command() == ["node", "/x/dsh.js"]
