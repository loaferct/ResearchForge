# ResearchForge Investigation Report

Project `T-2609.11572__scooped__nochal__s0` · model `ollama-cloud/nemotron-3-super` · status **incomplete**

> Labels: **[Evidence]** directly supported by a verified quote from a retrieved source; **[Inference]** reasoning derived from cited evidence; **[Hypothesis]** proposed, not validated; **[Assumption]** taken as given without evidence; **[Experimental result]** observed in an executed experiment.

## 1. Executive Summary

**Investigated:** The reliability of open‑domain question answering drops sharply when source texts are continuously amended, as in statutes, policies, or regulations. In such settings each new amendment supersedes earlier clauses while retaining much of the original wording, creating a dense semantic overlap across successive versions. Existing time‑aware retrieval techniques treat each version as an isolated snapshot and therefore cannot distinguish which revision best matches a time‑specific query. We propose to develop a retrieval‑agnostic framework that enriches any standard document retriever with a temporal relevance component: the rank of a candidate passage will be adjusted according to the elapsed time between the query’s target date and the passage’s version timestamp, while still leveraging its semantic similarity to the query. To evaluate the approach, we will construct a benchmark comprising regulatory documents with overlapping revisions and time‑stamped queries, measuring how well the combined temporal‑semantic ranking improves answer accuracy.

**Research question:** Does adding a temporal relevance component that adjusts passage rankings based on elapsed time between query target date and version timestamp improve answer accuracy (Exact Match and F1) over semantic-only retrievers and existing time-aware baselines for open-domain question answering on versioned regulatory documents?

**Literature investigated:** 94 papers retrieved from 7 searches (openalex: 44, crossref: 24, arxiv: 16, semantic_scholar: 10); 6 analyzed; 2 rated highly relevant.

**Assessment:** Promising but requires experimental validation. **[Inference]** The idea shows promise based on empirical evidence from related work (TempRALM) demonstrating that temporal relevance can significantly improve QA accuracy. However, critical uncertainties remain regarding its effectiveness in the specific context of versioned regulatory text with dense semantic overlap, potential confounding from recency bias, and the feasibility of a truly retrieval-agnostic temporal component. Validation through targeted experimentation is needed.

**Closest existing work:** Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval (2025) [1]; It's About Time: Incorporating Temporality in Retrieval Augmented Language Models (2024) [2]

**Potential overlap:** Our idea overlaps with existing work in combining temporal relevance with semantic similarity to improve retrieval quality. Re3 uses a query-aware gating mechanism to balance semantic and temporal information in general TIR, while TempRALM uses inverse time difference scoring in a RALM setting. Both demonstrate that temporal signals can enhance retrieval/QA performance.

**Potential distinction:** Our idea differs by targeting retrieval-agnostic application to open-domain QA over versioned regulatory documents, focusing on selecting the correct version for time-specific queries amidst dense semantic overlap across amendments, and proposing a benchmark specifically for regulatory text with overlapping versions. Unlike Re3's general TIR focus or TempRALM's RALM specificity, we aim for broad applicability across retriever types and a use case where temporal validity is critical for correctness.

**Major risk:** The primary risk is that observed improvements may stem from recency bias rather than genuine temporal relevance for time-specific queries; both Re3 and TempRALM optimize for recency (selecting freshest documents), which may not align with selecting the correct version for a specific point in time in regulatory contexts where older versions remain legally valid.

**Recommended experiment:** Evaluating Temporal Relevance Component for Question Answering over Versioned Regulatory Documents (E001)

**Research decision:** Insufficient evidence. **[Inference]** Basis: high-importance questions remain unresolved (U002, U004, U006, U007). This describes the state of the evidence, not the absolute value of the idea.

**Investigation:** 16 steps chosen from the research state; 7 uncertainties raised, 1 resolved, 6 still open or unresolved (Section 13, Appendix C).

**Stopped by a safety limit:** Stopping: iteration budget reached (16). Conclusions below cover only what was recorded before the limit.

**Claim grounding:** 17/19 evidence and inference claims have at least one verified source.

**Incomplete phases:** gaps, modifications. Sections that depend on them are marked as not recorded.

This report does not declare the idea novel. Absence of a matching paper in these searches does not establish novelty; see Section 13.

## 2. Original Research Idea

> The reliability of open‑domain question answering drops sharply when source texts are continuously amended, as in statutes, policies, or regulations. In such settings each new amendment supersedes earlier clauses while retaining much of the original wording, creating a dense semantic overlap across successive versions. Existing time‑aware retrieval techniques treat each version as an isolated snapshot and therefore cannot distinguish which revision best matches a time‑specific query. We propose to develop a retrieval‑agnostic framework that enriches any standard document retriever with a temporal relevance component: the rank of a candidate passage will be adjusted according to the elapsed time between the query’s target date and the passage’s version timestamp, while still leveraging its semantic similarity to the query. To evaluate the approach, we will construct a benchmark comprising regulatory documents with overlapping revisions and time‑stamped queries, measuring how well the combined temporal‑semantic ranking improves answer accuracy.

## 3. Formalized Research Question

**Research question:** Does adding a temporal relevance component that adjusts passage rankings based on elapsed time between query target date and version timestamp improve answer accuracy (Exact Match and F1) over semantic-only retrievers and existing time-aware baselines for open-domain question answering on versioned regulatory documents?

**Hypothesis:** **[Hypothesis]** Combining temporal relevance with semantic similarity in document ranking will significantly improve answer accuracy (Exact Match and F1) over semantic-only retrievers and existing time-aware baselines on a benchmark of versioned regulatory documents with time-stamped queries.

| Aspect | Formalization |
|---|---|
| Problem | The reliability of open-domain question answering drops sharply when source texts are continuously amended (e.g., statutes, policies, regulations) due to dense semantic overlap across versions, making it difficult for retrievers to identify the correct version for a time-specific query. |
| Target domain | Open-domain question answering over versioned regulatory documents. |
| Proposed method | A retrieval-agnostic framework that enriches any standard document retriever with a temporal relevance component. The framework adjusts the rank of a candidate passage by combining its semantic similarity to the query with a temporal relevance score based on the elapsed time between the query's target date and the passage's version timestamp (e.g., using a decay function or learned gating mechanism). |
| Target system | Not recorded |
| Expected contribution | A novel temporal relevance component that is retrieval-agnostic, a benchmark for evaluating QA over versioned regulatory documents, and empirical evidence that temporal relevance improves QA accuracy in continuously amended text settings. |
| Independent variables | Retrieval approach (baseline: semantic-only; proposed: semantic + temporal relevance component) |
| Dependent variables | Answer accuracy (Exact Match, F1 score) |
| Controls | Underlying retriever type (e.g., BM25, DPR), Dataset of versioned regulatory documents, Set of time-stamped queries, Evaluation metric |

**Assumptions**

- Version timestamps are available for each passage.
- Queries have an associated target date.
- Semantic similarity (e.g., from a dense retriever) is a relevant baseline.
- Temporal relevance can be modeled as a decreasing function of elapsed time.
- The framework can be applied to both dense and sparse retrievers without modification to their core.

**Expected benefits / potential risks**

_None recorded._

**Ambiguities**

| Question | Resolution | Resolved by |
|---|---|---|
| How to combine temporal relevance with semantic similarity? (e.g., weighted sum, gating mechanism) | Look at Re3 paper (arxiv:2509.01306) which uses a query-aware gating mechanism to balance relevance and recency. We can adopt a similar mechanism or use a simple weighted sum. | literature |
| What type of temporal decay function to use? (e.g., linear, exponential, step) | We will assume an exponential decay function based on common practice, but the exact form can be learned or tuned; this is a design choice to be explored. | assumption |
| What retrieval models to use as base? (dense, sparse) | We will test with both a dense retriever (e.g., DPR) and a sparse retriever (e.g., BM25) to demonstrate agnosticism. | assumption |
| What benchmark to use for versioned regulatory documents? | We will construct a benchmark using publicly available versioned regulatory documents (e.g., U.S. Code, Federal Regulations) and create time-stamped queries based on amendment dates. | assumption |
| What evaluation metrics beyond EM/F1? | We will use Exact Match and F1 as standard QA metrics. | assumption |
| How to handle queries that may have ambiguous target dates? | We assume each query will have a clear target date (e.g., "as of 2020-01-01"). | assumption |

## 4. Existing Research

Overlap values are heuristic signals assigned during analysis, not measurements of novelty.

| Paper | Relevance | Method | Problem / method / evaluation overlap | Read from |
|---|---|---|---|---|
| It's About Time: Incorporating Temporality in Retrieval Augmented Language Models (2024) [2] | high | TempRALM augments the retriever with a temporal score 𝜏(𝑞𝑡,𝑑𝑡) = 𝛼𝑠𝑐𝑎𝑙𝑒 𝑞𝑡−𝑑𝑡 (inverse of time difference) normalized to align with semantic score range, combined with semantic score 𝑠(𝑞,𝑑) = ⟨𝑓𝜃(𝑞),𝑓 𝜃(𝑑)⟩. The retriever fetches documents based on both semantic and temporal relevance. | 0.6 / 0.7 / 0.6 | full_text |
| Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval (2025) [1] | high | Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism. | 0.6 / 0.7 / 0.5 | abstract |
| Document Listing on Versioned Documents (2013) [3] | medium | Not stated in abstract. | 0.2 / 0.1 / 0.1 | abstract |
| Continuous Temporal Top-k Query over Versioned Documents (2014) [4] | medium | Not stated in abstract. | 0.3 / 0.2 / 0.1 | abstract |
| Managing Branch Versioning in Versioned/Temporal XML Documents (n.d.) [5] | medium | Not stated in abstract. | 0.3 / 0.2 / 0.1 | abstract |
| Temporal and multi-versioned XML documents: A survey (2014) [6] | medium | Not stated in abstract. | 0.3 / 0.2 / 0.1 | abstract |

