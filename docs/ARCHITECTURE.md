# ResearchForge Architecture

This document records how ResearchForge integrates with DeepSeek Harness (`dsh`), why it is structured the way it is, and where each responsibility lives. It was written after inspecting the DeepSeek Harness source (`github.com/deepseek-ai/deepseek-harness`, published as `@deepseek-ai/dsh@0.1.7-rc.2`).

## 1. Architecture analysis of DeepSeek Harness

| Concern | How dsh implements it | Where |
|---|---|---|
| Plugin system | Everything is a [Cordis](https://github.com/cordiverse/cordis) plugin. Plugins register services, typed events and reversible effects on a shared `ctx`. There is no privileged core. | `docs/architecture.md`, `docs/cordis-primer.md` |
| Composition / configuration | A **profile** (`$DSH_HOME/profiles/<name>`) stacks **bundles**; each bundle ships a `cordis.patch.yml`. Layers apply in order: bundles → profile patch → home patch → each `--patch <file>` overlay. A patch targets rows by `id` (replacing that row's whole `config`) or `insert`s new rows. | `packages/boot/app-boot`, `docs/user/develop/basic/publish.md` |
| Agent loop | `@deepseek-ai/dsh-agent-loop` (`ctx.agentLoop`) drives turns → steps → tool calls. Extension happens through `agent/*` and `tools/*` events, never by editing the loop. | `packages/core/agent-loop` |
| Tool registry | `ctx.tools.register(defineTool({...}))` in TypeScript, or any **MCP server** mounted through `@deepseek-ai/dsh-mcp-client`, whose tools appear as `mcp__<serverName>__<tool>`. | `packages/core/tools`, `packages/mcp/mcp-client` |
| Model abstraction | `ctx.llm` adapter seam. `dsh-llm-deepseek-api-key` serves `deepseek-official`; `dsh-llm-pi-ai` serves any catalog provider or a custom OpenAI‑compatible endpoint (`api: openai-completions`, `baseURL`, `apiKeyEnv`, `models`). The default route for fresh agents comes from the `agent-default-model` row. | `packages/llm/*`, `packages/core/agent-default-model` |
| Sessions / state | Append-only session event log persisted as JSONL (`dsh-session-persistence-jsonl`) under `$DSH_HOME`; a session can be resumed by id. Context compaction is a plugin (`dsh-compaction-basic`). | `packages/session/*`, `packages/compaction/*` |
| System prompt | `dsh-system-prompt` row, with `personaPrefix` / `personaSuffix` config and plugin-contributed sections. | `packages/core/system-prompt` |
| CLI | `dsh` launcher; `dsh --profile headless [--json] [--session-id <id>] [--patch <file>] "<task>"` runs one task and emits newline-delimited JSON events (`session`, `status`, `text`, `thinking`, `tool_call`, `tool_result`, `final`, `error`). | `apps/cli`, `packages/bundle/headless` |
| Safety | Sandbox backends (`sandbox-exec`/landlock) plus a user-approval seam. In headless mode there is no approval answerer, so every `ask` decision **fails closed**. | `packages/sandbox/*`, `packages/interaction/user-approval` |
| Logging / telemetry | Session log is the source of truth; OTEL telemetry plugin (can be disabled by patch). | `packages/session/session-telemetry-otel` |
| Python | `python/sdk` is a JSON-RPC stdio client for `dsh --profile sdk`. It is **not published to PyPI** (version `0.0.0.dev0`, pinned to an unpublished runtime wheel). | `python/sdk` |

## 2. Integration point

**ResearchForge attaches to dsh through two documented, zero-core-modification seams:**

1. **Tools → the MCP client seam.** ResearchForge's research tools are served by a Python MCP server (`python -m researchforge.mcp_server`). A dsh patch row mounts it with the in-box `@deepseek-ai/dsh-mcp-client`; the model sees `mcp__researchforge__search_papers`, `mcp__researchforge__record_claim`, and so on.
2. **Agent loop → the headless profile.** The ResearchForge orchestrator runs each investigation phase as a `dsh --profile headless --json` turn with a generated `--patch` overlay, resuming the same dsh session (`--session-id`) across phases. dsh owns the model call, the tool loop, session persistence and compaction; ResearchForge owns the research workflow, the evidence store and the report.

The same patch is also shipped as an installable **dsh bundle** (`dsh-bundle/`), so a user can run `dsh plugin --profile research add file:./dsh-bundle` and use the research tools interactively in `dsh web`.

```text
                        researchforge CLI / Web UI  (Python)
                                     │
                          ResearchOrchestrator
             phases · completion gates · state digest · event log
                                     │  one phase = one dsh turn (same session)
                                     ▼
 ┌──────────────── DeepSeek Harness (unmodified, dsh --profile headless) ────────────────┐
 │  agent-loop ── llm adapter (deepseek-official | pi-ai → Qwen/Llama/Mistral/… endpoint)│
 │      │           session log (JSONL) · compaction · sandbox · approval (fail-closed)   │
 │      └── tools registry ── dsh-mcp-client ──(stdio)──┐                                 │
 └──────────────────────────────────────────────────────┼─────────────────────────────────┘
                                                        ▼
                               researchforge.mcp_server  (Python, MCP)
                                     │
                              ResearchToolkit
        literature clients (arXiv · OpenAlex · Semantic Scholar · Crossref · GitHub)
        evidence manager (quote verification, paper-id validation)
        record_* tools → research workspace (idea.yaml, papers/, evidence/, …)
```

## 3. Files that need modification in DeepSeek Harness

**None.** Every change is a new file outside the dsh tree. The overlay only uses documented row operations:

| Row | Operation | Why |
|---|---|---|
| `mcp-researchforge` | `insert` a `@deepseek-ai/dsh-mcp-client` row | Mount the research tool server. |
| `system-prompt` | replace config | Research persona instead of "coding agent" (the headless bundle sets both prefix and suffix, so both are restated). |
| `agent-default-model` | replace config | Select the configured provider/model. |
| `llm-pi-ai` | replace config (only when a custom endpoint is configured) | Route to an OpenAI-compatible open-model server. |
| `tool-bash`, `tool-pwsh`, `tool-fs`, `tool-web`, `tool-subagent`, `tool-subagent-fork`, `tool-workflow`, `tool-jobs` | `disabled: true` | Least privilege: the research agent has no shell, no file writes outside its own record tools, no proprietary web search, and no delegation. Experiments run only through ResearchForge's approval-gated runner. |
| `session-telemetry-otel` | `disabled: true` | No investigation content leaves the machine as telemetry. |

## 4. New files

```text
pyproject.toml                   Python package (researchforge), console script `researchforge`
src/researchforge/
  config.py                      Settings (TOML file + environment); no hardcoded keys
  logging_setup.py               Structured JSON logging
  schemas.py                     Typed domain records (pydantic)
  workspace.py                   research_project/ layout, atomic persistence, resume state
  evidence.py                    Quote verification and claim-grounding checks
  literature/                    Async clients with retry/backoff + on-disk cache, dedup, relevance
  toolkit.py                     ResearchToolkit — every tool returns structured data
  mcp_server.py                  MCP exposure of the toolkit (stdio)
  permissions.py                 Read-only / local-compute / external-write action classes
  phases.py                      Phase definitions: prompt + completion gate
  orchestrator.py                Runs phases, enforces gates, records events, resumes
  runtime/dsh.py                 dsh headless runtime + overlay generation + JSON event parsing
  experiments/                   Approval-gated runner (local or Docker) and result verification
  report.py                      Deterministic report built only from recorded evidence
  evaluation/                    Retrieval, grounding, plan-completeness and efficiency metrics
  web/                           FastAPI app + dependency-free HTML/JS UI
  cli.py                         investigate · resume · report · experiment · status · serve · eval · doctor
dsh-bundle/                      Installable dsh bundle (package.json with dsh.bundle + cordis.patch.yml)
tests/                           Unit tests (mocked HTTP + scripted runtime) and an opt-in dsh e2e test
docs/                            This file, evaluation guide
```

## 5. Why this architecture

- **Smallest clean integration point.** MCP and patch overlays are the mechanisms dsh documents for external tools and composition. ResearchForge adds no TypeScript to dsh and depends on no pre-stable internal API. Upgrading dsh means changing one version string.
- **One strong orchestrator, not a swarm.** Phases run sequentially in one dsh session so the model keeps investigation context. The spec's "agents" (IdeaAnalyzer, CriticAgent, …) are **phases with dedicated prompts and record tools**, not separate autonomous agents.
- **The LLM reasons, Python enforces provenance.** The model cannot write free-form results; it must call `record_*` tools whose schemas are validated. A claim labelled `evidence` must cite a paper that was actually retrieved and include a quote that is verified against the stored abstract or full text. Unknown paper ids are rejected. The report is generated deterministically from these records, so it cannot cite a paper the tools never returned.
- **Workspace is the source of truth.** The dsh session gives conversational continuity, but every phase prompt also carries a compact state digest built from the workspace. An investigation can be resumed even if the dsh session is lost.
- **Open models by construction.** Model selection is a config value passed to dsh's own adapters. DeepSeek (open weights) is the default; any OpenAI-compatible server (vLLM, SGLang, Ollama, llama.cpp) hosting Qwen, Llama or Mistral works through `llm-pi-ai`.
- **Python where appropriate.** Literature access, evidence management, experiment execution, evaluation and the UI are Python; the agent runtime stays in dsh, where it already lives.

## 6. Phases

> **Superseded by the state-driven loop.** The orchestrator no longer runs these phases as a fixed sequence. A controller now picks one action per iteration from the research state (uncertainties, coverage, critique freshness, budgets). The gates below are still used as coverage checks. See [AGENT_LOOP.md](AGENT_LOOP.md).

| # | Phase | Required records (completion gate) |
|---|---|---|
| 1 | Formalize idea | `idea` record (problem, mechanism, hypothesis, variables, assumptions, ambiguities, search queries) |
| 2 | Literature search | at least `min_papers` retrieved papers from at least 2 distinct queries |
| 3 | Paper analysis | analyses for at least `min(papers_to_analyze, retrieved)` papers, each with overlap scores and a relation to the idea |
| 4 | Research landscape | `landscape` record whose categories reference retrieved papers |
| 5 | Critique | `critique` record (strongest for/against, unresolved question, confounder, closest work, overall status) plus grounded claims |
| 6 | Gap discovery | at least one evidence-linked gap, or an explicit "no gap supported" finding |
| 7 | Modifications | 2–5 modifications with qualitative difficulty ratings and rationale |
| 8 | Experiment design | at least one experiment plan with baselines, datasets, metrics, controls, ablations, failure conditions |
| 9 | Report | generated by Python from records (no model call) |

A phase that fails its gate is re-prompted with the specific missing items, up to `max_phase_attempts`. A phase still failing is marked `incomplete`; the report states which sections lack support instead of filling them with text.

## 7. Permission model

| Class | Examples | Policy |
|---|---|---|
| Read-only | `search_papers`, `get_paper`, `fetch_paper_text`, `inspect_repository` | Allowed automatically. |
| Workspace record | `record_*` | Allowed: writes only inside the project directory, schema-validated. |
| Local computation | install dependencies, run experiments, clone repositories | Never exposed to the model. The model may only *propose* an executable experiment spec. Running it requires `researchforge experiment <project> --run <id> --approve` or the UI's Approve button. Commands run as argv (no shell), confined to the experiment directory, with a timeout and a scrubbed environment, optionally inside Docker with `--network none`. |
| External write | pushing code, opening PRs, publishing | Not implemented. Any future implementation must require explicit confirmation. |

Inside dsh, the overlay disables shell and file-write tools, and headless mode fails closed on any approval request.

## 8. Risks

| Risk | Mitigation |
|---|---|
| dsh is a developer preview with breaking changes | Pin the dsh version in config; integration uses only documented patch rows and MCP; a `doctor` command checks the installation. |
| Literature APIs rate-limit anonymous clients (observed 429s from OpenAlex and Semantic Scholar) | Honor `Retry-After` with bounded exponential backoff, cache every response in the workspace, degrade per-source instead of failing the phase, and support optional API keys via environment variables. |
| Weaker open models may not follow tool protocols | Completion gates with targeted repair prompts; schema validation errors are returned to the model as actionable messages. |
| A source returns the wrong abstract for a paper (observed for H2O on OpenAlex) | Cross-source and title-name consistency checks flag it; a flagged abstract cannot supply direct evidence, so the quote must come from the full text. |
| Quote verification can reject valid paraphrases | `direct` support requires a verbatim quote; paraphrases must be `indirect` or `weak` support, which the report labels accordingly. |
| First `npx` launch downloads dsh (minutes) | `doctor` explains how to install `dsh` globally; the dsh command is configurable. |
| Headless adoption refuses a session recorded in a different working directory | The orchestrator always runs dsh with the project directory as its working directory. |

## 9. Verification of the integration

These checks run against the published `@deepseek-ai/dsh@0.1.7-rc.2`:

| Check | How |
|---|---|
| The generated overlay composes (MCP row inserted, persona and model rows replaced, tool and telemetry rows disabled, no unknown row ids) | `researchforge doctor`, which runs `dsh --profile headless --patch overlay.yml --dump-config` |
| The full phase loop runs through the real dsh binary | `pytest -m e2e`: dsh routes model requests to a scripted OpenAI-compatible server configured as a custom `llm-pi-ai` endpoint, launches the MCP server, and executes `mcp__researchforge__*` calls that write the workspace. Schema errors return to the model as tool errors; one dsh session is resumed across all phases. |
| The installable bundle works interactively | headless dsh with `dsh-bundle/cordis.patch.yml` launches the MCP server, which initializes `./.researchforge/interactive` and answers tool calls |
| Literature APIs | `pytest -m live`. Anonymous Semantic Scholar returned HTTP 429 and arXiv returned intermittent HTTP 406 under bursts; both are retried with backoff, and a source that still fails is recorded as `error` without failing the search. |

A run with a real model requires a model credential or endpoint and was not part of these checks.

## 10. Implementation plan

Milestones follow the project brief; each one leaves a working application.

1. dsh integration: overlay, MCP server skeleton, orchestrator, `investigate` producing a structured plan.
2. Literature search and retrieval with provenance and caching.
3. Paper analysis and evidence management (quote verification, claims).
4. Landscape and critique.
5. Idea modification.
6. Experiment planning.
7. Controlled experiment execution and verification.
8. Web UI, CLI and final report.
9. Evaluation suite, documentation and demo script.
