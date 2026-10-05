# Contributing to ResearchForge

Thanks for helping. Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) first. The short version: DeepSeek Harness runs the agent, ResearchForge supplies research tools over MCP plus the workflow, the evidence rules and the report.

## Setup

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
pytest                  # offline suite
pytest -m e2e           # needs Node.js >= 22.19; runs the real dsh binary with a scripted model
pytest -m live          # hits real literature APIs; may see rate limits
```

## Where things live

| Change | Place |
|---|---|
| A new literature source | `src/researchforge/literature/sources.py` (a client with `name` and `async search()`), register it in `ResearchToolkit.__init__` and `config.SOURCES` |
| A new tool for the agent | a method on `ResearchToolkit` returning JSON-serialisable data, plus one registration line in `mcp_server.build_server` |
| A new record type | a model in `schemas.py`, persistence in `workspace.py`, a `record_*` tool, and rendering in `report.py` |
| Phase behaviour | `phases.py`: prompt text and the completion gate |
| dsh composition | `runtime/dsh.py:build_overlay` (per-project) and `dsh-bundle/cordis.patch.yml` (installable bundle) |

## Rules

- **Do not modify DeepSeek Harness.** Integrate through documented seams: MCP tools, Cordis patch rows, the headless runner. If something truly requires a dsh change, open an issue explaining why.
- **No fabricated data.** Never fill a field the source did not return (citation counts, venues, years). Keep provenance (`sources`, `citation_count_source`).
- **Evidence rules are product behaviour.** Changes to `evidence.py` need tests showing what is accepted and what is rejected.
- **The report is deterministic.** `report.py` must not call a model. Every rendered statement needs a label: Evidence / Inference / Hypothesis / Experimental result.
- **Tools return structured data.** Raise `ToolError` with a message that tells the model how to fix the call.
- **Safety.** Nothing in the toolkit may execute local commands or write outside the project workspace. Execution belongs to `experiments/runner.py` behind explicit approval.
- **Credentials only from environment variables**, never in config files, overlays, caches or logs. The dsh overlay forwards key variables by reference (`!!js process.env.X`).
- **Tests describe behaviour.** Use the synthetic fixtures in `tests/support.py`; do not add real paper abstracts as fixtures.

## Pull requests

Keep changes focused, update the README or docs when behaviour changes, and include the test commands you ran.
