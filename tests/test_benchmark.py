"""Benchmark controls (docs/paper/research_plan.md): date cutoff, abstract corruption, ablation switches, TPAD scoring."""

import asyncio
import json
from datetime import date
from urllib.parse import unquote_plus

import pytest

import support
from support import FakeApis, ScriptedRuntime, make_toolkit

from researchforge.evaluation.tpad import TpadDataset, condition_settings, contamination, score_run, summarize
from researchforge.literature import controls
from researchforge.literature.fulltext import pdf_url_for
from researchforge.orchestrator import investigate, new_state
from researchforge.schemas import Paper
from researchforge.toolkit import ToolError


def run(coro):
    return asyncio.run(coro)


def with_literature(settings, **kw):
    return settings.model_copy(update={"literature": settings.literature.model_copy(update=kw)})


def with_investigation(settings, **kw):
    return settings.model_copy(update={"investigation": settings.investigation.model_copy(update=kw)})


@pytest.fixture(autouse=True)
def reset_verdicts():
    support.CHALLENGE_VERDICTS.clear()
    yield
    support.CHALLENGE_VERDICTS.clear()


# ---------------------------------------------------------------- publication-date cutoff


def test_visibility_rule_is_conservative():
    cutoff = date(2024, 5, 1)
    p = lambda **kw: Paper(id="x", title="t", source="arxiv", **kw)  # noqa: E731
    assert controls.visible(p(published="2024-04-30"), cutoff)
    assert not controls.visible(p(published="2024-05-01"), cutoff)
    assert controls.visible(p(year=2023), cutoff)
    assert not controls.visible(p(year=2024), cutoff)  # same year, no date: could be after the cutoff
    assert not controls.visible(p(), cutoff)
    assert controls.visible(p(), None)


def test_cutoff_is_sent_to_every_api_and_enforced_on_results(ws, settings):
    apis = FakeApis()
    tk = make_toolkit(ws, with_literature(settings, published_before=date(2024, 5, 1)), apis)
    res = run(tk.search_papers("kv cache eviction"))
    urls = [unquote_plus(u) for u in apis.calls]
    assert any("submittedDate:[190001010000 TO 202404302359]" in u for u in urls if "arxiv" in u)
    assert any("to_publication_date:2024-04-30" in u for u in urls if "openalex" in u)
    assert any("publicationDateOrYear=:2024-04-30" in u for u in urls if "semanticscholar" in u)
    assert any("until-pub-date:2024-04-30" in u for u in urls if "crossref" in u)
    # The fakes ignore the filters, so the toolkit must enforce the cutoff itself.
    ids = {r["id"] for r in res["results"]}
    assert ids == {"arxiv:9999.00001", "arxiv:9999.00002", "arxiv:9999.00003", "doi:10.9999/test.0", "doi:10.9999/test.1"}
    assert ws.paper("arxiv:9999.00001").published == "2024-02-15"
    hidden = controls.read_ledger(ws.root, "hidden.jsonl")
    assert hidden and any(h["published"] == "2024-05-15" for rec in hidden for h in rec["papers"])
    assert "cutoff" not in str(res)  # the model is not told
    with pytest.raises(ToolError, match="GitHub tools are unavailable"):
        run(tk.search_github("kv cache"))


def test_cutoff_pins_arxiv_full_text_to_first_version():
    paper = Paper(id="arxiv:9999.00001", arxiv_id="9999.00001", title="t", source="arxiv")
    assert pdf_url_for(paper) == "https://arxiv.org/pdf/9999.00001"
    assert pdf_url_for(paper, first_version=True) == "https://arxiv.org/pdf/9999.00001v1"


def test_merge_keeps_the_earliest_publication_date():
    from researchforge.literature.merge import merge_into
    a = Paper(id="arxiv:1", arxiv_id="1", title="Same Title For Both Records", source="openalex", published="2024-09-01")
    b = Paper(id="arxiv:1", arxiv_id="1", title="Same Title For Both Records", source="arxiv", published="2024-03-01")
    assert merge_into(a, b).published == "2024-03-01"
    assert merge_into(Paper(id="arxiv:1", title="Same Title For Both Records", source="s2"), b).published == "2024-03-01"


# ---------------------------------------------------------------- abstract corruption and the integrity switch


def corrupted_search(ws, settings, integrity):
    s = with_literature(settings, sources=["arxiv"], corrupt_abstracts=1.0, corruption_seed=7, integrity_checks=integrity)
    tk = make_toolkit(ws, s, FakeApis())
    run(tk.search_papers("kv cache eviction"))
    return tk


