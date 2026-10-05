# ResearchForge agent loop

This is the refined specification for the state-driven investigation loop, and a record of how it was implemented. It supersedes the fixed eight-phase sequence described in `ARCHITECTURE.md` §6.

## Refined prompt

> **Task.** Replace the fixed phase sequence in `src/researchforge/orchestrator.py` with a state-driven research controller. Do not modify DeepSeek Harness, the literature clients, the evidence rules, the experiment runner, or the report structure. Change or add only what this list requires.
>
> 1. **Controller.** On every iteration, the controller reads the research state and picks exactly one action from a closed set: `FORMALIZE, PLAN, SEARCH, READ, SYNTHESIZE, COMPARE, VERIFY, CRITIQUE, REFINE, PLAN_EXPERIMENT, EXPERIMENT, ANALYZE_RESULTS, FINALIZE`. It runs that action as one dsh headless turn in the same session, using the existing MCP tools. It then measures what changed in the workspace and records a decision.
> 2. **State.** Extend `ResearchState` with the loop phase, iteration, current action and focus, budget usage, decisions, and per-action retry counters. Store records the model writes (the investigation plan, uncertainties, refined directions, hypothesis evaluations) in the workspace, like the other records. Everything needed to resume lives on disk.
> 3. **Uncertainty drives the next step.** The model records open questions with an importance and a suggested next action (`SEARCH`, `COMPARE`, `VERIFY`, `REFINE`, `PLAN_EXPERIMENT`), and updates their status when it investigates them. The controller investigates the most important open uncertainty before moving on. An uncertainty that is still open after `max_uncertainty_attempts` is marked `unresolved` and reported as such.
> 4. **Critique inside the loop.** Critique runs once the landscape exists and again when enough new evidence has arrived since the last critique, up to `max_critiques`. Critique must record the uncertainties it raises.
> 5. **Direction can change.** `REFINE` records a refined direction with its rationale. The original idea and its formalization are never overwritten.
> 6. **Experiments.** An executable plan never runs without human approval. The controller records that approval is pending and finishes with status `awaiting_approval`. After an approved run, resuming leads to `ANALYZE_RESULTS`, which records `SUPPORTED`, `NOT_SUPPORTED` or `INCONCLUSIVE`. `SUPPORTED` is only accepted if the run passed verification. `NOT_SUPPORTED` opens a refinement uncertainty.
> 7. **Stopping.** `should_finalize` holds only when the question is formalized, a plan exists, literature and analyses meet their thresholds, the landscape and a critique exist, no high- or medium-importance uncertainty is open, a direction and an experiment plan exist, and any executed experiment has been evaluated. Budgets (`max_iterations`, `max_tool_calls`, `max_searches`, `max_papers`, `time_limit_s`) are safety stops, not the normal exit, and the report says when one was hit.
> 8. **Failures.** A model or runtime failure is retried with backoff up to `runtime_retries` times before the run stops, and it can be resumed. An action that produces no measurable progress `max_action_retries` times in a row is blocked. The controller records an unresolved uncertainty for it and picks the next best action.
> 9. **Transparency.** Each decision stores the action, focus, reason, supporting counts, expected outcome and observed outcome. No hidden reasoning is stored. Logs use `[RESEARCH] phase=… action=…` lines.
> 10. **UI and report.** The existing UI shows the current phase, action and focus, the open questions, and the decision log. The existing report adds the refined direction, the uncertainty ledger, the hypothesis evaluation and the investigation log.
> 11. **Tests.** Cover the transitions (intake → formalize → plan → investigate), uncertainty-driven detours, re-critique, finalization, retry and blocking on failure, the experiment feedback loop, budget stops and resume, using a scripted runtime.

## Implementation map

| Concern | Where |
|---|---|
| Controller, `decide_next_action`, `should_finalize`, budgets, progress measurement | `src/researchforge/controller.py` |
| Action prompts (reuse the phase instructions in `phases.py`) | `src/researchforge/actions.py` |
| Loop execution, retries, phase-status sync, resume | `src/researchforge/orchestrator.py` |
| New records: `InvestigationPlan`, `Uncertainty`, `Direction`, `HypothesisEvaluation`, `Decision` | `schemas.py`, `workspace.py` |
| New tools: `record_investigation_plan`, `record_uncertainty`, `update_uncertainty`, `record_direction`, `record_hypothesis_evaluation` | `toolkit.py`, `mcp_server.py` |
| Budgets | `[investigation]` in `config.py` |
| UI: current action, open questions, decision log | `web/static/app.js`, `web/app.py` |
| Report additions | `report.py` |

## Uncertainty-driven adaptive loop (enhancement)

The second revision makes the loop choose actions by the value of reducing specific uncertainties rather than by rule order.

### Action names

The specification's action names map onto the existing actions, so no tool was duplicated:

| Specification | Loop action | Tools it uses |
|---|---|---|
| SEARCH | `SEARCH` | `search_papers`, `expand_citations` |
| READ_PAPER | `READ` | `list_papers`, `fetch_paper_text`, `record_paper_analysis` |
| VERIFY_CLAIM | `VERIFY` | `fetch_paper_text`, `search_paper_text`, `record_claim` |
| COMPARE_METHODS | `COMPARE` | `get_paper`, `search_paper_text`, `record_claim` |
| LOOK_FOR_CONTRADICTORY_WORK | `CHALLENGE` | `search_papers`, `expand_citations`, `record_challenge_result` |
| INVESTIGATE_GAP | `INVESTIGATE_GAP` | `search_papers`, `record_challenge_result` |
| REFINE_HYPOTHESIS / REFINE_RESEARCH_QUESTION | `REFINE` | `record_gap`, `record_modification`, `record_direction` |
| DESIGN_EXPERIMENT | `PLAN_EXPERIMENT` | `record_experiment_plan` |
| RUN_EXPERIMENT | `EXPERIMENT` | existing approval-gated runner (never autonomous) |
| ANALYZE_EXPERIMENT | `ANALYZE_RESULTS` | `record_hypothesis_evaluation` |

