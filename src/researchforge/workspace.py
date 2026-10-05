"""The research workspace: one directory per investigation.

Layout::

    <project>/
    ├── idea.yaml                raw idea + formalized IdeaAnalysis
    ├── research_state.json      phase progress, dsh session id
    ├── events.jsonl             append-only progress/audit log
    ├── search_log.jsonl         every literature query and per-source status
    ├── papers/<id>.json         retrieved paper records (provenance included)
    ├── papers/text/<id>.txt     extracted full text, when fetched
    ├── papers/analyses/<id>.json
    ├── evidence/claims/C001.json
    ├── hypotheses/              landscape.json, critique.json, gaps/, modifications/, no_gap.json
    ├── experiments/plans/E001.json, experiments/<plan>/ (working dirs)
    ├── results/                 run records and experiment analyses
    ├── reports/                 report.md, report.html
    ├── cache/http/              literature API response cache
    └── dsh/                     generated overlay and raw dsh event streams

Several processes touch a workspace (the orchestrator, the MCP server that
dsh launches, the web UI), so every record lives in its own file, writes are
atomic (write + rename), and ids are allocated with exclusive file creation.
"""

from __future__ import annotations

import json
import os
import re
import secrets
import tempfile
import threading
from collections.abc import Iterator
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

try:
    import fcntl
except ImportError:  # Windows: in-process lock only
    fcntl = None  # type: ignore[assignment]

from researchforge.schemas import (
    Claim,
    Critique,
    Direction,
    HypothesisEvaluation,
    InvestigationPlan,
    Uncertainty,
    Event,
    ExperimentAnalysis,
    ExperimentPlan,
    ExperimentRun,
    Gap,
    IdeaAnalysis,
    Landscape,
    Modification,
    NoGapFinding,
    Paper,
    PaperAnalysis,
    ResearchState,
    SearchRecord,
    utcnow,
)

M = TypeVar("M", bound=BaseModel)

_SLUG_RE = re.compile(r"[^a-z0-9]+")
_event_lock = threading.Lock()


def slugify(text: str, max_len: int = 48) -> str:
    slug = _SLUG_RE.sub("-", text.lower()).strip("-")
    return (slug[:max_len].rstrip("-") or "project")


def safe_name(record_id: str) -> str:
    """Map a record id such as ``doi:10.1/x`` to a filesystem-safe name."""
    return re.sub(r"[^A-Za-z0-9._-]", "_", record_id)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


