# Evaluating ResearchForge

ResearchForge is evaluated on what it did, not on whether its prose sounds convincing. Run:

```sh
researchforge eval <project> --ground-truth kv-cache --k 5,10,20 --gap-sheet
```

The output is JSON. The web API also serves it at `/api/projects/<project>/eval?ground_truth=kv-cache`.

## Metrics

| Area | Metric | Source |
|---|---|---|
| Literature retrieval | precision@k and recall@k against a curated relevant set, for two rankings: `heuristic_relevance` (lexical score at retrieval) and `agent_tiers` (the agent's own relevance tiers from paper analysis); overall recall; list of missed papers | `papers/`, `papers/analyses/` |
| Claim grounding | share of evidence and inference claims with at least one verified source; ungrounded claim ids; counts by kind | `evidence/claims/` |
| Experiment planning | per plan, the presence of: ≥2 baselines, metrics, datasets/workloads, controls, ablations, failure conditions, confounders addressed, hardware, software environment, reproducibility notes, expected outcomes | `experiments/plans/` |
| Agent efficiency | tool calls (total and per tool), failed tool calls, duplicate searches, attempts per phase, token usage reported by dsh, wall-clock duration | `events.jsonl`, `search_log.jsonl`, `research_state.json` |
| Research-gap quality | no automatic metric; `--gap-sheet` exports each gap with its evidence and blank 1–5 rating fields (evidence support, novelty, actionability) for expert review | `hypotheses/gaps/` |

## Ground-truth datasets

Datasets live in `src/researchforge/evaluation/datasets/`. Each entry names a paper by arXiv id, DOI or exact title.

`kv-cache.yaml` covers the demo idea (request-aware dynamic KV-cache management). It lists 11 papers, and every entry was checked against OpenAlex on 2026-09-28. The set is not exhaustive: a relevant paper outside it counts as a miss in precision@k, so precision is a lower bound.

To add a dataset, write a YAML file with `name`, `idea`, `notes` (how and when entries were verified) and `relevant`. Verify each entry against a bibliographic source; never add an entry from memory alone.

## Suggested protocol

1. Run `researchforge investigate` on the dataset's `idea` with a fixed model and dsh version (both are recorded in `research_state.json` and `dsh/overlay.yml`).
2. Run `researchforge eval … --ground-truth <dataset> --gap-sheet`.
3. Have two reviewers rate the gap sheet independently.
4. Repeat for 3+ runs per model, because agent runs vary; report the mean and spread.
5. Compare models or prompt changes on the same datasets, looking at retrieval, grounding, plan completeness and efficiency together. A change that raises recall by doubling tool calls should be visible as such.

## Temporal prior-art detection (paper study)

The research study in [paper/research_plan.md](paper/research_plan.md) asks whether self-challenge helps an agent recognise ideas that are already published. It uses these pieces.

**Items** (`researchforge.evaluation.tpad`). A YAML dataset. Each item has:
- the idea text;
- the *realising paper*, with its first public date;
- a few earlier closest works.

Loading rejects prior work dated on or after the realising paper.

**Conditions.** `condition_settings(settings, item, condition)` returns the settings for one run:
- `scooped`: no cutoff.
- `prepub`: `literature.published_before` is set to the realising paper's date.

**What the cutoff does.**
- It is sent to every API: arXiv `submittedDate`, OpenAlex `to_publication_date`, Semantic Scholar `publicationDateOrYear`, Crossref `until-pub-date`.
- It is also enforced on every stored paper. A paper is visible only if its earliest known date is before the cutoff; with only a year, the year must be earlier.
- arXiv full text is pinned to v1, so later revisions cannot leak newer work.
- GitHub tools are disabled.
- Hidden papers are logged to `benchmark/hidden.jsonl`. The model is not told about the cutoff.

**Corruption.** `literature.corrupt_abstracts` swaps that share of each source's records for another record's abstract. The swap is deterministic per seed and record. Every swap is logged to `benchmark/corruptions.jsonl` with both abstracts.

**Ablation switches.**
- `investigation.challenge_conclusions`
- `investigation.recritique_on_contradiction`
- `investigation.controller_mode = "pipeline"`, with `pipeline_extra_searches` for a compute-matched variant
- `literature.integrity_checks`

**Scoring.** `score_run(ws, item, condition)` reads only workspace records. It reports:
- the verdict, and whether the realising paper was retrieved, analysed and cited with verified evidence;
- scoop detection (`scooped` runs), or leak and false-scoop candidate (`prepub` runs);
- prior-work recall and verified citation;
- cost and process counts;
- contamination, when corruption was active.

`summarize(scores)` aggregates rates per condition and excludes leaked `prepub` runs.

The batch runner, the item builder and the closed-book probe are not built yet (research_plan.md §8).
