"""Read-only GitHub inspection: find implementation evidence for papers.

ResearchForge never writes to GitHub. Signals extracted from a README are
keyword matches, reported as such.
"""

from __future__ import annotations

import base64
import re

from pydantic import BaseModel, Field

from researchforge.literature.http import CachedHttp, HttpError

API = "https://api.github.com"

BENCHMARK_TERMS = (
    "LongBench", "RULER", "Needle", "NIAH", "InfiniteBench", "L-Eval", "PG-19", "PG19", "WikiText", "C4", "MMLU",
    "GSM8K", "HumanEval", "MT-Bench", "ShareGPT", "LMSYS", "SQuAD", "HellaSwag", "ARC", "BigBench", "HELM",
    "ImageNet", "CIFAR", "COCO", "GLUE", "SuperGLUE", "SWE-bench", "ZeroSCROLLS", "SCROLLS",
)
MODEL_TERMS = (
    "Llama", "LLaMA", "Mistral", "Mixtral", "Qwen", "DeepSeek", "Gemma", "Phi", "OPT", "Falcon", "Vicuna",
    "GPT-2", "GPT-J", "GPT-NeoX", "Pythia", "BLOOM", "MPT", "Yi", "InternLM", "ChatGLM",
)
REPRO_FILES = {
    "requirements.txt": "pinned Python requirements",
    "environment.yml": "conda environment",
    "pyproject.toml": "Python project metadata",
    "setup.py": "setup script",
    "Dockerfile": "container build",
    "Makefile": "make targets",
    "scripts": "scripts directory",
    "configs": "configuration directory",
    "LICENSE": "license file",
}


class RepoSummary(BaseModel):
    full_name: str
    url: str
    description: str | None = None
    stars: int | None = None
    language: str | None = None
    topics: list[str] = Field(default_factory=list)
    license: str | None = None
    pushed_at: str | None = None
    archived: bool | None = None


class RepoInspection(RepoSummary):
    languages: dict[str, int] = Field(default_factory=dict)
    root_files: list[str] = Field(default_factory=list)
    readme_excerpt: str = ""
    mentioned_arxiv_ids: list[str] = Field(default_factory=list)
    benchmarks_mentioned: list[str] = Field(default_factory=list)
    models_mentioned: list[str] = Field(default_factory=list)
    reproducibility_signals: list[str] = Field(default_factory=list)
    signal_basis: str = "keyword matches in README and root file names (heuristic)"


def _parse_repo(data: dict) -> RepoSummary:
    return RepoSummary(
        full_name=data["full_name"],
        url=data.get("html_url") or f"https://github.com/{data['full_name']}",
        description=data.get("description"),
        stars=data.get("stargazers_count"),
        language=data.get("language"),
        topics=data.get("topics") or [],
        license=(data.get("license") or {}).get("spdx_id"),
        pushed_at=data.get("pushed_at"),
        archived=data.get("archived"),
    )


def repo_name_from_url(url: str) -> str | None:
    m = re.search(r"github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", url)
    return m.group(1).removesuffix(".git") if m else None


class GitHubClient:
    def __init__(self, http: CachedHttp, token: str | None = None) -> None:
        self.http = http
        self.headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def search(self, query: str, limit: int = 5) -> list[RepoSummary]:
        resp = await self.http.get(f"{API}/search/repositories", {"q": query, "per_page": limit, "sort": "stars"}, self.headers)
        return [_parse_repo(item) for item in resp.json().get("items", [])[:limit]]

    async def inspect(self, full_name: str) -> RepoInspection:
        repo = (await self.http.get(f"{API}/repos/{full_name}", headers=self.headers)).json()
        summary = _parse_repo(repo)
        languages = (await self.http.get(f"{API}/repos/{full_name}/languages", headers=self.headers)).json()
        try:
            contents = (await self.http.get(f"{API}/repos/{full_name}/contents/", headers=self.headers)).json()
            root_files = [c["name"] for c in contents if isinstance(c, dict)]
        except HttpError:
            root_files = []
        readme = ""
        try:
            data = (await self.http.get(f"{API}/repos/{full_name}/readme", headers=self.headers)).json()
            if data.get("encoding") == "base64":
                readme = base64.b64decode(data.get("content", "")).decode("utf-8", "replace")
        except HttpError:
            readme = ""
        lower = readme.lower()
        signals = [f"{name}: {desc}" for name, desc in REPRO_FILES.items() if name in root_files]
        if re.search(r"pip install|conda (env )?create|docker (build|run)", lower):
            signals.append("README contains installation commands")
        if re.search(r"python .*\.py|bash .*\.sh|torchrun|accelerate launch", lower):
            signals.append("README contains run commands")
        return RepoInspection(
            **summary.model_dump(),
            languages=languages if isinstance(languages, dict) else {},
            root_files=root_files[:60],
            readme_excerpt=readme[:4000],
            mentioned_arxiv_ids=sorted(set(re.findall(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", readme))),
            benchmarks_mentioned=[t for t in BENCHMARK_TERMS if re.search(rf"(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])", readme)],
            models_mentioned=[t for t in MODEL_TERMS if re.search(rf"(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])", readme)],
            reproducibility_signals=signals,
        )
