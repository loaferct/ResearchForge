"""Evaluation controls on the literature layer: a publication-date cutoff and abstract corruption.

Both exist for the temporal prior-art benchmark (docs/paper/research_plan.md §4). Neither is active
unless configured. The model is never told about either; the workspace keeps a ledger so the scorer
can check for leaks and measure contamination exactly.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

from researchforge.literature.merge import paper_keys
from researchforge.schemas import Paper, utcnow

LEDGER_DIR = "benchmark"


def visible(paper: Paper, before: date | None) -> bool:
    """Whether ``paper`` may be shown under a cutoff: published strictly before ``before``.

    Without a full date, the year must be earlier than the cutoff's year; a paper with no date at all
    is hidden. Being conservative here can only hide older work, never leak newer work.
    """
    if before is None:
        return True
    if paper.published:
        return paper.published < before.isoformat()
    return paper.year is not None and paper.year < before.year


def _append(root: Path, name: str, record: dict) -> None:
    path = root / LEDGER_DIR / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps({"at": utcnow().isoformat(), **record}) + "\n")


def record_hidden(root: Path, context: str, hidden: list[Paper]) -> None:
    if hidden:
        _append(root, "hidden.jsonl", {"context": context, "papers": [{"keys": paper_keys(p), "title": p.title, "published": p.published, "year": p.year} for p in hidden]})


def _draw(seed: int, source: str, paper: Paper) -> float:
    """A deterministic uniform draw per (seed, source, paper), so a record is corrupted consistently, like a bad API entry."""
    key = paper_keys(paper)[0] if paper_keys(paper) else paper.title
    digest = hashlib.sha256(f"{seed}|{source}|{key}".encode()).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def corrupt(root: Path, source: str, papers: list[Paper], rate: float, seed: int) -> list[Paper]:
    """Swap the abstract of a ``rate`` share of ``papers`` for another paper's abstract from the same response.

    Mirrors the misplaced-metadata failure found in OpenAlex (arXiv 2605.20168) and observed for H2O.
    Every swap is written to ``benchmark/corruptions.jsonl`` with the original and injected abstracts.
    """
    if rate <= 0:
        return papers
    donors = [p for p in papers if p.abstract]
    out = []
    for i, p in enumerate(papers):
        others = [d for d in donors if d.title != p.title and d.abstract != p.abstract]
        if not p.abstract or not others or _draw(seed, source, p) >= rate:
            out.append(p)
            continue
        donor = others[int(_draw(seed + 1, source, p) * len(others))]
        _append(root, "corruptions.jsonl", {
            "source": source, "keys": paper_keys(p), "title": p.title, "donor_title": donor.title,
            "original_abstract": p.abstract, "injected_abstract": donor.abstract,
        })
        out.append(p.model_copy(update={"abstract": donor.abstract}))
    return out


def read_ledger(root: Path, name: str) -> list[dict]:
    path = root / LEDGER_DIR / name
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
