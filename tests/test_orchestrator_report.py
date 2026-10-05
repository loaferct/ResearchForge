import re

from support import ScriptedRuntime

from researchforge.orchestrator import investigate
from researchforge.report import build_report
from researchforge.workspace import Workspace


def no_sleep(_s):
    return None


def test_full_investigation_produces_evidence_backed_report(ws, settings):
    rt = ScriptedRuntime(settings)
    state = investigate(ws, settings, rt, sleep=no_sleep)
    assert state.status == "complete", [(p.name, p.status, p.missing) for p in state.phases]
    assert rt.actions[:2] == ["FORMALIZE", "PLAN"] and rt.actions[-1] == "PLAN_EXPERIMENT"
    # the session id from the first step is reused for every later step
    assert {sid for _, _, sid in rt.calls[1:]} == {"session-test"}
    assert "Research idea: Can request-aware" in rt.prompts[0]
    assert '"outstanding_requirements"' in rt.prompts[1] and '"uncertainties"' in rt.prompts[1]

    md = ws.report_path("md").read_text()
    for n, title in enumerate(["Executive Summary", "Original Research Idea", "Formalized Research Question", "Existing Research", "Research Landscape",
                               "Closest Existing Work", "Potential Overlap", "Potential Research Gap", "Critique", "Proposed Modifications",
                               "Recommended Experimental Design", "Experimental Results", "Remaining Uncertainty", "Suggested Next Steps", "References"], 1):
        assert f"## {n}. {title}" in md
    assert "Promising but requires experimental validation" in md
    assert "status **complete**" in md
    assert "**[Evidence]**" in md and "**[Inference]**" in md and "**[Hypothesis]**" in md
    assert "Experiment not performed" in md
    assert "does not establish novelty" in md
    assert re.search(r"Refined direction \(D00\d, REFINE_SCOPE\)", md) and "Uncertainty ledger" in md and "## Appendix C. Investigation Log" in md
    assert "**Research decision:**" in md and "Alternatives considered" in md
    assert not re.search(r"\b(is|are) (definitely |truly |clearly )?novel\b|\bnovel idea\b", md, re.I)
    assert "—" not in md
    refs = md.split("## 15. References")[1].split("## Appendix")[0]
    for pid in re.findall(r"id `([^`]+)`", refs):
        assert ws.has_paper(pid)
    assert ws.report_path("html").read_text().startswith("<!doctype html>")
    events = ws.events()
    assert [e.phase for e in events if e.kind == "phase_end"][-1] == "report"


def test_action_without_progress_is_blocked_and_investigation_continues(ws, settings):
    rt = ScriptedRuntime(settings, skip={"SYNTHESIZE"})
    state = investigate(ws, settings, rt, sleep=no_sleep)
    assert rt.actions.count("SYNTHESIZE") == settings.investigation.max_action_retries
    assert "SYNTHESIZE:" in state.blocked_actions
    # the loop moved on to other work instead of stopping
    assert "CRITIQUE" in rt.actions and "PLAN_EXPERIMENT" in rt.actions
    assert state.phase("landscape").status == "incomplete"
    assert state.status == "incomplete"
    blocked_u = [u for u in ws.uncertainties() if u.source == "controller"]
    assert blocked_u and blocked_u[0].status == "unresolved"
    md = ws.report_path("md").read_text()
    assert "Incomplete phases:** landscape" in md
    assert "_Not recorded" in md.split("## 5. Research Landscape")[1].split("## 6.")[0]


def test_runtime_failure_retries_then_aborts_and_resume_continues(ws, settings):
    slept = []
    failing = ScriptedRuntime(settings, fail_action="CRITIQUE")
    state = investigate(ws, settings, failing, sleep=slept.append)
    assert state.status == "failed" and "MISSING_CREDENTIAL" in state.error
    assert failing.actions.count("CRITIQUE") == settings.investigation.runtime_retries + 1
    assert len(slept) == settings.investigation.runtime_retries and slept[1] > slept[0]  # exponential backoff
    assert state.phase("landscape").status == "complete"
    assert ws.report_path("md").exists()  # partial report still written

    resumed = ScriptedRuntime(settings)
    state = investigate(Workspace(ws.root), settings, resumed, sleep=no_sleep)
    assert state.status == "complete"
    assert resumed.actions[0] == "CRITIQUE"  # resumed where it stopped, not from the start
    assert "FORMALIZE" not in resumed.actions and "READ" not in resumed.actions


def test_report_without_records_marks_everything_not_recorded(ws, settings):
    md = build_report(ws, settings)
    assert md.count("_Not recorded") >= 8
    assert "No papers were cited" in md