<details><summary>Full paper analyses</summary>

#### It's About Time: Incorporating Temporality in Retrieval Augmented Language Models (2024) [2]

- **Problem:** Ensuring that users receive the most relevant and up-to-date information, especially in the presence of multiple versions of web content from different time points remains a critical challenge for information retrieval. This challenge has recently been compounded by the increased use of question answering tools trained on Wikipedia or web content and powered by large language models (LLMs) which have been found to make up information (or hallucinate), and in addition have been shown to struggle with the temporal dimensions of information. Even Retriever Augmented Language Models (RALMs) which incorporate a document database to reduce LLM hallucination are unable to handle temporal queries correctly.
- **Method:** TempRALM augments the retriever with a temporal score 𝜏(𝑞𝑡,𝑑𝑡) = 𝛼𝑠𝑐𝑎𝑙𝑒 𝑞𝑡−𝑑𝑡 (inverse of time difference) normalized to align with semantic score range, combined with semantic score 𝑠(𝑞,𝑑) = ⟨𝑓𝜃(𝑞),𝑓 𝜃(𝑑)⟩. The retriever fetches documents based on both semantic and temporal relevance.
- **Main contribution:** TempRALM, a temporally-aware Retriever Augmented Language Model (RALM) with few-shot learning extensions, demonstrating up to 74% improvement in Exact Match over baseline RALM without requiring model pre-training, recalculating or replacing the RALM document index, or adding other computationally intensive elements.
- **Key assumptions:** Timestamps are available for queries and documents.; Temporal relevance can be modeled as inversely proportional to time difference.; Semantic score from dense retriever (Contriever) is suitable for combining with temporal score.
- **Datasets / benchmarks:** Tennis grand slam time-sensitive dataset (curated for temporally evolving QA), TPQ-2019 and TPQ-2020 test sets (temporal proximity queries)
- **Baselines:** Atlas-large (pre-trained RALM model)
- **Metrics:** Exact Match, Recall@1, Recall@5
- **Results:** TempRALM improves Exact Match from 64.84 to 71.72 (32-shot), 74.68 to 75.78 (64-shot), 76.88 to 77.80 (128-shot); Recall@1 improves from 0.54 to 0.63 (TPQ-2019) and 0.24 to 0.64 (TPQ-2020); Recall@5 shows similar gains.
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** TempRALM augments a specific RALM (Atlas) with a temporal score based on inverse time difference, evaluated on a synthetic tennis dataset. Our idea proposes a retrieval-agnostic temporal relevance component that adjusts passage ranks based on elapsed time between query target date and version timestamp, targeting open-domain QA over continuously amended regulatory documents where amendments create dense semantic overlap across versions. We aim to improve answer accuracy (EM/F1) via a framework applicable to any retriever (dense/sparse), and we propose a benchmark of regulatory documents with overlapping revisions. _(basis: not stated)_

#### Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval (2025) [1]

- **Problem:** Temporal Information Retrieval (TIR) is a critical yet unresolved task for modern search systems, retrieving documents that not only satisfy a query's information need but also adhere to its temporal constraints.
- **Method:** Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism.
- **Main contribution:** Re3 framework and Re2Bench benchmark for disentangling and evaluating Relevance, Recency, and their hybrid combination in temporal information retrieval.
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** Re2Bench benchmark, Re2Bench
- **Baselines:** not stated in abstract
- **Metrics:** R@1 (Recall@1)
- **Results:** Re3 achieves state-of-the-art results, leading in R@1 across all three subsets of Re2Bench; ablation studies confirm robustness and generalization across diverse encoders and real-world settings.
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** Available online at https://anonymous.4open.science/r/Re3-0C5A
- **Relation to idea:** Re3 addresses general temporal information retrieval balancing relevance and recency via a query-aware gating mechanism. Our idea focuses on open-domain question answering over continuously amended regulatory documents where each new amendment supersedes earlier clauses, creating dense semantic overlap across versions. We propose a retrieval-agnostic temporal relevance component that adjusts passage ranks based on elapsed time between query target date and version timestamp, aiming to select the correct version for a time-specific query. While both incorporate temporal signals, Re3 targets general TIR benchmarks, whereas we target QA accuracy over versioned regulatory text, and our framework is designed to be agnostic to the underlying retriever. _(basis: not stated)_

#### Document Listing on Versioned Documents (2013) [3]

- **Problem:** Not stated in abstract; title suggests document listing on versioned documents.
- **Method:** Not stated in abstract.
- **Main contribution:** Not stated in abstract.
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** Not stated in abstract.
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** The paper focuses on document listing on versioned documents, which is related to versioned document handling. However, without abstract details, specific overlap with our idea (temporal relevance component for QA over regulatory text) cannot be determined. Likely deals with listing documents in a versioned setting rather than retrieval ranking for question answering. _(basis: not stated)_

#### Continuous Temporal Top-k Query over Versioned Documents (2014) [4]

- **Problem:** Not stated in abstract; title suggests continuous temporal top-k query processing over versioned documents.
- **Method:** Not stated in abstract.
- **Main contribution:** Not stated in abstract.
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** Not stated in abstract.
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** The paper focuses on continuous temporal top-k queries over versioned documents, which is related to versioned document retrieval. However, without abstract details, specific overlap with our idea (temporal relevance component for QA over regulatory text) cannot be determined. Likely deals with query processing rather than retrieval ranking for question answering. _(basis: not stated)_

#### Managing Branch Versioning in Versioned/Temporal XML Documents (n.d.) [5]

- **Problem:** Not stated in abstract; title suggests managing branch versioning in versioned/temporal XML documents.
- **Method:** Not stated in abstract.
- **Main contribution:** Not stated in abstract.
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** Not stated in abstract.
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** The paper focuses on managing branch versioning in versioned/temporal XML documents, which is related to versioned document handling. However, without abstract details, specific overlap with our idea (temporal relevance component for QA over regulatory text) cannot be determined. Likely concerns version control mechanisms rather than retrieval ranking for question answering. _(basis: not stated)_

#### Temporal and multi-versioned XML documents: A survey (2014) [6]

- **Problem:** Not stated in abstract; title indicates a survey on temporal and multi-versioned XML documents.
- **Method:** Not stated in abstract.
- **Main contribution:** Not stated in abstract.
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** Not stated in abstract.
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** The paper is a survey on temporal and multi-versioned XML documents, which is related to versioned document handling. However, without abstract details, specific overlap with our idea (temporal relevance component for QA over regulatory text) cannot be determined. Likely surveys versioned XML techniques rather than retrieval ranking for question answering. _(basis: not stated)_

</details>

## 5. Research Landscape

```text
Temporal Information Retrieval for Question Answering over Versioned Text
├── Temporal Relevance Ranking Methods  [1] [2]
├── Versioned Document Query Processing  [4] [5] [3]
└── Surveys on Temporal/Multi-versioned XML  [6]
```

**Where the idea fits:** **[Inference]** Temporal Relevance Ranking Methods

**Dominant approaches**

- Temporal relevance scoring combined with semantic similarity
- Query-aware gating mechanisms
- Inverse time difference scoring

**Common assumptions**

- Timestamps are available for queries and documents
- Temporal relevance decreases with time difference
- Semantic similarity from retrievers is a relevant signal

**Common datasets**

- Re2Bench
- Tennis grand slam time-sensitive dataset
- Versioned XML document collections (not specified)

**Common benchmarks**

- Re2Bench
- TPQ-2019/TPQ-2020
- Temporal top-k query benchmarks (not specified)

**Common metrics**

- Recall@1
- Exact Match
- F1
- Recall@5

**Underexplored combinations**

- **[Hypothesis]** Retrieval-agnostic temporal relevance for open-domain QA over regulatory text
- **[Hypothesis]** Handling dense semantic overlap across successive amendments
- **[Hypothesis]** Benchmark with overlapping versioned regulatory documents and time-stamped queries

**Limitations repeated across papers**

- Limited to specific retriever types (e.g., dense only) [2]
- Evaluation on synthetic or narrow datasets [2], [1]
- Lack of generalization to regulatory text 
- No consideration of dense semantic overlap across versions 

**Contradictions between papers**

- Existing time-aware retrieval techniques treat each version as an isolated snapshot, making it difficult to distinguish which revision matches a time-specific query. 

## 6. Closest Existing Work

**[Inference]** Re3 proposes a query-aware gating mechanism to balance relevance and recency in general temporal information retrieval, while TempRALM augments a RALM with inverse time difference scoring. Both combine temporal and semantic signals but target different settings (general TIR and RALMs respectively) and neither specifically addresses retrieval-agnostic application to open-domain QA over continuously amended regulatory documents with dense semantic overlap.

- Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval (2025) [1]: Re3 addresses general temporal information retrieval balancing relevance and recency via a query-aware gating mechanism. Our idea focuses on open-domain question answering over continuously amended regulatory documents where each new amendment supersedes earlier clauses, creating dense semantic overlap across versions. We propose a retrieval-agnostic temporal relevance component that adjusts passage ranks based on elapsed time between query target date and version timestamp, aiming to select the correct version for a time-specific query. While both incorporate temporal signals, Re3 targets general TIR benchmarks, whereas we target QA accuracy over versioned regulatory text, and our framework is designed to be agnostic to the underlying retriever.
- It's About Time: Incorporating Temporality in Retrieval Augmented Language Models (2024) [2]: TempRALM augments a specific RALM (Atlas) with a temporal score based on inverse time difference, evaluated on a synthetic tennis dataset. Our idea proposes a retrieval-agnostic temporal relevance component that adjusts passage ranks based on elapsed time between query target date and version timestamp, targeting open-domain QA over continuously amended regulatory documents where amendments create dense semantic overlap across versions. We aim to improve answer accuracy (EM/F1) via a framework applicable to any retriever (dense/sparse), and we propose a benchmark of regulatory documents with overlapping revisions.