def test_corruption_is_logged_and_deterministic(ws, settings, tmp_path):
    tk = corrupted_search(ws, settings, integrity=True)
    ledger = controls.read_ledger(ws.root, "corruptions.jsonl")
    assert ledger and all(r["injected_abstract"] != r["original_abstract"] for r in ledger)
    paper = ws.paper("arxiv:9999.00001")
    assert paper.abstract == next(r["injected_abstract"] for r in ledger if "arxiv:9999.00001" in r["keys"])
    from researchforge.workspace import Workspace
    other = Workspace.create(tmp_path / "other", "same idea")
    corrupted_search(other, settings, integrity=True)
    assert [r["donor_title"] for r in controls.read_ledger(other.root, "corruptions.jsonl")] == [r["donor_title"] for r in ledger]


def quote_injected(tk):
    abstract = tk.ws.paper("arxiv:9999.00001").abstract
    return tk.record_claim(statement="s", kind="evidence", confidence="medium",
                           evidence=[{"paper_id": "arxiv:9999.00001", "quote": abstract[:60], "support": "direct"}])


def test_integrity_checks_block_corrupted_evidence(ws, settings):
    tk = corrupted_search(ws, settings, integrity=True)
    assert ws.paper("arxiv:9999.00001").metadata_warnings  # injected abstract never names TestEvict
    with pytest.raises(ToolError, match="flagged"):
        quote_injected(tk)
    assert contamination(ws)["contaminated_evidence_items"] == 0


def test_without_integrity_checks_corrupted_evidence_is_counted(ws, settings):
    tk = corrupted_search(ws, settings, integrity=False)
    assert not ws.paper("arxiv:9999.00001").metadata_warnings
    quote_injected(tk)
    c = contamination(ws)
    assert c["contaminated_evidence_items"] == 1 and c["contamination_rate"] == 1.0
    assert c["corrupted_papers_flagged"] == 0


# ---------------------------------------------------------------- ablation switches


def test_recritique_switch_off_keeps_the_stale_critique(ws, settings):
    support.CHALLENGE_VERDICTS["critique"] = "weakened"
    s = with_investigation(settings, recritique_on_contradiction=False)
    state = investigate(ws, s, ScriptedRuntime(s), sleep=lambda _s: None)
    assert not any("predates contradicting evidence" in d.reason for d in state.decisions)


def test_challenge_switch_off_raises_no_challenges(ws, settings):
    s = with_investigation(settings, challenge_conclusions=False)
    rt = ScriptedRuntime(s)
    investigate(ws, s, rt, sleep=lambda _s: None)
    assert "CHALLENGE" not in rt.actions and "INVESTIGATE_GAP" not in rt.actions


def test_pipeline_mode_runs_a_fixed_sequence_with_extra_rounds(ws, settings):
    s = with_investigation(settings, controller_mode="pipeline", pipeline_extra_searches=1)
    rt = ScriptedRuntime(s)
    state = investigate(ws, s, rt, sleep=lambda _s: None)
    assert not set(rt.actions) & {"CHALLENGE", "INVESTIGATE_GAP", "COMPARE", "VERIFY"}
    first_critique = rt.actions.index("CRITIQUE")
    assert rt.actions[first_critique + 1: first_critique + 4] == ["SEARCH", "READ", "CRITIQUE"]
    assert rt.actions[-2:] == ["REFINE", "PLAN_EXPERIMENT"]
    assert not any(u.source == "controller" for u in ws.uncertainties())
    assert state.research_decision is not None and state.finalize_reason == "Fixed pipeline complete."


# ---------------------------------------------------------------- TPAD items and scoring


DATASET = """
name: tpad-test
items:
  - id: T1
    idea: Evict cached keys and values by page, choosing pages by their expected use.
    realising: {title: "TestPaged: Paged KV Cache Memory Management for Serving", arxiv: "9999.00004", published: 2024-05-15}
    prior_work:
      - {title: "TestEvict: Heavy-Hitter KV Cache Eviction", arxiv: "9999.00001", published: 2024-02-15}
      - {title: "TestSnap: Observation-Window KV Selection", arxiv: "9999.00003", published: 2024-04-15}
      - {title: "A Paper Nobody Retrieves", arxiv: "9999.99999", published: 2023-01-01}
"""


