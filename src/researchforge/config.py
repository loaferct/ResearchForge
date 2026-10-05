"""ResearchForge settings.

Settings come from, in increasing precedence: schema defaults, a TOML file
(``--config``, ``$RESEARCHFORGE_CONFIG`` or ``./researchforge.toml``), and
``RF_*`` environment variables for the most commonly changed values.
Credentials are never stored in settings; only the *names* of environment
variables that hold them.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

DEFAULT_DSH_VERSION = "0.1.7-rc.2"
SOURCES = ("arxiv", "openalex", "semantic_scholar", "crossref")
Source = Literal["arxiv", "openalex", "semantic_scholar", "crossref"]


class CustomEndpoint(BaseModel):
    """An OpenAI-compatible model server routed through dsh's ``llm-pi-ai`` adapter.

    Use this for self-hosted open-weight models (vLLM, SGLang, Ollama,
    llama.cpp server) or for gateways that host them.
    """

    provider_id: str = Field(pattern=r"^[a-z][a-z0-9-]*$")
    base_url: str
    api: Literal["openai-completions", "openai-responses", "anthropic-messages"] = "openai-completions"
    api_key_env: str | None = Field(
        default=None,
        description="Name of the environment variable holding the key. OpenAI-compatible servers need one even if unused.",
    )
    models: list[str] = Field(min_length=1)
    context_window: int | None = None
    max_tokens: int | None = None


class ModelSettings(BaseModel):
    provider: str = "deepseek-official"
    model: str = "deepseek-flash"
    reasoning_effort: str | None = None
    custom: CustomEndpoint | None = None


class DshSettings(BaseModel):
    command: list[str] | None = Field(
        default=None,
        description="argv prefix that launches dsh. Default: `dsh` on PATH, else `npx -y @deepseek-ai/dsh@<version>`.",
    )
    version: str = DEFAULT_DSH_VERSION
    home: str = "~/.researchforge/dsh-home"
    profile: str = "headless"
    phase_timeout_s: float = 1800.0
    extra_patches: list[str] = Field(default_factory=list)
    disable_tools: list[str] = Field(
        default_factory=lambda: [
            "tool-bash",
            "tool-pwsh",
            "tool-fs",
            "tool-web",
            "tool-jobs",
            "tool-subagent",
            "tool-subagent-fork",
            "tool-workflow",
        ]
    )
    disable_telemetry: bool = True

    def resolved_command(self) -> list[str]:
        if self.command:
            return list(self.command)
        if shutil.which("dsh"):
            return ["dsh"]
        return ["npx", "-y", f"@deepseek-ai/dsh@{self.version}"]

    def resolved_home(self) -> Path:
        return Path(os.path.expanduser(self.home)).resolve()


class LiteratureSettings(BaseModel):
    sources: list[Source] = Field(default_factory=lambda: list(SOURCES))
    max_results_per_source: int = Field(default=10, ge=1, le=50)
    timeout_s: float = 30.0
    max_retries: int = Field(default=4, ge=0, le=10)
    max_backoff_s: float = 40.0
    contact_email: str | None = Field(
        default=None, description="Sent as `mailto` to OpenAlex/Crossref polite pools when set."
    )
    semantic_scholar_api_key_env: str = "SEMANTIC_SCHOLAR_API_KEY"
    openalex_api_key_env: str = "OPENALEX_API_KEY"
    github_token_env: str = "GITHUB_TOKEN"
    max_pdf_bytes: int = 40_000_000
    cache_dir: str | None = Field(
        default=None, description="Shared HTTP cache for literature APIs (default: per project). Benchmark runs share one so every system sees the same responses."
    )
    integrity_checks: bool = Field(default=True, description="Detect mismatched abstracts across and within sources (docs/AGENT_LOOP.md, Source integrity).")
    # Evaluation controls (docs/paper/research_plan.md). Leave unset for normal use.
    published_before: date | None = Field(
        default=None, description="Hide every work published on or after this date (temporal benchmark cutoff). GitHub tools are disabled while it is set."
    )
    corrupt_abstracts: float = Field(default=0.0, ge=0.0, le=1.0, description="Share of retrieved records whose abstract is swapped for another's (robustness study only).")
    corruption_seed: int = 0


class InvestigationSettings(BaseModel):
    min_papers: int = Field(default=8, ge=1)
    min_queries: int = Field(default=2, ge=1)
    papers_to_analyze: int = Field(default=8, ge=1)
    max_phase_attempts: int = Field(default=2, ge=1, le=5)
    min_modifications: int = 2
    max_modifications: int = 5
    # Investigation-loop budgets: safety stops, not the normal exit (see docs/AGENT_LOOP.md).
    max_iterations: int = Field(default=40, ge=1)
    max_tool_calls: int = Field(default=600, ge=1)
    max_searches: int = Field(default=30, ge=1)
    max_papers: int = Field(default=150, ge=1)
    time_limit_s: float = Field(default=4 * 3600, gt=0)
    max_critiques: int = Field(default=3, ge=1)
    recritique_after_papers: int = Field(default=6, ge=1, description="Re-critique when this many papers arrived since the last critique.")
    max_uncertainty_attempts: int = Field(default=2, ge=1)
    max_action_retries: int = Field(default=2, ge=1, description="Consecutive no-progress runs before an action is blocked.")
    runtime_retries: int = Field(default=2, ge=0, description="Retries of a failed model/runtime turn before the run stops.")
    runtime_retry_backoff_s: float = Field(default=5.0, ge=0)
    max_tokens: int = Field(default=0, ge=0, description="Token budget across all steps (0 = unlimited); counted from provider usage reports.")
    max_experiment_runs: int = Field(default=3, ge=0, description="Experiment executions after which the loop stops proposing new experiments.")
    # Action selection (docs/AGENT_LOOP.md): score = importance * expected_gain * relevance * deficiency / cost
    action_costs: dict[str, float] = Field(default_factory=lambda: {
        "SEARCH": 1.0, "READ": 2.0, "COMPARE": 1.5, "VERIFY": 1.5, "CHALLENGE": 1.5, "INVESTIGATE_GAP": 1.5,
        "REFINE": 1.0, "PLAN_EXPERIMENT": 1.0,
    }, description="Relative cost estimates per action (roughly: expected tool calls and model effort).")
    min_action_score: float = Field(default=0.15, ge=0, description="Below this best score, further investigation is judged not worthwhile.")
    diminishing_window: int = Field(default=3, ge=1, description="Consecutive investigation steps inspected for diminishing returns.")
    diminishing_threshold: float = Field(default=0.0, ge=0, description="Total information gain over the window at or below which investigation stops.")
    challenge_conclusions: bool = Field(default=True, description="Search for contradictory work against the critique, gaps and new directions.")
    # Ablation switches (docs/paper/research_plan.md §5.1).
    recritique_on_contradiction: bool = Field(default=True, description="Re-run CRITIQUE when a challenge weakens or refutes a conclusion recorded after it.")
    controller_mode: Literal["adaptive", "pipeline"] = Field(
        default="adaptive", description="'pipeline' runs the fixed coverage sequence once and finalizes, without uncertainty-driven investigation."
    )
    pipeline_extra_searches: int = Field(default=0, ge=0, description="Pipeline mode only: additional SEARCH/READ rounds after the first critique (compute-matched baseline).")


class ExperimentSettings(BaseModel):
    backend: Literal["local", "docker"] = "local"
    docker_image: str = "python:3.12-slim"
    docker_network: str = "none"
    timeout_s: float = 3600.0
    env_passthrough: list[str] = Field(default_factory=lambda: ["PATH", "HOME", "LANG", "CUDA_VISIBLE_DEVICES"])
    large_improvement_threshold: float = Field(
        default=0.5, description="Relative improvement over baseline above which a result is flagged for review."
    )


class Settings(BaseModel):
    projects_dir: str = "./research_projects"
    model: ModelSettings = Field(default_factory=ModelSettings)
    dsh: DshSettings = Field(default_factory=DshSettings)
    literature: LiteratureSettings = Field(default_factory=LiteratureSettings)
    investigation: InvestigationSettings = Field(default_factory=InvestigationSettings)
    experiments: ExperimentSettings = Field(default_factory=ExperimentSettings)
    log_level: str = "INFO"

    def resolved_projects_dir(self) -> Path:
        return Path(os.path.expanduser(self.projects_dir)).resolve()


_ENV_OVERRIDES: dict[str, tuple[str, ...]] = {
    "RF_PROJECTS_DIR": ("projects_dir",),
    "RF_PROVIDER": ("model", "provider"),
    "RF_MODEL": ("model", "model"),
    "RF_REASONING_EFFORT": ("model", "reasoning_effort"),
    "RF_DSH_HOME": ("dsh", "home"),
    "RF_DSH_VERSION": ("dsh", "version"),
    "RF_CONTACT_EMAIL": ("literature", "contact_email"),
    "RF_LOG_LEVEL": ("log_level",),
}


def config_path(explicit: str | Path | None = None) -> Path | None:
    """The settings file in effect: ``explicit``, ``$RESEARCHFORGE_CONFIG`` or ``./researchforge.toml``."""
    return _config_path(explicit)


def _config_path(explicit: str | Path | None) -> Path | None:
    if explicit:
        return Path(explicit)
    env = os.environ.get("RESEARCHFORGE_CONFIG")
    if env:
        return Path(env)
    local = Path("researchforge.toml")
    return local if local.exists() else None


def load_dotenv(path: str | Path = ".env", environ: dict[str, str] | None = None) -> list[str]:
    """Read ``KEY=value`` lines from a local, gitignored ``.env`` into the environment.

    Variables already set are left alone. Returns the names that were set (never the values).
    Credentials stay in the environment; dsh reads them from there.
    """
    environ = os.environ if environ is None else environ
    path = Path(path)
    if not path.is_file():
        return []
    loaded = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.removeprefix("export ").split("=", 1)
        key, value = key.strip(), value.strip().strip("'\"")
        if key and value and key not in environ:
            environ[key] = value
            loaded.append(key)
    return loaded


def load_settings(path: str | Path | None = None, env: dict[str, str] | None = None) -> Settings:
    env = dict(os.environ) if env is None else env
    data: dict = {}
    cfg = _config_path(path)
    if cfg is not None:
        with open(cfg, "rb") as fh:
            data = json.load(fh) if cfg.suffix == ".json" else tomllib.load(fh)
    for var, keys in _ENV_OVERRIDES.items():
        value = env.get(var)
        if not value:
            continue
        node = data
        for key in keys[:-1]:
            node = node.setdefault(key, {})
        node[keys[-1]] = value
    if env.get("RF_DSH_COMMAND"):
        data.setdefault("dsh", {})["command"] = env["RF_DSH_COMMAND"].split()
    return Settings.model_validate(data)