## 7. Potential Overlap

**Overlap:** **[Inference]** Our idea overlaps with existing work in combining temporal relevance with semantic similarity to improve retrieval quality. Re3 uses a query-aware gating mechanism to balance semantic and temporal information in general TIR, while TempRALM uses inverse time difference scoring in a RALM setting. Both demonstrate that temporal signals can enhance retrieval/QA performance.

**Potential distinction:** **[Inference]** Our idea differs by targeting retrieval-agnostic application to open-domain QA over versioned regulatory documents, focusing on selecting the correct version for time-specific queries amidst dense semantic overlap across amendments, and proposing a benchmark specifically for regulatory text with overlapping versions. Unlike Re3's general TIR focus or TempRALM's RALM specificity, we aim for broad applicability across retriever types and a use case where temporal validity is critical for correctness.

**Novelty questions**

_None recorded._

## 8. Potential Research Gap

_Not recorded: this phase did not produce the required records._

## 9. Critique

| | |
|---|---|
| Strongest argument FOR | Empirical evidence from TempRALM shows that adding temporal relevance (inverse time difference scoring) to a retrieval-augmented language model improves Exact Match by up to 74% over baseline on temporal question answering tasks, demonstrating that temporal signals can significantly enhance QA accuracy when semantic similarity alone is insufficient to distinguish temporally relevant information. |
| Strongest argument AGAINST | The primary risk is that observed improvements may stem from recency bias rather than genuine temporal relevance for time-specific queries; both Re3 and TempRALM optimize for recency (selecting freshest documents), which may not align with selecting the correct version for a specific point in time in regulatory contexts where older versions remain legally valid. |
| Most important unresolved question | Does temporal relevance improve QA accuracy on versioned regulatory documents where amendments create dense semantic overlap across versions, making it difficult to distinguish the correct version for a time-specific query? |
| Most dangerous experimental confounder | Recency bias: the framework's tendency to favor more recent documents could improve metrics simply by returning newer information, regardless of whether that information is actually valid for the query's target date, especially problematic in regulatory text where older versions may still be legally applicable. |
| Closest existing work | [1], [2] |
| Potential contribution | **[Hypothesis]** A retrieval-agnostic temporal relevance component that adjusts passage ranks based on elapsed time between query target date and version timestamp, a benchmark of versioned regulatory documents with overlapping revisions and time-stamped queries, and empirical evidence showing improved answer accuracy (EM/F1) over semantic-only retrievers and existing time-aware baselines in continuously amended text settings. |

**Technical validity**

_None recorded._

**Experimental validity**

_None recorded._

**Practicality**

_None recorded._

## 10. Proposed Modifications

_Not recorded: this phase did not produce the required records._

## 11. Recommended Experimental Design

### E001: Evaluating Temporal Relevance Component for Question Answering over Versioned Regulatory Documents

- **Research question:** Does adding a temporal relevance component that adjusts passage rankings based on elapsed time between query target date and version timestamp improve answer accuracy (Exact Match and F1) over semantic-only retrievers and existing time-aware baselines for open-domain question answering on versioned regulatory documents?
- **Hypothesis:** **[Hypothesis]** Combining temporal relevance with semantic similarity in document ranking will significantly improve answer accuracy (Exact Match and F1) over semantic-only retrievers and existing time-aware baselines on a benchmark of versioned regulatory documents with overlapping revisions and time-stamped queries.
- **Proposed method:** A retrieval-agnostic temporal relevance component that computes a temporal score as a decaying function of elapsed time (e.g., exponential decay) between the query's target date and the document version's timestamp. This temporal score is combined with semantic similarity scores from a retriever (dense or sparse) via a weighted sum or lightweight gating mechanism, without modifying the retriever's core ranking algorithm. The framework is applied to both dense (DPR) and sparse (BM25) retrievers to demonstrate agnosticism.
- **Baselines:** BM25 (semantic-only), DPR (semantic-only), Date-filtering baseline (retrieve documents with version timestamp <= query date), Timestamp-aware re-ranking using Re3's query-aware gating mechanism applied to retriever output, Random temporal bias (shuffle temporal scores)
- **Datasets:** Constructed benchmark of versioned regulatory documents (e.g., U.S. Code, Code of Federal Regulations) with version timestamps and overlapping revisions, Time-stamped queries generated from amendment logs where answer validity depends on specific version at a given date, Evaluation set annotated by legal experts or via automated verification against official amendment history
- **Workloads:** Question answering over regulatory text
- **Hardware:** ["Single GPU (NVIDIA RTX 3090 or equivalent) for dense retriever experiments", "CPU-only for sparse retriever (BM25) experiments"]
- **Software environment:** ["Python 3.9+", "PyTorch 2.0+", "HuggingFace Transformers", "Faiss or Elasticsearch for vector/BM25 retrieval", "NumPy, pandas"]
- **Metrics:** Exact Match, F1 score, Mean Reciprocal Rank (MRR), Recall@5
- **Ablations:** No temporal component (semantic-only); Linear temporal decay function; Step temporal decay function; Weighted sum combination vs. gating mechanism; Dense retriever only; Sparse retriever only
- **Controls:** Same underlying retriever configuration across conditions; Identical document indexing and preprocessing; Fixed query set and evaluation splits; Consistent random seeds for reproducibility; Same hardware and software environment for comparable runs
- **Confounders addressed:** Recency bias (by including queries where the correct version is not the most recent); Timestamp noise (by using exact version timestamps from official sources); Semantic similarity confounding (by selecting document pairs with high lexical overlap but different temporal validity); Query ambiguity (by ensuring each query has a clear target date)
- **Expected outcomes:** ["Statistically significant improvement in Exact Match and F1 scores for the proposed temporal relevance component over all baselines, particularly on queries requiring non‑most‑recent versions.", "Ablations show that both the temporal decay function and combination method contribute to gains."]
- **Failure conditions:** No significant improvement (p > 0.05) over semantic‑only baselines; Degradation in performance on queries requiring older versions indicating recency bias dominance; High variance across runs suggesting instability
- **Reproducibility:** ["Provide open‑source code repository with scripts for benchmark construction, retrieval implementation, training/inference, and evaluation.", "Include detailed README, versioned data preprocessing steps, random seed configuration, and hardware specifications.", "Release the constructed benchmark under a permissive license."]
- **Related work:** [1], [2]

## 12. Experimental Results

Experiment not performed. The designs in Section 11 are untested.

## 13. Remaining Uncertainty

- Literature coverage: searched 7 queries over arxiv, crossref, openalex, semantic_scholar. Work outside these queries and sources, very recent preprints, and non-English work may be missing; the absence of matching work here does not establish novelty.
- Some source requests failed and their results are missing: semantic_scholar (api.semanticscholar.org failed after 5 attempts (HTTP 429)).
- Metadata warning for It's About Time: Incorporating Temporality in Retrieval Augmented Language Models (2024) [2]: abstract (from arxiv) never mentions 'It's About Time'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for The COMET Handbook: version 1.0 (2017) [7]: abstract (from openalex) never mentions 'The COMET Handbook'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for PullNet: Open Domain Question Answering with Iterative Retrieval on Knowledge Bases and Text (2019) [8]: abstract (from openalex) never mentions 'PullNet'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding (2019) [9]: abstract (from openalex) never mentions 'BERT'; it may belong to another work. Its abstract was not accepted as direct evidence.
- 5 of 6 analyses are based on abstracts only.
- Unresolved question: Does temporal relevance improve QA accuracy on versioned regulatory documents where amendments create dense semantic overlap across versions, making it difficult to distinguish the correct version for a time-specific query?
- Ambiguity (assumption): What type of temporal decay function to use? (e.g., linear, exponential, step); assumed: We will assume an exponential decay function based on common practice, but the exact form can be learned or tuned; this is a design choice to be explored.
- Ambiguity (assumption): What retrieval models to use as base? (dense, sparse); assumed: We will test with both a dense retriever (e.g., DPR) and a sparse retriever (e.g., BM25) to demonstrate agnosticism.
- Ambiguity (assumption): What benchmark to use for versioned regulatory documents?; assumed: We will construct a benchmark using publicly available versioned regulatory documents (e.g., U.S. Code, Federal Regulations) and create time-stamped queries based on amendment dates.
- Ambiguity (assumption): What evaluation metrics beyond EM/F1?; assumed: We will use Exact Match and F1 as standard QA metrics.
- Ambiguity (assumption): How to handle queries that may have ambiguous target dates?; assumed: We assume each query will have a clear target date (e.g., "as of 2020-01-01").
- Claims without a verified source: C008, C009.
- Phases that did not complete: gaps, modifications.
- No hypothesis in this report has been tested experimentally.

**Uncertainty ledger**

