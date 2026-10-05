# Paper plan: does self-challenge make research agents better at spotting prior art?

Status: draft, 2026-09-29. It builds on the gaps in [literature_review.md](literature_review.md) (G1–G5).

## 1. Positioning

**Working title.** *Scooped or Novel? A Temporal Benchmark and Controlled Ablations of Self-Challenge in Literature-Grounded Research-Idea Assessment.*

**One-sentence claim to test (not assume).** Given the same model and budget, an agent that searches for evidence against its own novelty and gap conclusions, and revises its critique when it finds some, detects already-published ideas more often and cites the realising paper as evidence. It does this without calling genuinely unpublished ideas "already explored" more often.

**Why this framing.**
- **G1.** AutoResearchEval [2608.14905] attributes the missing metacognitive loop to the model and leaves open whether orchestration can close it. This study tests exactly that, in one setting where the answer can be checked.
- **G2.** Novelty labels are subjective [2606.12071, 2409.04109]. The temporal prior-art protocol gives an objective target, so the claim is measurable.
- **The paper is honest either way.** If self-challenge does not help, that is a publishable negative result, and it would support the model-level reading of [2608.14905].

**What the paper does not claim** (see literature review §5):
- that quote-grounding, structured state, approval gates or adaptive stopping are new;
- that any idea is novel;
- that ResearchForge is better than an unnamed baseline without a matched budget.

## 2. Research questions

| RQ | Question | Gap |
|---|---|---|
| RQ1 | With visible literature, does self-challenge (CHALLENGE / INVESTIGATE_GAP plus re-critique) raise the scoop-detection rate and the realising-paper citation rate, compared with the same agent without it? | G1, G2 |
| RQ2 | With the literature cut off before publication, does self-challenge raise the false-scoop rate, i.e. over-skepticism? | G1, G2 |
| RQ3 | Is any gain from control or from compute? Compare a fixed pipeline given the adaptive agent's mean budget. | G1, G4 |
| RQ4 | When a controlled share of retrieved abstracts is swapped for wrong ones, how often do corrupted abstracts end up as evidence, and do ingest-time consistency checks prevent it? | G3 |
| RQ5 | Does information-gain stopping preserve verdict quality at lower cost? Is the decision rule-based on the evidence, measured as evidence–verdict agreement on a human-rated sample? | G4, G5 |
| RQ6 | Do the effects hold across at least one hosted and two open-weight backbones? | generality |

## 3. Contributions (conditional on the results)

- **C1.** A temporal prior-art detection protocol and dataset. Each item has an idea statement, a realising paper with its publication date, and a small set of closest prior works. The item is run in two conditions: literature visible, and literature cut off before publication. The protocol includes anti-leakage controls.
- **C2.** Controlled ablations of orchestration-level metacognition, with budgets matched: self-challenge, re-critique after contradiction, adaptive vs fixed control, and information-gain stopping.
- **C3.** A robustness study of bibliographic metadata corruption in research agents, together with a cheap ingest-time check and its measured effect.
- **C4.** Released instrument: the ResearchForge harness, per-run traces (decisions, candidates, information gain) and the scoring code. Traces address the reproducibility gap reported in [2608.05179].

## 4. Benchmark: Temporal Prior-Art Detection (TPAD)

### 4.1 Items

Each item is built from a *realising paper* P.

