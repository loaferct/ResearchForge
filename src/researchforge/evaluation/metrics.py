"""Measure an investigation instead of judging its prose.

* Literature retrieval: precision@k and recall@k against a curated set of
  relevant papers (``evaluation/datasets/*.yaml``), for two rankings: the
  heuristic retrieval ranking and the agent's own relevance tiers.
* Claim grounding: share of evidence/inference claims with a verified source.
* Experiment planning: presence of baselines, metrics, controls, ablations,
  failure conditions and reproducibility information.
* Agent efficiency: tool calls, failed calls, duplicate searches, phase
  attempts, token usage and wall-clock time, from the event log.

Research-gap quality has no automatic metric; ``gap_review_sheet`` exports
gaps with their evidence for expert rating.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from researchforge.evidence import grounding
from researchforge.literature.merge import title_key
from researchforge.literature.sources import query_terms
from researchforge.schemas import ExperimentPlan, Paper
from researchforge.workspace import Workspace

DATASETS_DIR = Path(__file__).parent / "datasets"
TIER_ORDER = {"high": 0, "medium": 1, "low": 2, "not_relevant": 3}


@dataclass
class GroundTruth:
    name: str
    idea: str
    relevant: list[dict]
    notes: str = ""

    @classmethod
    def load(cls, path: str | Path) -> "GroundTruth":
        path = Path(path)
        if not path.exists() and (DATASETS_DIR / f"{path}.yaml").exists():
            path = DATASETS_DIR / f"{path}.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return cls(name=data["name"], idea=data["idea"], relevant=data["relevant"], notes=data.get("notes", ""))

    def matches(self, paper: Paper) -> int | None:
        for i, item in enumerate(self.relevant):
            if item.get("arxiv") and paper.arxiv_id == str(item["arxiv"]):
                return i
            if item.get("doi") and paper.doi and paper.doi.lower() == str(item["doi"]).lower():
                return i
            if item.get("title") and title_key(item["title"]) == title_key(paper.title):
                return i
        return None


def precision_recall_at_k(ranked: list[Paper], truth: GroundTruth, k: int) -> dict:
    top = ranked[:k]
    hits = {truth.matches(p) for p in top} - {None}
    return {
        "k": k,
        "hits": len(hits),
        "precision": round(len(hits) / k, 4) if k else 0.0,
        "recall": round(len(hits) / len(truth.relevant), 4) if truth.relevant else 0.0,
    }


def rankings(ws: Workspace) -> dict[str, list[Paper]]:
    papers = ws.papers()
    tiers = {a.paper_id: a.relevance_tier for a in ws.analyses()}
    heuristic = sorted(papers, key=lambda p: -p.relevance)
    agent = sorted(papers, key=lambda p: (TIER_ORDER.get(tiers.get(p.id, ""), 4), -p.relevance))
    return {"heuristic_relevance": heuristic, "agent_tiers": agent}


def retrieval_metrics(ws: Workspace, truth: GroundTruth, ks: tuple[int, ...] = (5, 10, 20)) -> dict:
    all_hits = {truth.matches(p) for p in ws.papers()} - {None}
    return {
        "ground_truth": truth.name,
        "relevant_in_ground_truth": len(truth.relevant),
        "retrieved_papers": len(ws.papers()),
        "overall_recall": round(len(all_hits) / len(truth.relevant), 4) if truth.relevant else 0.0,
        "missed": [item.get("title") or item.get("arxiv") for i, item in enumerate(truth.relevant) if i not in all_hits],
        "rankings": {
            name: [precision_recall_at_k(ranked, truth, k) for k in ks] for name, ranked in rankings(ws).items()
        },
    }


PLAN_CHECKS = {
    "baselines (>=2)": lambda p: len(p.baselines) >= 2,
    "metrics": lambda p: bool(p.metrics),
    "datasets or workloads": lambda p: bool(p.datasets or p.workloads),
    "controls": lambda p: bool(p.controls),
    "ablations": lambda p: bool(p.ablations),
    "failure conditions": lambda p: bool(p.failure_conditions),
    "confounders addressed": lambda p: bool(p.confounders_addressed),
    "hardware": lambda p: bool(p.hardware.strip()),
    "software environment": lambda p: bool(p.software_environment.strip()),
    "reproducibility notes": lambda p: bool(p.reproducibility_notes.strip()),
    "expected outcomes": lambda p: bool(p.expected_outcomes.strip()),
}


def plan_completeness(plan: ExperimentPlan) -> dict:
    present = [name for name, check in PLAN_CHECKS.items() if check(plan)]
    missing = [name for name in PLAN_CHECKS if name not in present]
    return {"plan_id": plan.id, "score": round(len(present) / len(PLAN_CHECKS), 3), "missing": missing}


@dataclass
class Efficiency:
    tool_calls: Counter = field(default_factory=Counter)
    failed_tool_calls: int = 0
    duplicate_searches: int = 0
    phase_attempts: dict[str, int] = field(default_factory=dict)
    tokens: dict[str, float] = field(default_factory=dict)
    duration_s: float | None = None

    def as_dict(self) -> dict:
        return {
            "tool_calls_total": sum(self.tool_calls.values()),
            "tool_calls_by_tool": dict(self.tool_calls.most_common()),
            "failed_tool_calls": self.failed_tool_calls,
            "duplicate_searches": self.duplicate_searches,
            "phase_attempts": self.phase_attempts,
            "token_usage": self.tokens,
            "duration_s": self.duration_s,
        }


def efficiency(ws: Workspace) -> Efficiency:
    eff = Efficiency()
    events = ws.events()
    for e in events:
        if e.kind == "tool_call":
            eff.tool_calls[e.data.get("tool", "?")] += 1
        elif e.kind == "tool_result" and e.data.get("status") == "error":
            eff.failed_tool_calls += 1
        elif e.kind == "tool_result" and '"repeated": true' in str(e.data.get("result", "")):
            eff.duplicate_searches += 1
        elif e.kind == "info" and e.data.get("message") == "token usage":
            for k, v in (e.data.get("usage") or {}).items():
                if isinstance(v, (int, float)):
                    eff.tokens[k] = eff.tokens.get(k, 0) + v
    seen: Counter = Counter(" ".join(sorted(query_terms(s.query))) for s in ws.searches())
    eff.duplicate_searches += sum(n - 1 for n in seen.values() if n > 1)
    state = ws.state()
    if state:
        eff.phase_attempts = {p.name: p.attempts for p in state.phases if p.attempts}
    if len(events) >= 2:
        eff.duration_s = round((events[-1].ts - events[0].ts).total_seconds(), 1)
    return eff


def gap_review_sheet(ws: Workspace) -> list[dict]:
    """Rows for manual expert rating of gap quality (1-5 scales left blank)."""
    papers = {p.id: p.title for p in ws.papers()}
    return [
        {
            "gap_id": g.id,
            "gap": g.gap,
            "evidence": [f"{papers.get(i.paper_id, i.paper_id)} — {i.location}: {i.quote or ''} ({'verified' if i.verified else 'unverified'})" for i in g.evidence],
            "research_question": g.research_question,
            "agent_confidence": g.confidence,
            "rating_evidence_support_1_5": None,
            "rating_novelty_1_5": None,
            "rating_actionability_1_5": None,
            "reviewer_notes": "",
        }
        for g in ws.gaps()
    ]


def loop_metrics(ws: Workspace) -> dict:
    """Behaviour of the investigation loop, from recorded state (for comparison with simpler agent loops)."""
    state = ws.state()
    us, dirs = ws.uncertainties(), ws.directions()
    decisions = state.decisions if state else []
    steps = [d for d in decisions if d.action not in ("INTAKE", "FINALIZE", "EXPERIMENT")]
    gains = [d.info_gain for d in steps if d.info_gain is not None]
    actions = Counter(d.action for d in steps)
    return {
        "iterations": state.budget.iterations if state else 0,
        "tool_calls": state.budget.tool_calls if state else 0,
        "failed_tool_calls": state.budget.failed_tool_calls if state else 0,
        "runtime_failures": state.budget.runtime_failures if state else 0,
        "tokens": state.budget.tokens if state else 0,
        "elapsed_s": round(state.budget.seconds, 1) if state else 0.0,
        "searches": len(ws.searches()),
        "papers_retrieved": len(ws.papers()),
        "papers_read": len(ws.analyses()),
        "papers_full_text": sum(1 for p in ws.papers() if p.has_full_text),
        "actions": dict(actions.most_common()),
        "uncertainties_created": len(us),
        "uncertainties_created_by_controller": sum(1 for u in us if u.source == "controller"),
        "uncertainties_resolved": sum(1 for u in us if u.status == "resolved"),
        "uncertainties_unresolved": sum(1 for u in us if u.status in ("open", "partially_resolved", "unresolved")),
        "challenges": sum(1 for u in us if u.challenge_verdict),
        "contradictory_evidence_found": sum(1 for u in us if u.contradicting_paper_ids or u.challenge_verdict in ("weakened", "refuted")),
        "hypothesis_revisions": sum(1 for d in dirs if d.change_type in ("CHANGE_HYPOTHESIS", "CHANGE_RESEARCH_QUESTION")),
        "direction_changes": sum(1 for d in dirs if d.change_type != "KEEP_ORIGINAL"),
        "experiments_executed": len({r.plan_id for r in ws.runs()}),
        "hypothesis_evaluations": [e.verdict for e in ws.evaluations()],
        "information_gain_total": round(sum(gains), 2),
        "information_gain_per_step": round(sum(gains) / len(gains), 3) if gains else None,
        "zero_gain_steps": sum(1 for g in gains if g == 0),
        "investigation_closed": state.investigation_closed if state else None,
        "finalization_reason": state.finalize_reason if state else None,
        "research_decision": state.research_decision if state else None,
    }


def evaluate(ws: Workspace, truth: GroundTruth | None = None, ks: tuple[int, ...] = (5, 10, 20)) -> dict:
    g = grounding(ws.claims())
    plans = ws.plans()
    result = {
        "project": ws.name,
        "loop": loop_metrics(ws),
        "claim_grounding": {"grounded": g.grounded, "total": g.total, "rate": round(g.rate, 3), "by_kind": g.by_kind, "ungrounded": g.ungrounded_ids},
        "experiment_plans": [plan_completeness(p) for p in plans],
        "efficiency": efficiency(ws).as_dict(),
        "records": {
            "papers": len(ws.papers()),
            "analyses": len(ws.analyses()),
            "claims": len(ws.claims()),
            "gaps": len(ws.gaps()),
            "modifications": len(ws.modifications()),
            "plans": len(plans),
        },
    }
    if truth is not None:
        result["retrieval"] = retrieval_metrics(ws, truth, ks)
    return result


def parse_ks(text: str) -> tuple[int, ...]:
    return tuple(int(x) for x in re.split(r"[,\s]+", text.strip()) if x)
