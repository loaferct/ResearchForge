"""Batch runner for the TPAD study: items x conditions x systems x seeds, with resume and scoring.

A spec (YAML) names the dataset, the systems and conditions to run, common setting overrides (budgets),
and an output directory. Each run gets its own workspace and a ``settings.json`` that both the
orchestrator and the MCP server inside dsh read, so cutoffs and ablation switches reach the tools.
Results are appended to ``<out>/results.jsonl``; a finished run is never repeated.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable

import yaml
from pydantic import BaseModel, Field

from researchforge.config import Settings
from researchforge.evaluation.tpad import CONDITIONS, Condition, TpadDataset, TpadItem, condition_settings, score_run, summarize
from researchforge import _rust
from researchforge.workspace import Workspace

log = logging.getLogger("researchforge.bench")

# The systems of docs/paper/research_plan.md §5.1, as setting overrides.
SYSTEMS: dict[str, dict] = {
    "full": {},
    "nochal": {"investigation": {"challenge_conclusions": False}},
    "norecrit": {"investigation": {"recritique_on_contradiction": False}},
    "pipe": {"investigation": {"controller_mode": "pipeline"}},
    "pipe+": {"investigation": {"controller_mode": "pipeline", "pipeline_extra_searches": 3}},
    "noint": {"literature": {"integrity_checks": False}},
}
FINISHED = ("complete", "incomplete", "awaiting_approval")


class BenchSpec(BaseModel):
    dataset: str
    out: str
    systems: list[str] = Field(default_factory=lambda: ["full", "nochal", "pipe"])
    conditions: list[Condition] = Field(default_factory=lambda: list(CONDITIONS))
    seeds: int = Field(default=1, ge=1)
    items: list[str] | None = Field(default=None, description="Restrict to these item ids.")
    settings: dict = Field(default_factory=dict, description="Overrides applied to every run (budgets, cache).")
    corruption: dict | None = Field(default=None, description="e.g. {rate: 0.25, seed: 0}; applied to every run.")

    @classmethod
    def load(cls, path: str | Path) -> "BenchSpec":
        path = Path(path)
        spec = cls.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        base = path.parent
        spec.dataset = str((base / spec.dataset).resolve()) if not Path(spec.dataset).is_absolute() else spec.dataset
        spec.out = str((base / spec.out).resolve()) if not Path(spec.out).is_absolute() else spec.out
        cache = spec.settings.get("literature", {}).get("cache_dir")
        if cache and not Path(cache).expanduser().is_absolute():
            # Runs start the MCP server inside their own directory, so a relative cache path must be pinned here.
            spec.settings["literature"]["cache_dir"] = str((base / cache).resolve())
        unknown = [s for s in spec.systems if s not in SYSTEMS]
        if unknown:
            raise ValueError(f"unknown systems {unknown}; known: {sorted(SYSTEMS)}")
        return spec


def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        out[k] = deep_merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def run_settings(base: Settings, spec: BenchSpec, item: TpadItem, condition: Condition, system: str) -> Settings:
    data = deep_merge(base.model_dump(mode="json"), spec.settings)
    data = deep_merge(data, SYSTEMS[system])
    if spec.corruption:
        data = deep_merge(data, {"literature": {"corrupt_abstracts": spec.corruption.get("rate", 0.0),
                                                "corruption_seed": spec.corruption.get("seed", 0)}})
    return condition_settings(Settings.model_validate(data), item, condition)


def run_key(item: str, condition: str, system: str, seed: int) -> str:
    return f"{item}__{condition}__{system}__s{seed}"


def planned_runs(spec: BenchSpec, ds: TpadDataset) -> list[tuple[TpadItem, Condition, str, int]]:
    items = [i for i in ds.items if spec.items is None or i.id in spec.items]
    return [(i, c, s, seed) for i in items for c in spec.conditions for s in spec.systems for seed in range(spec.seeds)]


def load_results(out: Path) -> dict[str, dict]:
    path = out / "results.jsonl"
    if not path.exists():
        return {}
    if _rust.is_available():
        res = _rust.load_results(path)
        if res is not None:
            return res
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {r["key"]: r for r in rows}


_write_lock = threading.Lock()


def append_result(out: Path, row: dict) -> None:
    with _write_lock, open(out / "results.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row) + "\n")


def run_one(base: Settings, spec: BenchSpec, item: TpadItem, condition: Condition, system: str, seed: int,
            runtime_factory: Callable[[Settings, Path], object], investigate_fn=None) -> dict:
    from researchforge.orchestrator import investigate

    investigate_fn = investigate_fn or investigate
    out = Path(spec.out)
    key = run_key(item.id, condition, system, seed)
    root = out / "runs" / key
    settings = run_settings(base, spec, item, condition, system)
    settings = settings.model_copy(update={"projects_dir": str(root.parent)})
    if (root / "idea.yaml").exists():
        ws = Workspace(root)
    else:
        root.parent.mkdir(parents=True, exist_ok=True)
        ws = Workspace.init_at(root, item.idea)
    cfg = root / "settings.json"
    cfg.write_text(settings.model_dump_json(indent=1), encoding="utf-8")
    started = time.time()
    error = None
    try:
        investigate_fn(ws, settings, runtime_factory(settings, cfg))
    except Exception as exc:  # a crashed run is recorded, not fatal to the batch
        log.exception("run failed", extra={"key": key})
        error = f"{type(exc).__name__}: {exc}"
    row = {"key": key, "item": item.id, "condition": condition, "system": system, "seed": seed,
           "model": f"{settings.model.custom.provider_id if settings.model.custom else settings.model.provider}/{settings.model.model}",
           "wall_s": round(time.time() - started, 1), "error": error, **score_run(ws, item, condition)}
    return row


def run_bench(spec: BenchSpec, base: Settings, runtime_factory: Callable[[Settings, Path], object], workers: int = 1,
              investigate_fn=None, progress: Callable[[str], None] = print) -> list[dict]:
    ds = TpadDataset.load(spec.dataset)
    out = Path(spec.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "spec.json").write_text(spec.model_dump_json(indent=1), encoding="utf-8")
    done = {k for k, r in load_results(out).items() if r.get("status") in FINISHED and not r.get("error")}
    todo = [r for r in planned_runs(spec, ds) if run_key(r[0].id, r[1], r[2], r[3]) not in done]
    progress(f"{len(done)} runs already finished; {len(todo)} to run with {workers} worker(s)")
    rows = []
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        futures = {pool.submit(run_one, base, spec, *r, runtime_factory, investigate_fn): r for r in todo}
        for fut in as_completed(futures):
            row = fut.result()
            append_result(out, row)
            rows.append(row)
            progress(f"{row['key']}: status={row['status']} verdict={row['verdict']} tool_calls={row['cost']['tool_calls']} "
                     f"wall={row['wall_s']}s" + (f" ERROR {row['error']}" if row["error"] else ""))
    return rows


def score_bench(spec: BenchSpec) -> dict:
    """Latest result per run, summarised per system (leaked prepub runs excluded)."""
    results = [r for r in load_results(Path(spec.out)).values() if not r.get("error")]
    by_system: dict[str, list[dict]] = {}
    for r in results:
        by_system.setdefault(r["system"], []).append(r)
    return {system: summarize(rows) for system, rows in sorted(by_system.items())}
