"""Evidence validation: the rules that keep claims tied to retrieved sources.

Rules enforced when a claim, gap or critique is recorded:

* Every referenced paper id must be a paper this investigation retrieved.
* ``direct`` support requires a verbatim quote that is found (after
  whitespace/typography normalisation) in the stored abstract or full text.
* A claim of kind ``evidence`` needs at least one verified quote.
* A claim of kind ``inference`` needs at least one evidence item.
* ``experimental`` claims must reference a recorded experiment run.
* ``hypothesis`` claims may have no evidence; they are reported as untested.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

from researchforge.schemas import Claim, EvidenceItem
from researchforge.workspace import Workspace

_DASHES = dict.fromkeys(map(ord, "‐‑‒–—−"), "-")
_QUOTES = {ord("‘"): "'", ord("’"): "'", ord("“"): '"', ord("”"): '"'}
MIN_QUOTE_CHARS = 20


class EvidenceError(ValueError):
    """A record violates an evidence rule. The message is shown to the model."""


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(_DASHES).translate(_QUOTES)
    text = re.sub(r"-\s*\n\s*", "", text)  # de-hyphenate line breaks from PDF extraction
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def quote_in(quote: str, haystack: str) -> bool:
    q = normalize(quote).strip(" .,;:\"'")
    if len(q) < MIN_QUOTE_CHARS:
        return False
    h = normalize(haystack)
    if q in h:
        return True
    # Tolerate ellipses: every fragment must appear, in order.
    parts = [p.strip(" .,;:") for p in re.split(r"\s*(?:\.\.\.|…)\s*", q) if p.strip(" .,;:")]
    if len(parts) > 1 and all(len(p) >= 8 for p in parts):
        pos = 0
        for p in parts:
            idx = h.find(p, pos)
            if idx < 0:
                return False
            pos = idx + len(p)
        return True
    return False


@dataclass
class EvidenceCheck:
    items: list[EvidenceItem]
    warnings: list[str] = field(default_factory=list)


def check_paper_ids(ws: Workspace, paper_ids: list[str], what: str = "paper_ids") -> None:
    unknown = [pid for pid in paper_ids if not ws.has_paper(pid)]
    if unknown:
        raise EvidenceError(
            f"{what} references papers that were never retrieved in this investigation: {unknown}. "
            "Use ids returned by search_papers/list_papers; do not invent papers."
        )


def verify_items(ws: Workspace, items: list[EvidenceItem]) -> EvidenceCheck:
    checked: list[EvidenceItem] = []
    warnings: list[str] = []
    run_ids = {r.id for r in ws.runs()}
    for i, item in enumerate(items):
        if item.paper_id is None and item.experiment_run_id is None:
            raise EvidenceError(f"evidence[{i}] must reference a paper_id or an experiment_run_id")
        if item.experiment_run_id is not None and item.experiment_run_id not in run_ids:
            raise EvidenceError(f"evidence[{i}] references unknown experiment run {item.experiment_run_id!r}")
        verified, note = False, None
        if item.paper_id is not None:
            paper = ws.paper(item.paper_id)
            if paper is None:
                raise EvidenceError(
                    f"evidence[{i}] cites {item.paper_id!r}, which was never retrieved. Only cite ids from search_papers/list_papers."
                )
            if item.quote:
                sources = [("abstract", paper.abstract or "")]
                text = ws.paper_text(item.paper_id)
                if text:
                    sources.append(("full text", text))
                found = next((label for label, hay in sources if hay and quote_in(item.quote, hay)), None)
                if found == "abstract" and paper.metadata_warnings:
                    # The stored abstract may belong to another work; only the paper's own text can confirm the quote.
                    if item.support == "direct":
                        raise EvidenceError(
                            f"evidence[{i}] quotes the abstract of {item.paper_id}, but that abstract is flagged "
                            f"({paper.metadata_warnings[0]}). Call fetch_paper_text and quote the paper's own text, or mark support 'indirect'."
                        )
                    note = f"quote found only in a flagged abstract ({paper.metadata_warnings[0]})"
                elif found:
                    verified, note = True, f"quote found in {found}"
                else:
                    note = "quote not found in retrieved abstract/full text"
            else:
                note = "no quote provided"
            if item.support == "direct" and not verified:
                hint = "" if paper.has_full_text else " Call fetch_paper_text first if the passage is not in the abstract."
                raise EvidenceError(
                    f"evidence[{i}] claims direct support from {item.paper_id} but its quote "
                    f"({'missing' if not item.quote else 'not found verbatim'}) could not be verified. "
                    f"Provide an exact quote of at least {MIN_QUOTE_CHARS} characters, or mark support as 'indirect'/'weak'.{hint}"
                )
            if item.quote and not verified:
                warnings.append(f"evidence[{i}]: {note}; recorded as unverified")
        else:
            verified, note = True, "experiment run recorded by ResearchForge"
        checked.append(item.model_copy(update={"verified": verified, "verification_note": note}))
    return EvidenceCheck(checked, warnings)


def validate_claim(ws: Workspace, claim: Claim) -> tuple[Claim, list[str]]:
    check = verify_items(ws, claim.evidence)
    items = check.items
    if claim.kind == "evidence" and not any(i.verified and i.paper_id for i in items):
        raise EvidenceError(
            "a claim of kind 'evidence' needs at least one verified quote from a retrieved paper. "
            "Record it as kind 'inference' if it is your conclusion from the sources."
        )
    if claim.kind == "inference" and not items:
        raise EvidenceError("a claim of kind 'inference' must list the evidence it is derived from")
    if claim.kind == "experimental" and not any(i.experiment_run_id for i in items):
        raise EvidenceError("a claim of kind 'experimental' must reference an experiment_run_id")
    return claim.model_copy(update={"evidence": items}), check.warnings


@dataclass
class GroundingReport:
    total: int
    grounded: int
    by_kind: dict[str, int]
    ungrounded_ids: list[str]

    @property
    def rate(self) -> float:
        return self.grounded / self.total if self.total else 0.0


def grounding(claims: list[Claim]) -> GroundingReport:
    """A claim is grounded when it has at least one verified evidence item."""
    by_kind: dict[str, int] = {}
    grounded, ungrounded = 0, []
    considered = 0
    for c in claims:
        by_kind[c.kind] = by_kind.get(c.kind, 0) + 1
        if c.kind in ("hypothesis", "assumption"):  # stated as untested; never counted as grounded evidence
            continue
        considered += 1
        if any(i.verified for i in c.evidence):
            grounded += 1
        else:
            ungrounded.append(c.id)
    return GroundingReport(total=considered, grounded=grounded, by_kind=by_kind, ungrounded_ids=ungrounded)
