"""Source-integrity checks (mismatched abstracts) and critique revision after contradicting evidence."""

import pytest

import support
from support import ScriptedRuntime

from researchforge.evidence import EvidenceError, validate_claim
from researchforge.literature.merge import consistency_warnings, merge_into, refresh_warnings, title_fit
from researchforge.orchestrator import investigate
from researchforge.schemas import Claim, EvidenceItem, Paper

H2O_TITLE = "H$_2$O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models"
# The abstract OpenAlex returned for arXiv 2306.14048 on 2026-09-28 (it belongs to a different system).
WRONG_ABSTRACT = ("Hyde-IKV is a dynamic management system for the Key-Value (KV) cache in Small Language Models (SLMs). "
                  "It tackles the memory bottleneck of long-context inference by intelligently prioritizing and compressing the stored context.")
RIGHT_ABSTRACT = ("We introduce Heavy Hitter Oracle (H2O), a KV cache eviction policy that dynamically retains a balance of recent and "
                  "heavy-hitter tokens, reducing the memory footprint of generative inference in large language models.")


def paper(source, abstract):
    return Paper(id="arxiv:2306.14048", arxiv_id="2306.14048", title=H2O_TITLE, source=source, sources=[source], abstract=abstract, abstract_source=source)


def test_abstract_that_never_names_the_method_is_flagged():
    flagged = refresh_warnings(paper("openalex", WRONG_ABSTRACT))
    assert flagged.metadata_warnings and "never mentions 'H$_2$O'" in flagged.metadata_warnings[0]
    assert consistency_warnings(paper("arxiv", RIGHT_ABSTRACT)) == []
    no_name = Paper(id="x", title="Efficient Streaming Language Models with Attention Sinks", source="arxiv", abstract="unrelated text")
    assert consistency_warnings(no_name) == []  # no method-name prefix: no single-source judgement


def test_disagreeing_sources_keep_the_abstract_that_matches_the_title():
    merged = merge_into(paper("openalex", WRONG_ABSTRACT), paper("arxiv", RIGHT_ABSTRACT), keep_id=True)
    assert merged.abstract == RIGHT_ABSTRACT and merged.abstract_source == "arxiv"
    assert any("disagree" in w for w in merged.metadata_warnings)
    assert title_fit(H2O_TITLE, RIGHT_ABSTRACT) > title_fit(H2O_TITLE, WRONG_ABSTRACT)
    # agreeing sources: no warning, and the longer abstract wins only when it fits the title at least as well
    same = merge_into(paper("arxiv", RIGHT_ABSTRACT), paper("semantic_scholar", RIGHT_ABSTRACT + " Code is available."), keep_id=True)
    assert same.metadata_warnings == []


def test_flagged_abstract_cannot_supply_direct_evidence(ws):
    ws.save_paper(refresh_warnings(paper("openalex", WRONG_ABSTRACT)))
    quote = "dynamic management system for the Key-Value (KV) cache"
    with pytest.raises(EvidenceError, match="flagged"):
        validate_claim(ws, Claim(statement="s", kind="evidence", confidence="high",
                                 evidence=[EvidenceItem(paper_id="arxiv:2306.14048", quote=quote, support="direct")]))
    claim, warnings = validate_claim(ws, Claim(statement="s", kind="inference", confidence="low",
                                               evidence=[EvidenceItem(paper_id="arxiv:2306.14048", quote=quote, support="indirect")]))
    assert not claim.evidence[0].verified and "flagged abstract" in claim.evidence[0].verification_note
    # the paper's own full text can still confirm a quote
    ws.save_paper_text("arxiv:2306.14048", "[[page 1]]\n" + RIGHT_ABSTRACT)
    claim, _ = validate_claim(ws, Claim(statement="s", kind="evidence", confidence="high",
                                        evidence=[EvidenceItem(paper_id="arxiv:2306.14048", quote="a KV cache eviction policy that dynamically retains", support="direct")]))
    assert claim.evidence[0].verified and claim.evidence[0].verification_note == "quote found in full text"


def test_critique_is_revised_after_contradicting_evidence(ws, settings):
    support.CHALLENGE_VERDICTS["critique"] = "weakened"
    try:
        rt = ScriptedRuntime(settings)
        state = investigate(ws, settings, rt, sleep=lambda s: None)
    finally:
        support.CHALLENGE_VERDICTS.clear()
    actions = rt.actions
    first_challenge = actions.index("CHALLENGE")
    assert actions[first_challenge + 1] == "CRITIQUE"  # stale assessment revised right after the contradiction
    recritique = next(d for d in state.decisions if d.action == "CRITIQUE" and "predates contradicting evidence" in d.reason)
    assert "weakened" in recritique.reason
    assert state.critiques == 2 and actions.count("CRITIQUE") == 2
    assert state.status == "complete"
