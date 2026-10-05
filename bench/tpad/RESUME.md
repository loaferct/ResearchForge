# TPAD pilot: status and how to resume

Stopped cleanly on 2026-09-30 so the computer could be shut down.

## Status

**Stage 1:** 8 of 104 runs finished (items 2609.12230 and 2609.11572, all four runs each).

**Two runs in progress** resume from their last completed turn:
- `T-2609.11446__scooped__full__s0` (turn 6)
- `T-2609.11446__scooped__nochal__s0` (turn 2)

**Stage 2** (the `pipe` system, 52 runs) has not started.

**Agent model:** `nemotron-3-super` on Ollama Cloud. The key is in `.env` and the endpoint in `researchforge.toml`, both gitignored.

**Other runs, excluded from analysis:**
- `runs-calib`: DeepSeek calibration run.
- `runs-deepseek-stopped`: DeepSeek runs stopped before completion.
- `runs-nemotron-45min-excluded`: runs under the old caps.

The reasons are in `docs/paper/research_plan.md` §10.

## Resume (from the project root)

```sh
cd /Users/kingsofttech/KINGSOFT-PROJECTS/LF
# Stage 1: restarts the runner if it dies; finished runs are never repeated.
nohup sh bench/tpad/watchdog.sh bench/tpad/pilot-stage1.yaml 104 > bench/tpad/watchdog.log 2>&1 &
# When stage 1 is done, run stage 2 (adds the `pipe` system; finished runs are skipped):
#   nohup sh bench/tpad/watchdog.sh bench/tpad/pilot.yaml 156 > bench/tpad/watchdog-stage2.log 2>&1 &
```

## Check progress

```sh
wc -l bench/tpad/runs-pilot/results.jsonl          # finished runs
.venv/bin/researchforge bench score bench/tpad/pilot.yaml
```

## Analyse and build the paper

```sh
.venv/bin/python scripts/tpad_analyze.py bench/tpad/runs-pilot --paper docs/paper/latex \
    --items bench/tpad/items.yaml --exclude-items T-2609.12230
cd docs/paper/latex && tectonic -X compile main.tex
```

The results, discussion and abstract sections are still placeholders. They are to be written only from `analysis.json` and the generated tables.