def test_dataset_rejects_prior_work_after_the_realising_paper(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(DATASET.replace("published: 2023-01-01", "published: 2025-01-01"))
    with pytest.raises(ValueError, match="must predate"):
        TpadDataset.load(bad)


def test_tpad_conditions_and_scoring(tmp_path, settings):
    from researchforge.workspace import Workspace
    path = tmp_path / "tpad.yaml"
    path.write_text(DATASET)
    item = TpadDataset.load(path).items[0]
    scores = []
    for condition in ("scooped", "prepub"):
        s = condition_settings(settings, item, condition)
        assert s.literature.published_before == (date(2024, 5, 15) if condition == "prepub" else None)
        ws = Workspace.create(tmp_path / condition, item.idea)
        tk = make_toolkit(ws, s, FakeApis())
        run(tk.search_papers("kv cache eviction"))
        tk.record_claim(statement="Paged management exists", kind="evidence", confidence="medium",
                        evidence=[{"paper_id": "arxiv:9999.00001", "quote": "keeps heavy-hitter tokens", "support": "direct"}])
        state = new_state(ws, s)
        state.research_decision = "ALREADY_WELL_EXPLORED" if condition == "scooped" else "PROMISING"
        ws.save_state(state)
        scores.append(score_run(ws, item, condition))
    scooped, prepub = scores
    assert scooped["realising_retrieved"] and scooped["scoop_detected"] and not scooped["realising_cited_verified"]
    assert prepub["leak"] is False and not prepub["realising_retrieved"] and not prepub["false_scoop_candidate"]
    assert prepub["prior_work_recall"] == round(2 / 3, 3) and prepub["prior_work_missing"] == ["A Paper Nobody Retrieves"]
    assert prepub["prior_work_cited_verified"] == round(1 / 3, 3)
    summary = summarize(scores)
    assert summary["scooped"]["scoop_detection"] == 1.0 and summary["prepub"]["excluded_for_leak"] == 0


def test_dotenv_loads_missing_variables_only(tmp_path):
    from researchforge.config import load_dotenv
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nOLLAMA_API_KEY='abc'\nexport OTHER=1\nEMPTY=\nALREADY=new\n")
    environ = {"ALREADY": "old"}
    assert load_dotenv(env_file, environ) == ["OLLAMA_API_KEY", "OTHER"]
    assert environ == {"ALREADY": "old", "OLLAMA_API_KEY": "abc", "OTHER": "1"}
    assert load_dotenv(tmp_path / "missing", environ) == []


def test_bench_runs_the_matrix_resumes_and_scores(tmp_path, settings):
    from researchforge.evaluation.bench import BenchSpec, load_results, run_bench, score_bench
    (tmp_path / "tpad.yaml").write_text(DATASET)
    (tmp_path / "spec.yaml").write_text("dataset: tpad.yaml\nout: out\nsystems: [full, pipe]\nconditions: [scooped]\n"
                                        "settings: {investigation: {max_iterations: 30}}\n")
    spec = BenchSpec.load(tmp_path / "spec.yaml")
    seen = []

    def fake_investigate(ws, s, runtime):
        seen.append((ws.root.name, s.investigation.controller_mode, s.investigation.max_iterations,
                     json.loads((ws.root / "settings.json").read_text())["investigation"]["controller_mode"]))
        state = new_state(ws, s)
        state.status, state.research_decision = "complete", "PROMISING"
        ws.save_state(state)

    rows = run_bench(spec, settings, lambda s, cfg: None, workers=2, investigate_fn=fake_investigate, progress=lambda m: None)
    assert sorted(r["key"] for r in rows) == ["T1__scooped__full__s0", "T1__scooped__pipe__s0"]
    assert sorted(seen) == [("T1__scooped__full__s0", "adaptive", 30, "adaptive"), ("T1__scooped__pipe__s0", "pipeline", 30, "pipeline")]
    assert run_bench(spec, settings, lambda s, cfg: None, investigate_fn=fake_investigate, progress=lambda m: None) == []
    assert len(load_results(tmp_path / "out")) == 2
    assert score_bench(spec)["pipe"]["scooped"]["runs"] == 1


def test_first_assessment_is_challenged_right_after_the_critique(ws, settings):
    rt = ScriptedRuntime(settings)
    investigate(ws, settings, rt, sleep=lambda _s: None)
    first_critique = rt.actions.index("CRITIQUE")
    assert rt.actions[first_critique + 1] == "CHALLENGE"
    s = with_investigation(settings, challenge_conclusions=False)
    rt2 = ScriptedRuntime(s)
    from researchforge.workspace import Workspace
    investigate(Workspace.create(ws.root.parent / "other", ws.raw_idea), s, rt2, sleep=lambda _s: None)
    assert "CHALLENGE" not in rt2.actions


def test_turn_timeout_stops_child_processes_that_hold_the_output_open(ws, settings):
    import time as _time
    from researchforge.runtime.dsh import DshHeadlessRuntime
    s = settings.model_copy(update={"dsh": settings.dsh.model_copy(update={"phase_timeout_s": 1.0})})
    # Like `npx` -> dsh -> MCP server: the launcher's child keeps stdout open after the launcher is killed.
    script = ["sh", "-c", "(while true; do echo '{}'; sleep 0.2; done) & wait", "fake-dsh"]
    started = _time.monotonic()
    out = DshHeadlessRuntime(s, command=script).run_phase(ws, "prompt", phase="t", session_id=None, on_event=lambda *_: None)
    assert _time.monotonic() - started < 10
    assert not out.ok and "exceeded" in (out.error or "")