| Id | Question | Category | Importance | Status | Evidence for / against | Resolution |
|---|---|---|---|---|---|---|
| U002 | How similar is our proposed method to Re3 (arxiv:2509.01306) which balances relevance and recency via a query-aware gating mechanism? | overlap | high | unresolved | [1], [2] / none | Both Re3 and our idea combine semantic and temporal information to improve retrieval/temporal reasoning. However, Re3 uses a query-aware gating mechanism to dynamically balance relevance and recency in general temporal information retrieval, while our idea proposes a retrieval-agnostic temporal relevance component that adjusts passage ranks based on elapsed time between query target date and version timestamp, targeting open-domain QA over continuously amended regulatory documents where amendments create dense semantic overlap. The core concept of integrating temporal signals overlaps, but the mechanisms, evaluation settings, and application specifics differ. |
| U004 | Does temporal relevance actually improve QA accuracy, or could it hurt due to noise or misalignment? | validity | high | open | [2] / none | Experiment plan designed to test whether adding a temporal relevance component improves QA accuracy on versioned regulatory documents; results pending. |
| U006 | Does temporal relevance improve QA accuracy on versioned regulatory documents where amendments create dense semantic overlap across versions, making it difficult to distinguish the correct version for a time-specific query? | validity | high | unresolved | [2], [1] / none | No existing work directly evaluates temporal relevance for QA over versioned regulatory documents; TempRALM uses tennis grand slam data and Re3 focuses on general TIR benchmarks, leaving the effect on versioned regulatory text with dense semantic overlap untested. |
| U007 | Can a temporal relevance component based on elapsed time be effectively applied to both dense (e.g., DPR) and sparse (e.g., BM25) retrievers without modification to their core algorithms, given differences in score distributions and normalization? | feasibility | high | unresolved | [2], [1] / none | Existing work shows TempRALM is designed for dense retrievers (Contriever-based) with no mention of sparse retrievers, while Re3 demonstrates generalization across diverse dense encoders but not sparse. No evidence demonstrates application to both dense (e.g., DPR) and sparse (e.g., BM25) retrievers without modification to core algorithms, leaving the feasibility of a truly retrieval-agnostic temporal relevance component unresolved. |
| U003 | Can we construct a benchmark of versioned regulatory documents with time-stamped queries? | feasibility | medium | open | none / none | Not recorded |
| U005 | Could observed improvements be due to better retrieval of recent documents rather than temporal relevance per se? | confounder | medium | partially resolved | none / none | While TempRALM's scoring mechanism inherently prefers more recent passages within the valid temporal window, their evaluation shows largest improvements when querying about past events where semantic matching to current text fails (different years), suggesting the temporal component primarily helps select passages from the correct time period rather than merely preferring recent documents. However, their evaluation design (where correct answers are always the most recent valid passage) prevents disentangling whether improvements come from selecting the correct time period versus preferring the most recent passage within that period. Re3's Re2Bench, designed to disentangle relevance and recency, may offer a cleaner assessment. |
| U001 | Is there existing work that combines temporal relevance with semantic similarity in a retrieval-agnostic way for QA over versioned regulatory text? | novelty | high | resolved | [1], [2], [10] / none | No existing work explicitly combines temporal relevance with semantic similarity in a retrieval-agnostic way for QA over versioned regulatory text. Related work includes Re3 (arxiv:2509.01306) which balances semantic and temporal information via a query-aware gating mechanism for general temporal information retrieval, and TempRALM (arxiv:2401.13222) which adds a temporal score to a specific RALM, but neither targets retrieval-agnostic application to versioned regulatory QA. Policy document QA studies (e.g., arxiv:2601.15457) focus on RAG architectures without temporal components. Thus the gap remains. |

## 14. Suggested Next Steps

1. Run the recommended experiment E001 (Evaluating Temporal Relevance Component for Question Answering over Versioned Regulatory Documents) with budget-matched baselines.
2. Resolve: Does temporal relevance improve QA accuracy on versioned regulatory documents where amendments create dense semantic overlap across versions, making it difficult to distinguish the correct version for a time-specific query?
3. Design a control for the confounder: Recency bias: the framework's tendency to favor more recent documents could improve metrics simply by returning newer information, regardless of whether that information is actually valid for the query's target date, especially problematic in regulatory text where older versions may still be legally applicable.
4. Read the full text of the closest work analyzed only from abstracts: [1].
5. Search for work newer than the most recent retrieved paper (2026) before claiming a distinction.

## 15. References

1. Jiawei Cao, Jie Ouyang, Zhaomeng Zhou et al.. **Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2509.01306> (id `arxiv:2509.01306`; retrieved from arxiv)
2. Anoushka Gade, Jorjeta Jetcheva. **It's About Time: Incorporating Temporality in Retrieval Augmented Language Models**. _arXiv (preprint)_, 2024. <https://arxiv.org/abs/2401.13222> (id `arxiv:2401.13222`; retrieved from arxiv)
3. Francisco Claude, J. Ian Munro. **Document Listing on Versioned Documents**. _Lecture Notes in Computer Science_, 2013. <https://doi.org/10.1007/978-3-319-02432-5_12> (id `doi:10.1007/978-3-319-02432-5_12`; retrieved from crossref; 8 citations per crossref)
4. Chao Lan, Yong Zhang, Chunxiao Xing et al.. **Continuous Temporal Top-k Query over Versioned Documents**. _Lecture Notes in Computer Science_, 2014. <https://doi.org/10.1007/978-3-319-08010-9_55> (id `doi:10.1007/978-3-319-08010-9_55`; retrieved from crossref; 0 citations per crossref)
5. Luis J. Arévalo Rosado, Antonio Polo Márquez, Jorge Martínez Gil. **Managing Branch Versioning in Versioned/Temporal XML Documents**. _Lecture Notes in Computer Science_, n.d.. <https://doi.org/10.1007/978-3-540-75288-2_9> (id `doi:10.1007/978-3-540-75288-2_9`; retrieved from crossref; 4 citations per crossref)
6. Sidra Faisal, Mansoor Sarwar. **Temporal and multi-versioned XML documents: A survey**. _Information Processing & Management_, 2014. <https://doi.org/10.1016/j.ipm.2013.08.003> (id `doi:10.1016/j.ipm.2013.08.003`; retrieved from crossref; 19 citations per crossref)
7. Paula Ruth Williamson, Douglas G. Altman, Heather Bagley et al.. **The COMET Handbook: version 1.0**. _Trials_, 2017. <https://doi.org/10.1186/s13063-017-1978-4> (id `doi:10.1186/s13063-017-1978-4`; retrieved from openalex; 2085 citations per openalex)
8. Haitian Sun, Tania Bedrax-Weiss, William W. Cohen. **PullNet: Open Domain Question Answering with Iterative Retrieval on Knowledge Bases and Text**. 2019. <https://doi.org/10.18653/v1/d19-1242> (id `doi:10.18653/v1/d19-1242`; retrieved from openalex; 333 citations per openalex)
9. Jacob Devlin, Ming‐Wei Chang, Kenton Lee et al.. **BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding**. 2019. <https://doi.org/10.18653/v1/n19-1423> (id `doi:10.18653/v1/n19-1423`; retrieved from openalex; 33744 citations per openalex)
10. A. Maharjan, Umesh Yadav. **Chunking, Retrieval, and Re-ranking: An Empirical Evaluation of RAG Architectures for Policy Document Question Answering**. _arXiv.org_, 2026. <https://www.semanticscholar.org/paper/f3d7e0165df8da3fad6cbfb776e0371c31d68c48> doi:10.48550/arxiv.2601.15457 (id `arxiv:2601.15457`; retrieved from semantic_scholar; 3 citations per semantic_scholar)

<details><summary>Other retrieved papers (not cited in this report)</summary>

