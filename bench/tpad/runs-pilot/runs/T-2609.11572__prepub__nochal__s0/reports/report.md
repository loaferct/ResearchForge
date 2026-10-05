# ResearchForge Investigation Report

Project `T-2609.11572__prepub__nochal__s0` · model `ollama-cloud/nemotron-3-super` · status **incomplete**

> Labels: **[Evidence]** directly supported by a verified quote from a retrieved source; **[Inference]** reasoning derived from cited evidence; **[Hypothesis]** proposed, not validated; **[Assumption]** taken as given without evidence; **[Experimental result]** observed in an executed experiment.

## 1. Executive Summary

**Investigated:** The reliability of open‑domain question answering drops sharply when source texts are continuously amended, as in statutes, policies, or regulations. In such settings each new amendment supersedes earlier clauses while retaining much of the original wording, creating a dense semantic overlap across successive versions. Existing time‑aware retrieval techniques treat each version as an isolated snapshot and therefore cannot distinguish which revision best matches a time‑specific query. We propose to develop a retrieval‑agnostic framework that enriches any standard document retriever with a temporal relevance component: the rank of a candidate passage will be adjusted according to the elapsed time between the query’s target date and the passage’s version timestamp, while still leveraging its semantic similarity to the query. To evaluate the approach, we will construct a benchmark comprising regulatory documents with overlapping revisions and time‑stamped queries, measuring how well the combined temporal‑semantic ranking improves answer accuracy.

**Research question:** Does adding a temporal relevance component based on exponential decay of time difference between query target date and passage version timestamp improve Exact Match and F1 scores of a standard retriever (e.g., BM25) on a benchmark of evolving regulatory documents compared to using semantic similarity alone?

**Literature investigated:** 109 papers retrieved from 7 searches (openalex: 43, crossref: 41, arxiv: 21, semantic_scholar: 5); 6 analyzed; 1 rated highly relevant.

**Assessment:** Promising but requires experimental validation. **[Inference]** The idea is grounded in empirical evidence of temporal decay and addresses a clear gap in mitigating this decay for version-specific QA. However, key uncertainties remain regarding benchmark feasibility, optimal temporal weighting function, and confounding factors (e.g., retrieval matching meaning). Without empirical validation demonstrating improved QA accuracy, the contribution remains promising but unproven.

**Closest existing work:** Temporal Decay of Co-Citation Predictability: A 20-Year Statute Retrieval Benchmark from 396M Ukrainian Court Citations (2026) [1]; Time Present and Time Past: Benchmarking Large Language Models on Temporally Evolving Document Understanding (2026) [2]; IMPROVING LONG-TAIL RECOMMENDATION VIA ROULETTE WHEEL SELECTION USING HYBRID RATING AND TEMPORAL DECAY WEIGHTING (2026) [3]; Not All Memories Age the Same: Autodiscovery of Adaptive Decay in Knowledge Graphs (2026) [4]

**Potential overlap:** Overlap exists in the problem domain (legal/statutory texts that evolve over time) and the observation that retrieval signals degrade temporally (C001, C003). The proposed work shares the assumption that temporal proximity correlates with relevance (C008) and that standard retrievers provide combinable semantic scores (C009).

**Potential distinction:** Unlike prior work that merely diagnoses decay (arxiv:2605.17639) or applies temporal weighting to other modalities (recommendation, knowledge graphs, video), this work proposes a retrieval-agnostic framework specifically for open-domain question answering that adjusts retriever rankings based on elapsed time between query target date and passage version timestamp, while preserving semantic similarity. It targets end-to-end QA accuracy rather than retrieval-only metrics or proxy tasks.

**Major risk:** The closest existing work already analyzes temporal decay in legal statutes (C001) and applies temporal weighting in other domains (e.g., recommendation, knowledge graphs), suggesting the core concept may not be novel. Moreover, the approach faces technical risks due to non-uniform decay patterns (C004) and a major experimental confounder: retrieval often matches meaning rather than time (C006), making it difficult to isolate the true effect of temporal weighting on version selection.

**Research decision:** Insufficient evidence. **[Inference]** Basis: high-importance questions remain unresolved (U003, U005, U006, U009, U010, U011). This describes the state of the evidence, not the absolute value of the idea.

**Investigation:** 11 steps chosen from the research state; 11 uncertainties raised, 0 resolved, 11 still open or unresolved (Section 13, Appendix C).

**Stopped by a safety limit:** Stopping: time budget reached (3600 s). Conclusions below cover only what was recorded before the limit.

**Claim grounding:** 20/20 evidence and inference claims have at least one verified source.

**Incomplete phases:** gaps, modifications, experiments. Sections that depend on them are marked as not recorded.

This report does not declare the idea novel. Absence of a matching paper in these searches does not establish novelty; see Section 13.

## 2. Original Research Idea

> The reliability of open‑domain question answering drops sharply when source texts are continuously amended, as in statutes, policies, or regulations. In such settings each new amendment supersedes earlier clauses while retaining much of the original wording, creating a dense semantic overlap across successive versions. Existing time‑aware retrieval techniques treat each version as an isolated snapshot and therefore cannot distinguish which revision best matches a time‑specific query. We propose to develop a retrieval‑agnostic framework that enriches any standard document retriever with a temporal relevance component: the rank of a candidate passage will be adjusted according to the elapsed time between the query’s target date and the passage’s version timestamp, while still leveraging its semantic similarity to the query. To evaluate the approach, we will construct a benchmark comprising regulatory documents with overlapping revisions and time‑stamped queries, measuring how well the combined temporal‑semantic ranking improves answer accuracy.

## 3. Formalized Research Question

**Research question:** Does adding a temporal relevance component based on exponential decay of time difference between query target date and passage version timestamp improve Exact Match and F1 scores of a standard retriever (e.g., BM25) on a benchmark of evolving regulatory documents compared to using semantic similarity alone?

**Hypothesis:** **[Hypothesis]** Adding a temporal relevance component to a standard retriever will significantly improve answer accuracy (Exact Match and F1) on time-specific questions over evolving regulatory documents compared to using semantic similarity alone.

| Aspect | Formalization |
|---|---|
| Problem | The reliability of open-domain question answering drops sharply when source texts are continuously amended, as in statutes, policies, or regulations. In such settings each new amendment supersedes earlier clauses while retaining much of the original wording, creating a dense semantic overlap across successive versions. Existing time-aware retrieval techniques treat each version as an isolated snapshot and therefore cannot distinguish which revision best matches a time-specific query. |
| Target domain | Open-domain question answering over evolving regulatory documents (statutes, policies, regulations). |
| Proposed method | A retrieval-agnostic framework that enriches any standard document retriever with a temporal relevance component: the rank of a candidate passage is adjusted according to the elapsed time between the query’s target date and the passage’s version timestamp (e.g., using exponential decay), while still leveraging its semantic similarity to the query. |
| Target system | Open-domain QA pipeline consisting of a retriever and a reader (e.g., BERT-based QA model). The framework modifies the retriever's ranking. |
| Expected contribution | A novel temporal relevance weighting scheme that is retriever-agnostic, a benchmark of regulatory documents with versioned passages and time-stamped queries, and empirical demonstration that temporal-semantic ranking improves QA accuracy over strong baselines. |
| Independent variables | presence and strength of temporal relevance component (e.g., lambda parameter) |
| Dependent variables | Answer accuracy (Exact Match, F1) |
| Controls | Underlying retriever (BM25), Dataset, Queries, Semantic similarity metric (e.g., BM25 score), Evaluation protocol |

**Assumptions**

- Passage version timestamps are available or can be inferred from document metadata.
- Temporal proximity between query target date and passage version correlates with relevance (more recent versions are more relevant for queries about current state, older versions for past states).
- Standard retriever provides a semantic similarity score that can be combined with temporal weight.
- Answer accuracy can be measured using Exact Match and F1 scores.
- The benchmark can be constructed from publicly available regulatory corpora with version history.

**Expected benefits / potential risks**

- Benefit: Improved ability to select the correct version of a clause for time-specific questions
- Benefit: Reduced confusion due to semantic overlap
- Benefit: Better alignment with temporal intent of queries
- Risk: Over-reliance on temporal weight may degrade performance for timeless queries or where older versions are relevant
- Risk: Inaccurate timestamps may hurt performance
- Risk: Added complexity may not generalize to non-regulatory domains

**Ambiguities**

| Question | Resolution | Resolved by |
|---|---|---|
| Which baseline retriever should be used (e.g., BM25 vs dense retriever like DPR)? | Not recorded | assumption |
| What is the exact form of the temporal weighting function (exponential decay, linear, etc.) and how to set its hyperparameters? | Not recorded | assumption |
| How to construct a benchmark of regulatory documents with version history and create time-stamped queries? | Not recorded | assumption |
| How to obtain time-specific queries for evaluation (manual annotation vs synthetic generation)? | Not recorded | assumption |

## 4. Existing Research

Overlap values are heuristic signals assigned during analysis, not measurements of novelty.

| Paper | Relevance | Method | Problem / method / evaluation overlap | Read from |
|---|---|---|---|---|
| Temporal Decay of Co-Citation Predictability: A 20-Year Statute Retrieval Benchmark from 396M Ukrainian Court Citations (2026) [1] | high | The authors build annual snapshots (2007-2026) of Ukrainian court decisions, extract codex-article citations, and construct article co-citation matrices. They evaluate retrieval performance using a leave-one-out citation prediction protocol over the bipartite citation graph, measuring metrics such a | 0.6 / 0.3 / 0.2 | full_text |
| Not All Memories Age the Same: Autodiscovery of Adaptive Decay in Knowledge Graphs (2026) [4] | medium | The authors propose a hierarchical framework that replaces uniform decay with a continuous decay surface parameterized by velocity (observation frequency) and volatility (value change measured via embedding distance). The decay surface has three levels: domain-level (universal patterns), context-lev | 0.4 / 0.3 / 0.2 | abstract |
| An Efficient Document Retrieval for Korean Open-Domain Question Answering Based on ColBERT (2023) [5] | medium | The authors propose a Korean document retrieval method using ColBERT’s late interaction paradigm to efficiently compute relevance between questions and documents. They construct a Korean dataset from AI-Hub corpora and compare their method against BM25, dense retrieval with BERT-based Korean models  | 0.4 / 0.2 / 0.1 | abstract |
| Earlier Tokens Contribute More: Learning Direct Preference Optimization From Temporal Decay Perspective (2025) [6] | low | The authors propose an enhanced preference optimization method that incorporates a temporal decay factor (gamma) to adjust reward influence based on token position in the sequence, prioritizing earlier tokens. This dynamic weighting mechanism adapts to evolving human preferences and mitigates overfi | 0.1 / 0.1 / 0.1 | abstract |
| Temporal Weighting Appearance-Aligned Network for Nighttime Video Retrieval (2022) [7] | low | Not stated in abstract. | 0.1 / 0.1 / 0.1 | abstract |
| IMPROVING LONG-TAIL RECOMMENDATION VIA ROULETTE WHEEL SELECTION USING HYBRID RATING AND TEMPORAL DECAY WEIGHTING (2026) [3] | low | The authors integrate Roulette Wheel Selection with hybrid rating (combining multiple signals) and temporal decay weighting to create a stochastic framework for recommendation. They test on the Goodreads Poetry dataset using four embedding models (SBERT-Tuned, SBERT, FastText, Word2Vec) and compare  | 0.2 / 0.2 / 0.1 | abstract |

