"""Clients for open scholarly APIs: arXiv, OpenAlex, Semantic Scholar, Crossref.

Each client maps the provider's response to :class:`Paper` without inventing
values: a field the provider does not return stays ``None``.
"""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from typing import Protocol

from researchforge.literature.http import CachedHttp
from researchforge.schemas import Paper

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"
_ARXIV_ID_RE = re.compile(r"arxiv\.org/(?:abs|pdf)/([0-9]{4}\.[0-9]{4,5}|[a-z\-]+(?:\.[A-Z]{2})?/[0-9]{7})(?:v\d+)?", re.I)
_GITHUB_RE = re.compile(r"https?://(?:www\.)?github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", re.I)
_STOP = frozenset(
    "a an and are as at be by can for from how in into is it of on or that the this to via what when which while with without "
    "does do we our using use based towards toward".split()
)


def query_terms(query: str) -> list[str]:
    return [t for t in re.findall(r"[A-Za-z0-9][A-Za-z0-9\-]*", query.lower()) if t not in _STOP]


def strip_version(arxiv_id: str) -> str:
    return re.sub(r"v\d+$", "", arxiv_id)


def arxiv_id_from_url(url: str | None) -> str | None:
    if not url:
        return None
    m = _ARXIV_ID_RE.search(url)
    return strip_version(m.group(1)) if m else None


def github_urls(*texts: str | None) -> list[str]:
    urls: list[str] = []
    for text in texts:
        for u in _GITHUB_RE.findall(text or ""):
            u = u.rstrip(".,;)")
            if u.lower().endswith(".git"):
                u = u[:-4]
            if u not in urls:
                urls.append(u)
    return urls


def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi.strip(), flags=re.I)
    return doi.lower() or None


def clean_text(text: str | None) -> str | None:
    if not text:
        return None
    text = re.sub(r"<[^>]+>", " ", text)  # JATS / HTML tags in Crossref abstracts
    text = html.unescape(re.sub(r"\s+", " ", text)).strip()
    return text or None


def iso_date(value: str | None) -> str | None:
    """The YYYY-MM-DD prefix of a provider date, or None when the provider gives no full date."""
    return value[:10] if value and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value[:10]) else None


def paper_id(*, arxiv_id=None, doi=None, openalex_id=None, s2_id=None) -> str:
    if arxiv_id:
        return f"arxiv:{arxiv_id}"
    if doi:
        return f"doi:{doi}"
    if openalex_id:
        return f"openalex:{openalex_id}"
    if s2_id:
        return f"s2:{s2_id}"
    raise ValueError("paper has no identifier")


class SourceClient(Protocol):
    name: str

    async def search(self, query: str, limit: int, year_from: int | None = None, before: date | None = None) -> list[Paper]: ...


class ArxivClient:
    name = "arxiv"
    url = "https://export.arxiv.org/api/query"

    def __init__(self, http: CachedHttp) -> None:
        self.http = http

    async def search(self, query: str, limit: int, year_from: int | None = None, before: date | None = None) -> list[Paper]:
        terms = query_terms(query)
        if not terms:
            return []
        search_query = " AND ".join(f"all:{t}" for t in terms[:8])
        if before:
            search_query += f" AND submittedDate:[190001010000 TO {(before - timedelta(days=1)):%Y%m%d}2359]"
        resp = await self.http.get(
            self.url, {"search_query": search_query, "start": 0, "max_results": limit, "sortBy": "relevance"}
        )
        papers = self.parse(resp.text)
        if year_from:
            papers = [p for p in papers if p.year is None or p.year >= year_from]
        return papers

    @staticmethod
    def parse(xml_text: str) -> list[Paper]:
        root = ET.fromstring(xml_text)
        papers = []
        for entry in root.findall(f"{ATOM}entry"):
            abs_url = (entry.findtext(f"{ATOM}id") or "").strip()
            aid = arxiv_id_from_url(abs_url)
            title = clean_text(entry.findtext(f"{ATOM}title"))
            if not aid or not title or title.lower() == "error":
                continue
            pdf_url = next(
                (l.get("href") for l in entry.findall(f"{ATOM}link") if l.get("title") == "pdf" or l.get("type") == "application/pdf"),
                f"https://arxiv.org/pdf/{aid}",
            )
            published = entry.findtext(f"{ATOM}published") or ""
            abstract = clean_text(entry.findtext(f"{ATOM}summary"))
            comment = entry.findtext(f"{ARXIV}comment")
            journal_ref = clean_text(entry.findtext(f"{ARXIV}journal_ref"))
            papers.append(
                Paper(
                    id=paper_id(arxiv_id=aid),
                    title=title,
                    authors=[clean_text(a.findtext(f"{ATOM}name")) or "" for a in entry.findall(f"{ATOM}author")],
                    year=int(published[:4]) if published[:4].isdigit() else None,
                    published=iso_date(published),
                    venue=journal_ref or "arXiv (preprint)",
                    url=f"https://arxiv.org/abs/{aid}",
                    pdf_url=pdf_url,
                    abstract=abstract,
                    doi=normalize_doi(entry.findtext(f"{ARXIV}doi")),
                    arxiv_id=aid,
                    source="arxiv",
                    sources=["arxiv"],
                    code_urls=github_urls(abstract, comment),
                )
            )
        return papers