- Faster temporal range queries over versioned text (2011) <https://doi.org/10.1145/2009916.2009993> `doi:10.1145/2009916.2009993`
- ExpandFuse: A Hybrid Retrieval Framework with Query Expansion and Topic-Aware Reranking for Multi-Hop Question Answering (2025) <https://www.semanticscholar.org/paper/985710e9819315617b6fd4c46abf8650efabb30a> `doi:10.1109/bigdata66926.2025.11402490`
- Enhancing Temporal Knowledge Graph Question Answering via Multi-level Temporal Knowledge Retrieval with Large Language Models (2025) <https://doi.org/10.1109/bigdia68682.2025.11382820> `doi:10.1109/bigdia68682.2025.11382820`
- MARA: A Multimodal Adaptive Retrieval-Augmented Framework for Document Question Answering (2025) <https://www.semanticscholar.org/paper/b1e326eb8586518b3d1c8b3fed0b438a396a072e> `arxiv:2604.16313`
- Agnostic Multi-Source Retrieval-Augmented Generation for Documents and Database Question Answering (2026) <https://doi.org/10.62710/qw0ytn73> `doi:10.62710/qw0ytn73`
- Bridging dual knowledge graphs for multi-hop question answering in construction safety (2025) <https://www.semanticscholar.org/paper/a001f67d26416bdadeb40811e682c169d640770a> `arxiv:2507.13625`
- DocQA: Document Driven Question Answering (2024) <https://www.semanticscholar.org/paper/6baa3c135c951cadb5dd365c497492d67631a3ea> `doi:10.17148/iarjset.2024.11515`
- TwiRGCN: Temporally Weighted Graph Convolution for Question Answering over Temporal Knowledge Graphs (2022) <https://arxiv.org/abs/2210.06281> `arxiv:2210.06281`
- Federated Retrieval Augmented Generation for Multi-Product Question Answering (2025) <https://www.semanticscholar.org/paper/95264cbf4d69375d9d9857cde061bfb8435451fc> `arxiv:2501.14998`
- LeAdQA: LLM-Driven Context-Aware Temporal Grounding for Video Question Answering (2025) <https://arxiv.org/abs/2507.14784> `arxiv:2507.14784`
- Question Answering under Temporal Conflict: Evaluating and Organizing Evolving Knowledge with LLMs (2025) <https://arxiv.org/abs/2506.07270> `arxiv:2506.07270`
- Preparing a collection of radiology examinations for distribution and retrieval (2015) <https://doi.org/10.1093/jamia/ocv080> `doi:10.1093/jamia/ocv080`
- Membership Inference Attacks for Retrieval Based In-Context Learning for Document Question Answering (2026) <https://www.semanticscholar.org/paper/456f1efeb1ba8ae7df6f9b0c44225a1ef7b5d399> `arxiv:2605.04116`
- TVQA+: Spatio-Temporal Grounding for Video Question Answering (2019) <https://arxiv.org/abs/1904.11574> `arxiv:1904.11574`
- Complex Temporal Question Answering on Knowledge Graphs (2021) <https://arxiv.org/abs/2109.08935> `arxiv:2109.08935`
- ForecastTKGQuestions: A Benchmark for Temporal Question Answering and Forecasting over Temporal Knowledge Graphs (2022) <https://arxiv.org/abs/2208.06501> `arxiv:2208.06501`
- Relevance of Topic and Focus for Automatic Question Answering (1983) <https://doi.org/10.1007/978-94-009-7016-8_11> `doi:10.1007/978-94-009-7016-8_11`
- TempRAA: temporal relation-aware alignment for enhancing LLMs reasoning in time-sensitive knowledge graph question answering (2026) <https://doi.org/10.1007/s10844-026-01027-w> `doi:10.1007/s10844-026-01027-w`
- M3TQA: Multi-View, Multi-Hop and Multi-Stage Reasoning for Temporal Question Answering (2024) <https://doi.org/10.1109/icassp48485.2024.10448071> `doi:10.1109/icassp48485.2024.10448071`
- Enhancing Visual Question Answering: A Novel Approach to Determining Question Relevance (2024) <https://doi.org/10.1109/icitiit61487.2024.10580857> `doi:10.1109/icitiit61487.2024.10580857`
- Generative long-form question answering : relevance, faithfulness, and succinctness (n.d.) <https://doi.org/10.14711/thesis-991013106451503412> `doi:10.14711/thesis-991013106451503412`
- Question Calibration and Multi-Hop Modeling for Temporal Question Answering (2024) <https://doi.org/10.1609/aaai.v38i17.29903> `doi:10.1609/aaai.v38i17.29903`
- Open Domain Question Answering Using Early Fusion of Knowledge Bases and Text (2018) <https://doi.org/10.18653/v1/d18-1455> `doi:10.18653/v1/d18-1455`
- Question Answering over Linked Data with Vague Temporal Adverbials (2025) <https://doi.org/10.5220/0013778400004000> `doi:10.5220/0013778400004000`
- Belief detection and temporal analysis of experts in question answering communities : case strudy on stack overflow (n.d.) <https://doi.org/10.70675/4cc30d33z4a62z4702zaf1cz54bc6900cb64> `doi:10.70675/4cc30d33z4a62z4702zaf1cz54bc6900cb64`
- Retrieval-Augmented Visual Question Answering via Built-in Autoregressive Search Engines (2025) <https://www.semanticscholar.org/paper/f40a03ac7d216205a70d28cfcea14cd69b9d46fb> `arxiv:2502.16641`
- EviGraphRAG: Constraint-Verified Retrieval-Augmented Question Answering over Event Knowledge Graphs (2026) <https://www.semanticscholar.org/paper/18792898ea10b2ef47e846c29d7ccbca796507f8> `doi:10.32604/cmc.2026.089159`
- Parameter-Efficient Abstractive Question Answering over Tables or Text (2022) <https://doi.org/10.18653/v1/2022.dialdoc-1.5> `doi:10.18653/v1/2022.dialdoc-1.5`
- MoQA: Benchmarking Multi-Type Open-Domain Question Answering (2023) <https://doi.org/10.18653/v1/2023.dialdoc-1.2> `doi:10.18653/v1/2023.dialdoc-1.2`
- Question Answering For Toxicological Information Extraction (2022) <https://drops.dagstuhl.de/entities/document/10.4230/OASIcs.SLATE.2022.3> `doi:10.4230/oasics.slate.2022.3`
- Vista: Scene-Aware Optimization for Streaming Video Question Answering under Post-Hoc Queries (2026) <https://arxiv.org/abs/2602.08448> `arxiv:2602.08448`
- APEX-MEM: Agentic Semi-Structured Memory with Temporal Reasoning for Long-Term Conversational AI (2026) <https://arxiv.org/abs/2604.14362> `arxiv:2604.14362`
- TDR 2 A：Time-sensitive Decomposition-Retrieval-Reorganization Agent for Temporal Knowledge Graph Question Answering (2025) <https://doi.org/10.2139/ssrn.5624243> `doi:10.2139/ssrn.5624243`
- Passage retrieval for question answering using sliding windows (2008) <https://doi.org/10.3115/1641451.1641455> `doi:10.3115/1641451.1641455`
- Comparing Statistical Models for Retrieval based Question-answering Dialogue: BERT vs Relevance Models (2023) <https://doi.org/10.32473/flairs.36.133386> `doi:10.32473/flairs.36.133386`
- Graph-Structured Representations for Visual Question Answering (2017) <https://doi.org/10.1109/cvpr.2017.344> `arxiv:1609.05600`
- Progressive Spatio-temporal Perception for Audio-Visual Question Answering (2023) <https://arxiv.org/abs/2308.05421> `arxiv:2308.05421`
- Improving Multi-hop Question Answering over Knowledge Graphs using Knowledge Base Embeddings (2020) <https://doi.org/10.18653/v1/2020.acl-main.412> `doi:10.18653/v1/2020.acl-main.412`
- Which academic search systems are suitable for systematic reviews or meta‐analyses? Evaluating retrieval qualities of Google Scholar, PubMed, and 26 other resources (2019) <https://doi.org/10.1002/jrsm.1378> `doi:10.1002/jrsm.1378`
- Visual information retrieval (1997) <https://doi.org/10.1145/253769.253798> `doi:10.1145/253769.253798`
- Information retrieval on the web (2000) <https://doi.org/10.1145/358923.358934> `doi:10.1145/358923.358934`
- CourseTimeQA: A Lecture-Video Benchmark and a Latency-Constrained Cross-Modal Fusion Method for Timestamped QA (2025) <https://arxiv.org/abs/2512.00360> `arxiv:2512.00360`
- AI-Assisted Pipeline for Dynamic Generation of Trustworthy Health Supplement Content at Scale (2018) <http://arxiv.org/abs/1810.04805> `arxiv:1810.04805`
- The development of animal personality: relevance, concepts and perspectives (2009) <https://doi.org/10.1111/j.1469-185x.2009.00103.x> `doi:10.1111/j.1469-185x.2009.00103.x`
- A Long Short-Term Memory Model for Answer Sentence Selection in Question Answering (2015) <https://doi.org/10.3115/v1/p15-2116> `doi:10.3115/v1/p15-2116`
- Proceedings of the 1st Workshop on Document-grounded Dialogue and Conversational Question Answering (DialDoc 2021) (2021) <https://doi.org/10.18653/v1/2021.dialdoc-1> `doi:10.18653/v1/2021.dialdoc-1`
- Proceedings of the Second DialDoc Workshop on Document-grounded Dialogue and Conversational Question Answering (2022) <https://doi.org/10.18653/v1/2022.dialdoc-1> `doi:10.18653/v1/2022.dialdoc-1`
- Proceedings of the Third DialDoc Workshop on Document-grounded Dialogue and Conversational Question Answering (2023) <https://doi.org/10.18653/v1/2023.dialdoc-1> `doi:10.18653/v1/2023.dialdoc-1`
- Vision-language models for medical report generation and visual question answering: a review (2024) <https://doi.org/10.3389/frai.2024.1430984> `arxiv:2403.02469`
- Complex Knowledge Base Question Answering: A Survey (2022) <https://doi.org/10.1109/tkde.2022.3223858> `doi:10.1109/tkde.2022.3223858`
- Is Question Answering fit for the Semantic Web?: A survey (2011) <https://doi.org/10.3233/sw-2011-0041> `doi:10.3233/sw-2011-0041`
- Bias and Unfairness in Information Retrieval Systems: New Challenges in the LLM Era (2024) <https://doi.org/10.1145/3637528.3671458> `arxiv:2404.11457`
- How UMass-FSD Inadvertently Leverages Temporal Bias (2020) <https://doi.org/10.1145/3397271.3401306> `doi:10.1145/3397271.3401306`
- Bounding Knowledge Decay From Agnostic Temporal Generalization (2025) <https://doi.org/10.31219/osf.io/nm7zr_v2> `doi:10.31219/osf.io/nm7zr_v2`
- Attention-Based Complex Logical Query on Temporal Knowledge Graph via Graph Neural Network (2024) <https://doi.org/10.1109/tbdata.2024.3489421> `doi:10.1109/tbdata.2024.3489421`
- Temporal Tree of Thought: Reasoning-Guided Visual Cue Search for Long-Video Understanding (2026) <https://arxiv.org/abs/2608.27871> `arxiv:2608.27871`
- Not All Videos Become Outdated: Short-Video Recommendation by Learning to Deconfound Release Interval Bias (2024) <https://arxiv.org/abs/2408.17332> `arxiv:2408.17332`
- CAST: Modeling Visual State Transitions for Consistent Video Retrieval (2026) <https://arxiv.org/abs/2603.08648> `arxiv:2603.08648`
- Deconfounded Video Moment Retrieval with Causal Intervention (2021) <https://doi.org/10.1145/3404835.3462823> `doi:10.1145/3404835.3462823`
- Multilevel Language and Vision Integration for Text-to-Clip Retrieval (2019) <https://doi.org/10.1609/aaai.v33i01.33019062> `doi:10.1609/aaai.v33i01.33019062`
- The Web as a Knowledge-Base for Answering Complex Questions (2018) <https://doi.org/10.18653/v1/n18-1059> `arxiv:1803.06643`
- Reinforcement learning with time intervals for temporal knowledge graph reasoning (2023) <https://doi.org/10.1016/j.is.2023.102292> `doi:10.1016/j.is.2023.102292`
- A survey on temporal knowledge graph embedding: Models and applications (2024) <https://doi.org/10.1016/j.knosys.2024.112454> `doi:10.1016/j.knosys.2024.112454`
- Temporal knowledge graph query model fusing fuzzy information modeling and dynamic path memory network (2026) <https://doi.org/10.1016/j.neucom.2026.134983> `doi:10.1016/j.neucom.2026.134983`
- The Neuroscience of Natural Rewards: Relevance to Addictive Drugs (2002) <https://doi.org/10.1523/jneurosci.22-09-03306.2002> `doi:10.1523/jneurosci.22-09-03306.2002`
- Semantic Parsing on Freebase from Question-Answer Pairs (2013) <https://doi.org/10.18653/v1/d13-1160> `doi:10.18653/v1/d13-1160`
- Fintech, regulatory arbitrage, and the rise of shadow banks (2018) <https://doi.org/10.1016/j.jfineco.2018.03.011> `doi:10.1016/j.jfineco.2018.03.011`
- The imperative for regulatory oversight of large language models (or generative AI) in healthcare (2023) <https://doi.org/10.1038/s41746-023-00873-0> `doi:10.1038/s41746-023-00873-0`
- Regulatory Question-Answering using Generative AI (2025) <https://www.semanticscholar.org/paper/c38e59b523c7821a6da5fb274234b4013553752c> `s2:c38e59b523c7821a6da5fb274234b4013553752c`
- Adaptive Retrieval Agents: Internalizing Local Context and Scaling up to the Web (2000) <https://doi.org/10.1023/a:1007653114902> `doi:10.1023/a:1007653114902`
- Key-Value Retrieval Networks for Task-Oriented Dialogue (2017) <https://doi.org/10.18653/v1/w17-5506> `arxiv:1705.05414`
- Mapping 'when'-clauses in Latin American and Caribbean languages: an experiment in subtoken-based typology (2024) <https://arxiv.org/abs/2404.18257> `arxiv:2404.18257`
- Temporal User-Agnostic Ranking: Detecting Preference Evolution while Preserving Ethical Principles (2026) <https://doi.org/10.1145/3805712.3809900> `doi:10.1145/3805712.3809900`
- Occipito-temporal connections in the human brain (2003) <https://doi.org/10.1093/brain/awg203> `doi:10.1093/brain/awg203`
- MultiSum: A Multi-Facet Approach for Extractive Social Summarization Utilizing Semantic and Sociological Relationships (2024) <https://doi.org/10.1609/aaai.v38i17.29939> `doi:10.1609/aaai.v38i17.29939`
- The PRISMA Statement for Reporting Systematic Reviews and Meta-Analyses of Studies That Evaluate Health Care Interventions: Explanation and Elaboration (2009) <https://doi.org/10.1371/journal.pmed.1000100> `doi:10.1371/journal.pmed.1000100`
- Modeling Relational Data with Graph Convolutional Networks (2018) <https://doi.org/10.1007/978-3-319-93417-4_38> `arxiv:1703.06103`
- Advances and Open Problems in Federated Learning (2020) <https://doi.org/10.1561/2200000083> `arxiv:1912.04977`
- When Is a Recommendation Model Wrong? A Model-Agnostic Tree-Based Approach to Detecting Biases in Recommendations (2021) <https://doi.org/10.1007/978-3-030-78818-6_9> `doi:10.1007/978-3-030-78818-6_9`
- ImageNet classification with deep convolutional neural networks (2017) <https://doi.org/10.1145/3065386> `doi:10.1145/3065386`
- Domain-agnostic Question-Answering with Adversarial Training (2019) <https://doi.org/10.18653/v1/d19-5826> `doi:10.18653/v1/d19-5826`
- A Survey of Task-Oriented Knowledge Graph Reasoning: Status, Applications, and Prospects (2025) <https://doi.org/10.36227/techrxiv.174961563.32605293/v1> `doi:10.36227/techrxiv.174961563.32605293/v1`
- Exploiting Generative AI to Scale up Intelligent Tutoring Systems (2023) <https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITP.2023.19> `doi:10.4230/lipics.itp.2023.19`
- Large-scale Semantic Parsing via Schema Matching and Lexicon Extension (2013) <http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.361.3926> `openalex:W2163561827`