<details><summary>Full paper analyses</summary>

#### Temporal Decay of Co-Citation Predictability: A 20-Year Statute Retrieval Benchmark from 396M Ukrainian Court Citations (2026) [1]

- **Problem:** The paper investigates the temporal decay of co-citation predictability in legal statutes, questioning the assumption that co-citation structure provides a stable retrieval signal over time. It constructs a longitudinal benchmark to measure how retrieval performance degrades across annual snapshots of court decisions.
- **Method:** The authors build annual snapshots (2007-2026) of Ukrainian court decisions, extract codex-article citations, and construct article co-citation matrices. They evaluate retrieval performance using a leave-one-out citation prediction protocol over the bipartite citation graph, measuring metrics such as Adamic-Adar MRR and Hit@k. They also include a BM25 text baseline and analyze decay across article frequency bands and legal domains, complemented by embedding drift analysis with E5-large to explain semantic shifts.
- **Main contribution:** A 20-year statute retrieval benchmark (UA-StatuteRetrieval) comprising 396 million citations from 101 million Ukrainian court decisions, demonstrating significant temporal decay of co-citation predictability (33-47% MRR decline), revealing non-uniform decay across legal domains and article frequencies, providing embedding drift analysis as mechanistic explanation, and releasing the benchmark for reproducibility.
- **Key assumptions:** Co-citation structure reflects retrieval signal for legal statutes.; Leave-one-out citation prediction is a valid proxy for retrieval performance.; Temporal train/test split simulates real-world temporal shift.; Embedding drift captures semantic changes in citation contexts.
- **Datasets / benchmarks:** UA-StatuteRetrieval: Ukrainian Unified State Register of Court Decisions (2007-2026), 101M decisions, 396M codex-article citations, UA-StatuteRetrieval (own benchmark), Referenced legal retrieval benchmarks: BSARD (Belgian), SCALE, LeSICiN (Indian)
- **Baselines:** Adamic-Adar, Common Neighbors, Degree, Random, BM25
- **Metrics:** MRR (Mean Reciprocal Rank), Hit@1, Hit@5, Hit@10, Hit@20
- **Results:** "Adamic-Adar MRR declines 33% on a fixed article set (from 0.43 to 0.29) and 47% under a train/test temporal split (from 0.51 to 0.27). BM25 baseline decays 31%. Civil law degrades from MRR 0.35 to 0.15 post-2017 reform, while criminal procedure remains stable (~0.40). Hub articles (>100K citations) resist decay; mid-frequency articles (1K-10K) lose half their predictability. Embedding drift shows a 4.3% semantic shift in citation contexts over 12 years."
- **Limitations:** Evaluation is a proxy (citation prediction) rather than end-user question answering.; Focuses exclusively on co-citation signal, ignoring textual retrieval methods.; Limited to Ukrainian legal system; may not generalize to other jurisdictions.; Does not propose or test mitigation strategies for temporal decay.
- **Future work:** Extend benchmark to other legal systems and document types.; Investigate hybrid retrieval methods combining graph-based and textual signals.; Study impact of temporal decay on end-to-end QA systems and develop mitigation techniques.; Explore incremental updating of retrieval indexes to counteract decay.
- **Code availability:** No code availability stated in the paper.
- **Relation to idea:** The paper measures temporal decay of co-citation predictability as a proxy for retrieval stability, while our work proposes a retrieval-agnostic temporal relevance component to mitigate degradation in open-domain QA over evolving regulatory texts. _(basis: Heuristic estimation based on shared focus on temporal aspects in legal texts and retrieval performance, but differing in goal (diagnosis vs mitigation) and method (analysis vs weighting).)_

#### Not All Memories Age the Same: Autodiscovery of Adaptive Decay in Knowledge Graphs (2026) [4]

- **Problem:** Existing temporal knowledge graph approaches apply uniform decay to all facts, ignoring that different knowledge types have different temporal dynamics. This leads to poor retrieval performance because the core issue is identifying what is important at query time, not just latency or throughput.
- **Method:** The authors propose a hierarchical framework that replaces uniform decay with a continuous decay surface parameterized by velocity (observation frequency) and volatility (value change measured via embedding distance). The decay surface has three levels: domain-level (universal patterns), context-level (setting-dependent), and entity-level (personalized). Parameters are learned from data via survival analysis on edge lifetimes, where the event is value supersession (a meaningfully different value replacing the current one). No predefined taxonomies are needed.
- **Main contribution:** A hierarchical adaptive decay framework for knowledge graphs that models temporal heterogeneity via velocity-volatility decay surface with three levels (domain, context, entity). Parameters learned from data through survival analysis. Experiments show recovery of planted parameters, emergence of velocity-volatility clusters aligning with persistence patterns, and near-universal Lindy effect. Uniform decay performs 18x worse than no temporal weighting, while heterogeneous decay substantially improves performance.
- **Key assumptions:** Knowledge edge lifetimes follow a survival process where supersession events indicate meaningful value changes.; Velocity and volatility are sufficient signals to capture heterogeneous temporal dynamics across knowledge types.; Learning decay parameters from observed lifetimes via survival analysis yields effective adaptive decay functions.
- **Datasets / benchmarks:** Synthetic temporal knowledge graphs, 107 Wikipedia articles, 1,163 patient records from Synthea clinical EHR simulator, Uniform decay baseline, No temporal weighting
- **Baselines:** Uniform decay
- **Metrics:** HDBSCAN ARI (for parameter recovery), Performance improvement over baselines
- **Results:** "HDBSCAN ARI = 1.0 for synthetic graphs, indicating perfect recovery of planted hierarchical parameters. On real-world data, velocity-volatility clusters emerge and align with observable persistence patterns, showing Lindy effect (Weibull shape k < 1). Uniform decay performs 18x worse than no temporal weighting; heterogeneous decay recovers from this, with each hierarchy level contributing measurable improvement."
- **Limitations:** Focuses on knowledge graph edge prediction, not document retrieval or question answering.; Does not explicitly address versioned textual documents or evolving regulatory texts.; Survival analysis assumes supersession events are observable and definable.
- **Future work:** Apply framework to document-level temporal retrieval (e.g., versioned legal texts).; Investigate integration with retrieval-augmented generation for evolving knowledge.; Explore decay surfaces for other modalities (e.g., temporal knowledge bases, time series).
- **Code availability:** No code availability stated in the abstract.
- **Relation to idea:** The paper proposes adaptive temporal decay for knowledge graph retrieval based on velocity and volatility, while our work proposes a retrieval-agnostic temporal relevance component for open-domain QA over evolving regulatory documents using version timestamps. _(basis: Heuristic: both deal with temporal weighting for retrieval, but differ in modality (knowledge graphs vs text documents), granularity (edge level vs passage level), and specific mechanism (adaptive decay surface vs elapsed time weighting).)_

#### An Efficient Document Retrieval for Korean Open-Domain Question Answering Based on ColBERT (2023) [5]

- **Problem:** Open-domain question answering requires retrieving relevant documents from a large corpus. Existing dense retrieval methods improve accuracy but increase computational burden, necessitating efficient models that balance accuracy and speed.
- **Method:** The authors propose a Korean document retrieval method using ColBERT’s late interaction paradigm to efficiently compute relevance between questions and documents. They construct a Korean dataset from AI-Hub corpora and compare their method against BM25, dense retrieval with BERT-based Korean models (KoBERT), and KoSBERT.
- **Main contribution:** A Korean open-domain QA retrieval method leveraging ColBERT’s late interaction for efficient relevance computation. Experiments show higher accuracy than BM25 and lower search time than dense retrieval with KoBERT, with best performance using KoSBERT.
- **Key assumptions:** ColBERT’s late interaction paradigm can efficiently compute relevance for QA retrieval.; Korean language models (KoSBERT) pre-trained to position semantically similar sentences closely improve retrieval performance.; The constructed Korean dataset is representative for open-domain QA evaluation.
- **Datasets / benchmarks:** Korean dataset constructed from various AI-Hub corpora, BM25, Dense retrieval with BERT-based Korean models (KoBERT), KoSBERT
- **Baselines:** BM25, Dense retrieval with BERT-based Korean models (KoBERT)
- **Metrics:** Search accuracy, Inference time
- **Results:** "The proposed method achieves higher accuracy than BM25 and requires less search time than dense retrieval employing KoBERT. The most outstanding performance is observed when using KoSBERT, which positions semantically similar sentences closely in vector space."
- **Limitations:** Focuses on Korean language QA, not multilingual or cross-lingual.; Does not consider temporal aspects or document versioning.; Limited to retrieval efficiency trade-off; does not address evolving document collections.
- **Future work:** Extend approach to multilingual open-domain QA.; Incorporate temporal dynamics for evolving document collections.; Investigate hybrid retrieval combining ColBERT with temporal relevance components.
- **Code availability:** No code availability stated in the abstract.
- **Relation to idea:** The paper improves retrieval efficiency for open-domain QA using ColBERT, but does not address temporal degradation or versioning of documents. Our work focuses on adding temporal relevance weighting to handle continuously amended texts. _(basis: Heuristic: both concern open-domain QA retrieval, but differ in focus (efficiency vs temporal robustness) and lack temporal component in the paper.)_

#### Earlier Tokens Contribute More: Learning Direct Preference Optimization From Temporal Decay Perspective (2025) [6]

