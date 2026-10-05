"""ResearchToolkit: every capability the research agent can call.

All methods return JSON-serialisable structured data. Validation failures
raise :class:`ToolError` whose message tells the model how to fix the call.
The toolkit is transport-independent: the MCP server exposes it to dsh, and
tests call it directly.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, ValidationError

from researchforge import phases
from researchforge.config import Settings
from researchforge.evidence import EvidenceError, check_paper_ids, validate_claim, verify_items
from researchforge.literature import controls
from researchforge.literature.fulltext import FullTextUnavailable, fetch_full_text, find_passages, section_outline
from researchforge.literature.github import GitHubClient, repo_name_from_url
from researchforge.literature.http import CachedHttp, HttpError
from researchforge.literature.merge import dedupe, merge_into, paper_keys, refresh_warnings, relevance
from researchforge.literature.sources import (
    ArxivClient,
    CrossrefClient,
    OpenAlexClient,
    SemanticScholarClient,
    SourceClient,
    query_terms,
)
from researchforge.schemas import (
    Claim,
    Critique,
    Direction,
    HypothesisEvaluation,
    InvestigationPlan,
    Uncertainty,
    EvidenceItem,
    ExperimentPlan,
    Gap,
    IdeaAnalysis,
    Landscape,
    Modification,
    NoGapFinding,
    Paper,
    PaperAnalysis,
    SearchRecord,
    SourceStatus,
    Support,
)
from researchforge.workspace import Workspace

log = logging.getLogger("researchforge.toolkit")


class ToolError(ValueError):
    """A tool call that cannot succeed as given. The message is model-facing."""


class EvidenceInput(BaseModel):
    """One piece of evidence. Cite only papers returned by search_papers/list_papers."""

    paper_id: str | None = Field(default=None, description="Id of a retrieved paper, e.g. arxiv:2306.14048.")
    experiment_run_id: str | None = Field(default=None, description="Id of a recorded experiment run.")
    location: str = Field(default="abstract", description="'abstract', 'p. 5', 'Table 2', ...")
    quote: str | None = Field(default=None, description="Verbatim source text; required for direct support.")
    support: Support = Field(default="indirect", description="direct = quote states it; indirect = implied; weak = tangential.")

    def to_item(self) -> EvidenceItem:
        return EvidenceItem(**self.model_dump())


def _compact(p: Paper) -> dict:
    return {
        "id": p.id,
        "title": p.title,
        "year": p.year,
        "venue": p.venue,
        "authors": p.authors[:3] + (["et al."] if len(p.authors) > 3 else []),
        "citation_count": p.citation_count,
        "citation_count_source": p.citation_count_source,
        "relevance": p.relevance,
        "sources": p.sources,
        "has_abstract": bool(p.abstract),
        **({"metadata_warnings": p.metadata_warnings} if p.metadata_warnings else {}),
    }


def _normalize_query(q: str) -> str:
    return " ".join(sorted(query_terms(q)))


class ResearchToolkit:
    def __init__(
        self,
        ws: Workspace,
        settings: Settings,
        *,
        http: CachedHttp | None = None,
        env: dict[str, str] | None = None,
    ) -> None:
        self.ws = ws
        self.settings = settings
        lit = settings.literature
        env = dict(os.environ) if env is None else env
        self.http = http or CachedHttp(
            Path(os.path.expanduser(lit.cache_dir)).resolve() if lit.cache_dir else ws.root / "cache" / "http",
            shared_pacing=lit.cache_dir is not None,
            timeout_s=lit.timeout_s,
            max_retries=lit.max_retries,
            max_backoff_s=lit.max_backoff_s,
        )
        self.clients: dict[str, SourceClient] = {
            "arxiv": ArxivClient(self.http),
            "openalex": OpenAlexClient(self.http, lit.contact_email, env.get(lit.openalex_api_key_env)),
            "semantic_scholar": SemanticScholarClient(self.http, env.get(lit.semantic_scholar_api_key_env)),
            "crossref": CrossrefClient(self.http, lit.contact_email),
        }
        self.github = GitHubClient(self.http, env.get(lit.github_token_env))

    # ================================================================ read-only

    def get_research_state(self) -> dict:
        """Compact digest of everything recorded so far, plus each phase's outstanding requirements."""
        ws = self.ws
        idea = ws.idea_analysis()
        analyzed = {a.paper_id: a.relevance_tier for a in ws.analyses()}
        papers = sorted(ws.papers(), key=lambda p: -p.relevance)
        state = ws.state()
        return {
            "project": ws.name,
            "raw_idea": ws.raw_idea,
            "idea_analysis": json.loads(idea.model_dump_json(exclude={"recorded_at", "raw_idea"})) if idea else None,
            "papers": {
                "count": len(papers),
                "analyzed": len(analyzed),
                "top": [
                    {"id": p.id, "title": p.title, "year": p.year, "relevance": p.relevance, "tier": analyzed.get(p.id)}
                    for p in papers[:40]
                ],
            },
            "searches": [s.query for s in ws.searches()],
            "claims": [{"id": c.id, "kind": c.kind, "statement": c.statement[:160]} for c in ws.claims()],
            "landscape_recorded": ws.landscape() is not None,
            "critique_recorded": ws.critique() is not None,
            "gaps": [{"id": g.id, "gap": g.gap[:160]} for g in ws.gaps()],
            "no_gap_finding": ws.no_gap() is not None,
            "modifications": [{"id": m.id, "title": m.title} for m in ws.modifications()],
            "experiment_plans": [{"id": p.id, "title": p.title, "status": p.status} for p in ws.plans()],
            "investigation": {
                "iteration": state.budget.iterations if state else 0,
                "loop_phase": state.loop_phase if state else "INTAKE",
                "current_action": state.current_action if state else None,
                "current_focus": state.current_focus if state else None,
                "recent_decisions": [
                    {"iteration": d.iteration, "action": d.action, "reason": d.reason, "outcome": d.outcome}
                    for d in (state.decisions[-5:] if state else [])
                ],
            },
            "investigation_plan": json.loads(plan.model_dump_json(exclude={"recorded_at"})) if (plan := ws.investigation_plan()) else None,
            "uncertainties": [
                {"id": u.id, "question": u.question, "category": u.category, "importance": u.importance, "status": u.status,
                 "next_action": u.next_action, "possible_actions": u.possible_actions, "attempts": u.attempts,
                 "supporting": u.supporting_paper_ids, "contradicting": u.contradicting_paper_ids,
                 "confidence": u.confidence, "challenge_verdict": u.challenge_verdict, "raised_by": u.source}
                for u in ws.uncertainties()
            ],
            "original_hypothesis": idea.hypothesis if idea else None,
            "current_direction": json.loads(d.model_dump_json(exclude={"recorded_at"})) if (d := (ws.directions() or [None])[-1]) else None,
            "hypothesis_evaluations": [{"plan_id": e.plan_id, "verdict": e.verdict} for e in ws.evaluations()],
            "experiment_results": [{"plan_id": a.plan_id, "status": a.status, "summary": a.summary} for a in ws.experiment_analyses()],
            "outstanding_requirements": {
                spec.name: missing
                for spec in phases.PHASES
                if (missing := spec.check(ws, self.settings))
            },
        }

    async def search_papers(
        self,
        query: str,
        sources: list[str] | None = None,
        limit_per_source: int | None = None,
        year_from: int | None = None,
    ) -> dict:
        query = query.strip()
        if len(query_terms(query)) == 0:
            raise ToolError("query has no searchable terms")
        inv = self.settings.investigation
        if self.ws.search_count() >= inv.max_searches:
            raise ToolError(f"search budget reached ({inv.max_searches} searches). Work with the retrieved papers: compare, verify or record findings.")
        if self.ws.paper_count() >= inv.max_papers:
            raise ToolError(f"paper budget reached ({inv.max_papers} papers). Analyze and compare the retrieved papers instead of searching.")
        allowed = self.settings.literature.sources
        sources = [s for s in (sources or allowed) if s in allowed]
        if not sources:
            raise ToolError(f"no enabled sources selected; enabled sources are {allowed}")
        limit = min(limit_per_source or self.settings.literature.max_results_per_source, 50)

        norm = _normalize_query(query)
        for prior in self.ws.searches():
            if _normalize_query(prior.query) == norm and {s.source for s in prior.sources} >= set(sources):
                known = [p for pid in prior.paper_ids if (p := self.ws.paper(pid))]
                return {
                    "query": query,
                    "repeated": True,
                    "note": "This query was already run in this investigation; returning its stored results. Try a different formulation to find new work.",
                    "results": [_compact(p) for p in known],
                    "total_papers": self.ws.paper_count(),
                }

        lit = self.settings.literature
        results = await asyncio.gather(
            *(self.clients[s].search(query, limit, year_from, lit.published_before) for s in sources), return_exceptions=True
        )
        statuses, found = [], []
        for source, res in zip(sources, results):
            if isinstance(res, BaseException):
                log.warning("source failed", extra={"source": source, "error": str(res)})
                statuses.append(SourceStatus(source=source, status="error", detail=str(res)[:300]))
            else:
                statuses.append(SourceStatus(source=source, status="ok", count=len(res)))
                found.extend(controls.corrupt(self.ws.root, source, res, lit.corrupt_abstracts, lit.corruption_seed))

        idea = self.ws.idea_analysis()
        terms = query_terms(" ".join((idea.keywords if idea else []) + [query]))
        stored = self._store_papers(dedupe(found, lit.integrity_checks), query, terms)
        self.ws.append_search(SearchRecord(query=query, sources=statuses, paper_ids=[p.id for p in stored]))
        return {
            "query": query,
            "sources": [s.model_dump() for s in statuses],
            "results": [_compact(p) for p in sorted(stored, key=lambda p: -p.relevance)],
            "total_papers": self.ws.paper_count(),
        }

    def _store_papers(self, papers: list[Paper], query: str | None, terms: list[str]) -> list[Paper]:
        lit = self.settings.literature
        existing = self.ws.papers()
        index = {k: p for p in existing for k in paper_keys(p)}
        stored, hidden = [], []
        for p in papers:
            match = next((index[k] for k in paper_keys(p) if k in index), None)
            if match is not None:
                p = merge_into(match, p, keep_id=True, integrity=lit.integrity_checks)
            if not controls.visible(p, lit.published_before):
                hidden.append(p)
                continue
            if query and query not in p.queries:
                p = p.model_copy(update={"queries": p.queries + [query]})
            p = refresh_warnings(p.model_copy(update={"relevance": max(p.relevance, relevance(p, terms))}), lit.integrity_checks)
            self.ws.save_paper(p)
            for k in paper_keys(p):
                index[k] = p
            stored.append(p)
        controls.record_hidden(self.ws.root, query or "", hidden)
        return stored

    def _require_paper(self, paper_id: str) -> Paper:
        paper = self.ws.paper(paper_id)
        if paper is None:
            raise ToolError(f"unknown paper id {paper_id!r}; use ids returned by search_papers or list_papers")
        return paper

    def get_paper(self, paper_id: str) -> dict:
        paper = self._require_paper(paper_id)
        analysis = next((a for a in self.ws.analyses() if a.paper_id == paper_id), None)
        return {
            "paper": json.loads(paper.model_dump_json()),
            "analysis": json.loads(analysis.model_dump_json()) if analysis else None,
        }

    def list_papers(self, min_relevance: float = 0.0, only_unanalyzed: bool = False, limit: int = 60) -> dict:
        analyzed = {a.paper_id: a.relevance_tier for a in self.ws.analyses()}
        papers = [
            p for p in sorted(self.ws.papers(), key=lambda p: -p.relevance)
            if p.relevance >= min_relevance and not (only_unanalyzed and p.id in analyzed)
        ]
        return {
            "total": len(papers),
            "papers": [{**_compact(p), "analysis_tier": analyzed.get(p.id)} for p in papers[:limit]],
        }

    async def fetch_paper_text(self, paper_id: str) -> dict:
        paper = self._require_paper(paper_id)
        text = self.ws.paper_text(paper_id)
        if text is None:
            try:
                text = await fetch_full_text(self.http, paper, self.settings.literature.max_pdf_bytes,
                                             first_version=self.settings.literature.published_before is not None)
            except (FullTextUnavailable, HttpError) as exc:
                raise ToolError(f"full text unavailable for {paper_id}: {exc}. Work from the abstract and mark analyzed_from='abstract'.") from exc
            self.ws.save_paper_text(paper_id, text)
            self.ws.save_paper(paper.model_copy(update={"has_full_text": True}))
        pages = len(re.findall(r"\[\[page \d+\]\]", text))
        return {
            "paper_id": paper_id,
            "pages": pages,
            "chars": len(text),
            "outline": section_outline(text),
            "excerpt": text[:3000],
            "hint": "Use search_paper_text to locate passages (with page numbers) to quote as evidence.",
        }

    async def search_paper_text(self, paper_id: str, pattern: str, max_passages: int = 6) -> dict:
        if self.ws.paper_text(paper_id) is None:
            await self.fetch_paper_text(paper_id)
        text = self.ws.paper_text(paper_id) or ""
        passages = find_passages(text, pattern, limit=max(1, min(max_passages, 15)))
        return {"paper_id": paper_id, "pattern": pattern, "passages": passages}

    async def expand_citations(
        self, paper_id: str, direction: Literal["references", "citations"] = "citations", limit: int = 10
    ) -> dict:
        paper = self._require_paper(paper_id)
        oa: OpenAlexClient = self.clients["openalex"]  # type: ignore[assignment]
        oa_id = paper.openalex_id
        if not oa_id:
            try:
                found = await oa.lookup(doi=paper.doi, arxiv_id=paper.arxiv_id)
            except HttpError as exc:
                raise ToolError(f"OpenAlex lookup failed: {exc}") from exc
            if not found or not found.openalex_id:
                raise ToolError(f"{paper_id} could not be matched to an OpenAlex work; citation expansion unavailable")
            oa_id = found.openalex_id
            self.ws.save_paper(paper.model_copy(update={"openalex_id": oa_id}))
        try:
            related = await oa.related(oa_id, direction, min(limit, 25))
        except HttpError as exc:
            raise ToolError(f"OpenAlex citation expansion failed: {exc}") from exc
        lit = self.settings.literature
        related = controls.corrupt(self.ws.root, "openalex", related, lit.corrupt_abstracts, lit.corruption_seed)
        idea = self.ws.idea_analysis()
        terms = query_terms(" ".join(idea.keywords if idea else []))
        stored = self._store_papers(dedupe(related, lit.integrity_checks), f"{direction} of {paper_id}", terms)
        self.ws.append_search(
            SearchRecord(
                query=f"{direction} of {paper_id}",
                sources=[SourceStatus(source="openalex", status="ok", count=len(related))],
                paper_ids=[p.id for p in stored],
            )
        )
        return {"paper_id": paper_id, "direction": direction, "results": [_compact(p) for p in stored]}

    def _require_github(self) -> None:
        # A repository can reveal work published after an evaluation cutoff, and GitHub has no date filter for that.
        if self.settings.literature.published_before is not None:
            raise ToolError("GitHub tools are unavailable in this investigation. Work from the retrieved papers.")

    async def search_github(self, query: str, limit: int = 5) -> dict:
        self._require_github()
        try:
            repos = await self.github.search(query, min(limit, 10))
        except HttpError as exc:
            raise ToolError(f"GitHub search failed: {exc}") from exc
        return {"query": query, "repositories": [r.model_dump() for r in repos]}

    async def inspect_repository(self, repository: str, paper_id: str | None = None) -> dict:
        self._require_github()
        name = repo_name_from_url(repository) if "github.com" in repository else repository.strip("/")
        if not name or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", name):
            raise ToolError("repository must be 'owner/name' or a github.com URL")
        try:
            inspection = await self.github.inspect(name)
        except HttpError as exc:
            raise ToolError(f"could not inspect {name}: {exc}") from exc
        linked = False
        if paper_id:
            paper = self._require_paper(paper_id)
            if inspection.url not in paper.code_urls:
                self.ws.save_paper(paper.model_copy(update={"code_urls": paper.code_urls + [inspection.url]}))
            linked = True
            if paper.arxiv_id and paper.arxiv_id not in inspection.mentioned_arxiv_ids:
                inspection.reproducibility_signals.append(
                    f"README does not mention arXiv {paper.arxiv_id}; the link to the paper is unconfirmed"
                )
        return {"repository": inspection.model_dump(), "linked_to_paper": paper_id if linked else None}

    def get_records(self, kind: Literal["claims", "gaps", "modifications", "experiment_plans", "analyses", "landscape", "critique"]) -> dict:
        ws = self.ws
        loaders = {
            "claims": ws.claims,
            "gaps": ws.gaps,
            "modifications": ws.modifications,
            "experiment_plans": ws.plans,
            "analyses": ws.analyses,
            "landscape": lambda: [x] if (x := ws.landscape()) else [],
            "critique": lambda: [x] if (x := ws.critique()) else [],
        }
        if kind not in loaders:
            raise ToolError(f"kind must be one of {sorted(loaders)}")
        return {"kind": kind, "records": [json.loads(r.model_dump_json()) for r in loaders[kind]()]}

    # ================================================================ records

    @staticmethod
    def _build(cls: type[BaseModel], data: dict):
        try:
            return cls.model_validate(data)
        except ValidationError as exc:
            raise ToolError(f"invalid {cls.__name__}: {exc}") from exc

    def record_idea_analysis(self, **fields) -> dict:
        analysis = self._build(IdeaAnalysis, {**fields, "raw_idea": self.ws.raw_idea})
        if len(analysis.search_queries) < 2:
            raise ToolError("provide at least two distinct search_queries")
        self.ws.save_idea_analysis(analysis)
        return {"ok": True, "recorded": "idea_analysis", "open_ambiguities": [a.question for a in analysis.ambiguities if a.resolved_by == "unresolved"]}

    def record_paper_analysis(self, **fields) -> dict:
        analysis = self._build(PaperAnalysis, fields)
        paper = self._require_paper(analysis.paper_id)
        if analysis.analyzed_from == "full_text" and not paper.has_full_text:
            raise ToolError("analyzed_from='full_text' requires fetch_paper_text to have succeeded for this paper")
        self.ws.save_analysis(analysis)
        remaining = len([p for p in self.ws.papers() if p.relevance > 0]) - len(self.ws.analyses())
        return {"ok": True, "recorded": "paper_analysis", "paper_id": analysis.paper_id, "unanalyzed_papers": max(remaining, 0)}

    def record_claim(self, statement: str, kind: str, confidence: str, evidence: list[dict] | None = None, tags: list[str] | None = None, phase: str = "") -> dict:
        items = [EvidenceInput.model_validate(e).to_item() for e in (evidence or [])]
        claim = self._build(Claim, {"statement": statement, "kind": kind, "confidence": confidence, "evidence": items, "tags": tags or [], "phase": phase or self._current_phase()})
        if claim.kind == "experimental":
            raise ToolError("experimental claims are recorded by ResearchForge from verified experiment runs, not by the agent")
        try:
            claim, warnings = validate_claim(self.ws, claim)
        except EvidenceError as exc:
            raise ToolError(str(exc)) from exc
        claim = self.ws.save_claim(claim)
        return {"ok": True, "claim_id": claim.id, "verified_evidence": sum(i.verified for i in claim.evidence), "warnings": warnings}

    def record_landscape(self, **fields) -> dict:
        landscape = self._build(Landscape, fields)
        ids = [pid for c in landscape.categories for pid in c.paper_ids]
        ids += [pid for f in landscape.repeated_limitations + landscape.contradictions for pid in f.paper_ids]
        self._check_ids(ids)
        names = {c.name for c in landscape.categories}
        orphans = [c.parent for c in landscape.categories if c.parent and c.parent not in names]
        if orphans:
            raise ToolError(f"categories reference unknown parent categories: {orphans}")
        self.ws.save_landscape(landscape)
        return {"ok": True, "recorded": "landscape", "categories": len(landscape.categories)}

    def record_critique(self, **fields) -> dict:
        critique = self._build(Critique, fields)
        points = critique.novelty + critique.technical_validity + critique.experimental_validity + critique.practicality
        self._check_ids(critique.closest_paper_ids + [pid for p in points for pid in p.paper_ids])
        known_claims = {c.id for c in self.ws.claims()}
        unknown = sorted({cid for p in points for cid in p.claim_ids if cid not in known_claims})
        if unknown:
            raise ToolError(f"critique cites unknown claim ids {unknown}; record them with record_claim first")
        self.ws.save_critique(critique)
        return {"ok": True, "recorded": "critique", "overall_status": critique.overall_status}

    def record_gap(self, evidence: list[dict], id: str | None = None, **fields) -> dict:
        items = [EvidenceInput.model_validate(e).to_item() for e in evidence]
        gap = self._build(Gap, {**fields, "evidence": items, "id": id or ""})
        self._check_ids(gap.related_paper_ids)
        if id and not any(g.id == id for g in self.ws.gaps()):
            raise ToolError(f"no gap with id {id!r} to update")
        try:
            check = verify_items(self.ws, gap.evidence)
        except EvidenceError as exc:
            raise ToolError(str(exc)) from exc
        if not any(i.paper_id for i in check.items):
            raise ToolError("a gap must cite at least one retrieved paper as evidence")
        gap = self.ws.save_gap(gap.model_copy(update={"evidence": check.items}))
        return {"ok": True, "gap_id": gap.id, "warnings": check.warnings}

    def record_no_gap(self, rationale: str, paper_ids: list[str]) -> dict:
        self._check_ids(paper_ids)
        if not paper_ids:
            raise ToolError("cite the papers whose coverage leads to this conclusion")
        self.ws.save_no_gap(NoGapFinding(rationale=rationale, paper_ids=paper_ids))
        return {"ok": True, "recorded": "no_gap_finding"}

    def record_modification(self, id: str | None = None, **fields) -> dict:
        mod = self._build(Modification, {**fields, "id": id or ""})
        self._check_ids(mod.related_paper_ids)
        existing = self.ws.modifications()
        if id and not any(m.id == id for m in existing):
            raise ToolError(f"no modification with id {id!r} to update")
        if not id and len(existing) >= self.settings.investigation.max_modifications:
            raise ToolError(f"already {len(existing)} modifications (maximum {self.settings.investigation.max_modifications}); revise one by passing its id")
        gap_ids = {g.id for g in self.ws.gaps()}
        unknown = [g for g in mod.addresses_gap_ids if g not in gap_ids]
        if unknown:
            raise ToolError(f"unknown gap ids {unknown}")
        mod = self.ws.save_modification(mod)
        return {"ok": True, "modification_id": mod.id}

    def record_experiment_plan(self, id: str | None = None, **fields) -> dict:
        plan = self._build(ExperimentPlan, {**fields, "id": id or ""})
        self._check_ids(plan.related_paper_ids)
        if plan.related_modification_id and not any(m.id == plan.related_modification_id for m in self.ws.modifications()):
            raise ToolError(f"unknown modification id {plan.related_modification_id!r}")
        if id and self.ws.plan(id) is None:
            raise ToolError(f"no experiment plan with id {id!r} to update")
        if plan.execution is not None:
            roles = {a.role for a in plan.execution.arms}
            if "baseline" not in roles:
                raise ToolError("an executable experiment needs at least one arm with role 'baseline'")
            plan = plan.model_copy(update={"status": "awaiting_approval"})
        plan = self.ws.save_plan(plan)
        note = (
            "Execution requires explicit human approval (researchforge experiment <project> --run <id> --approve)."
            if plan.execution
            else "Plan recorded (no executable spec)."
        )
        return {"ok": True, "plan_id": plan.id, "status": plan.status, "note": note}

    # ================================================================ investigation loop records

    def record_investigation_plan(self, questions: list[str], search_topics: list[str], comparison_targets: list[str] | None = None) -> dict:
        plan = self._build(InvestigationPlan, {"questions": questions, "search_topics": search_topics, "comparison_targets": comparison_targets or []})
        self.ws.save_plan_of_investigation(plan)
        return {"ok": True, "recorded": "investigation_plan", "questions": len(plan.questions), "search_topics": len(plan.search_topics)}

    def record_uncertainty(self, question: str, importance: str, next_action: str = "SEARCH", rationale: str = "",
                           paper_ids: list[str] | None = None, description: str = "", category: str = "other",
                           possible_actions: list[str] | None = None, confidence: float | None = None, confidence_basis: str = "",
                           supporting_paper_ids: list[str] | None = None, contradicting_paper_ids: list[str] | None = None) -> dict:
        self._check_ids((paper_ids or []) + (supporting_paper_ids or []) + (contradicting_paper_ids or []))
        if confidence is not None and not confidence_basis.strip():
            raise ToolError("a confidence value needs a confidence_basis (what evidence it rests on); omit confidence if you cannot justify one")
        norm = " ".join(question.lower().split())
        for u in self.ws.uncertainties():
            if " ".join(u.question.lower().split()) == norm and u.status in ("open", "partially_resolved"):
                return {"ok": True, "uncertainty_id": u.id, "note": "already recorded; use update_uncertainty to change it"}
        u = self._build(Uncertainty, {
            "question": question, "importance": importance, "next_action": next_action, "rationale": rationale,
            "paper_ids": paper_ids or [], "source": self._loop_phase(), "description": description, "category": category,
            "possible_actions": possible_actions or [], "confidence": confidence, "confidence_basis": confidence_basis,
            "supporting_paper_ids": supporting_paper_ids or [], "contradicting_paper_ids": contradicting_paper_ids or [],
        })
        u = self.ws.save_uncertainty(u)
        return {"ok": True, "uncertainty_id": u.id}

    def update_uncertainty(self, id: str, status: str, resolution: str = "", paper_ids: list[str] | None = None,
                           claim_ids: list[str] | None = None, next_action: str | None = None,
                           supporting_paper_ids: list[str] | None = None, contradicting_paper_ids: list[str] | None = None,
                           confidence: float | None = None, confidence_basis: str = "") -> dict:
        u = self.ws.uncertainty(id)
        if u is None:
            raise ToolError(f"unknown uncertainty id {id!r}; see get_research_state")
        self._check_ids((paper_ids or []) + (supporting_paper_ids or []) + (contradicting_paper_ids or []))
        known_claims = {c.id for c in self.ws.claims()}
        unknown = [c for c in (claim_ids or []) if c not in known_claims]
        if unknown:
            raise ToolError(f"unknown claim ids {unknown}; record them with record_claim first")
        if status in ("resolved", "partially_resolved") and not resolution.strip():
            raise ToolError("explain the resolution: what the evidence shows")
        if confidence is not None and not confidence_basis.strip():
            raise ToolError("a confidence value needs a confidence_basis (what evidence it rests on)")
        merge = lambda a, b: list(dict.fromkeys(a + (b or [])))  # noqa: E731
        update = {"status": status, "resolution": resolution or u.resolution,
                  "paper_ids": merge(u.paper_ids, paper_ids), "claim_ids": merge(u.claim_ids, claim_ids),
                  "supporting_paper_ids": merge(u.supporting_paper_ids, supporting_paper_ids),
                  "contradicting_paper_ids": merge(u.contradicting_paper_ids, contradicting_paper_ids)}
        if next_action:
            update["next_action"] = next_action
        if confidence is not None:
            update["confidence"], update["confidence_basis"] = confidence, confidence_basis
        u = self._build(Uncertainty, {**u.model_dump(), **update})
        self.ws.save_uncertainty(u)
        return {"ok": True, "uncertainty_id": u.id, "status": u.status}

    def record_challenge_result(self, uncertainty_id: str, verdict: str, rationale: str,
                                supporting_paper_ids: list[str] | None = None, contradicting_paper_ids: list[str] | None = None) -> dict:
        """Close a contradictory-evidence search: does the challenged conclusion hold?"""
        u = self.ws.uncertainty(uncertainty_id)
        if u is None:
            raise ToolError(f"unknown uncertainty id {uncertainty_id!r}")
        self._check_ids((supporting_paper_ids or []) + (contradicting_paper_ids or []))
        if verdict in ("weakened", "refuted") and not contradicting_paper_ids:
            raise ToolError(f"a '{verdict}' verdict needs contradicting_paper_ids: cite the retrieved papers that contradict the conclusion")
        if not self.ws.searches():
            raise ToolError("no search has been run; a conclusion cannot be challenged without searching for contradicting work")
        if not rationale.strip():
            raise ToolError("state what was searched and what it showed")
        update = {"status": "resolved", "challenge_verdict": verdict, "resolution": rationale,
                  "supporting_paper_ids": list(dict.fromkeys(u.supporting_paper_ids + (supporting_paper_ids or []))),
                  "contradicting_paper_ids": list(dict.fromkeys(u.contradicting_paper_ids + (contradicting_paper_ids or [])))}
        u = self._build(Uncertainty, {**u.model_dump(), **update})
        self.ws.save_uncertainty(u)
        follow_up = " ResearchForge will raise a refinement question." if verdict in ("weakened", "refuted") else ""
        return {"ok": True, "uncertainty_id": u.id, "verdict": verdict, "note": f"Challenge recorded.{follow_up}"}

    def record_direction(self, direction: str, hypothesis: str, rationale: str, modification_id: str | None = None,
                         paper_ids: list[str] | None = None, change_type: str = "REFINE_SCOPE", research_question: str | None = None,
                         confidence: str = "medium", uncertainty_ids: list[str] | None = None) -> dict:
        self._check_ids(paper_ids or [])
        if modification_id and not any(m.id == modification_id for m in self.ws.modifications()):
            raise ToolError(f"unknown modification id {modification_id!r}")
        known_u = {u.id for u in self.ws.uncertainties()}
        unknown = [x for x in (uncertainty_ids or []) if x not in known_u]
        if unknown:
            raise ToolError(f"unknown uncertainty ids {unknown}")
        if change_type == "CHANGE_RESEARCH_QUESTION" and not (research_question or "").strip():
            raise ToolError("CHANGE_RESEARCH_QUESTION requires the new research_question")
        previous = self.ws.directions()
        d = self._build(Direction, {
            "direction": direction, "hypothesis": hypothesis, "rationale": rationale, "modification_id": modification_id,
            "paper_ids": paper_ids or [], "change_type": change_type, "research_question": research_question,
            "confidence": confidence, "uncertainty_ids": uncertainty_ids or [],
            "previous_direction_id": previous[-1].id if previous else None,
        })
        d = self.ws.save_direction(d)
        return {"ok": True, "direction_id": d.id, "change_type": d.change_type, "previous_direction_id": d.previous_direction_id,
                "note": "The original idea and hypothesis are kept unchanged."}

    def record_hypothesis_evaluation(self, plan_id: str, verdict: str, rationale: str, next_step: str = "") -> dict:
        analysis = next((a for a in self.ws.experiment_analyses() if a.plan_id == plan_id), None)
        if analysis is None:
            raise ToolError(f"no executed and analyzed experiment for plan {plan_id!r}; hypotheses can only be evaluated against real runs")
        if verdict == "SUPPORTED" and analysis.status != "PASSED":
            raise ToolError(f"experiment {plan_id} did not pass verification ({analysis.status}); it cannot support the hypothesis. Use INCONCLUSIVE or NOT_SUPPORTED.")
        e = self._build(HypothesisEvaluation, {"plan_id": plan_id, "verdict": verdict, "rationale": rationale, "run_ids": analysis.run_ids, "next_step": next_step})
        self.ws.save_evaluation(e)
        return {"ok": True, "plan_id": plan_id, "verdict": e.verdict}

    # ================================================================ helpers

    def _loop_phase(self) -> str:
        state = self.ws.state()
        return state.loop_phase if state else ""


    def _check_ids(self, paper_ids: list[str]) -> None:
        try:
            check_paper_ids(self.ws, list(dict.fromkeys(paper_ids)))
        except EvidenceError as exc:
            raise ToolError(str(exc)) from exc

    def _current_phase(self) -> str:
        state = self.ws.state()
        if state:
            running = next((p.name for p in state.phases if p.status == "running"), None)
            if running:
                return running
        return ""


def toolkit_for(project_dir: str | Path, settings: Settings) -> ResearchToolkit:
    return ResearchToolkit(Workspace(Path(project_dir)), settings)