class OpenAlexClient:
    name = "openalex"
    url = "https://api.openalex.org/works"

    def __init__(self, http: CachedHttp, mailto: str | None = None, api_key: str | None = None) -> None:
        self.http, self.mailto, self.api_key = http, mailto, api_key

    def _params(self, extra: dict) -> dict:
        params = dict(extra)
        if self.mailto:
            params["mailto"] = self.mailto
        if self.api_key:
            params["api_key"] = self.api_key
        return params

    async def search(self, query: str, limit: int, year_from: int | None = None, before: date | None = None) -> list[Paper]:
        params = {"search": query, "per-page": limit}
        filters = [f"from_publication_date:{year_from}-01-01"] if year_from else []
        if before:
            filters.append(f"to_publication_date:{before - timedelta(days=1)}")
        if filters:
            params["filter"] = ",".join(filters)
        resp = await self.http.get(self.url, self._params(params))
        return [p for p in (self.parse_work(w) for w in resp.json().get("results", [])) if p]

    async def related(self, openalex_id: str, direction: str, limit: int) -> list[Paper]:
        """``direction`` is ``references`` (works it cites) or ``citations`` (works citing it).

        OpenAlex's ``cited_by:W`` filter selects the works W cites; ``cites:W``
        selects the works that cite W.
        """
        filter_key = "cited_by" if direction == "references" else "cites"
        params = {"filter": f"{filter_key}:{openalex_id}", "per-page": limit, "sort": "cited_by_count:desc"}
        resp = await self.http.get(self.url, self._params(params))
        return [p for p in (self.parse_work(w) for w in resp.json().get("results", [])) if p]

    async def lookup(self, *, doi: str | None = None, arxiv_id: str | None = None) -> Paper | None:
        if doi:
            resp = await self.http.get(f"{self.url}/doi:{doi}", self._params({}))
            return self.parse_work(resp.json())
        if arxiv_id:
            resp = await self.http.get(self.url, self._params({"filter": f"locations.landing_page_url:https://arxiv.org/abs/{arxiv_id}", "per-page": 1}))
            results = resp.json().get("results", [])
            return self.parse_work(results[0]) if results else None
        return None

    @staticmethod
    def abstract_from_index(index: dict | None) -> str | None:
        if not index:
            return None
        positions = [(pos, word) for word, poss in index.items() for pos in poss]
        return " ".join(word for _, word in sorted(positions)) or None

    @classmethod
    def parse_work(cls, work: dict) -> Paper | None:
        title = clean_text(work.get("display_name") or work.get("title"))
        if not title:
            return None
        oa_id = (work.get("id") or "").rsplit("/", 1)[-1] or None
        doi = normalize_doi(work.get("doi"))
        locations = work.get("locations") or []
        arxiv_id = next((a for loc in locations if (a := arxiv_id_from_url(loc.get("landing_page_url")))), None)
        primary = work.get("primary_location") or {}
        venue = ((primary.get("source") or {}).get("display_name")) or None
        best = work.get("best_oa_location") or {}
        abstract = cls.abstract_from_index(work.get("abstract_inverted_index"))
        return Paper(
            id=paper_id(arxiv_id=arxiv_id, doi=doi, openalex_id=oa_id),
            title=title,
            authors=[(a.get("author") or {}).get("display_name", "") for a in work.get("authorships") or []],
            year=work.get("publication_year"),
            published=iso_date(work.get("publication_date")),
            venue=venue,
            url=primary.get("landing_page_url") or (f"https://doi.org/{doi}" if doi else work.get("id")),
            pdf_url=best.get("pdf_url"),
            abstract=abstract,
            doi=doi,
            arxiv_id=arxiv_id,
            openalex_id=oa_id,
            source="openalex",
            sources=["openalex"],
            citation_count=work.get("cited_by_count"),
            citation_count_source="openalex" if work.get("cited_by_count") is not None else None,
            code_urls=github_urls(abstract),
        )