- **Problem:** Direct Preference Optimization (DPO) for aligning LLMs with human feedback suffers from length bias, generating overly long responses. Existing solutions uniformly treat reward contributions across sequences, ignoring temporal dynamics of token importance.
- **Method:** The authors propose an enhanced preference optimization method that incorporates a temporal decay factor (gamma) to adjust reward influence based on token position in the sequence, prioritizing earlier tokens. This dynamic weighting mechanism adapts to evolving human preferences and mitigates overfitting to less pertinent data.
- **Main contribution:** Temporal decay-enhanced Direct Preference Optimization (D2PO) that adjusts reward influence via a gamma-controlled decay factor, prioritizing earlier tokens. Experiments show consistent improvements of 5.9-8.8 points on AlpacaEval 2 and 3.3-9.7 points on Arena-Hard across model architectures, while maintaining performance on MMLU, GSM8K, and MATH benchmarks.
- **Key assumptions:** Earlier tokens in a sequence are more critical for alignment with human preferences than later tokens.; A temporal decay factor can effectively capture the decreasing relevance of tokens across sequence positions.; Incorporating temporal dynamics into DPO reduces length bias without compromising general capabilities.
- **Datasets / benchmarks:** AlpacaEval 2, Arena-Hard, MMLU, GSM8K, MATH, Vanilla DPO, SimPO, SamPO
- **Baselines:** Vanilla DPO
- **Metrics:** AlpacaEval 2 score, Arena-Hard score, MMLU, GSM8K, MATH
- **Results:** "D2PO outperforms vanilla DPO by 5.9-8.8 points on AlpacaEval 2 and 3.3-9.7 points on Arena-Hard across model sizes. Performance on mathematical and reasoning benchmarks is enhanced without compromising general capabilities."
- **Limitations:** Focuses on preference optimization for LLM alignment, not retrieval or question answering.; Temporal decay applied to token positions in sequences, not document version timestamps.; Does not address evolving document collections or versioned texts.
- **Future work:** Apply temporal decay weighting to other LLM alignment methods (e.g., PPO, RLHF).; Investigate adaptive gamma scheduling based on sequence length or task difficulty.; Explore integration with retrieval-augmented generation for temporally evolving knowledge.
- **Code availability:** Code available at https://github.com/LotuSrc/D2PO (stated in abstract).
- **Relation to idea:** The paper applies temporal decay to token-level reward contributions in preference optimization for LLM alignment, while our work proposes temporal relevance weighting at the document retrieval level for time-specific QA over evolving regulatory texts. _(basis: Heuristic: both involve temporal decay but different domains (LLM alignment vs document retrieval) and different granularity (token position vs document version).)_

#### Temporal Weighting Appearance-Aligned Network for Nighttime Video Retrieval (2022) [7]

- **Problem:** Not stated in abstract (paper focuses on nighttime video retrieval using temporal weighting and appearance-aligned network).
- **Method:** Not stated in abstract.
- **Main contribution:** Not stated in abstract.
- **Key assumptions:** Not recorded
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** Not stated in abstract.
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** Not stated in abstract.
- **Relation to idea:** The paper addresses temporal weighting for video retrieval, which is unrelated to open-domain question answering over evolving regulatory texts. _(basis: Heuristic: only superficial keyword overlap (temporal weighting) but different modality and task.)_

#### IMPROVING LONG-TAIL RECOMMENDATION VIA ROULETTE WHEEL SELECTION USING HYBRID RATING AND TEMPORAL DECAY WEIGHTING (2026) [3]

- **Problem:** The paper addresses popularity bias in recommendation systems, where user interactions concentrate on popular items, leaving long-tail items undiscovered. It proposes to mitigate this bias using temporal decay weighting combined with hybrid ratings and Roulette Wheel Selection to improve long-tail discoverability.
- **Method:** The authors integrate Roulette Wheel Selection with hybrid rating (combining multiple signals) and temporal decay weighting to create a stochastic framework for recommendation. They test on the Goodreads Poetry dataset using four embedding models (SBERT-Tuned, SBERT, FastText, Word2Vec) and compare stochastic (S) approach versus deterministic Top-N selection.
- **Main contribution:** A novel stochastic framework that integrates Roulette Wheel Selection with hybrid rating and temporal decay weighting to improve long-tail discoverability in recommendation systems. Empirical validation on Goodreads Poetry dataset shows up to 461.71% increase in Catalog Coverage with minimal Recall reduction, decreased Gini-index, and improved Novelty scores, demonstrating robustness across embedding models.
- **Key assumptions:** Temporal decay weighting can reduce popularity bias by giving less weight to older interactions.; Hybrid rating combines multiple signals to improve relevance estimation.; Roulette Wheel Selection provides stochasticity that enhances long-tail exposure without drastically hurting relevance.
- **Datasets / benchmarks:** Goodreads Poetry dataset, Deterministic Top-N selection (baseline)
- **Baselines:** Deterministic (D) Top-N selection
- **Metrics:** Catalog Coverage, Recall, Gini-index, Novelty scores
- **Results:** "SBERT-Tuned model achieved 461.71% increase in Catalog Coverage with 2.15% Recall reduction. FastText: 381.72% coverage increase. Word2Vec: 225.15% coverage increase. Gini-index decreased consistently. Novelty scores improved by +16% to +29%."
- **Limitations:** Focused on recommendation domain, not question answering.; Evaluated only on a single dataset (Goodreads Poetry).; Does not address temporal evolution of document content or versioning.; Temporal decay weighting applied to user interactions, not document versions.
- **Future work:** Apply framework to other recommendation domains (e.g., news, movies).; Investigate hybrid temporal decay functions.; Explore integration with deep learning models for end-to-end training.; Evaluate on cold-start scenarios and temporal shifts in item popularity.
- **Code availability:** No code availability stated in the abstract.
- **Relation to idea:** The paper uses temporal decay weighting to mitigate popularity bias in recommendation systems, while our work proposes temporal relevance weighting to improve retrieval for time-specific open-domain question answering over evolving regulatory texts. _(basis: Heuristic: both use temporal weighting but different tasks (recommendation vs QA) and different temporal signals (user interaction age vs document version timestamp).)_

</details>

## 5. Research Landscape

```text
Temporal Retrieval for Evolving Documents in Question Answering
├── Temporal Decay Analysis in Legal/Statutory Context  [1]
├── Temporal Weighting Applications in Other Modalities  [7] [3] [4]
├── Open-Domain QA Retrieval Efficiency  [5]
├── Preference Optimization / LLM Alignment with Temporal Decay  [6]
└── Temporal Relevance Weighting for Retrieval-Augmented Question Answering over Evolving Regulatory Texts
```

**Where the idea fits:** **[Inference]** Temporal Relevance Weighting for Retrieval-Augmented Question Answering over Evolving Regulatory Texts

**Dominant approaches**

- BM25 retrieval
- Dense retrieval (ColBERT, BERT-based)
- Co-citation analysis
- Uniform temporal decay weighting
- Adaptive temporal decay surfaces
- Stochastic selection with temporal weighting

**Common assumptions**

- Temporal proximity between document version timestamp and query target date correlates with relevance.
- Standard retriever provides a semantic similarity score that can be combined with temporal weight.
- Version timestamps are available or can be inferred from document metadata.
- Answer accuracy can be measured using standard QA metrics (Exact Match, F1).

**Common datasets**

- UA-StatuteRetrieval (Ukrainian court decisions)
- Goodreads Poetry dataset
- Korean QA dataset (AI-Hub corpora)
- AlpacaEval 2
- Arena-Hard
- MMLU
- GSM8K
- MATH
- Synthetic temporal knowledge graphs
- 107 Wikipedia articles
- 1,163 patient records (Synthea EHR)

**Common benchmarks**

- UA-StatuteRetrieval (own benchmark)
- BSARD (Belgian statutory)
- SCALE
- LeSICiN (Indian legal)
- Deterministic Top-N selection (recognition)
- Vanilla DPO
- SimPO
- SamPO
- Uniform decay baseline
- No temporal weighting

**Common metrics**

- MRR (Mean Reciprocal Rank)
- Hit@1
- Hit@5
- Hit@10
- Hit@20
- Exact Match (EM)
- F1 score
- Catalog Coverage
- Recall
- Gini-index
- Novelty scores
- AlpacaEval score
- Arena-Hard score
- HDBSCAN ARI

**Underexplored combinations**

- **[Hypothesis]** Temporal relevance weighting combined with dense retrievers (e.g., ColBERT, DPR) for open-domain QA over versioned regulatory texts.
- **[Hypothesis]** Hybrid graph-text temporal retrieval approaches for legal statutes (combining co-citation signals with textual relevance and temporal weighting).
- **[Hypothesis]** Benchmark construction for temporal QA using publicly available versioned regulatory corpora (e.g., US Code, Federal Regulations, international equivalents) with time-stamped queries.
- **[Hypothesis]** Evaluation of temporal relevance component using end-to-end QA pipelines (retriever + reader) rather than retrieval-only metrics.

**Limitations repeated across papers**

- Evaluation is a proxy (e.g., citation prediction) rather than end-user question answering. [1]
- Focuses on a specific modality (video, recommendation, knowledge graphs) not textual document retrieval or QA. [7], [3], [4]
- Limited to a specific language or domain (e.g., Korean QA, Ukrainian legal system). [5], [1]
- Does not address evolving document collections or versioned texts. [6], [5]
- Does not propose or test mitigation strategies for temporal decay. [1]

**Contradictions between papers**

- Some works find uniform temporal decay performs poorly compared to no temporal weighting (arxiv:2604.26970), while others apply uniform temporal decay weighting with positive results in recommendation (doi:10.33480/jitk.v12i1.8240) - suggesting effectiveness may depend on domain and signal type. [4], [3]

## 6. Closest Existing Work

**[Inference]** These papers study temporal aspects in retrieval or related fields: arxiv:2605.17639 analyzes temporal decay of co-citation predictability in Ukrainian statutes; arxiv:2608.08512 presents a benchmark for version resolution in evolving documents and identifies retrieval matching meaning as a key challenge; doi:10.33480/jitk.v12i1.8240 applies temporal decay weighting to mitigate popularity bias in recommendation systems; arxiv:2604.26970 proposes adaptive temporal decay for knowledge graphs. None propose a retrieval-agnostic temporal relevance component for open-domain question answering over evolving regulatory texts.