</details>

## Appendix A. Evidence Ledger

### [Evidence] claims (4)

- **[Evidence]** TempRALM introduces a temporal score 𝜏(𝑞𝑡,𝑑𝑡) = 𝛼𝑠𝑐𝑎𝑙𝑒 𝑞𝑡−𝑑𝑡 (inverse of time difference) normalized to align with semantic score range, combined with semantic score 𝑠(𝑞,𝑑) = ⟨𝑓𝜃(𝑞),𝑓 𝜃(𝑑)⟩, where the retriever fetches documents based on both semantic and temporal relevance. _(claim C001, confidence: high)_
  - [2], p. 4 (direct support, verified) "Temporal Score We introduce a new method called TempRALM, which augments the retriever with a temporal score𝜏(𝑞𝑡,𝑑𝑡), where𝑞𝑡 is the timestamp of the query𝑞, and𝑑𝑡 is the timestamp of document𝑑. To calculate 𝜏(𝑞𝑡,𝑑𝑡), we take the reciprocal of the time difference between𝑞𝑡 and𝑑𝑡 to ensure that the temporal score is inversely proportional to the time difference (and thus smaller differences in time result in a larger score), and use a scaling factor𝛼 to tune the temporal score’s importance relative to the importance of the semantic score. The temporal score formulation is as follows: 𝜏(𝑞𝑡,𝑑𝑡) = 𝛼𝑠𝑐𝑎𝑙𝑒 𝑞𝑡−𝑑𝑡"