class SemanticScholarClient:
    name = "semantic_scholar"
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = "title,abstract,year,publicationDate,venue,authors,citationCount,externalIds,url,openAccessPdf"

    def __init__(self, http: CachedHttp, api_key: str | None = None) -> None:
        self.http, self.api_key = http, api_key

    async def search(self, query: str, limit: int, year_from: int | None = None, before: date | None = None) -> list[Paper]:
        params = {"query": query, "limit": limit, "fields": self.fields}
        if year_from:
            params["year"] = f"{year_from}-"
        if before:
            start = f"{year_from}-01-01" if year_from else ""
            params["publicationDateOrYear"] = f"{start}:{before - timedelta(days=1)}"
        headers = {"x-api-key": self.api_key} if self.api_key else None
        resp = await self.http.get(self.url, params, headers)
        return [p for p in (self.parse(d) for d in resp.json().get("data") or []) if p]

    @staticmethod
    def parse(data: dict) -> Paper | None:
        title = clean_text(data.get("title"))
        if not title:
            return None
        ext = data.get("externalIds") or {}
        arxiv_id = strip_version(ext["ArXiv"]) if ext.get("ArXiv") else None
        doi = normalize_doi(ext.get("DOI"))
        abstract = clean_text(data.get("abstract"))
        return Paper(
            id=paper_id(arxiv_id=arxiv_id, doi=doi, s2_id=data.get("paperId")),
            title=title,
            authors=[a.get("name", "") for a in data.get("authors") or []],
            year=data.get("year"),
            published=iso_date(data.get("publicationDate")),
            venue=data.get("venue") or None,
            url=data.get("url"),
            pdf_url=(data.get("openAccessPdf") or {}).get("url") or None,
            abstract=abstract,
            doi=doi,
            arxiv_id=arxiv_id,
            s2_id=data.get("paperId"),
            source="semantic_scholar",
            sources=["semantic_scholar"],
            citation_count=data.get("citationCount"),
            citation_count_source="semantic_scholar" if data.get("citationCount") is not None else None,
            code_urls=github_urls(abstract),
        )


class CrossrefClient:
    name = "crossref"
    url = "https://api.crossref.org/works"

    def __init__(self, http: CachedHttp, mailto: str | None = None) -> None:
        self.http, self.mailto = http, mailto

    async def search(self, query: str, limit: int, year_from: int | None = None, before: date | None = None) -> list[Paper]:
        params = {"query.bibliographic": query, "rows": limit}
        filters = [f"from-pub-date:{year_from}"] if year_from else []
        if before:
            filters.append(f"until-pub-date:{before - timedelta(days=1)}")
        if filters:
            params["filter"] = ",".join(filters)
        if self.mailto:
            params["mailto"] = self.mailto
        resp = await self.http.get(self.url, params)
        return [p for p in (self.parse(i) for i in resp.json().get("message", {}).get("items", [])) if p]

    @staticmethod
    def parse(item: dict) -> Paper | None:
        titles = item.get("title") or []
        title = clean_text(titles[0]) if titles else None
        doi = normalize_doi(item.get("DOI"))
        if not title or not doi:
            return None
        parts = ((item.get("issued") or {}).get("date-parts") or [[None]])[0]
        container = item.get("container-title") or []
        abstract = clean_text(item.get("abstract"))
        return Paper(
            id=paper_id(doi=doi),
            title=title,
            authors=[" ".join(x for x in (a.get("given"), a.get("family")) if x) or a.get("name", "") for a in item.get("author") or []],
            year=parts[0] if parts and isinstance(parts[0], int) else None,
            published=f"{parts[0]:04d}-{parts[1]:02d}-{parts[2]:02d}" if len(parts) == 3 and all(isinstance(x, int) for x in parts) else None,
            venue=clean_text(container[0]) if container else None,
            url=item.get("URL") or f"https://doi.org/{doi}",
            abstract=abstract,
            doi=doi,
            source="crossref",
            sources=["crossref"],
            citation_count=item.get("is-referenced-by-count"),
            citation_count_source="crossref" if item.get("is-referenced-by-count") is not None else None,
            code_urls=github_urls(abstract),
        )