- Temporal Decay of Co-Citation Predictability: A 20-Year Statute Retrieval Benchmark from 396M Ukrainian Court Citations (2026) [1]: The paper measures temporal decay of co-citation predictability as a proxy for retrieval stability, while our work proposes a retrieval-agnostic temporal relevance component to mitigate degradation in open-domain QA over evolving regulatory texts.
- Time Present and Time Past: Benchmarking Large Language Models on Temporally Evolving Document Understanding (2026) [2] (not analyzed in detail)
- IMPROVING LONG-TAIL RECOMMENDATION VIA ROULETTE WHEEL SELECTION USING HYBRID RATING AND TEMPORAL DECAY WEIGHTING (2026) [3]: The paper uses temporal decay weighting to mitigate popularity bias in recommendation systems, while our work proposes temporal relevance weighting to improve retrieval for time-specific open-domain question answering over evolving regulatory texts.
- Not All Memories Age the Same: Autodiscovery of Adaptive Decay in Knowledge Graphs (2026) [4]: The paper proposes adaptive temporal decay for knowledge graph retrieval based on velocity and volatility, while our work proposes a retrieval-agnostic temporal relevance component for open-domain QA over evolving regulatory documents using version timestamps.

## 7. Potential Overlap

**Overlap:** **[Inference]** Overlap exists in the problem domain (legal/statutory texts that evolve over time) and the observation that retrieval signals degrade temporally (C001, C003). The proposed work shares the assumption that temporal proximity correlates with relevance (C008) and that standard retrievers provide combinable semantic scores (C009).

**Potential distinction:** **[Inference]** Unlike prior work that merely diagnoses decay (arxiv:2605.17639) or applies temporal weighting to other modalities (recommendation, knowledge graphs, video), this work proposes a retrieval-agnostic framework specifically for open-domain question answering that adjusts retriever rankings based on elapsed time between query target date and passage version timestamp, while preserving semantic similarity. It targets end-to-end QA accuracy rather than retrieval-only metrics or proxy tasks.

**Novelty questions**

_None recorded._

## 8. Potential Research Gap

_Not recorded: this phase did not produce the required records._

## 9. Critique

| | |
|---|---|
| Strongest argument FOR | The idea addresses a well-documented problem: temporal degradation of retrieval signals in evolving regulatory texts, evidenced by significant decay in co-citation predictability (C001, C003). A retrieval-agnostic temporal relevance component offers a principled way to mitigate this degradation while preserving semantic similarity, potentially improving version-specific question answering. |
| Strongest argument AGAINST | The closest existing work already analyzes temporal decay in legal statutes (C001) and applies temporal weighting in other domains (e.g., recommendation, knowledge graphs), suggesting the core concept may not be novel. Moreover, the approach faces technical risks due to non-uniform decay patterns (C004) and a major experimental confounder: retrieval often matches meaning rather than time (C006), making it difficult to isolate the true effect of temporal weighting on version selection. |
| Most important unresolved question | How to construct a realistic benchmark of versioned regulatory documents with time-stamped queries that adequately tests temporal relevance, and what is the optimal form and parameterization of the temporal weighting function for this setting? |
| Most dangerous experimental confounder | The confounding effect where retrieval systems match semantic meaning rather than temporal correctness (C006), which could lead to spurious improvements attributed to temporal weighting when gains are actually due to better semantic matching. |
| Closest existing work | [1], [2], [3], [4] |
| Potential contribution | **[Hypothesis]** A novel temporal relevance weighting scheme that can be combined with any standard retriever to improve retrieval of time-specific versions; a benchmark comprising versioned regulatory documents (e.g., statutes, policies) with timestamped questions; empirical demonstration that temporal-semantic ranking improves answer accuracy (Exact Match, F1) over strong baselines. |

**Technical validity**

_None recorded._

**Experimental validity**

_None recorded._

**Practicality**

_None recorded._

## 10. Proposed Modifications

_Not recorded: this phase did not produce the required records._

## 11. Recommended Experimental Design

_Not recorded: this phase did not produce the required records._

## 12. Experimental Results

Experiment not performed. The designs in Section 11 are untested.

## 13. Remaining Uncertainty

- Literature coverage: searched 7 queries over arxiv, crossref, openalex, semantic_scholar. Work outside these queries and sources, very recent preprints, and non-English work may be missing; the absence of matching work here does not establish novelty.
- Some source requests failed and their results are missing: semantic_scholar (api.semanticscholar.org failed after 5 attempts (HTTP 429)).
- Metadata warning for Deterministic Legal Agents: A Canonical Primitive API for Auditable Reasoning over Temporal Knowledge Graphs (2025) [8]: abstract (from arxiv) never mentions 'Deterministic Legal Agents'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Beyond Semantics: How Temporal Biases Shape Retrieval in Transformer and State-Space Models (2025) [9]: abstract (from arxiv) never mentions 'Beyond Semantics'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Bridging the Gap: Query by Semantic Example (2007) [10]: abstract (from openalex) never mentions 'Bridging the Gap'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Imaging Cognition II: An Empirical Review of 275 PET and fMRI Studies (2000) [11]: abstract (from openalex) never mentions 'Imaging Cognition II'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for The COMET Handbook: version 1.0 (2017) [12]: abstract (from openalex) never mentions 'The COMET Handbook'; it may belong to another work. Its abstract was not accepted as direct evidence.
- 5 of 6 analyses are based on abstracts only.
- Unresolved question: How to construct a realistic benchmark of versioned regulatory documents with time-stamped queries that adequately tests temporal relevance, and what is the optimal form and parameterization of the temporal weighting function for this setting?
- Ambiguity (assumption): Which baseline retriever should be used (e.g., BM25 vs dense retriever like DPR)?
- Ambiguity (assumption): What is the exact form of the temporal weighting function (exponential decay, linear, etc.) and how to set its hyperparameters?
- Ambiguity (assumption): How to construct a benchmark of regulatory documents with version history and create time-stamped queries?
- Ambiguity (assumption): How to obtain time-specific queries for evaluation (manual annotation vs synthetic generation)?
- Phases that did not complete: gaps, modifications, experiments.
- No hypothesis in this report has been tested experimentally.

**Uncertainty ledger**