**Selection.**
- P is an arXiv CS paper (initially cs.LG, cs.CL and cs.IR, where ResearchForge's sources are strongest).
- P was published after the training cutoff of every backbone used (§6).
- P has a method contribution that can be stated as a proposal.

**Idea text.** An 80–150-word proposal derived from P's abstract.
1. A different LLM rewrites it, removing names, acronyms, numbers and results, and phrasing it as a plan.
2. A human checks two things: the proposal is recognisably P's core idea, and it contains no identifying strings.
3. The item records the paraphrase's word 5-gram overlap with P's abstract. Items above a threshold are rewritten.

**Collision set C(P).** P, plus two or three of its closest prior works. A human picks these from P's own reference list (via the Semantic Scholar references API), choosing works P positions itself against. This set is the retrieval target, in the spirit of the bibliography-grounded design of [2608.16645].

**Closed-book probe.** Before any run, each backbone is asked whether it knows a paper that realises the idea. Items where it names P are excluded for that backbone.

### 4.2 Conditions

| Condition | Literature visible | Correct outcome |
|---|---|---|
| **SCOOPED** | everything up to the run date | Verdict `ALREADY_WELL_EXPLORED` (or `NEEDS_MODIFICATION` with P named as direct overlap), and P used as verified evidence |
| **PRE-PUB** | only works published before P's date | Verdict other than `ALREADY_WELL_EXPLORED`, unless the cited prior work really covers the idea (adjudicated by humans, see §5) |

**How the cutoff is enforced.** It applies at the literature layer, to search, citation expansion, lookup and full-text fetch, so that search-time contamination [2606.05241] cannot reach P.

### 4.3 Corruption condition (RQ4)

The same items are run with a corruption rate r ∈ {0.1, 0.25}.

**Injection.** For a fraction r of the papers returned by any source, the abstract is replaced with the abstract of a different retrieved paper. This mirrors the "misplaced metadata" failure mode of [2605.20168] and the real case described in [AGENT_LOOP.md](../AGENT_LOOP.md#source-integrity).

**Record-keeping.** The injector records which papers it corrupted, so contamination can be measured exactly.

## 5. Systems, metrics, statistics

### 5.1 Systems

All systems use the same backbone, dsh version and hard budgets.

| Id | System | Switches |
|---|---|---|
| S-full | ResearchForge adaptive loop | defaults |
| S-nochal | no self-challenge | `challenge_conclusions = false` |
| S-norecrit | no re-critique after contradiction | `recritique_on_contradiction = false` |
| S-pipe | fixed pipeline: formalize → plan → search → read → synthesize → critique → finalize, with no uncertainty loop | `controller_mode = "pipeline"` |
| S-pipe+ | fixed pipeline with extra searches up to S-full's mean tool calls (the compute control for RQ3) | `controller_mode = "pipeline"`, `pipeline_extra_searches` |
| S-noint | S-full without source-integrity checks (RQ4 only) | `literature.integrity_checks = false` |

### 5.2 Metrics

All metrics are computed from the workspace, not from the report prose.

- **Scoop detection** (SCOOPED): the share of items whose verdict is `ALREADY_WELL_EXPLORED`, or `NEEDS_MODIFICATION` with a verified overlap claim on P.
- **Realising-paper evidence** (SCOOPED): P was retrieved, analysed, and cited in at least one claim with verified evidence.
- **False-scoop rate** (PRE-PUB): the share of items with verdict `ALREADY_WELL_EXPLORED`. Two raters adjudicate each one as justified or unjustified from its cited evidence; inter-rater agreement is reported as Cohen's κ.
- **Collision recall** (both conditions): the share of C(P) \ {P} retrieved, and the share cited with verified evidence.
- **Contamination** (corruption condition): the share of verified evidence items whose quote came from a corrupted abstract, and the verdict flip rate relative to r = 0.
- **Evidence–verdict agreement**: human rating on a stratified sample of 60 runs. Does the cited evidence support the verdict? This follows NovGauge's faithfulness notion [2609.11234].
- **Cost**: tool calls, tokens, searches, wall-clock time and iterations (already recorded in `loop_metrics`).
- **Process**: challenges run, contradictions found, critique revisions and direction changes (already recorded).

### 5.3 Statistics

- **Design.** Paired by item, with 2 seeds per (item, system, condition).
- **Tests.**
  - McNemar's test on the binary outcomes, applied to the per-item majority vote over seeds.
  - Paired bootstrap with 95% confidence intervals on rates and costs.
  - Holm correction across the RQ1–RQ3 comparisons.
- **Pilot.** 20 items with S-full and S-nochal. The pilot fixes the idea-writing procedure, estimates discordance, and sets N by power analysis. The expected N is 100–150 items.

## 6. Models and reproducibility

- **Backbones.** DeepSeek through dsh (the current default), plus at least two open-weight models served through an OpenAI-compatible endpoint (the `llm-pi-ai` path that already works). Every backbone's documented training cutoff is recorded, and item selection starts after the latest one.
- **Recorded per run.** Everything needed for replication is already written to the workspace: dsh version, overlay, model, settings, seeds, every decision with its candidates, and the search log. The release includes the traces and the literature cache, so scores can be recomputed offline.

## 7. Threats to validity

- **Parametric leakage.** The model may know P from training. Mitigations: selection after the cutoff, and the closed-book probe (§4.1).
- **Paraphrase leakage.** The idea text may carry identifying wording. Mitigations: the n-gram threshold and the human check.
- **"Already explored" is not binary.** P may be incremental over C(P), so a PRE-PUB "explored" verdict can be right. Mitigation: human adjudication instead of automatic scoring.
- **Search API drift.** Mitigation: cache all API responses on first use and re-score from the cache.
- **Single domain.** CS only; external validity to biomedicine is not claimed.
- **Compute confound.** S-pipe+ handles this (RQ3).

## 8. Implementation roadmap

| # | Piece | Status |
|---|---|---|
| 1 | Publication-date cutoff (`published_before`) enforced in search, citation expansion and lookup | **done**: sent to all four APIs and enforced on stored papers; arXiv full text pinned to v1; GitHub disabled; hidden-paper ledger |
| 2 | Ablation switches: `controller_mode`, `recritique_on_contradiction`, `integrity_checks`, `pipeline_extra_searches` | **done** (`literature.integrity_checks`; the others under `[investigation]`) |
| 3 | Benchmark item schema and loader (`evaluation/tpad.py`), plus an example dataset | **schema and loader done**; no real items yet (they need the builder and human checks) |
| 4 | Scorer: detection, realising-paper evidence, false scoop, collision recall, contamination and cost, read from a workspace | **done** (`score_run`, `summarize`, `contamination`) |
| 5 | Corruption injector at the literature layer, with a ledger of what was corrupted | **done** (`literature/controls.py`) |
| 6 | Batch runner (`researchforge bench`) over items × systems × conditions × seeds, with resume | to build |
| 7 | Item builder: fetch P and its references from Semantic Scholar, generate the paraphrase, write out an item for human review | to build; human-in-the-loop |
| 8 | Closed-book probe | to build |
| 9 | Pilot (20 items), then full runs | after 1–8 |

**Order.** Pieces 1–5 are needed under any variant of this plan and are built first. Pieces 6–8 follow once the switches and scorer are tested.

## 9. Venue and scope, honestly

- **Workshop paper.** A 20–40-item pilot with S-full vs S-nochal vs S-pipe on one backbone is a realistic workshop paper (agents-for-science or AI-for-research workshops, Agents4Science).
- **Main-conference paper** (ACL, EMNLP or NeurIPS Datasets & Benchmarks). This needs the full TPAD set (100–150 items), all six RQs, two or more backbones and the human adjudication. The benchmark (C1) plus a clear answer to the question left open by [2608.14905] is the part reviewers are likely to value. Stronger results do not make it "novel"; the protocol does.

## 10. Pre-registered pilot outcomes (fixed 2026-09-30, before any pilot run)

One calibration run (item T-2609.11572, `full`, SCOOPED) was made to set budgets. It is excluded from analysis. It showed two things:
- The agent concluded "substantial overlap" from earlier work without ever retrieving the realising paper. The paper was retrievable by exact title through arXiv and OpenAlex.
- Turns 11–26 were spent on repeated experiment plans.

The pilot outcomes are therefore fixed as follows, before any pilot run exists.

**Primary outcomes.**
- **Realising-paper evidence (SCOOPED):** the realising paper is retrieved, and is cited in a claim with verified evidence.
- **Verdict discrimination (per item):** the decision is `ALREADY_WELL_EXPLORED` under SCOOPED and not under PREPUB. This is the discriminating form of "detection".

**Secondary outcomes.**
- verdict-only scoop detection;
- false-scoop candidates under PREPUB;
- `ALREADY_WELL_EXPLORED` under both conditions (a sign of indiscriminate scepticism);
- prior-work recall;
- cost.

**Design.**
- Systems: `full`, `nochal`, `pipe`, with 20 turns, 250 tool calls, 14 searches, 90 papers and 45 minutes per run.
- Stage 1 runs `full` and `nochal`; stage 2 adds `pipe`.
- One run per (item, condition, system).

**Revision (2026-09-30, after the first Nemotron run and before any other).**
- **What the first run showed.** It ran under a 45-minute cap and ended after 9 turns. Its read turn hit the 15-minute turn timeout, and its self-challenge never ran; the controller chose a search and a re-critique first. Under those caps, `full` and `nochal` would barely differ.
- **Controller change.** When self-challenge is on, the controller now challenges the first critique immediately after recording it. With it off, the controller proceeds as before, so the systems differ in exactly that step and what follows from it.
- **New caps.** 16 turns, 60 minutes and 6 papers read per run, with a 20-minute limit per turn.
- **Exclusions.** The two runs under the old caps are excluded (`bench/tpad/runs-nemotron-45min-excluded`).

**Fix (2026-09-30, after 3 finished runs).**
- **Bug.** The 20-minute turn timeout killed only the `npx` launcher. dsh and the tool server kept the output stream open, so one turn ran 38 minutes.
- **Fix.** Turns now run in their own process group, which is killed as a whole on timeout; there is a regression test in `tests/test_benchmark.py`.
- **Runs affected.** The 3 runs finished before the fix (item 2609.12230: SCOOPED `full` and `nochal`, PREPUB `full`) are kept. The analysis also reports results without that item. The two runs in progress were resumed from their last completed turn.
