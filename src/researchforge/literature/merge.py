"""Deduplication across sources and heuristic relevance scoring."""

from __future__ import annotations

import re

from researchforge.literature.sources import query_terms
from researchforge.schemas import Paper


DISAGREEMENT = 0.2  # word-set Jaccard below which two abstracts are treated as describing different works
_NAME_RE = re.compile(r"[^a-z0-9]")


def _words(text: str) -> set[str]:
    return {t for t in query_terms(text) if len(t) > 3}


def abstract_overlap(a: str, b: str) -> float:
    wa, wb = _words(a), _words(b)
    return len(wa & wb) / len(wa | wb) if wa and wb else 1.0


def title_name(title: str) -> str | None:
    """The method name in titles like 'SnapKV: LLM Knows ...' (short prefix before a colon), normalised."""
    if ":" not in title:
        return None
    prefix = title.split(":", 1)[0]
    if len(prefix.split()) > 3:
        return None
    name = _NAME_RE.sub("", prefix.lower().replace("$", "").replace("_", ""))
    return name if len(name) >= 2 else None


def title_fit(title: str, abstract: str) -> float:
    """Share of distinctive title words found in the abstract, plus 1 if the title's method name appears."""
    words = _words(title)
    fit = len(words & _words(abstract)) / len(words) if words else 0.0
    name = title_name(title)
    if name and name in _NAME_RE.sub("", abstract.lower()):
        fit += 1.0
    return fit


def refresh_warnings(paper: Paper, integrity: bool = True) -> Paper:
    """Set the abstract's source and recompute the single-source warning for the abstract now stored.

    With ``integrity`` off (ablation), no warning is kept or added.
    """
    source = paper.abstract_source or (paper.source if paper.abstract else None)
    updated = paper.model_copy(update={"abstract_source": source})
    if not integrity:
        return updated.model_copy(update={"metadata_warnings": []})
    kept = [w for w in paper.metadata_warnings if "never mentions" not in w]
    return updated.model_copy(update={"metadata_warnings": list(dict.fromkeys(kept + consistency_warnings(updated)))})


def consistency_warnings(paper: Paper) -> list[str]:
    """Single-source check: an abstract that never names the method in the title may belong to another work."""
    name = title_name(paper.title)
    if paper.abstract and name and name not in _NAME_RE.sub("", paper.abstract.lower()):
        return [f"abstract (from {paper.abstract_source or paper.source}) never mentions '{paper.title.split(':', 1)[0].strip()}'; it may belong to another work"]
    return []


def title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())


def paper_keys(p: Paper) -> list[str]:
    return _keys(p)


def _keys(p: Paper) -> list[str]:
    keys = []
    if p.arxiv_id:
        keys.append(f"arxiv:{p.arxiv_id}")
    if p.doi:
        keys.append(f"doi:{p.doi}")
    tk = title_key(p.title)
    if len(tk) >= 20:
        keys.append(f"title:{tk}")
    return keys


def merge_into(base: Paper, other: Paper, keep_id: bool = False, integrity: bool = True) -> Paper:
    """Fill ``base``'s missing fields from ``other`` and union provenance.

    Identity fields prefer arXiv, then DOI, unless ``keep_id`` is set (a paper
    already shown to the model keeps its id). A citation count is kept together
    with the source that reported it; counts from different sources are never
    mixed or averaged. The publication date is the earliest any source reports.
    With ``integrity`` off (ablation), disagreeing abstracts are not detected
    and the longer abstract wins.
    """
    update: dict = {}
    for field in ("venue", "year", "published", "url", "pdf_url", "doi", "arxiv_id", "openalex_id", "s2_id"):
        if getattr(base, field) in (None, "") and getattr(other, field) not in (None, ""):
            update[field] = getattr(other, field)
    if base.venue == "arXiv (preprint)" and other.venue and other.venue != "arXiv (preprint)":
        update["venue"] = other.venue
    if base.published and other.published and other.published < base.published:
        update["published"] = other.published
    base_abs, other_abs = base.abstract or "", other.abstract or ""
    warnings = list(dict.fromkeys(base.metadata_warnings + other.metadata_warnings))
    if other_abs and not base_abs:
        update["abstract"], update["abstract_source"] = other_abs, other.abstract_source or other.source
    elif base_abs and other_abs and not integrity:
        if len(other_abs) > len(base_abs) * 1.5:
            update["abstract"], update["abstract_source"] = other_abs, other.abstract_source or other.source
    elif base_abs and other_abs:
        fit_base, fit_other = title_fit(base.title, base_abs), title_fit(base.title, other_abs)
        if abstract_overlap(base_abs, other_abs) < DISAGREEMENT:
            # Sources disagree about the abstract: keep the one consistent with the title and say so.
            keep_other = fit_other > fit_base
            chosen = other if keep_other else base
            warnings.append(
                f"abstracts from {base.abstract_source or base.source} and {other.abstract_source or other.source} disagree; "
                f"kept the one from {chosen.abstract_source or chosen.source}, which matches the title better"
            )
            if keep_other:
                update["abstract"], update["abstract_source"] = other_abs, other.abstract_source or other.source
        elif len(other_abs) > len(base_abs) * 1.5 and fit_other >= fit_base:
            update["abstract"], update["abstract_source"] = other_abs, other.abstract_source or other.source
    update["metadata_warnings"] = warnings
    if base.citation_count is None and other.citation_count is not None:
        update["citation_count"] = other.citation_count
        update["citation_count_source"] = other.citation_count_source
    if not base.authors and other.authors:
        update["authors"] = other.authors
    update["sources"] = sorted(set(base.sources) | set(other.sources))
    update["queries"] = list(dict.fromkeys(base.queries + other.queries))
    update["code_urls"] = list(dict.fromkeys(base.code_urls + other.code_urls))
    merged = base.model_copy(update=update)
    if keep_id:
        return merged
    arxiv_id = merged.arxiv_id
    if arxiv_id and not merged.id.startswith("arxiv:"):
        merged = merged.model_copy(update={"id": f"arxiv:{arxiv_id}"})
    elif merged.doi and merged.id.split(":", 1)[0] in ("openalex", "s2"):
        merged = merged.model_copy(update={"id": f"doi:{merged.doi}"})
    return merged


def dedupe(papers: list[Paper], integrity: bool = True) -> list[Paper]:
    out: list[Paper] = []
    index: dict[str, int] = {}
    for p in papers:
        hit = next((index[k] for k in _keys(p) if k in index), None)
        if hit is None:
            out.append(p)
            hit = len(out) - 1
        else:
            out[hit] = merge_into(out[hit], p, integrity=integrity)
        for k in _keys(out[hit]):
            index[k] = hit
    return out


def relevance(paper: Paper, terms: list[str]) -> float:
    """Heuristic lexical relevance in [0, 1].

    The share of distinct idea/query terms that occur in the title (weight 2)
    or abstract (weight 1). It is a ranking signal for triage only; the agent's
    paper analysis decides actual relevance.
    """
    distinct = list(dict.fromkeys(t for t in terms if len(t) > 2))
    if not distinct:
        return 0.0
    title = set(query_terms(paper.title))
    abstract = set(query_terms(paper.abstract or ""))
    score = sum(2.0 if t in title else 1.0 if t in abstract else 0.0 for t in distinct)
    return round(score / (2.0 * len(distinct)), 4)
