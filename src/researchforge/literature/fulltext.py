"""Full-text retrieval for open-access papers (arXiv or an open-access PDF URL).

Extracted text keeps ``[[page N]]`` markers so evidence can cite a location.
"""

from __future__ import annotations

import io
import re

from researchforge.literature.http import CachedHttp
from researchforge.schemas import Paper


class FullTextUnavailable(RuntimeError):
    pass


def pdf_url_for(paper: Paper, first_version: bool = False) -> str | None:
    """The PDF to read. ``first_version`` pins arXiv papers to v1, whose date is the paper's own publication
    date, so a later revision cannot leak work published after an evaluation cutoff."""
    if paper.arxiv_id:
        return f"https://arxiv.org/pdf/{paper.arxiv_id}{'v1' if first_version else ''}"
    return paper.pdf_url


def extract_pdf_text(data: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise FullTextUnavailable("PDF extraction needs the optional 'pypdf' package: pip install 'researchforge[pdf]'") from exc
    reader = PdfReader(io.BytesIO(data))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # pypdf raises many types on malformed pages
            text = f"[text extraction failed on this page: {type(exc).__name__}]"
        pages.append(f"[[page {i}]]\n{text}")
    return "\n\n".join(pages)


async def fetch_full_text(http: CachedHttp, paper: Paper, max_bytes: int, first_version: bool = False) -> str:
    url = pdf_url_for(paper, first_version)
    if not url:
        raise FullTextUnavailable(f"no open-access PDF is known for {paper.id}")
    resp = await http.get(url, binary=True, max_bytes=max_bytes)
    data = resp.content or b""
    if not data.startswith(b"%PDF"):
        raise FullTextUnavailable(f"{url} did not return a PDF")
    text = extract_pdf_text(data)
    if len(re.sub(r"\[\[page \d+\]\]|\s", "", text)) < 500:
        raise FullTextUnavailable(f"{url} contains too little extractable text (scanned PDF?)")
    return text


def find_passages(text: str, pattern: str, context: int = 300, limit: int = 8) -> list[dict]:
    """Case-insensitive search over extracted text, returning page-located passages."""
    try:
        regex = re.compile(pattern, re.I)
    except re.error:
        regex = re.compile(re.escape(pattern), re.I)
    out = []
    for m in regex.finditer(text):
        page_marks = list(re.finditer(r"\[\[page (\d+)\]\]", text[: m.start()]))
        page = page_marks[-1].group(1) if page_marks else "?"
        start, end = max(0, m.start() - context), min(len(text), m.end() + context)
        passage = re.sub(r"\s+", " ", text[start:end]).strip()
        out.append({"location": f"p. {page}", "passage": passage})
        if len(out) >= limit:
            break
    return out


def section_outline(text: str, limit: int = 40) -> list[dict]:
    """Guess section headings ("3 Method", "4.2 Results") with their pages."""
    outline, page = [], "1"
    for line in text.splitlines():
        pm = re.fullmatch(r"\[\[page (\d+)\]\]", line.strip())
        if pm:
            page = pm.group(1)
            continue
        if re.fullmatch(r"(\d{1,2}(\.\d{1,2})?|[A-H])\.?\s+[A-Z][A-Za-z ,:\-]{2,60}", line.strip()):
            outline.append({"heading": line.strip(), "location": f"p. {page}"})
            if len(outline) >= limit:
                break
    return outline