### Selection

Once the coverage prerequisites are met (formalize, plan, minimum literature, reading, synthesis, first critique), every open uncertainty contributes one candidate per action that could reduce it:

```
score = importance x expected_gain x relevance x evidence_deficiency / cost
```

| Term | Source |
|---|---|
| importance | the recorded importance: high 3, medium 2, low 1 |
| relevance | a fixed weight per category: novelty, overlap and contradiction 1.0; validity, confounder and direction 0.9; evaluation 0.8; feasibility 0.7; other 0.6 |
| evidence deficiency | 1.0 with no linked evidence; 0.6 with one-sided evidence; 0.35 with both supporting and contradicting evidence; x0.7 if partially resolved |
| expected gain | a documented prior per action, averaged with the information gain that action actually produced earlier in this run, and halved per earlier attempt on the same question |
| cost | `action_costs` in the configuration |

The controller never sets a confidence value. Uncertainty confidence is reported by the model, and only together with a stated basis. Each decision records the ranked candidates, the chosen score with its terms, the expected gain, the estimated cost, the tools used, the state changes and the observed information gain.

**Observed information gain.** A step earns:
- 0.5 per new relevant paper (capped at 2);
- 0.5 per new analysis;
- 1 per newly verified claim;
- 2 per resolved uncertainty;
- 2 per newly contradicted conclusion;
- 1 per new structural record (idea, plan, landscape, critique, direction, experiment plan, hypothesis evaluation).

### Questions the controller raises itself

- It challenges the critique's assessment, each gap and each new direction with a contradictory-evidence search (`CHALLENGE` / `INVESTIGATE_GAP`). A verdict of `weakened` or `refuted` requires contradicting papers that were actually retrieved.
- A weakened or refuted conclusion becomes a high-importance refinement question.
- An experiment that did not support the hypothesis becomes a refinement question, which the controller may pursue by refining directly or by searching for explanations. An inconclusive experiment becomes a follow-up check.

### Direction changes

`record_direction` takes a `change_type`:
- `KEEP_ORIGINAL`
- `REFINE_SCOPE`
- `MODIFY_METHOD`
- `CHANGE_RESEARCH_QUESTION` (requires the new question)
- `CHANGE_HYPOTHESIS`
- `REJECT_DIRECTION`

Each direction also records the previous direction, the supporting papers, the motivating uncertainties and a confidence. The original idea is never overwritten. A rejected direction is not challenged further.

### Stopping

Uncertainty investigation closes when either:
- the last `diminishing_window` investigation steps produced at most `diminishing_threshold` information gain (diminishing returns); or
- the best candidate scores below `min_action_score` (not worthwhile).

Open questions at that point are marked unresolved, and the reason is recorded. Questions raised after the closure, for example by a new direction or an experiment result, reopen investigation. The budgets (`max_iterations`, `max_tool_calls`, `max_tokens`, `time_limit_s`, `max_searches`, `max_papers`, `max_experiment_runs`) remain safety limits.

At the end the controller records a research decision describing the state of the evidence: `PROMISING`, `NEEDS_MODIFICATION`, `ALREADY_WELL_EXPLORED`, `INSUFFICIENT_EVIDENCE`, `EXPERIMENTALLY_SUPPORTED` or `EXPERIMENTALLY_UNSUPPORTED`. The derivation is in `controller.research_decision`.

### Epistemic kinds

Claims can be `evidence`, `inference`, `hypothesis`, `assumption` or `experimental`. Assumptions and hypotheses never count toward claim grounding. Speculation is not recorded as a finding.

### Metrics

`researchforge eval` and `/api/projects/<p>/eval` include a `loop` block:
- iterations, tool calls, failed calls, runtime failures, tokens and elapsed time;
- searches, papers retrieved, read and read in full text;
- action counts;
- uncertainties created (and how many the controller raised), resolved and unresolved;
- challenges and contradictory evidence found;
- hypothesis revisions and direction changes;
- experiments executed and hypothesis evaluations;
- total and per-step information gain, and zero-gain steps;
- why investigation closed, the finalization reason and the research decision.

### Critique revision after contradicting evidence

If a challenge weakens or refutes a conclusion after the current critique was recorded, the controller runs `CRITIQUE` again before continuing (within `max_critiques`), so the assessment shown in the report never predates evidence against it.

### Source integrity

Literature APIs sometimes attach the wrong abstract to a paper. On 2026-09-28, OpenAlex returned the abstract of an unrelated system ("Hyde-IKV") for H2O (arXiv 2306.14048). Two checks guard against this:

- **Cross-source.** When two sources' abstracts share less than 20% of their distinctive words, the one that better matches the title is kept, and the paper records a warning.
- **Single-source.** An abstract that never names the method in a title such as "H2O: ..." is flagged.

A flagged abstract cannot supply direct evidence: the quote must be confirmed in the paper's full text (`fetch_paper_text`). Warnings appear on the paper in the Literature view, in `list_papers` / `search_papers` results, and in the report's Remaining Uncertainty section.
