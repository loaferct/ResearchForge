"""Temporal Prior-Art Detection (TPAD): items, run conditions and scoring.

Design: docs/paper/research_plan.md §4-5. An item is an idea whose realisation (the *realising paper*) was
published on a known date, plus a few closest prior works. Each item is run in two conditions:

* ``scooped``: the literature is visible up to today, so the right outcome is to find the realising paper and
  conclude the idea is already explored;
* ``prepub``: works published on or after the realising paper's date are hidden, so the realising paper must
  not be found, and an "already explored" verdict needs human adjudication.

Scores are computed from the workspace records (papers, claims, research decision, ledgers), never from report
prose.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from researchforge.config import Settings
from researchforge.evaluation.metrics import loop_metrics
from researchforge.evidence import quote_in
from researchforge.literature import controls
from researchforge.literature.merge import paper_keys, title_key
from researchforge.schemas import Paper
from researchforge import _rust
from researchforge.workspace import Workspace

Condition = Literal["scooped", "prepub"]
CONDITIONS: tuple[Condition, ...] = ("scooped", "prepub")
SCOOP_VERDICT = "ALREADY_WELL_EXPLORED"


class PaperRef(BaseModel):
    title: str
    arxiv: str | None = None
    doi: str | None = None
    published: date | None = Field(default=None, description="First public version (arXiv v1 date for arXiv papers).")

    def matches(self, paper: Paper) -> bool:
        if self.arxiv and paper.arxiv_id == self.arxiv:
            return True
        if self.doi and paper.doi and paper.doi.lower() == self.doi.lower():
            return True
        return title_key(self.title) == title_key(paper.title)


class TpadItem(BaseModel):
    id: str
    idea: str = Field(description="The proposal the agent receives; must not name the realising paper, its method name or its results.")
    realising: PaperRef
    prior_work: list[PaperRef] = Field(default_factory=list, description="Closest earlier works, chosen by a human from the realising paper's references.")
    domain: str = ""
    verification: str = Field(default="", description="How and when the references and the paraphrase were checked, and by whom.")


class TpadDataset(BaseModel):
    name: str
    description: str = ""
    items: list[TpadItem]

    @classmethod
    def load(cls, path: str | Path) -> "TpadDataset":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        ds = cls.model_validate(data)
        for item in ds.items:
            if item.realising.published is None:
                raise ValueError(f"item {item.id}: realising.published is required (the prepub cutoff)")
            late = [w.title for w in item.prior_work if w.published and w.published >= item.realising.published]
            if late:
                raise ValueError(f"item {item.id}: prior work must predate the realising paper: {late}")
        return ds


def condition_settings(base: Settings, item: TpadItem, condition: Condition) -> Settings:
    """Settings for one run: the cutoff for ``prepub``, otherwise unchanged."""
    lit = base.literature.model_copy(update={"published_before": item.realising.published if condition == "prepub" else None})
    return base.model_copy(update={"literature": lit})


def _find(ws: Workspace, ref: PaperRef) -> Paper | None:
    return next((p for p in ws.papers() if ref.matches(p)), None)


def _verified_cites(ws: Workspace) -> dict[str, int]:
    """paper id -> number of claims citing it with verified evidence."""
    if _rust.is_available():
        res = _rust.verified_cites(ws.root)
        if res is not None:
            return res
    counts: dict[str, int] = {}
    for c in ws.claims():
        for pid in {e.paper_id for e in c.evidence if e.paper_id and e.verified}:
            counts[pid] = counts.get(pid, 0) + 1
    return counts


def contamination(ws: Workspace) -> dict:
    """Verified evidence whose quote came from an injected (wrong) abstract, per the corruption ledger."""
    ledger = controls.read_ledger(ws.root, "corruptions.jsonl")
    by_key: dict[str, list[dict]] = {}
    for rec in ledger:
        for k in rec["keys"]:
            by_key.setdefault(k, []).append(rec)
    total = contaminated = 0
    examples = []
    for c in ws.claims():
        for e in c.evidence:
            if not (e.paper_id and e.verified and e.quote):
                continue
            total += 1
            paper = ws.paper(e.paper_id)
            recs = [r for k in (paper_keys(paper) if paper else []) for r in by_key.get(k, [])]
            if any(quote_in(e.quote, r["injected_abstract"]) and not quote_in(e.quote, r["original_abstract"]) for r in recs):
                contaminated += 1
                examples.append({"claim": c.id, "paper_id": e.paper_id, "quote": e.quote[:160]})
    corrupted_ids = {p.id for p in ws.papers() if any(k in by_key for k in paper_keys(p))}
    return {
        "corrupted_records_injected": len(ledger),
        "corrupted_papers_in_workspace": len(corrupted_ids),
        "corrupted_papers_flagged": sum(1 for p in ws.papers() if p.id in corrupted_ids and p.metadata_warnings),
        "verified_evidence_items": total,
        "contaminated_evidence_items": contaminated,
        "contamination_rate": round(contaminated / total, 4) if total else None,
        "examples": examples[:10],
    }


def score_run(ws: Workspace, item: TpadItem, condition: Condition) -> dict:
    state = ws.state()
    verdict = state.research_decision if state else None
    cites = _verified_cites(ws)
    analysed = {a.paper_id for a in ws.analyses()}
    realising = _find(ws, item.realising)
    realising_cited = bool(realising and cites.get(realising.id))
    prior = [(ref, _find(ws, ref)) for ref in item.prior_work]
    prior_found = [p for _, p in prior if p]
    loop = loop_metrics(ws)
    result: dict = {
        "item": item.id,
        "condition": condition,
        "status": state.status if state else None,
        "verdict": verdict,
        "verdict_basis": state.research_decision_basis if state else None,
        "realising_retrieved": realising is not None,
        "realising_analysed": bool(realising and realising.id in analysed),
        "realising_cited_verified": realising_cited,
        "prior_work_recall": round(len(prior_found) / len(prior), 3) if prior else None,
        "prior_work_cited_verified": round(sum(1 for p in prior_found if cites.get(p.id)) / len(prior), 3) if prior else None,
        "prior_work_missing": [ref.title for ref, p in prior if p is None],
        "cost": {k: loop[k] for k in ("iterations", "tool_calls", "tokens", "elapsed_s", "searches", "papers_retrieved", "papers_read")},
        "process": {k: loop[k] for k in ("challenges", "contradictory_evidence_found", "direction_changes", "uncertainties_created_by_controller")},
    }
    if condition == "scooped":
        # Detected: the verdict says the idea is explored, or the agent changed course with the realising paper as verified evidence.
        result["scoop_detected"] = verdict == SCOOP_VERDICT or (verdict == "NEEDS_MODIFICATION" and realising_cited)
    else:
        # The cutoff must have hidden the realising paper; if it is in the workspace, the run is invalid.
        result["leak"] = realising is not None
        result["false_scoop_candidate"] = verdict == SCOOP_VERDICT  # needs human adjudication (research_plan.md §5.2)
    if controls.read_ledger(ws.root, "corruptions.jsonl"):
        result["contamination"] = contamination(ws)
    return result


def summarize(scores: list[dict]) -> dict:
    """Rates per condition over a list of ``score_run`` results (one system, one backbone)."""
    out: dict = {}
    for cond in CONDITIONS:
        rows = [s for s in scores if s["condition"] == cond and not s.get("leak")]
        if not rows:
            continue
        rate = lambda key: round(sum(1 for r in rows if r.get(key)) / len(rows), 3)  # noqa: E731
        recalls = [r["prior_work_recall"] for r in rows if r["prior_work_recall"] is not None]
        out[cond] = {
            "runs": len(rows),
            "excluded_for_leak": sum(1 for s in scores if s["condition"] == cond and s.get("leak")),
            "realising_retrieved": rate("realising_retrieved"),
            "realising_cited_verified": rate("realising_cited_verified"),
            "prior_work_recall_mean": round(sum(recalls) / len(recalls), 3) if recalls else None,
            "mean_tool_calls": round(sum(r["cost"]["tool_calls"] for r in rows) / len(rows), 1),
            **({"scoop_detection": rate("scoop_detected")} if cond == "scooped" else {"false_scoop_candidates": rate("false_scoop_candidate")}),
        }
    return out