| Id | Question | Category | Importance | Status | Evidence for / against | Resolution |
|---|---|---|---|---|---|---|
| U003 | How to construct a benchmark of regulatory documents with version history and create time-stamped questions for evaluating temporal relevance in QA? | feasibility | high | partially resolved | [1], [2] / none | Benchmark construction for versioned regulatory documents is feasible, as demonstrated by UA-StatuteRetrieval (arxiv:2605.17639) which built annual snapshots from 396M Ukrainian court citations, and TIDE (arxiv:2608.08512) which collected 644 PDFs of Bangladesh customs instruments (Acts, Orders, Rules) spanning 1969–2025, parsed them to preserve clauses and metadata, and generated expert-verified QA pairs. A similar approach can be applied to other regulatory corpora (e.g., US Code, Federal Regulations) by sourcing versioned documents, extracting timestamped clauses, and creating time-stamped questions via expert verification or semi-automatic methods using amendment metadata. |
| U005 | Are there existing retrieval methods that already combine temporal proximity with semantic similarity for document retrieval in evolving text collections? | overlap | high | partially resolved | [13], [14] / none | Existing work shows methods that combine temporal proximity with semantic similarity for document retrieval, such as TPOUR (Temporal Preference Optimization for Unsupervised Retrieval) which guides the retriever to favor temporally aligned documents via temporal preference optimization, and semantic modelling of document focus-time for temporal information retrieval. However, these methods often require supervised or specialized training and may not be retrieval-agnostic or tailored to versioned regulatory documents with explicit timestamps. |
| U006 | What sources of versioned regulatory documents (statutes, policies, regulations) with accessible version history and timestamps are publicly available for constructing a benchmark? | feasibility | high | partially resolved | [1], [2] / none | Sources of versioned regulatory documents with accessible version history and timestamps include the Ukrainian Unified State Register of Court Decisions (as demonstrated by the extraction of 396 million codex-article citations to construct annual retrieval benchmarks) and Bangladeshi customs instruments (Acts, Orders, Rules) as demonstrated by the TIDE dataset comprising 3 Acts, 20 GOs, 609 SROs, and 12 Rules spanning 1969–2025. This indicates that such sources are publicly available for constructing a benchmark. |
| U009 | How can we mitigate the confound where retrieval systems match semantic meaning rather than temporal correctness, ensuring that temporal weighting actually influences version selection in open-domain question answering? | confounder | high | partially resolved | [2], [13] / none | The confound where retrieval systems match semantic meaning rather than temporal correctness is a recognized challenge in temporal QA (C005, C006). Existing work like TIDE mitigates this through evaluation design using a "hard date gate" that separates correct meaning from correct time (C013, C014). Retrieval-level approaches such as our proposed temporal relevance framework may address this confound earlier in the pipeline by directly influencing which passages are retrieved based on temporal proximity (C016), unlike specialized methods that require specific training or architectures (C017). |
| U010 | How can we empirically validate that a temporal relevance component actually influences version selection in retrieval rather than merely improving semantic matching, given the confound where retrieval systems match meaning rather than time? | evaluation | high | partially resolved | [2] / none | Empirical validation that a temporal relevance component influences version selection rather than merely improving semantic matching can be achieved through evaluation designs that separate temporal correctness from semantic meaning, such as TIDE's 'hard date gate' which measures strict accuracy (requiring both correct meaning and correct time) versus partial accuracy (credit for correct dates even when meaning is wrong). Improvements in strict accuracy indicate true temporal retrieval capability, while improvements only in partial accuracy suggest better semantic matching without temporal correctness. |
| U011 | Given that retrieval systems tend to match meaning rather than time, what form of temporal relevance weighting (e.g., simple exponential decay, learned temporal embeddings, hybrid approaches) is most likely to effectively shift retrieval behavior toward temporal correctness without being overwhelmed by semantic signals? | validity | high | partially resolved | [13], [4] / none | Evidence suggests that learned or adaptive temporal weighting functions (e.g., TPOUR's temporal preference optimization with learned time embedding, or hierarchical decay surfaces parameterized by velocity and volatility) can effectively balance temporal and semantic signals by learning from data, rather than relying on a fixed exponential decay that may be overwhelmed by semantic signals. This indicates that adaptive or learned forms are more promising for shifting retrieval behavior toward temporal correctness. |
| U001 | Which baseline retriever should be used for the temporal relevance framework (e.g., BM25 vs dense retriever like DPR)? | feasibility | medium | open | none / none | Not recorded |
| U002 | What is the exact form of the temporal weighting function (exponential decay, linear, etc.) and how should its hyperparameters be set for optimal performance? | other | medium | open | none / none | Not recorded |
| U004 | How to obtain time-specific questions for evaluation (manual annotation vs synthetic generation) and ensure they accurately reflect temporal information needs? | feasibility | medium | open | none / none | Not recorded |
| U007 | Which evaluation metrics are most appropriate for measuring the impact of temporal relevance on answer accuracy in open-domain QA, and how do they handle the temporal dimension of correctness? | evaluation | medium | open | none / none | Not recorded |
| U008 | Can a simple temporal relevance component (e.g., exponential decay based solely on elapsed time) effectively handle non-uniform decay across legal domains, or is domain-adaptive weighting necessary to capture varying decay rates? | validity | medium | open | none / none | Not recorded |

## 14. Suggested Next Steps

1. Resolve: How to construct a realistic benchmark of versioned regulatory documents with time-stamped queries that adequately tests temporal relevance, and what is the optimal form and parameterization of the temporal weighting function for this setting?
2. Design a control for the confounder: The confounding effect where retrieval systems match semantic meaning rather than temporal correctness (C006), which could lead to spurious improvements attributed to temporal weighting when gains are actually due to better semantic matching.
3. Read the full text of the closest work analyzed only from abstracts: [3], [4].
4. Search for work newer than the most recent retrieved paper (2026) before claiming a distinction.

## 15. References

1. Volodymyr Ovcharov. **Temporal Decay of Co-Citation Predictability: A 20-Year Statute Retrieval Benchmark from 396M Ukrainian Court Citations**. _arXiv.org_, 2026. <https://www.semanticscholar.org/paper/e4c6767c37dee633c63a589d7ab490ec41cc181f> doi:10.48550/arxiv.2605.17639 (id `arxiv:2605.17639`; retrieved from arxiv, semantic_scholar; 2 citations per semantic_scholar)
2. Mahbub E Sobhani, Md. Faiyaz Abdullah Sayeedi, Fahmid Hasan Chowdhury et al.. **Time Present and Time Past: Benchmarking Large Language Models on Temporally Evolving Document Understanding**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2608.08512> (id `arxiv:2608.08512`; retrieved from arxiv)
3. Andy Maulana Yusuf, Miftah Farid Adiwisastra, Faizal Riza et al.. **IMPROVING LONG-TAIL RECOMMENDATION VIA ROULETTE WHEEL SELECTION USING HYBRID RATING AND TEMPORAL DECAY WEIGHTING**. _JITK (Jurnal Ilmu Pengetahuan dan Teknologi Komputer)_, 2026. <https://www.semanticscholar.org/paper/f6df9ea6ea0ea06cf3507ea496e84a5b3c0f5d94> doi:10.33480/jitk.v12i1.8240 (id `doi:10.33480/jitk.v12i1.8240`; retrieved from semantic_scholar; 0 citations per semantic_scholar)
4. Mandar Karhade. **Not All Memories Age the Same: Autodiscovery of Adaptive Decay in Knowledge Graphs**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2604.26970> (id `arxiv:2604.26970`; retrieved from arxiv)
5. Byungha Kang, Yeonghwa Kim, Youhyun Shin. **An Efficient Document Retrieval for Korean Open-Domain Question Answering Based on ColBERT**. _Applied Sciences_, 2023. <https://doi.org/10.3390/app132413177> (id `doi:10.3390/app132413177`; retrieved from crossref; 2 citations per crossref)
6. Ruichen Shao, Bei Li, Gangao Liu et al.. **Earlier Tokens Contribute More: Learning Direct Preference Optimization From Temporal Decay Perspective**. _International Conference on Learning Representations_, 2025. <https://www.semanticscholar.org/paper/e43fa63d5b79b65b8dc2abb7aa5bc903471be6f7> doi:10.48550/arxiv.2502.14340 (id `arxiv:2502.14340`; retrieved from semantic_scholar; 10 citations per semantic_scholar)
7. Weijian Ruan, Yiran Tao, Linjun Ruan et al.. **Temporal Weighting Appearance-Aligned Network for Nighttime Video Retrieval**. _IEEE Signal Processing Letters_, 2022. <https://doi.org/10.1109/lsp.2022.3207620> (id `doi:10.1109/lsp.2022.3207620`; retrieved from crossref; 0 citations per crossref)
8. Hudson de Martim. **Deterministic Legal Agents: A Canonical Primitive API for Auditable Reasoning over Temporal Knowledge Graphs**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2510.06002> (id `arxiv:2510.06002`; retrieved from arxiv)
9. Anooshka Bajaj, Deven Mahesh Mistry, Sahaj Singh Maini et al.. **Beyond Semantics: How Temporal Biases Shape Retrieval in Transformer and State-Space Models**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2510.22752> (id `arxiv:2510.22752`; retrieved from arxiv)
10. Nikhil Rasiwasia, P.J. Moreno, Nuno M. Vasconcelos. **Bridging the Gap: Query by Semantic Example**. _IEEE Transactions on Multimedia_, 2007. <https://doi.org/10.1109/tmm.2007.900138> (id `doi:10.1109/tmm.2007.900138`; retrieved from openalex; 249 citations per openalex)
11. Roberto Eduardo Luis Cabeza, Lars H Nyberg. **Imaging Cognition II: An Empirical Review of 275 PET and fMRI Studies**. _Journal of Cognitive Neuroscience_, 2000. <https://doi.org/10.1162/08989290051137585> (id `doi:10.1162/08989290051137585`; retrieved from openalex; 3657 citations per openalex)
12. Paula Ruth Williamson, Douglas G. Altman, Heather Bagley et al.. **The COMET Handbook: version 1.0**. _Trials_, 2017. <https://doi.org/10.1186/s13063-017-1978-4> (id `doi:10.1186/s13063-017-1978-4`; retrieved from openalex; 2086 citations per openalex)
13. HyunJin Kim, Jaejun Shim, Young Jin Kim et al.. **Temporal Preference Optimization for Unsupervised Retrieval**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2606.17664> (id `arxiv:2606.17664`; retrieved from arxiv)
14. Lirong Zhang, Hideo Joho, Hai-Tao Yu. **Semantic Modelling of Document Focus-Time for Temporal Information Retrieval**. _Companion Proceedings of the Web Conference 2022_, 2022. <https://doi.org/10.1145/3487553.3524668> (id `doi:10.1145/3487553.3524668`; retrieved from crossref; 1 citations per crossref)

<details><summary>Other retrieved papers (not cited in this report)</summary>

- ChroniclingAmericaQA: A Large-scale Question Answering Dataset based on Historical American Newspaper Pages (2024) <https://arxiv.org/abs/2403.17859> `arxiv:2403.17859`
- Question Answering under Temporal Conflict: Evaluating and Organizing Evolving Knowledge with LLMs (2025) <https://arxiv.org/abs/2506.07270> `arxiv:2506.07270`
- Temporal-Aware RAG for Multilingual ESG Document Retrieval: A Low-Resource Approach to Time-Sensitive Question Answering (2025) <https://doi.org/10.1109/bigdata66926.2025.11402566> `doi:10.1109/bigdata66926.2025.11402566`
- Document GraphRAG: Knowledge Graph Enhanced Retrieval Augmented Generation for Document Question Answering Within the Manufacturing Domain (2025) <https://doi.org/10.3390/electronics14112102> `doi:10.3390/electronics14112102`
- Unified Interactive Multimodal Moment Retrieval via Cascaded Embedding-Reranking and Temporal-Aware Score Fusion (2025) <https://arxiv.org/abs/2512.12935> `arxiv:2512.12935`
- Self-Aware Vector Embeddings for Retrieval-Augmented Generation: A Neuroscience-Inspired Framework for Temporal, Confidence-Weighted, and Relational Knowledge (2026) <https://arxiv.org/abs/2604.20598> `arxiv:2604.20598`
- SentryLine: Evidence-Grounded Question Answering over Evolving Documents in Oncology Care (2026) <https://arxiv.org/abs/2609.08364> `arxiv:2609.08364`
- Question Answering Evaluation (2022) <https://doi.org/10.1007/978-3-031-16552-8_3> `doi:10.1007/978-3-031-16552-8_3`
- Question Answering over Text (2022) <https://doi.org/10.1007/978-3-031-16552-8_5> `doi:10.1007/978-3-031-16552-8_5`
- Question Answering over Knowledge Base (2022) <https://doi.org/10.1007/978-3-031-16552-8_6> `doi:10.1007/978-3-031-16552-8_6`
- Future Directions of Question Answering (2022) <https://doi.org/10.1007/978-3-031-16552-8_9> `doi:10.1007/978-3-031-16552-8_9`
- Graph-based term weighting for information retrieval (2011) <https://doi.org/10.1007/s10791-011-9172-x> `doi:10.1007/s10791-011-9172-x`
- Forgetting in immediate serial recall: Decay, temporal distinctiveness, or interference? (2008) <https://doi.org/10.1037/0033-295x.115.3.544> `doi:10.1037/0033-295x.115.3.544`
- Question Answering (2012) <https://doi.org/10.1093/oxfordhb/9780199276349.013.0031> `doi:10.1093/oxfordhb/9780199276349.013.0031`
- Temporal User-Agnostic Ranking: Detecting Preference Evolution while Preserving Ethical Principles (2026) <https://www.semanticscholar.org/paper/12abf7f6ce9d4358937dfcc2fedee5ed4a572950> `doi:10.1145/3805712.3809900`
- TDR 2 A：Time-sensitive Decomposition-Retrieval-Reorganization Agent for Temporal Knowledge Graph Question Answering (2025) <https://doi.org/10.2139/ssrn.5624243> `doi:10.2139/ssrn.5624243`
- Improving text retrieval precision and answer accuracy in question answering systems (2008) <https://doi.org/10.3115/1641451.1641452> `doi:10.3115/1641451.1641452`
- Exact phrases in information retrieval for question answering (2008) <https://doi.org/10.3115/1641451.1641453> `doi:10.3115/1641451.1641453`
- Passage retrieval for question answering using sliding windows (2008) <https://doi.org/10.3115/1641451.1641455> `doi:10.3115/1641451.1641455`
- Web Document Retrieval Using Passage Retrieval, Connectivity Information, and Automatic Link Weighting–TREC-9 Report (2000) <https://doi.org/10.6028/nist.sp.500-249.padova> `doi:10.6028/nist.sp.500-249.padova`
- Time-Sensitive Weighting for Microblog Retrieval (2011) <https://doi.org/10.6028/nist.sp.500-296.microblog-udel_fang> `doi:10.6028/nist.sp.500-296.microblog-udel_fang`
- From document retrieval to question answering (2003) <https://research.utwente.nl/en/publications/3c5b1ae9-93f7-4a7c-8b8b-a0f894a87a17> `openalex:W2111572281`
- DeepSpecs: Expert-Level Questions Answering in 5G (2025) <https://arxiv.org/abs/2511.01305> `arxiv:2511.01305`
- Toward expert-level medical question answering with large language models (2025) <https://doi.org/10.1038/s41591-024-03423-7> `doi:10.1038/s41591-024-03423-7`
- Proceedings of the 1st Workshop on Document-grounded Dialogue and Conversational Question Answering (DialDoc 2021) (2021) <https://doi.org/10.18653/v1/2021.dialdoc-1> `doi:10.18653/v1/2021.dialdoc-1`
- Parameter-Efficient Abstractive Question Answering over Tables or Text (2022) <https://doi.org/10.18653/v1/2022.dialdoc-1.5> `doi:10.18653/v1/2022.dialdoc-1.5`
- Proceedings of the Second DialDoc Workshop on Document-grounded Dialogue and Conversational Question Answering (2022) <https://doi.org/10.18653/v1/2022.dialdoc-1> `doi:10.18653/v1/2022.dialdoc-1`
- Proceedings of the Third DialDoc Workshop on Document-grounded Dialogue and Conversational Question Answering (2023) <https://doi.org/10.18653/v1/2023.dialdoc-1> `doi:10.18653/v1/2023.dialdoc-1`
- TV-RAG: A Temporal-aware and Semantic Entropy-Weighted Framework for Long Video Retrieval and Understanding (2025) <https://arxiv.org/abs/2512.23483> `arxiv:2512.23483`
- TFPS: A Temporal Filtration-enhanced Positive Sample Set Construction Method for Implicit Collaborative Filtering (2026) <https://arxiv.org/abs/2602.22521> `arxiv:2602.22521`
- Limitations of Open-Domain Question Answering Benchmarks for Document-level Reasoning (2023) <https://doi.org/10.1145/3539618.3592011> `doi:10.1145/3539618.3592011`
- Functional Anatomic Studies of Memory Retrieval for Auditory Words and Visual Pictures (1996) <https://doi.org/10.1523/jneurosci.16-19-06219.1996> `doi:10.1523/jneurosci.16-19-06219.1996`
- MoQA: Benchmarking Multi-Type Open-Domain Question Answering (2023) <https://doi.org/10.18653/v1/2023.dialdoc-1.2> `doi:10.18653/v1/2023.dialdoc-1.2`
- Methods for using textual entailment in open-domain question answering (2006) <https://doi.org/10.3115/1220175.1220289> `doi:10.3115/1220175.1220289`
- Evaluation of semantic similarity metrics applied to the automatic retrieval of medical documents: An UMLS approach (2016) <https://doi.org/10.1016/j.eswa.2015.09.028> `doi:10.1016/j.eswa.2015.09.028`
- Semantic proximity in information retrieval and documents classification (2013) <https://doi.org/10.1109/cinti.2013.6705178> `doi:10.1109/cinti.2013.6705178`
- TempRet: Temporal Enhancement and Two-Stage Reranking for CVPR 2026 EPIC-KITCHENS-100 Multi-Instance Retrieval Challenge (2026) <https://arxiv.org/abs/2605.24470> `arxiv:2605.24470`
- The nature and time‐course of medial temporal lobe contributions to semantic retrieval: An fMRI study on verbal fluency (2011) <https://doi.org/10.1002/hipo.20985> `doi:10.1002/hipo.20985`
- The Dynamics of Semantic and Temporal Cuing During Episodic Memory Retrieval (2008) <https://doi.org/10.1037/e527312012-919> `doi:10.1037/e527312012-919`
- Lexical retrieval and semantic knowledge in patients with left inferior temporal lobe lesions (2008) <https://doi.org/10.1080/02687030701294491> `doi:10.1080/02687030701294491`
- Anterior temporal involvement in semantic word retrieval: voxel-based lesion-symptom mapping evidence from aphasia (2009) <https://doi.org/10.1093/brain/awp284> `doi:10.1093/brain/awp284`
- Executive Semantic Processing Is Underpinned by a Large-scale Neural Network: Revealing the Contribution of Left Prefrontal, Posterior Temporal, and Parietal Cortex to Controlled Retrieval and Selection Using TMS (2011) <https://doi.org/10.1162/jocn_a_00123> `doi:10.1162/jocn_a_00123`
- Competitive Semantic Memory Retrieval: Temporal Dynamics Revealed by Event-Related Potentials (2016) <https://doi.org/10.1371/journal.pone.0150091> `doi:10.1371/journal.pone.0150091`
- Medial Temporal Lobe Activity during Retrieval of Semantic Memory Is Related to the Age of the Memory (2009) <https://doi.org/10.1523/jneurosci.4545-08.2009> `doi:10.1523/jneurosci.4545-08.2009`
- Automatic and Controlled Semantic Retrieval: TMS Reveals Distinct Contributions of Posterior Middle Temporal Gyrus and Angular Gyrus (2015) <https://doi.org/10.1523/jneurosci.4705-14.2015> `doi:10.1523/jneurosci.4705-14.2015`
- Emphasizing temporal and semantic associations from encoding affects free recall at retrieval (2022) <https://doi.org/10.31234/osf.io/q4dpg> `doi:10.31234/osf.io/q4dpg`
- Fortunate Recall: Ontology-Driven Memory Lifecycle Management for Persistent Coherence in LLMs (2026) <https://arxiv.org/abs/2609.10413> `arxiv:2609.10413`
- An Answer to the Question: ‘What is Enlightenment?’ (1991) <https://doi.org/10.1017/cbo9780511809620.005> `doi:10.1017/cbo9780511809620.005`
- Mars Climate Sounder limb profile retrieval of atmospheric temperature, pressure, and dust and water ice opacity (2009) <https://doi.org/10.1029/2009je003358> `doi:10.1029/2009je003358`
- An Improved Soil Moisture Retrieval Algorithm for ERS and METOP Scatterometer Observations (2009) <https://doi.org/10.1109/tgrs.2008.2011617> `doi:10.1109/tgrs.2008.2011617`
- Dynamical and Microphysical Retrieval from Doppler Radar Observations Using a Cloud Model and Its Adjoint. Part II: Retrieval Experiments of an Observed Florida Convective Storm (1998) <https://doi.org/10.1175/1520-0469(1998)055<0835:damrfd>2.0.co;2> `doi:10.1175/1520-0469(1998)055<0835:damrfd>2.0.co;2`
- Combining Open Domain Question Answering with a Task-Oriented Dialog System (2021) <https://doi.org/10.18653/v1/2021.dialdoc-1.5> `doi:10.18653/v1/2021.dialdoc-1.5`
- Retrieval-Augmented Detection: Grounding Intrusion Analysis in Historical Incident Corpora (2026) <https://www.semanticscholar.org/paper/4d2eddfee44b4297f6c109af1ff30f644cf0a480> `doi:10.36948/ijfmr.2026.v08i04.85144`
- The islamic statute of the Mudejars in the light of a new source (1996) <https://doi.org/10.3989/alqantara.1996.v17.i1.539> `doi:10.3989/alqantara.1996.v17.i1.539`
- Dissecting Temporal Understanding in Text-to-Audio Retrieval (2024) <https://arxiv.org/abs/2409.00851> `arxiv:2409.00851`
- Temporal Information Retrieval via Time-Specifier Model Merging (2025) <https://arxiv.org/abs/2507.06782> `arxiv:2507.06782`
- Efficient Temporal-aware Matryoshka Adaptation for Temporal Information Retrieval (2026) <https://arxiv.org/abs/2601.05549> `arxiv:2601.05549`
- SEMANTIC MOTION CONCEPT RETRIEVAL IN NON-STATIC BACKGROUND UTILIZING SPATIAL-TEMPORAL VISUAL INFORMATION (2013) <https://doi.org/10.1142/s1793351x13400035> `doi:10.1142/s1793351x13400035`
- Unsupervised, Efficient and Semantic Expertise Retrieval (2016) <https://doi.org/10.1145/2872427.2882974> `arxiv:1608.06651`
- Similarity-Based Retrieval of Temporal Specifications and its Application to the Retrieval of Multimedia Documents (2005) <https://doi.org/10.1007/s11042-005-2717-5> `doi:10.1007/s11042-005-2717-5`
- Similarity Breeds Proximity: Pattern Similarity within and across Contexts Is Related to Later Mnemonic Judgments of Temporal Proximity (2014) <https://doi.org/10.1016/j.neuron.2014.01.042> `doi:10.1016/j.neuron.2014.01.042`
- Retrieval of Patent Documents from Heterogeneous Sources Using Ontologies and Similarity Analysis (2011) <https://doi.org/10.1109/icsc.2011.34> `doi:10.1109/icsc.2011.34`
- Similarity-based retrieval of temporal documents (2000) <https://doi.org/10.1145/357744.357955> `doi:10.1145/357744.357955`
- Study of Semantic Retrieval by Data Similarity of Trademarks (2015) <https://doi.org/10.21275/v4i11.nov151799> `doi:10.21275/v4i11.nov151799`
- Is Question Answering fit for the Semantic Web?: A survey (2011) <https://doi.org/10.3233/sw-2011-0041> `doi:10.3233/sw-2011-0041`
- Faculty Opinions recommendation of Similarity breeds proximity: pattern similarity within and across contexts is related to later mnemonic judgments of temporal proximity. (2014) <https://doi.org/10.3410/f.718304632.793492550> `doi:10.3410/f.718304632.793492550`
- SEMANTIC IDENTIFICATION AND VISUALIZATION OF SIGNIFICANT WORDS WITHIN DOCUMENTS - Approach to Visualize Relevant Words within Documents to a Search Query by Word Similarity Computation (2010) <https://doi.org/10.5220/0003099004810486> `doi:10.5220/0003099004810486`
- CONCORDIA: COmputing semaNtic sentenCes for fRench Clinical Documents sImilArity (2021) <https://doi.org/10.5220/0010687500003058> `doi:10.5220/0010687500003058`
- Gradient-based learning applied to document recognition (1998) <https://doi.org/10.1109/5.726791> `doi:10.1109/5.726791`
- Tensor Manifold-Based Graph-Vector Fusion for AI-Native Academic Literature Retrieval (2026) <https://arxiv.org/abs/2604.16416> `arxiv:2604.16416`
- Where Is the Semantic System? A Critical Review and Meta-Analysis of 120 Functional Neuroimaging Studies (2009) <https://doi.org/10.1093/cercor/bhp055> `doi:10.1093/cercor/bhp055`
- Research of cross-media information retrieval model based on multimodal fusion and temporal-spatial context semantic (2009) <https://doi.org/10.3724/sp.j.1087.2009.01182> `doi:10.3724/sp.j.1087.2009.01182`
- A Survey on Knowledge Graphs: Representation, Acquisition, and Applications (2021) <https://doi.org/10.1109/tnnls.2021.3070843> `arxiv:2002.00388`
- Episodic Memory Retrieval, Parietal Cortex, and the Default Mode Network: Functional and Topographic Analyses (2011) <https://doi.org/10.1523/jneurosci.3335-10.2011> `doi:10.1523/jneurosci.3335-10.2011`
- Multilevel Language and Vision Integration for Text-to-Clip Retrieval (2019) <https://doi.org/10.1609/aaai.v33i01.33019062> `doi:10.1609/aaai.v33i01.33019062`
- Decoupling Semantics and Logic: A Training-Free Coarse-to-Fine Pipeline for Video Retrieval-Augmented Generation (2026) <https://arxiv.org/abs/2606.07924> `arxiv:2606.07924`
- WordNet: An electronic lexical database . Ed. by Christiane Fellbaum. Cambridge, MA: MIT Press, 1998. Pp. xxii, 423. (2000) <https://doi.org/10.2307/417141> `doi:10.2307/417141`
- Which academic search systems are suitable for systematic reviews or meta‐analyses? Evaluating retrieval qualities of Google Scholar, PubMed, and 26 other resources (2019) <https://doi.org/10.1002/jrsm.1378> `doi:10.1002/jrsm.1378`
- Overview of the Coupled Model Intercomparison Project Phase 6 (CMIP6) experimental design and organization (2016) <https://doi.org/10.5194/gmd-9-1937-2016> `doi:10.5194/gmd-9-1937-2016`
- Maintaining knowledge about temporal intervals (1983) <https://doi.org/10.1145/182.358434> `doi:10.1145/182.358434`
- The crucial role of semantic discovery and markup in geo-temporal search (2010) <https://doi.org/10.1145/1871962.1871966> `doi:10.1145/1871962.1871966`
- Triadic Temporal-Semantic Alignment for Weakly Supervised Video Moment Retrieval (2024) <https://doi.org/10.2139/ssrn.4726553> `doi:10.2139/ssrn.4726553`
- A unified model of human semantic knowledge and its disorders (2017) <https://doi.org/10.1038/s41562-016-0039> `doi:10.1038/s41562-016-0039`
- The Organization and Operation of Inferior Temporal Cortex (2018) <https://doi.org/10.1146/annurev-vision-091517-034202> `doi:10.1146/annurev-vision-091517-034202`
- The evidence for a temporal processing deficit linked to dyslexia: A review (1995) <https://doi.org/10.3758/bf03210983> `doi:10.3758/bf03210983`
- Semantic memory: A review of methods, models, and current challenges (2020) <https://doi.org/10.3758/s13423-020-01792-x> `doi:10.3758/s13423-020-01792-x`
- Retrieval-Augmented Generation for Large Language Models: A Survey (2023) <http://arxiv.org/abs/2312.10997> `arxiv:2312.10997`
- Continual lifelong learning with neural networks: A review (2019) <https://doi.org/10.1016/j.neunet.2019.01.012> `arxiv:1802.07569`
- A systematic literature review of blockchain-based applications: Current status, classification and open issues (2018) <https://doi.org/10.1016/j.tele.2018.11.006> `doi:10.1016/j.tele.2018.11.006`
- European Guidelines on cardiovascular disease prevention in clinical practice (version 2012) (2012) <https://doi.org/10.1093/eurheartj/ehs092> `doi:10.1093/eurheartj/ehs092`
- Development and Distortion of Malaysian Public- Private Partnerships: Patronage, Privatised Profits and Pitfalls DOI: 10.1111/j.1467- 8500.2009.00655.x (2010) <http://civis.se/Cifras-de-la-situacion-de-los-y> `doi:10.1111/j.1467-`
- The MODIS Aerosol Algorithm, Products, and Validation (2005) <https://doi.org/10.1175/jas3385.1> `doi:10.1175/jas3385.1`
- Super-Statutes (2001) <https://doi.org/10.2307/1373022> `doi:10.2307/1373022`
- A Taxonomy of Privacy (2006) <https://doi.org/10.2307/40041279> `doi:10.2307/40041279`
- The Interpretation of Multilingual Statutes by the European Court of Justice (2009) <https://brooklynworks.brooklaw.edu/bjil/vol34/iss2/1> `openalex:W2268102062`

</details>

## Appendix A. Evidence Ledger

### [Evidence] claims (11)

- **[Evidence]** Co-citation structure is widely assumed to provide stable retrieval signal in legal information systems. We test this assumption longitudinally by constructing UA-StatuteRetrieval, a benchmark that measures co-citation predictability across 20 annual snapshots (2007-2026) of 396 million codex citations from 101 million Ukrainian court decisions. _(claim C001, confidence: high)_
  - [1], abstract (direct support, verified) "Co-citation structure is widely assumed to provide stable retrieval signal in legal information systems. We test this assumption longitudinally by constructing UA-StatuteRetrieval, a benchmark that measures co-citation predictability across 20 annual snapshots (2007-2026) of 396 million codex citations from 101 million Ukrainian court decisions."
- **[Evidence]** The decay is non-uniform: criminal procedure maintains stable co-citation patterns (MRR ∼0.40), while civil law degrades from 0.35 to 0.15, coinciding with the 2017 judicial reform. _(claim C003, confidence: high)_
  - [1], p. 1 (direct support, verified) "The decay is non-uniform: criminal procedure maintains stable co-citation patterns (MRR ∼0.40), while civil law degrades from 0.35 to 0.15, coinciding with the 2017 judicial reform."
- **[Evidence]** Third, retrieval matches meaning rather than time (Zhang et al., 2025). _(claim C005, confidence: high)_
  - [2], p. 1 (direct support, verified) "Third, retrieval matches meaning rather than time (Zhang et al., 2025)."
- **[Evidence]** Unsupervised dense retrievers struggle to capture temporal relevance, retrieving semantically related but temporally misaligned documents. We propose TPOUR (Temporal Preference Optimization for Unsupervised Retriever), which uses Temporal Retrieval Preference Optimization (TRPO) to reinterprets preference learning in the temporal dimension, guiding the retriever to favor temporally aligned documents. _(claim C012, confidence: high)_
  - [13], abstract (direct support, verified) "Unsupervised dense retrievers offer scalability by learning semantic similarity from unlabeled documents via contrastive learning, but they struggle to capture the temporal relevance, retrieving semantically related but temporally misaligned documents-an important aspect when a document collection spans multiple time periods (e.g., retrieving documents from 2018-2025 for "Who is the president in 2019?" introduces temporal ambiguity). Existing methods rely on supervised training with explicit timestamps, which are not always feasible. We propose TPOUR (Temporal Preference Optimization for Unsupervised Retriever), which uses our novel training method Temporal Retrieval Preference Optimization (TRPO). TRPO reinterprets preference learning in the temporal dimension, guiding the retriever to favor temporally aligned documents."
- **[Evidence]** We designed a unified evaluation protocol across the parametric, gold-context, and retrieval settings, scored by an LLM council with a hard date gate that separates correct meaning from correct time. _(claim C013, confidence: high)_
  - [2], p. 2 (direct support, verified) "We designed a unified evaluation protocol across the parametric, gold-context, and retrieval settings, scored by an LLM council with a hard date gate that separates correct meaning from correct time."
- **[Evidence]** The date gate separates correct meaning from correct time. _(claim C014, confidence: high)_
  - [2], p. 7 (direct support, verified) "The date gate separates correct meaning from correct time"
- **[Evidence]** The date gate separates correct meaning from correct time. _(claim C019, confidence: high)_
  - [2], p. 7 (direct support, verified) "The date gate separates correct meaning from correct time"
- **[Evidence]** The partial score retains credit for correct dates even when the meaning is wrong, whereas meaning earns credit only when every reference date is satisfied. _(claim C020, confidence: high)_
  - [2], p. 7 (direct support, verified) "partial score retains credit for correct dates even when the meaning is wrong, whereas meaning earns credit only when every reference date is satisfied"
- **[Evidence]** From the Ukrainian Unified State Register of Court Decisions (ЄДРСР, 101M decisions, 2007–2026), we extract 396 million codex-article citations and construct annual retrieval benchmarks spanning 20 years. _(claim C023, confidence: high)_
  - [1], p. 1 (direct support, verified) "extract 396 million codex-article citations and construct annual retrieval benchmarks spanning 20 years"
- **[Evidence]** We collected 644 PDFs from official the website 1: 3 Acts of Parliament, 20 General Orders (GOs), 609 Statutory Regulatory Orders (SROs), and 12 Rules, spanning 1969 to 2025. _(claim C024, confidence: high)_
  - [2], p. 2 (direct support, verified) "We collected 644 PDFs from official the website 1: 3 Acts of Parliament, 20 General Orders (GOs), 609 Statutory Regulatory Orders (SROs), and 12 Rules, spanning 1969 to 2025."
- **[Evidence]** From the Ukrainian Unified State Register of Court Decisions, we extract 396 million codex-article citations. _(claim C025, confidence: high)_
  - [1], p. 1 (direct support, verified) "extract 396 million codex-article citations"

### [Inference] claims (9)

- **[Inference]** The proposed temporal relevance framework overlaps significantly with arxiv:2605.17639 in focusing on temporal degradation in legal/statutory texts and acknowledging the problem of outdated retrieval signals, but differs in goal (diagnosing decay vs mitigating it via retrieval-agnostic temporal weighting) and method (analyzing co-citation predictability vs adjusting retriever rankings with temporal relevance). _(claim C002, confidence: medium)_
  - [1], abstract (direct support, verified) "Co-citation structure is widely assumed to provide stable retrieval signal in legal information systems. We test this assumption longitudinally by constructing UA-StatuteRetrieval, a benchmark that measures co-citation predictability across 20 annual snapshots (2007-2026) of 396 million codex citations from 101 million Ukrainian court decisions."
- **[Inference]** The non-uniform decay of co-citation predictability across legal domains (e.g., stable criminal procedure vs degrading civil law) poses a technical risk that a simple temporal relevance component (e.g., exponential decay based solely on elapsed time) may not adequately capture varying decay rates, potentially reducing effectiveness if not adapted to domain-specific dynamics. _(claim C004, confidence: medium)_
  - [1], p. 1 (direct support, verified) "The decay is non-uniform: criminal procedure maintains stable co-citation patterns (MRR ∼0.40), while civil law degrades from 0.35 to 0.15, coinciding with the 2017 judicial reform."
- **[Inference]** The observation that retrieval matches meaning rather than time presents a major experimental confounder: any observed improvement from adding temporal relevance could be due to better semantic matching rather than correct temporal selection, making it difficult to isolate the true effect of temporal weighting on version-specific retrieval. _(claim C006, confidence: medium)_
  - [2], p. 1 (direct support, verified) "Third, retrieval matches meaning rather than time (Zhang et al., 2025)."
- **[Inference]** While the TIDE paper addresses the meaning vs. time confound through evaluation design (hard date gate), our proposed temporal relevance framework aims to mitigate this confound at the retrieval level by explicitly incorporating temporal relevance into the retrieval ranking process, potentially reducing the need for post-retrieval correction. _(claim C015, confidence: medium)_
  - [2], p. 7 (direct support, verified) "The date gate separates correct meaning from correct time"
- **[Inference]** Unlike evaluation-only approaches like the hard date gate in TIDE that separate correct meaning from correct time post-retrieval, retrieval-level temporal relevance weighting directly influences which passages are retrieved by adjusting ranks based on temporal proximity, potentially addressing the meaning vs. time confound earlier in the pipeline. _(claim C016, confidence: medium)_
  - [2], p. 7 (direct support, verified) "The date gate separates correct meaning from correct time"
- **[Inference]** Existing temporal retrieval methods like TPOUR require specialized training or architectural changes to specific retriever types, whereas our proposed retrieval-agnostic temporal relevance component can be combined with any standard retriever (e.g., BM25, DPR, ColBERT) by adjusting passage ranks based on temporal proximity without modifying the underlying retriever. _(claim C017, confidence: medium)_
  - [13], abstract (direct support, verified) "We propose TPOUR (Temporal Preference Optimization for Unsupervised Retriever), which uses our novel training method Temporal Retrieval Preference Optimization (TRPO)."
- **[Inference]** Learned temporal weighting functions (e.g., via temporal preference optimization or adaptive decay surfaces) are more likely to effectively shift retrieval behavior toward temporal correctness without being overwhelmed by semantic signals compared to fixed exponential decay, because they can learn the appropriate balance from data. _(claim C018, confidence: medium)_
  - [13], abstract (direct support, verified) "We propose TPOUR (Temporal Preference Optimization for Unsupervised Retriever), which uses our novel training method Temporal Retrieval Preference Optimization (TRPO). TRPO reinterprets preference learning in the temporal dimension, guiding the retriever to favor temporally aligned documents."
  - [4], p. 1 (direct support, verified) "We propose a hierarchical framework that replaces uniform decay with a continuous decay surface parameterized by two orthogonal signals: velocity (how frequently a concept is observed) and volatility (how much the value changes between observations, measured via embedding distance)."
- **[Inference]** By using a hard date gate that separates correct meaning from correct time, TIDE's evaluation protocol can empirically validate whether a retrieval component actually influences version selection rather than merely improving semantic matching, as improvements in strict accuracy (requiring both correct meaning and correct time) indicate true temporal retrieval capability. _(claim C021, confidence: medium)_
  - [2], p. 7 (direct support, verified) "The date gate separates correct meaning from correct time"
  - [2], p. 7 (direct support, verified) "partial score retains credit for correct dates even when the meaning is wrong, whereas meaning earns credit only when every reference date is satisfied"
- **[Inference]** To empirically validate that our temporal relevance component influences version selection rather than merely improving semantic matching, we can adapt evaluation methodologies like TIDE's hard date gate, measuring improvements in strict accuracy (requiring both correct meaning and correct time) as evidence of true temporal retrieval capability. _(claim C022, confidence: medium)_
  - [2], p. 7 (direct support, verified) "The date gate separates correct meaning from correct time"
  - [2], p. 7 (direct support, verified) "partial score retains credit for correct dates even when the meaning is wrong, whereas meaning earns credit only when every reference date is satisfied"

### [Assumption] claims (5)

- **[Assumption]** Passage version timestamps are available or can be inferred from document metadata. _(claim C007, confidence: medium)_
- **[Assumption]** Temporal proximity between query target date and passage version correlates with relevance (more recent versions are more relevant for queries about current state, older versions for past states). _(claim C008, confidence: medium)_
- **[Assumption]** Standard retriever provides a semantic similarity score that can be combined with temporal weight. _(claim C009, confidence: medium)_
- **[Assumption]** Answer accuracy can be measured using Exact Match and F1 scores. _(claim C010, confidence: medium)_
- **[Assumption]** The benchmark can be constructed from publicly available regulatory corpora with version history. _(claim C011, confidence: medium)_

## Appendix B. Search Log

| Query | Sources (status: results) | Papers |
|---|---|---|
| temporal relevance retrieval open-domain question answering document versioning | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 10 |
| temporal document versioning question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 15 |
| temporal weighting function retrieval question answering | arxiv (ok: 1), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 10 |
| temporal decay weighting retrieval | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 19 |
| statute versioning question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 10 |
| temporal proximity semantic similarity retrieval evolving documents | arxiv (ok: 0), openalex (ok: 10), semantic_scholar (error: 0), crossref (ok: 10) | 20 |
| temporal semantic retrieval | arxiv (ok: 10), openalex (ok: 10), semantic_scholar (error: 0), crossref (ok: 10) | 28 |

## Appendix C. Investigation Log

Each step was chosen by the ResearchForge controller from the recorded research state.

| Step | Phase | Action | Why | Alternatives considered | Outcome | Information gain |
|---|---|---|---|---|---|---|
| 0 | INTAKE | INTAKE | Research idea received. | none | idea stored in the workspace | n/a |
| 1 | FORMALIZE | FORMALIZE | The idea has not been formalized into a testable research question. | none | +63 papers; +5 searches; +4 uncertainties; idea formalized | 3 |
| 2 | PLAN | PLAN | No investigation plan exists yet, so it is unclear what must be determined. | none | +3 uncertainties; investigation plan recorded | 1 |
| 3 | INVESTIGATE | READ | Retrieved papers have not been analyzed enough to judge overlap. | none | +6 analyses | 3 |
| 4 | SYNTHESIZE | SYNTHESIZE | Analyses exist but the field has not been mapped. | none | landscape recorded | 1 |
| 5 | CRITIQUE | CRITIQUE | The idea has not been challenged yet. | none | +11 claims; +6 verified claims; +2 uncertainties; critique recorded | 7 |
| 6 | UNCERTAINTY | SEARCH (U005: Are there existing retrieval methods that already combine temporal proximi) | Most valuable next step for high-importance overlap question U005: score 1.8 = importance 3 x expected gain 0.6 x relevance 1 x evidence deficiency 1 / cost 1. Next best: SEARCH on U009 (1.62). | SEARCH U009 (1.62); SEARCH U003 (1.26) | +46 papers; +2 searches; +1 claims; +1 verified claims; uncertainties updated: U005 | 3 |
| 7 | UNCERTAINTY | COMPARE (U009: How can we mitigate the confound where retrieval systems match semantic me) | Most valuable next step for high-importance confounder question U009: score 1.08 = importance 3 x expected gain 0.6 x relevance 0.9 x evidence deficiency 1 / cost 1.5. Next best: READ on U009 (1.012). | READ U009 (1.012); COMPARE U003 (0.84) | +5 claims; +5 verified claims; +2 uncertainties; uncertainties updated: U009 | 5 |
| 8 | UNCERTAINTY | COMPARE (U011: Given that retrieval systems tend to match meaning rather than time, what ) | Most valuable next step for high-importance validity question U011: score 1.44 = importance 3 x expected gain 0.8 x relevance 0.9 x evidence deficiency 1 / cost 1.5. Next best: COMPARE on U010 (1.28). | COMPARE U010 (1.28); COMPARE U003 (1.12) | +1 claims; +1 verified claims; uncertainties updated: U011 | 1 |
| 9 | UNCERTAINTY | COMPARE (U010: How can we empirically validate that a temporal relevance component actual) | Most valuable next step for high-importance evaluation question U010: score 1.03 = importance 3 x expected gain 0.644 x relevance 0.8 x evidence deficiency 1 / cost 1.5. Next best: COMPARE on U003 (0.902). | COMPARE U003 (0.902); COMPARE U006 (0.902) | +4 claims; +4 verified claims; uncertainties updated: U010; runtime note: phase exceeded 1200.0s and was stopped | 4 |
| 10 | UNCERTAINTY | COMPARE (U003: How to construct a benchmark of regulatory documents with version history ) | Most valuable next step for high-importance feasibility question U003: score 1.026 = importance 3 x expected gain 0.733 x relevance 0.7 x evidence deficiency 1 / cost 1.5. Next best: COMPARE on U006 (1.026). | COMPARE U006 (1.026); COMPARE U008 (0.88) | +2 claims; +2 verified claims; uncertainties updated: U003 | 2 |
| 11 | UNCERTAINTY | COMPARE (U006: What sources of versioned regulatory documents (statutes, policies, regula) | Most valuable next step for high-importance feasibility question U006: score 1.008 = importance 3 x expected gain 0.72 x relevance 0.7 x evidence deficiency 1 / cost 1.5. Next best: COMPARE on U008 (0.864). | COMPARE U008 (0.864); READ U006 (0.787) | +1 claims; +1 verified claims; uncertainties updated: U006 | 1 |
| 12 | FINALIZE | FINALIZE | Stopping: time budget reached (3600 s). | none | finalizing | n/a |