class Workspace:
    def __init__(self, root: Path) -> None:
        self.root = Path(root).resolve()

    # ------------------------------------------------------------ creation

    @classmethod
    def create(cls, projects_dir: Path, idea: str, name: str | None = None) -> "Workspace":
        projects_dir.mkdir(parents=True, exist_ok=True)
        base = slugify(name or idea)
        candidate = projects_dir / base
        while True:
            try:
                candidate.mkdir()
                break
            except FileExistsError:
                candidate = projects_dir / f"{base}-{secrets.token_hex(2)}"
        return cls.init_at(candidate, idea)

    @classmethod
    def init_at(cls, root: Path, idea: str) -> "Workspace":
        """Initialise the layout at ``root``; an existing idea.yaml is kept."""
        ws = cls(root)
        for sub in ws.SUBDIRS:
            (ws.root / sub).mkdir(parents=True, exist_ok=True)
        if not (ws.root / "idea.yaml").exists():
            atomic_write_text(ws.root / "idea.yaml", yaml.safe_dump({"raw_idea": idea}, sort_keys=False, allow_unicode=True))
        return ws

    SUBDIRS = (
        "papers/text",
        "papers/analyses",
        "evidence/claims",
        "hypotheses/gaps",
        "hypotheses/modifications",
        "hypotheses/uncertainties",
        "hypotheses/directions",
        "experiments/plans",
        "results",
        "reports",
        "cache/http",
        "dsh",
    )

    @classmethod
    def open(cls, projects_dir: Path, project: str) -> "Workspace":
        path = Path(project)
        if not path.is_absolute() and not path.exists():
            path = projects_dir / project
        if not (path / "idea.yaml").exists():
            raise FileNotFoundError(f"no ResearchForge project at {path}")
        return cls(path)

    @property
    def name(self) -> str:
        return self.root.name

    # ------------------------------------------------------------ generic io

    def _write_model(self, path: Path, model: BaseModel) -> None:
        atomic_write_text(path, model.model_dump_json(indent=2))

    def _read_model(self, path: Path, cls: type[M]) -> M | None:
        if not path.exists():
            return None
        return cls.model_validate_json(path.read_text(encoding="utf-8"))

    def _read_dir(self, directory: Path, cls: type[M]) -> list[M]:
        if not directory.exists():
            return []
        return [cls.model_validate_json(p.read_text(encoding="utf-8")) for p in sorted(directory.glob("*.json"))]

    def allocate_id(self, directory: Path, prefix: str) -> str:
        """Allocate the next sequential id (``C001``) by exclusively creating its file."""
        directory.mkdir(parents=True, exist_ok=True)
        existing = [int(m.group(1)) for p in directory.glob(f"{prefix}*.json") if (m := re.fullmatch(rf"{prefix}(\d+)\.json", p.name))]
        n = max(existing, default=0) + 1
        while True:
            record_id = f"{prefix}{n:03d}"
            try:
                fd = os.open(directory / f"{record_id}.json", os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return record_id
            except FileExistsError:
                n += 1

    # ------------------------------------------------------------ idea

    @property
    def raw_idea(self) -> str:
        data = yaml.safe_load((self.root / "idea.yaml").read_text(encoding="utf-8")) or {}
        return data.get("raw_idea", "")

    def save_idea_analysis(self, analysis: IdeaAnalysis) -> None:
        data = {"raw_idea": self.raw_idea, "analysis": json.loads(analysis.model_dump_json())}
        atomic_write_text(self.root / "idea.yaml", yaml.safe_dump(data, sort_keys=False, allow_unicode=True))

    def idea_analysis(self) -> IdeaAnalysis | None:
        data = yaml.safe_load((self.root / "idea.yaml").read_text(encoding="utf-8")) or {}
        analysis = data.get("analysis")
        return IdeaAnalysis.model_validate(analysis) if analysis else None

    # ------------------------------------------------------------ papers

    def paper_path(self, paper_id: str) -> Path:
        return self.root / "papers" / f"{safe_name(paper_id)}.json"

    def save_paper(self, paper: Paper) -> None:
        self._write_model(self.paper_path(paper.id), paper)

    def paper(self, paper_id: str) -> Paper | None:
        return self._read_model(self.paper_path(paper_id), Paper)

    def papers(self) -> list[Paper]:
        return self._read_dir(self.root / "papers", Paper)

    def paper_count(self) -> int:
        directory = self.root / "papers"
        if not directory.exists():
            return 0
        return sum(1 for p in directory.glob("*.json"))

    def iter_papers(self) -> Iterator[Paper]:
        directory = self.root / "papers"
        if not directory.exists():
            return
        for p in sorted(directory.glob("*.json")):
            yield Paper.model_validate_json(p.read_text(encoding="utf-8"))

    def has_paper(self, paper_id: str) -> bool:
        return self.paper_path(paper_id).exists()

    def text_path(self, paper_id: str) -> Path:
        return self.root / "papers" / "text" / f"{safe_name(paper_id)}.txt"

    def has_paper_text(self, paper_id: str) -> bool:
        return self.text_path(paper_id).exists()

    def paper_text(self, paper_id: str) -> str | None:
        path = self.text_path(paper_id)
        return path.read_text(encoding="utf-8") if path.exists() else None

    def save_paper_text(self, paper_id: str, text: str) -> None:
        atomic_write_text(self.text_path(paper_id), text)

    def save_analysis(self, analysis: PaperAnalysis) -> None:
        self._write_model(self.root / "papers" / "analyses" / f"{safe_name(analysis.paper_id)}.json", analysis)

    def analyses(self) -> list[PaperAnalysis]:
        return self._read_dir(self.root / "papers" / "analyses", PaperAnalysis)

    def analysis_count(self) -> int:
        directory = self.root / "papers" / "analyses"
        if not directory.exists():
            return 0
        return sum(1 for p in directory.glob("*.json"))

    def append_search(self, record: SearchRecord) -> None:
        with open(self.root / "search_log.jsonl", "a", encoding="utf-8") as fh:
            fh.write(record.model_dump_json() + "\n")

    def searches(self) -> list[SearchRecord]:
        path = self.root / "search_log.jsonl"
        if not path.exists():
            return []
        return [SearchRecord.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def search_count(self) -> int:
        path = self.root / "search_log.jsonl"
        if not path.exists():
            return 0
        with open(path, "rb") as fh:
            return sum(1 for line in fh if line.strip())

    def claim_count(self) -> int:
        directory = self.root / "evidence" / "claims"
        if not directory.exists():
            return 0
        return sum(1 for p in directory.glob("*.json"))

    # ------------------------------------------------------------ evidence & hypotheses

    def save_claim(self, claim: Claim) -> Claim:
        directory = self.root / "evidence" / "claims"
        if not claim.id:
            claim = claim.model_copy(update={"id": self.allocate_id(directory, "C")})
        self._write_model(directory / f"{claim.id}.json", claim)
        return claim

    def claims(self) -> list[Claim]:
        return [c for c in self._read_dir_nonempty(self.root / "evidence" / "claims", Claim)]

    def _read_dir_nonempty(self, directory: Path, cls: type[M]) -> Iterator[M]:
        # Skip placeholder files created by allocate_id whose content is not yet written.
        if not directory.exists():
            return
        for p in sorted(directory.glob("*.json")):
            text = p.read_text(encoding="utf-8")
            if text.strip():
                yield cls.model_validate_json(text)

    def save_landscape(self, landscape: Landscape) -> None:
        self._write_model(self.root / "hypotheses" / "landscape.json", landscape)

    def landscape(self) -> Landscape | None:
        return self._read_model(self.root / "hypotheses" / "landscape.json", Landscape)

    def save_critique(self, critique: Critique) -> None:
        self._write_model(self.root / "hypotheses" / "critique.json", critique)

    def critique(self) -> Critique | None:
        return self._read_model(self.root / "hypotheses" / "critique.json", Critique)

    def save_gap(self, gap: Gap) -> Gap:
        directory = self.root / "hypotheses" / "gaps"
        if not gap.id:
            gap = gap.model_copy(update={"id": self.allocate_id(directory, "G")})
        self._write_model(directory / f"{gap.id}.json", gap)
        return gap

    def gaps(self) -> list[Gap]:
        return list(self._read_dir_nonempty(self.root / "hypotheses" / "gaps", Gap))

    def save_no_gap(self, finding: NoGapFinding) -> None:
        self._write_model(self.root / "hypotheses" / "no_gap.json", finding)

    def no_gap(self) -> NoGapFinding | None:
        return self._read_model(self.root / "hypotheses" / "no_gap.json", NoGapFinding)

    def save_modification(self, mod: Modification) -> Modification:
        directory = self.root / "hypotheses" / "modifications"
        if not mod.id:
            mod = mod.model_copy(update={"id": self.allocate_id(directory, "M")})
        self._write_model(directory / f"{mod.id}.json", mod)
        return mod

    def modifications(self) -> list[Modification]:
        return list(self._read_dir_nonempty(self.root / "hypotheses" / "modifications", Modification))

    # ------------------------------------------------------------ investigation loop records

    def save_plan_of_investigation(self, plan: InvestigationPlan) -> None:
        self._write_model(self.root / "hypotheses" / "investigation_plan.json", plan)

    def investigation_plan(self) -> InvestigationPlan | None:
        return self._read_model(self.root / "hypotheses" / "investigation_plan.json", InvestigationPlan)

    def save_uncertainty(self, u: Uncertainty) -> Uncertainty:
        directory = self.root / "hypotheses" / "uncertainties"
        if not u.id:
            u = u.model_copy(update={"id": self.allocate_id(directory, "U")})
        self._write_model(directory / f"{u.id}.json", u.model_copy(update={"updated_at": utcnow()}))
        return u

    def uncertainties(self) -> list[Uncertainty]:
        return list(self._read_dir_nonempty(self.root / "hypotheses" / "uncertainties", Uncertainty))

    def uncertainty(self, uid: str) -> Uncertainty | None:
        return next((u for u in self.uncertainties() if u.id == uid), None)

    def save_direction(self, d: Direction) -> Direction:
        directory = self.root / "hypotheses" / "directions"
        if not d.id:
            d = d.model_copy(update={"id": self.allocate_id(directory, "D")})
        self._write_model(directory / f"{d.id}.json", d)
        return d

    def directions(self) -> list[Direction]:
        return list(self._read_dir_nonempty(self.root / "hypotheses" / "directions", Direction))

    def save_evaluation(self, e: HypothesisEvaluation) -> None:
        self._write_model(self.root / "results" / f"{safe_name(e.plan_id)}.evaluation.json", e)

    def evaluations(self) -> list[HypothesisEvaluation]:
        return [
            HypothesisEvaluation.model_validate_json(p.read_text(encoding="utf-8"))
            for p in sorted((self.root / "results").glob("*.evaluation.json"))
        ]

    # ------------------------------------------------------------ experiments

    def save_plan(self, plan: ExperimentPlan) -> ExperimentPlan:
        directory = self.root / "experiments" / "plans"
        if not plan.id:
            plan = plan.model_copy(update={"id": self.allocate_id(directory, "E")})
        self._write_model(directory / f"{plan.id}.json", plan)
        return plan

    def plans(self) -> list[ExperimentPlan]:
        return list(self._read_dir_nonempty(self.root / "experiments" / "plans", ExperimentPlan))

    def plan(self, plan_id: str) -> ExperimentPlan | None:
        path = self.root / "experiments" / "plans" / f"{safe_name(plan_id)}.json"
        if not path.exists() or not path.read_text(encoding="utf-8").strip():
            return None
        return ExperimentPlan.model_validate_json(path.read_text(encoding="utf-8"))

    def experiment_dir(self, plan_id: str) -> Path:
        path = self.root / "experiments" / safe_name(plan_id)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def save_run(self, run: ExperimentRun) -> None:
        self._write_model(self.root / "results" / "runs" / f"{safe_name(run.id)}.json", run)

    def runs(self, plan_id: str | None = None) -> list[ExperimentRun]:
        runs = self._read_dir(self.root / "results" / "runs", ExperimentRun)
        return [r for r in runs if plan_id is None or r.plan_id == plan_id]

    def save_experiment_analysis(self, analysis: ExperimentAnalysis) -> None:
        self._write_model(self.root / "results" / f"{safe_name(analysis.plan_id)}.analysis.json", analysis)

    def experiment_analyses(self) -> list[ExperimentAnalysis]:
        return [
            ExperimentAnalysis.model_validate_json(p.read_text(encoding="utf-8"))
            for p in sorted((self.root / "results").glob("*.analysis.json"))
        ]

    # ------------------------------------------------------------ state & events

    def save_state(self, state: ResearchState) -> None:
        state.updated_at = utcnow()
        self._write_model(self.root / "research_state.json", state)

    def state(self) -> ResearchState | None:
        return self._read_model(self.root / "research_state.json", ResearchState)

    def append_event(self, kind: str, phase: str | None = None, **data) -> Event:
        path = self.root / "events.jsonl"
        with _event_lock, open(path, "a+", encoding="utf-8") as fh:
            if fcntl is not None:
                fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                fh.seek(0)
                seq = sum(1 for line in fh if line.strip())
                event = Event(seq=seq, kind=kind, phase=phase, data=data)
                fh.write(event.model_dump_json() + "\n")
                fh.flush()
            finally:
                if fcntl is not None:
                    fcntl.flock(fh, fcntl.LOCK_UN)
        return event

    def events(self, after: int = -1) -> list[Event]:
        path = self.root / "events.jsonl"
        if not path.exists():
            return []
        out = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                event = Event.model_validate_json(line)
                if event.seq > after:
                    out.append(event)
        return out

    def report_path(self, fmt: str = "md") -> Path:
        return self.root / "reports" / f"report.{fmt}"


def list_projects(projects_dir: Path) -> list[Workspace]:
    if not projects_dir.exists():
        return []
    return [Workspace(p) for p in sorted(projects_dir.iterdir()) if (p / "idea.yaml").exists()]
