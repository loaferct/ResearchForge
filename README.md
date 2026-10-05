# ResearchForge

**ResearchForge turns a research idea into an evidence-backed investigation.**

Give it an idea such as *"Can request-aware dynamic KV-cache management reduce LLM inference memory and latency without significantly degrading accuracy?"* and it autonomously:

1. formalizes the idea into a testable research question, variables and assumptions;
2. searches open scholarly sources (arXiv, OpenAlex, Semantic Scholar, Crossref) and follows the citation graph;
3. analyzes the closest papers, reading full text and inspecting their code repositories where available;
4. maps the research landscape;
5. tries to **disprove** the idea: closest work, overlap, confounders, practicality;
6. identifies research gaps, each tied to evidence;
7. proposes 2–5 concrete modifications;
8. designs an experiment plan, and runs it if you approve an executable spec;
9. writes a report in which every statement is labelled **Evidence**, **Inference**, **Hypothesis** or **Experimental result**.

It never tells you an idea is novel because a model thinks so. A claim labelled *evidence* must quote a retrieved paper, and ResearchForge checks that quote against the stored abstract or full text before accepting the claim. The report is generated from recorded data, not written by the model, so it cannot cite a paper the tools never retrieved.

ResearchForge is built on [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (`dsh`) and requires no changes to it. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

```text
researchforge CLI / web UI (Python)
        │  one phase = one dsh headless turn, same dsh session throughout
        ▼
DeepSeek Harness (unmodified): agent loop · model adapters · sessions · compaction · sandbox
        │  @deepseek-ai/dsh-mcp-client (stdio)
        ▼
researchforge.mcp_server → literature clients · evidence checks · research workspace
```

## Quick start

Requirements: Python ≥ 3.10, Node.js ≥ 22.19 (for `dsh`), and a model endpoint (see [Models](#models)).

```sh
git clone <this repository> researchforge && cd researchforge
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[pdf]"
npm install -g @deepseek-ai/dsh@0.1.7-rc.2   # optional: otherwise ResearchForge runs it through npx

export DEEPSEEK_API_KEY=...                  # or configure an open-model endpoint, see below
researchforge doctor                         # checks Python, Node, dsh, credentials and the dsh overlay

researchforge investigate \
  --idea "Can dynamic KV-cache eviction reduce LLM inference memory while preserving long-context accuracy?"
```

Output while it works:

```text
Phase 1 — Formalizing idea
  • get_research_state
  • search_papers
  • record_idea_analysis
✓ formalize: complete

Phase 2 — Literature investigation
  • search_papers
  • expand_citations
…
Status: complete
Report: research_projects/can-dynamic-kv-cache-eviction-reduce-llm-inference/reports/report.md
```

## How the agent decides what to do

ResearchForge does not run a fixed script. On each step, a controller reads the research state and picks one action: formalize, plan, search, read, synthesize, compare, verify, critique, refine, plan an experiment, analyze results, or finalize. The model records open questions (**uncertainties**) with an importance and the action that would resolve them, and the controller investigates the important ones before it finishes. Critique repeats when enough new evidence arrives. A refined direction is recorded alongside the original idea, never over it. The loop stops when the research conditions are met: question formalized, literature checked, overlap examined, important uncertainties investigated, idea critiqued, direction and experiment plan recorded. Budgets (steps, tool calls, searches, papers, time) are only safety limits. Every step is logged as a decision with its reason and observed outcome, and shown in the UI and in the report's investigation log. Details: [docs/AGENT_LOOP.md](docs/AGENT_LOOP.md).

## Commands

| Command | What it does |
|---|---|
| `researchforge investigate --idea "…" [--name N] [-v]` | Create a project and run all phases |
| `researchforge resume <project>` | Continue from the first unfinished phase, reusing the dsh session and cached searches |
| `researchforge status <project>` | Phase progress, attempts, tool calls, missing requirements |
| `researchforge report <project> [--format md\|html\|path]` | Regenerate the report from recorded data |
| `researchforge experiment <project>` | List experiment plans |
| `researchforge experiment <project> --run E001` | Preview the exact commands a plan would run (nothing executes) |
| `researchforge experiment <project> --run E001 --approve` | Execute after explicit approval, then verify the results |
| `researchforge serve [--port 8765]` | Web UI at `http://127.0.0.1:8765` |
| `researchforge eval <project> [--ground-truth kv-cache] [--gap-sheet]` | Evaluation metrics (see [docs/EVALUATION.md](docs/EVALUATION.md)) |
| `researchforge list` | List projects |
| `researchforge doctor` | Check the installation |

## Web UI

`researchforge serve` starts a local, dependency-free UI. The home page is a single landing page (what ResearchForge does, how an investigation runs, what you get, how it runs on your terms) with the idea form in the hero. Enter an idea, press **Investigate research idea**, and follow progress in the numbered rail on the left. The rail doubles as navigation: **Overview, Literature, Research map, Critique, Potential gaps, Modifications, Experiments, Final report**, plus the **Evidence ledger** and an activity log. Every statement carries a margin rule that shows how certain it is: solid for evidence (a verified quote), dashed for inference, dotted for hypothesis, double for an experimental result. An executable experiment offers **Preview commands**, then **Approve and run**.

The UI opens in light mode; **Dark mode** in the header switches it and the choice is remembered in the browser. The design follows Anthropic's `frontend-design` skill (Apache-2.0) and the `taste-skill` / `redesign-skill` pair from [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) (MIT), all vendored in `.claude/skills/`. The visual theme is the Atlas Admin design system, specified in [docs/DESIGN.md](docs/DESIGN.md). Fonts are self-hosted from `web/static/fonts/`: Inter for text and IBM Plex Mono for figures and labels, both under the SIL Open Font License (license files alongside).

The server binds to `127.0.0.1` and has no authentication. Do not expose it on a shared network.

## Models

ResearchForge does not call any model API itself. The model is whatever route DeepSeek Harness is configured with, and no proprietary API is required.

| | Default | Alternatives |
|---|---|---|
| **Model** | `deepseek-flash` | Any model served by an OpenAI-compatible endpoint, e.g. Qwen3, Llama 3.x, Mistral/Mixtral, DeepSeek-V3/R1 weights |
| **Provider** | `deepseek-official` (DeepSeek's API, via dsh's `dsh-llm-deepseek-api-key` adapter) | Self-hosted vLLM, SGLang, Ollama or llama.cpp server, or a gateway, via dsh's `dsh-llm-pi-ai` adapter |
| **License** | Hosted model: see DeepSeek's terms and the model card for the specific model. DeepSeek has published open weights (e.g. DeepSeek-V3, DeepSeek-R1) under the MIT license. | Check each model card. For example, Qwen3 is released under Apache-2.0, Llama under Meta's Llama Community License, and many Mistral models under Apache-2.0. |

To use a self-hosted open-weight model, add this to `researchforge.toml`:

```toml
[model]
model = "Qwen/Qwen3-32B"

[model.custom]
provider_id = "local-vllm"
base_url = "http://127.0.0.1:8000/v1"
api = "openai-completions"
api_key_env = "LOCAL_LLM_API_KEY"   # OpenAI-compatible servers need some key, even if unused
models = ["Qwen/Qwen3-32B"]
context_window = 131072
```

**Ollama Cloud.** Hosted DeepSeek and other open-weight models work the same way.

1. Put the key in a local `.env` file (gitignored) as `OLLAMA_API_KEY=...`. The `researchforge` command loads `./.env` at start-up, and variables already set in the shell take precedence.
2. Add this to `researchforge.toml`:

```toml
[model]
model = "deepseek-v4.1-flash"

[model.custom]
provider_id = "ollama-cloud"
base_url = "https://ollama.com/v1"
api = "openai-completions"
api_key_env = "OLLAMA_API_KEY"
models = ["deepseek-v4.1-flash", "deepseek-v4-pro:0813", "gpt-oss:120b"]
```

Ids come from `GET https://ollama.com/v1/models`.

On 2026-09-30, the DeepSeek models returned HTTP 402 ("not included in your free usage") on an account without usage credits. `gpt-oss:120b` worked on free usage. To switch models for one run, set `RF_MODEL=gpt-oss:120b`.

ResearchForge turns this into a `llm-pi-ai` provider row and selects it through dsh's `agent-default-model` row. Tool use is essential, so choose a model with reliable function calling. Weak tool-callers trigger more repair prompts, and phases may end `incomplete`; the report says so rather than filling the gaps.

### Where model outputs are consumed

| Model output | Where it goes | Safeguard |
|---|---|---|
| Arguments to `record_*` tools | Validated against typed schemas, then written to the project workspace | Invalid calls are rejected with an explanation. Paper ids must belong to retrieved papers. A `direct` quote must be found verbatim in the retrieved text. |
| Arguments to read-only tools (`search_papers`, `fetch_paper_text`, …) | HTTP requests to open literature APIs and GitHub (read-only) | Responses are cached; nothing is written to external services. |
| Free-text replies | The event log (`events.jsonl`) and the UI activity feed only | Never copied into the report. |
| Proposed experiment `execution` specs | Saved as `awaiting_approval` | Never executed without an explicit human `--approve` or UI approval. Commands run without a shell, in a confined directory, with a scrubbed environment and a timeout; Docker with `--network none` is optional. |
| The report | Not written by the model | Built deterministically from validated records. |

## Research workspace

Every investigation is a directory that can be resumed and audited:

```text
research_projects/<project>/
├── idea.yaml              raw idea + formalized analysis
├── research_state.json    phase status, attempts, dsh session id
├── events.jsonl           everything that happened (tool calls, errors, phase results)
├── search_log.jsonl       every query and each source's status
├── papers/                retrieved papers with provenance; text/ and analyses/
├── evidence/claims/       claims with evidence items and verification results
├── hypotheses/            landscape, critique, gaps, modifications
├── experiments/           plans and working directories
├── results/               experiment runs (command, env, commit, hardware, stdout/stderr) and verification
├── reports/               report.md, report.html
├── cache/http/            cached API responses (no credentials)
└── dsh/                   generated dsh overlay and raw dsh event streams per phase
```

## Safety and permissions

| Class | Examples | Policy |
|---|---|---|
| Read-only | literature search, paper and full-text retrieval, repository inspection | Automatic |
| Workspace records | `record_*` tools | Automatic, schema-validated, confined to the project directory |
| Local computation | cloning a repository, installing dependencies, running experiments | Only through `researchforge experiment … --approve` or the UI's approval button; never available to the model |
| External writes | pushing code, opening PRs, publishing | Not implemented |

Inside dsh, the generated overlay disables the shell, file-write, web-search, delegation and workflow tools for the research agent, and turns off dsh telemetry. dsh's headless mode fails closed on any approval request.

## Using the tools inside `dsh web`

The same tools can be added to any dsh profile as a bundle:

```sh
pip install -e /path/to/researchforge
dsh plugin --profile research add file:/path/to/researchforge/dsh-bundle
RESEARCHFORGE_PYTHON=$(which python) dsh --profile research web
```

Records go to `./.researchforge/interactive`, or to `$RESEARCHFORGE_PROJECT_DIR`.

## Configuration

Settings come from `researchforge.toml` (or `--config`, or `$RESEARCHFORGE_CONFIG`), overridden by `RF_*` environment variables. See [researchforge.example.toml](researchforge.example.toml). Credentials are only ever read from environment variables:

| Variable | Used for |
|---|---|
| `DEEPSEEK_API_KEY` | the default DeepSeek route, read by dsh |
| your `api_key_env` | a custom open-model endpoint, read by dsh |
| `SEMANTIC_SCHOLAR_API_KEY`, `OPENALEX_API_KEY`, `GITHUB_TOKEN` | optional; they raise literature API rate limits |
| `RF_CONTACT_EMAIL` | optional; OpenAlex/Crossref "polite pool" contact |

Anonymous literature APIs rate-limit aggressively; during development we observed HTTP 429 from Semantic Scholar and throttling from arXiv. ResearchForge retries with backoff, caches every response, and records a failing source as `error` in the search log instead of failing the phase. Setting the optional keys helps.

## Development

```sh
pip install -e ".[dev]"
pytest                 # unit and integration tests (offline, mocked HTTP, scripted agent)
pytest -m e2e          # real dsh + real MCP server + a scripted OpenAI-compatible model (no API key needed)
pytest -m live         # real literature APIs
```

The `e2e` test runs the actual `dsh` binary, pointed at a local scripted Chat Completions server configured as a custom `llm-pi-ai` endpoint. This exercises overlay composition, MCP launch, tool naming, argument transport, error propagation and session resumption. The scripted server is test infrastructure only.

See [CONTRIBUTING.md](CONTRIBUTING.md), [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/EVALUATION.md](docs/EVALUATION.md) and [docs/DEMO.md](docs/DEMO.md).

## Docker

```sh
docker build -t researchforge .
docker run --rm -it -p 127.0.0.1:8765:8765 -e DEEPSEEK_API_KEY -v "$PWD/research_projects:/app/research_projects" researchforge
```

## License

MIT. DeepSeek Harness is MIT-licensed. Literature metadata comes from the respective providers under their terms of use.