- **[Evidence]** Re3 proposes a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism to address the intertwined challenges of relevance (alignment with query's temporal requirements) and recency (selecting the freshest document) in temporal information retrieval. _(claim C002, confidence: high)_
  - [1], abstract (direct support, verified) "To address this gap, we introduce Re2Bench, a benchmark specifically designed to disentangle and evaluate Relevance, Recency, and their hybrid combination. Building on this foundation, we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism."
- **[Evidence]** Re3 ablation studies show strong generalization across diverse encoders, indicating the framework works with different dense retriever backbones, but does not mention evaluation with sparse retrievers such as BM25. _(claim C017, confidence: high)_
  - [1], abstract (direct support, verified) "Ablation studies with backbone sensitivity tests confirm robustness, showing strong generalization across diverse encoders and real-world settings."
- **[Evidence]** TempRALM uses a dense retriever based on Contriever, an information retrieval approach based on continuous dense embeddings, indicating a focus on dense retrievers without mention of sparse retrievers such as BM25. _(claim C018, confidence: high)_
  - [2], p. 4 (direct support, verified) "The retriever is based on the Contriever [ 7], an information retrieval approach based on continuous dense embeddings."

### [Inference] claims (15)

- **[Inference]** A key technical risk is ensuring the temporal relevance component is truly retrieval-agnostic and can be applied to both dense (e.g., DPR) and sparse (e.g., BM25) retrievers without requiring modification to their core ranking algorithms, as differences in score distributions and normalization requirements may affect how temporal scores combine with semantic scores. _(claim C003, confidence: medium)_
  - [2], p. 4 (direct support, verified) "Temporal Score We introduce a new method called TempRALM, which augments the retriever with a temporal score𝜏(𝑞𝑡,𝑑𝑡), where𝑞𝑡 is the timestamp of the query𝑞, and𝑑𝑡 is the timestamp of document𝑑. To calculate 𝜏(𝑞𝑡,𝑑𝑡), we take the reciprocal of the time difference between𝑞𝑡 and𝑑𝑡 to ensure that the temporal score is inversely proportional to the time difference (and thus smaller differences in time result in a larger score), and use a scaling factor𝛼 to tune the temporal score’s importance relative to the importance of the semantic score. The temporal score formulation is as follows: 𝜏(𝑞𝑡,𝑑𝑡) = 𝛼𝑠𝑐𝑎𝑙𝑒 𝑞𝑡−𝑑𝑡"
  - [1], abstract (direct support, verified) "To address this gap, we introduce Re2Bench, a benchmark specifically designed to disentangle and evaluate Relevance, Recency, and their hybrid combination. Building on this foundation, we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism."
- **[Inference]** A major experimental confounder is that observed improvements in answer accuracy could stem from the framework's tendency to favor more recent documents (recency bias) rather than genuinely selecting the correct version for a time-specific query, especially in regulatory texts where older versions may still be legally valid for certain time points. _(claim C004, confidence: medium)_
  - [2], p. 4 (direct support, verified) "Temporal Score We introduce a new method called TempRALM, which augments the retriever with a temporal score𝜏(𝑞𝑡,𝑑𝑡), where𝑞𝑡 is the timestamp of the query𝑞, and𝑑𝑡 is the timestamp of document𝑑. To calculate 𝜏(𝑞𝑡,𝑑𝑡), we take the reciprocal of the time difference between𝑞𝑡 and𝑑𝑡 to ensure that the temporal score is inversely proportional to the time difference (and thus smaller differences in time result in a larger score), and use a scaling factor𝛼 to tune the temporal score’s importance relative to the importance of the semantic score. The temporal score formulation is as follows: 𝜏(𝑞𝑡,𝑑𝑡) = 𝛼𝑠𝑐𝑎𝑙𝑒 𝑞𝑡−𝑑𝑡"
  - [1], abstract (direct support, verified) "This task is shaped by two challenges: Relevance, ensuring alignment with the query's explicit temporal requirements, and Recency, selecting the freshest document among multiple versions. Existing methods often address the two challenges in isolation, relying on brittle heuristics that fail in scenarios where temporal requirements and staleness resistance are intertwined."
- **[Inference]** Re3 uses a query-aware gating mechanism to dynamically balance semantic and temporal information, which may be more complex and less retrieval-agnostic than a simple temporal relevance component based on elapsed time. _(claim C006, confidence: medium)_
  - [1], abstract (direct support, verified) "Building on this foundation, we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism."
- **[Inference]** Our proposed idea differs from Re3 and TempRALM by targeting retrieval-agnostic application to open-domain question answering over continuously amended regulatory documents, where amendments create dense semantic overlap across versions, making it difficult to distinguish the correct version for a time-specific query. _(claim C007, confidence: medium)_
  - [1], abstract (indirect support, verified) "Building on this foundation, we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism."
  - [2], p. 4 (indirect support, unverified) "We show that our approach results in up to 74% improvement in performance over the baseline RALM model, without requiring model pre-training, recalculating or replacing the RALM document index, or adding other computationally intensive elements."
- **[Inference]** A key technical risk is ensuring the temporal relevance component is truly retrieval-agnostic and can be applied to both dense (e.g., DPR) and sparse (e.g., BM25) retrievers without requiring modification to their core ranking algorithms, as differences in score distributions and normalization requirements may affect how temporal scores combine with semantic scores. _(claim C008, confidence: medium)_
  - [2], p. 4 (indirect support, unverified) "To align the temporal score with the numerical range of the semantic score from equation 1, we employ a normalization process. In particular, we subtract from each temporal score, the mean over the temporal scores of all(𝑞,𝑑) pairs,𝜇𝜏 , and divide by the standard deviation over the temporal scores of all(𝑞,𝑑) pairs, 𝜎𝜏 . The normalized temporal score is then scaled to the range of the relevance score by multiplying with standard deviation of semantic scores𝜎𝑠 and adding mean of semantic scores𝜇𝑠 (both computed over the scores of all(𝑞,𝑑) pairs): 𝜏(𝑞𝑡,𝑑𝑡) = 𝜏(𝑞𝑡,𝑑𝑡)− 𝜇𝜏 𝜎𝜏 ×𝜎𝑠+𝜇𝑠"
  - [2], p. 5 (indirect support, unverified) "based on a general-purpose dense retriever that uses a dual- encoder architecture, based on the Contriever [7] and a sequence- to-sequence model built on the Fusion-in-Decoder architecture [3] which uses T5-1.1 [15] with a language modeling adaptation."
- **[Inference]** Existing temporal relevance methods like TempRALM are designed for specific retriever types (e.g., dense Contriever-based) with score normalization tailored to those retrievers, while our idea proposes a retrieval-agnostic component that can be applied to both dense and sparse retrievers without modification to their core algorithms. _(claim C009, confidence: medium)_
  - [2], p. 5 (indirect support, unverified) "based on a general-purpose dense retriever that uses a dual- encoder architecture, based on the Contriever [7]"
  - [2], p. 4 (indirect support, unverified) "To align the temporal score with the numerical range of the semantic score from equation 1, we employ a normalization process"
- **[Inference]** A major experimental confounder is that observed improvements in answer accuracy could stem from the framework's tendency to favor more recent documents (recency bias) rather than genuinely selecting the correct version for a time-specific query, especially in regulatory texts where older versions may still be legally valid for certain time points. _(claim C010, confidence: medium)_
  - [2], p. 4 (indirect support, verified) "To calculate 𝜏(𝑞𝑡,𝑑𝑡), we take the reciprocal of the time difference between𝑞𝑡 and𝑑𝑡 to ensure that the temporal score is inversely proportional to the time difference (and thus smaller differences in time result in a larger score)"
  - [1], abstract (indirect support, verified) "This task is shaped by two challenges: Relevance, ensuring alignment with the query's explicit temporal requirements, and Recency, selecting the freshest document among multiple versions."
- **[Inference]** TempRALM's evaluation shows that temporal augmentation improves performance most when query and passage time periods don't match (e.g., different years), but within the valid temporal window (passages at or before query time), the inverse time difference scoring still favors more recent passages, creating a potential confound where improvements could stem from recency bias rather than genuine temporal relevance for time-specific queries. _(claim C011, confidence: high)_
  - [2], p. 5 (direct support, verified) "Figure 4: Questions asking about the winner, runner-up, finalists and score asked at different timestamps, where the right answer corresponds to the most recent tennis match that occurred before the query timestamp (denoting passages that refer to future information relative to the time of the event specified in the query), to completely eliminate these passages from being considered while ranking the𝑡𝑜𝑝𝑘 . We re-write the retrieval computation as follows: 𝑇𝑒𝑚𝑝𝑅𝑒𝑡 𝑡(𝑞,𝑑,𝑞𝑡,𝑑𝑡 ) = ( 𝑠(𝑞,𝑑)+ 𝜏(𝑞𝑡,𝑑𝑡) if𝑞𝑡≥𝑑𝑡 −∞, otherwise"
  - [2], p. 4 (direct support, verified) "To calculate 𝜏(𝑞𝑡,𝑑𝑡), we take the reciprocal of the time difference between𝑞𝑡 and𝑑𝑡 to ensure that the temporal score is inversely proportional to the time difference (and thus smaller differences in time result in a larger score)"
  - [2], p. 6 (direct support, verified) "However, when the year in the timestamp of the query does not match that in the text passage (TPQ-2020 experiments), TempRALM outperforms unmodified Atlas by 49% in the 32 few-shot learning experiment, 67% in the 64 few-shot learning experiment, and 74% in the 128 few-shot learning experiment."
- **[Inference]** Re3 introduces Re2Bench specifically designed to disentangle and evaluate Relevance, Recency, and their hybrid combination, suggesting their evaluation approach aims to separate the effects of semantic content matching from temporal preferences, potentially reducing the recency bias confound present in methods that use simple temporal scoring. _(claim C012, confidence: medium)_
  - [1], abstract (direct support, verified) "To address this gap, we introduce Re2Bench, a benchmark specifically designed to disentangle and evaluate Relevance, Recency, and their hybrid combination."
- **[Inference]** TempRALM's evaluation results counter the recency bias confound concern: temporal augmentation improves performance most when querying about past events where semantic matching to current text fails (different years), showing the temporal component helps select passages from the correct time period rather than simply preferring recent documents. When query and passage time periods match, semantic alone suffices; when they don't match, temporal augmentation is needed to recover the correct temporal context. _(claim C013, confidence: high)_
  - [2], p. 6 (direct support, verified) "We observe that when the timestamp year of the query matches that of the event (and thus the date referenced in the corresponding text passage), the unmodified Atlas model performs comparably to TempRALM. In these scenarios, the semantic score captures the matching date pattern between the query and the passage. However, when the year in the timestamp of the query does not match that in the text passage (TPQ-2020 experiments), TempRALM outperforms unmodified Atlas by 49% in the 32 few-shot learning experiment, 67% in the 64 few-shot learning experiment, and 74% in the 128 few-shot learning experiment."
- **[Inference]** TempRALM's evaluation design limits assessment of recency bias confound: their query construction ensures the correct answer always corresponds to the most recent tennis match before the query timestamp, so they never test cases where the correct answer is an older valid passage. This prevents disentangling whether temporal augmentation helps by selecting the correct time period versus simply preferring more recent passages within that period. _(claim C014, confidence: medium)_
  - [2], p. 5 (direct support, verified) "Figure 4: Questions asking about the winner, runner-up, finalists and score asked at different timestamps, where the right answer corresponds to the most recent tennis match that occurred before the query timestamp (denoting passages that refer to future information relative to the time of the event specified in the query), to completely eliminate these passages from being considered while ranking the𝑡𝑜𝑝𝑘"
- **[Inference]** Re3's Re2Bench benchmark is specifically designed to disentangle and evaluate Relevance, Recency, and their hybrid combination, suggesting their evaluation approach can distinguish between improvements from selecting the correct time period versus simply preferring more recent passages within that period, potentially providing a cleaner assessment of temporal relevance contributions. _(claim C015, confidence: medium)_
  - [1], abstract (direct support, verified) "To address this gap, we introduce Re2Bench, a benchmark specifically designed to disentangle and evaluate Relevance, Recency, and their hybrid combination."
- **[Inference]** Unlike TempRALM's inverse time difference scoring which gradually prefers more recent passages within the valid temporal window, our proposed temporal relevance component could be designed to primarily filter out future information (passages with timestamps > query target date) while treating all past passages more equally, reducing recency bias confound when the goal is to find the version in effect at a specific time point rather than the most recent version overall. _(claim C016, confidence: medium)_
  - [2], p. 4 (indirect support, verified) "To calculate 𝜏(𝑞𝑡,𝑑𝑡), we take the reciprocal of the time difference between𝑞𝑡 and𝑑𝑡 to ensure that the temporal score is inversely proportional to the time difference (and thus smaller differences in time result in a larger score)"
  - [2], p. 5 (indirect support, verified) "Figure 4: Questions asking about the winner, runner-up, finalists and score asked at different timestamps, where the right answer corresponds to the most recent tennis match that occurred before the query timestamp"
- **[Inference]** Re3 uses a query-aware gating mechanism to dynamically balance semantic and temporal information, which requires learning a gating function that may depend on the query and potentially adds complexity compared to a simple temporal relevance component based on elapsed time (e.g., exponential decay) combined with semantic similarity via a weighted sum or lightweight gating. _(claim C019, confidence: medium)_
  - [1], abstract (direct support, verified) "Building on this foundation, we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism."
- **[Inference]** No existing work directly evaluates whether adding a temporal relevance component improves answer accuracy for open-domain question answering over versioned regulatory documents with overlapping revisions and time-stamped queries; TempRALM is evaluated on a tennis grand slam dataset (p. 5) and Re3 introduces Re2Bench for general temporal information retrieval (abstract). _(claim C020, confidence: medium)_
  - [2], p. 5 (direct support, verified) "In particular, we curated a dataset based on tennis grand slam data, where 4 major tournaments take place every year and answers to the queries depend on when the query is asked, with respect to the timing of the tournament."
  - [1], abstract (direct support, verified) "To address this gap, we introduce Re2Bench, a benchmark specifically designed to disentangle and evaluate Relevance, Recency, and their hybrid combination."

### [Assumption] claims (1)

- **[Assumption]** Assumptions underlying the proposed framework: (1) Version timestamps are available for each passage in regulatory documents. (2) Queries have an associated target date indicating when the information should be valid. (3) Semantic similarity from a retriever (e.g., dense or sparse) is a relevant baseline for measuring document relevance to queries. (4) Temporal relevance can be modeled as a decreasing function of elapsed time between query target date and version timestamp. (5) The framework can be applied to both dense and sparse retrievers without modification to their core ranking algorithms. _(claim C005, confidence: medium)_
  - [2], p. 4 (direct support, verified) "Temporal Score We introduce a new method called TempRALM, which augments the retriever with a temporal score𝜏(𝑞𝑡,𝑑𝑡), where𝑞𝑡 is the timestamp of the query𝑞, and𝑑𝑡 is the timestamp of document𝑑. To calculate 𝜏(𝑞𝑡,𝑑𝑡), we take the reciprocal of the time difference between𝑞𝑡 and𝑑𝑡 to ensure that the temporal score is inversely proportional to the time difference (and thus smaller differences in time result in a larger score), and use a scaling factor𝛼 to tune the temporal score’s importance relative to the importance of the semantic score. The temporal score formulation is as follows: 𝜏(𝑞𝑡,𝑑𝑡) = 𝛼𝑠𝑐𝑎𝑙𝑒 𝑞𝑡−𝑑𝑡"
  - [1], abstract (direct support, verified) "To address this gap, we introduce Re2Bench, a benchmark specifically designed to disentangle and evaluate Relevance, Recency, and their hybrid combination. Building on this foundation, we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism."

## Appendix B. Search Log

| Query | Sources (status: results) | Papers |
|---|---|---|
| temporal relevance retrieval versioned documents | arxiv (ok: 3), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 13 |
| temporal relevance question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 15 |
| references of arxiv:2210.06281 | openalex (ok: 10) | 10 |
| citations of arxiv:2210.06281 | openalex (ok: 10) | 10 |
| retrieval agnostic temporal relevance question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 20 |
| temporal bias retrieval agnostic | arxiv (ok: 3), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 12 |
| versioned regulatory document question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 15 |

## Appendix C. Investigation Log

Each step was chosen by the ResearchForge controller from the recorded research state.

| Step | Phase | Action | Why | Alternatives considered | Outcome | Information gain |
|---|---|---|---|---|---|---|
| 0 | INTAKE | INTAKE | Research idea received. | none | idea stored in the workspace | n/a |
| 1 | FORMALIZE | FORMALIZE | The idea has not been formalized into a testable research question. | none | +13 papers; +1 searches; idea formalized | 3 |
| 2 | PLAN | PLAN | No investigation plan exists yet, so it is unclear what must be determined. | none | +5 uncertainties; investigation plan recorded | 1 |
| 3 | INVESTIGATE | SEARCH (temporal relevance) | Literature coverage is insufficient: at least 2 distinct search queries (have 1). | none | +35 papers; +3 searches | 2 |
| 4 | INVESTIGATE | READ | Retrieved papers have not been analyzed enough to judge overlap. | none | +4 analyses | 2 |
| 5 | INVESTIGATE | READ | Retrieved papers have not been analyzed enough to judge overlap. | none | +2 analyses | 1 |
| 6 | SYNTHESIZE | SYNTHESIZE | Analyses exist but the field has not been mapped. | none | landscape recorded | 1 |
| 7 | CRITIQUE | CRITIQUE | The idea has not been challenged yet. | none | +5 claims; +5 verified claims; +2 uncertainties; critique recorded; uncertainties updated: U002, U004 | 6 |
| 8 | UNCERTAINTY | SEARCH (U001: Is there existing work that combines temporal relevance with semantic simi) | Most valuable next step for high-importance novelty question U001: score 1.139 = importance 3 x expected gain 0.633 x relevance 1 x evidence deficiency 0.6 / cost 1. Next best: PLAN_EXPERIMENT on U006 (1.08). | PLAN_EXPERIMENT U006 (1.08); VERIFY U006 (1.08) | +46 papers; +3 searches; +1 resolved uncertainties; uncertainties updated: U001 | 4 |
| 9 | UNCERTAINTY | PLAN_EXPERIMENT (U006: Does temporal relevance improve QA accuracy on versioned regulatory docume) | Most valuable next step for high-importance validity question U006: score 1.08 = importance 3 x expected gain 0.4 x relevance 0.9 x evidence deficiency 1 / cost 1. Next best: VERIFY on U006 (1.08). | VERIFY U006 (1.08); COMPARE U007 (0.84) | +1 experiment plans | 1 |
| 10 | UNCERTAINTY | COMPARE (U007: Can a temporal relevance component based on elapsed time be effectively ap) | Most valuable next step for high-importance feasibility question U007: score 0.84 = importance 3 x expected gain 0.6 x relevance 0.7 x evidence deficiency 1 / cost 1.5. Next best: VERIFY on U007 (0.84). | VERIFY U007 (0.84); COMPARE U005 (0.72) | +5 claims; +3 verified claims | 3 |
| 11 | UNCERTAINTY | COMPARE (U005: Could observed improvements be due to better retrieval of recent documents) | Most valuable next step for medium-importance confounder question U005: score 0.96 = importance 2 x expected gain 0.8 x relevance 0.9 x evidence deficiency 1 / cost 1.5. Next best: VERIFY on U007 (0.84). | VERIFY U007 (0.84); VERIFY U005 (0.72) | +6 claims; +6 verified claims; uncertainties updated: U005 | 6 |
| 12 | UNCERTAINTY | VERIFY (U007: Can a temporal relevance component based on elapsed time be effectively ap) | Most valuable next step for high-importance feasibility question U007: score 0.84 = importance 3 x expected gain 0.6 x relevance 0.7 x evidence deficiency 1 / cost 1.5. Next best: COMPARE on U002 (0.728). | COMPARE U002 (0.728); VERIFY U006 (0.648) | +2 claims; +2 verified claims; uncertainties updated: U007 | 2 |
| 13 | UNCERTAINTY | COMPARE (U002: How similar is our proposed method to Re3 (arxiv:2509.01306) which balance) | Most valuable next step for high-importance overlap question U002: score 0.728 = importance 3 x expected gain 0.867 x relevance 1 x evidence deficiency 0.42 / cost 1.5. Next best: VERIFY on U006 (0.684). | VERIFY U006 (0.684); VERIFY U004 (0.479) | +1 claims; +1 verified claims | 1 |
| 14 | UNCERTAINTY | VERIFY (U006: Does temporal relevance improve QA accuracy on versioned regulatory docume) | Most valuable next step for high-importance validity question U006: score 0.684 = importance 3 x expected gain 0.633 x relevance 0.9 x evidence deficiency 0.6 / cost 1.5. Next best: VERIFY on U002 (0.532). | VERIFY U002 (0.532); VERIFY U004 (0.479) | +1 claims; +1 verified claims | 1 |
| 15 | UNCERTAINTY | VERIFY (U002: How similar is our proposed method to Re3 (arxiv:2509.01306) which balance) | Most valuable next step for high-importance overlap question U002: score 0.448 = importance 3 x expected gain 0.533 x relevance 1 x evidence deficiency 0.42 / cost 1.5. Next best: PLAN_EXPERIMENT on U004 (0.416). | PLAN_EXPERIMENT U004 (0.416); VERIFY U004 (0.403) | no recorded change | 0 |
| 16 | UNCERTAINTY | PLAN_EXPERIMENT (U004: Does temporal relevance actually improve QA accuracy, or could it hurt due) | Most valuable next step for high-importance validity question U004: score 0.416 = importance 3 x expected gain 0.367 x relevance 0.9 x evidence deficiency 0.42 / cost 1. Next best: READ on U003 (0.35). | READ U003 (0.35); VERIFY U004 (0.302) | uncertainties updated: U004 | 0 |
| 17 | FINALIZE | FINALIZE | Stopping: iteration budget reached (16). | none | finalizing | n/a |
