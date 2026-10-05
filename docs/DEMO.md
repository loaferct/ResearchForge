# Demo script (5 minutes)

**Idea:** *Can request-aware dynamic KV-cache management reduce LLM inference memory and latency without significantly degrading accuracy?*

## Before the demo

```sh
researchforge doctor                 # all checks green
researchforge serve                  # http://127.0.0.1:8765
```

Use a model with reliable tool calling. Set `SEMANTIC_SCHOLAR_API_KEY` and `RF_CONTACT_EMAIL` if you have them, since anonymous literature APIs throttle. Run the investigation once beforehand to warm the dsh install and to know the timing. For the live demo, start a fresh project; the cached responses make repeated searches fast.

## Timeline

| Time | Show | Point to make |
|---|---|---|
| 00:00 | Paste the idea and press **Investigate research idea** | One input; everything else is autonomous |
| 00:15 | Rail: **Overview** ✓ | The idea becomes a testable research question, variables, and ambiguities resolved by assumption or by quick searches |
| 00:30 | Rail note and activity log: `search_papers`, `expand_citations` | Real queries to arXiv, OpenAlex, Semantic Scholar and Crossref; failures appear as source errors, not silent gaps |
| 01:00 | **Literature** | Every paper shows its sources, and citation counts show which source reported them |
| 01:30 | **Research map** | Taxonomy with paper references; where the idea sits |
| 02:00 | **Critique**: closest existing work | The agent looked for the work that could make the idea redundant |
| 02:30 | Critique: strongest argument against, most dangerous confounder | ResearchForge tries to disprove the idea |
| 03:00 | **Potential gaps** | Each gap has quotes marked *verified* against the retrieved text |
| 03:30 | **Modifications** | 2–5 directions with qualitative difficulty and stated basis; one recommended |
| 04:00 | **Experiments** | Baselines, metrics, controls, ablations and falsifying outcomes; execution would need approval |
| 04:30 | **Final report** | Sections 1–15; the executive summary does not say "novel" |
| 05:00 | **Evidence ledger** and `events.jsonl` | The evidence trail: each claim, its label, the quote, and whether it was verified |

## If something fails live

- A source shows `error`: that is the throttling path working as designed. The other sources continue.
- A phase ends `incomplete`: the report marks the section *Not recorded*. Press **Resume investigation** to retry that phase with a targeted repair prompt.
- No model key: `researchforge doctor` shows it. For an offline demo of the plumbing, run `pytest -m e2e -s`, which drives the real dsh with a scripted model.
