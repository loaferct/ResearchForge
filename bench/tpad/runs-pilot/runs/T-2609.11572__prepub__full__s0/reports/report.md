# ResearchForge Investigation Report

Project `T-2609.11572__prepub__full__s0` · model `ollama-cloud/nemotron-3-super` · status **incomplete**

> Labels: **[Evidence]** directly supported by a verified quote from a retrieved source; **[Inference]** reasoning derived from cited evidence; **[Hypothesis]** proposed, not validated; **[Assumption]** taken as given without evidence; **[Experimental result]** observed in an executed experiment.

## 1. Executive Summary

**Investigated:** The reliability of open‑domain question answering drops sharply when source texts are continuously amended, as in statutes, policies, or regulations. In such settings each new amendment supersedes earlier clauses while retaining much of the original wording, creating a dense semantic overlap across successive versions. Existing time‑aware retrieval techniques treat each version as an isolated snapshot and therefore cannot distinguish which revision best matches a time‑specific query. We propose to develop a retrieval‑agnostic framework that enriches any standard document retriever with a temporal relevance component: the rank of a candidate passage will be adjusted according to the elapsed time between the query’s target date and the passage’s version timestamp, while still leveraging its semantic similarity to the query. To evaluate the approach, we will construct a benchmark comprising regulatory documents with overlapping revisions and time‑stamped queries, measuring how well the combined temporal‑semantic ranking improves answer accuracy.

**Research question:** Does adding a temporal relevance component to a standard document retriever improve answer accuracy in open-domain question answering over continuously amended regulatory texts compared to using semantic similarity alone?

**Literature investigated:** 101 papers retrieved from 5 searches (openalex: 44, crossref: 44, semantic_scholar: 10, arxiv: 3); 24 analyzed; 3 rated highly relevant.

**Assessment:** Promising but requires experimental validation. **[Inference]** While published work shows that key aspects of the idea exist in related forms (regulatory QA benchmarks with temporal reasoning, semantic-temporal balancing frameworks), the specific combination of a retrieval-agnostic temporal relevance component applied to any retriever for versioned regulatory document QA remains to be empirically validated. The idea addresses a real problem but requires demonstration that the proposed approach provides significant gains over existing methods when applied to this specific domain.

**Closest existing work:** IndiaFinBench: An Evaluation Benchmark for Large Language Model Performance on Indian Financial Regulatory Text (2026) [1]; Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval (2025) [2]

**Potential overlap:** Both our idea and existing work (IndiaFinBench, Re3) address temporal aspects of regulatory documents: IndiaFinBench creates benchmarks with temporal reasoning tasks for regulatory QA, while Re3 provides a framework for balancing semantic and temporal signals in retrieval. Our idea combines these threads by proposing a retrieval-agnostic temporal component for versioned regulatory document QA.

**Potential distinction:** Our idea specifically proposes a retrieval-agnostic temporal component (designed to work with any base retriever) for open-domain QA over versioned regulatory texts, focusing on using version timestamps to adjust passage rankings. While IndiaFinBench shows regulatory QA benchmarks with temporal reasoning exist, and Re3 shows semantic-temporal balancing exists, the specific application of a learnable or adaptive temporal relevance component to any retriever for regulatory QA benchmarking may still offer novelty if shown to be effective.

**Major risk:** Published work shows significant overlap with the proposed idea: IndiaFinBench (2026) already provides an evaluation benchmark for regulatory text that includes temporal reasoning tasks requiring models to identify which version of a rule was in force at a given time and addresses references chains of superseding circulars. Re3 (2025) proposes a unified framework that dynamically balances semantic and temporal information through a query-aware gating mechanism. Applying such temporal-semantic balancing to versioned regulatory documents may represent a straightforward extension rather than fundamental novelty.

**Research decision:** Insufficient evidence. **[Inference]** Basis: high-importance questions remain unresolved (U001, U002, U005, U006, U008, U009, U010, U011, U012, U013, U014, U015, U016, U018, U019, U020). This describes the state of the evidence, not the absolute value of the idea.

**Investigation:** 13 steps chosen from the research state; 20 uncertainties raised, 3 resolved, 17 still open or unresolved (Section 13, Appendix C).

**Stopped by a safety limit:** Stopping: time budget reached (3600 s). Conclusions below cover only what was recorded before the limit.

**Claim grounding:** 10/18 evidence and inference claims have at least one verified source.

**Incomplete phases:** gaps, modifications, experiments. Sections that depend on them are marked as not recorded.

This report does not declare the idea novel. Absence of a matching paper in these searches does not establish novelty; see Section 13.

## 2. Original Research Idea

> The reliability of open‑domain question answering drops sharply when source texts are continuously amended, as in statutes, policies, or regulations. In such settings each new amendment supersedes earlier clauses while retaining much of the original wording, creating a dense semantic overlap across successive versions. Existing time‑aware retrieval techniques treat each version as an isolated snapshot and therefore cannot distinguish which revision best matches a time‑specific query. We propose to develop a retrieval‑agnostic framework that enriches any standard document retriever with a temporal relevance component: the rank of a candidate passage will be adjusted according to the elapsed time between the query’s target date and the passage’s version timestamp, while still leveraging its semantic similarity to the query. To evaluate the approach, we will construct a benchmark comprising regulatory documents with overlapping revisions and time‑stamped queries, measuring how well the combined temporal‑semantic ranking improves answer accuracy.

## 3. Formalized Research Question

**Research question:** Does adding a temporal relevance component to a standard document retriever improve answer accuracy in open-domain question answering over continuously amended regulatory texts compared to using semantic similarity alone?

**Hypothesis:** **[Hypothesis]** Combining temporal relevance (based on time proximity) with semantic similarity will significantly improve answer accuracy (e.g., Exact Match or F1) in open-domain QA over continuously amended regulatory texts compared to using semantic similarity alone or existing time-aware retrieval techniques that treat versions independently.

| Aspect | Formalization |
|---|---|
| Problem | The reliability of open-domain question answering drops when source texts are continuously amended (e.g., statutes, policies, regulations) because each new amendment supersedes earlier clauses while retaining much of the original wording, creating dense semantic overlap across versions. Existing time-aware retrieval techniques treat each version as an isolated snapshot and therefore cannot distinguish which revision best matches a time-specific query. |
| Target domain | Open-domain question answering over continuously amended regulatory texts (statutes, policies, regulations). |
| Proposed method | A retrieval-agnostic framework that enriches any standard document retriever with a temporal relevance component. The rank of a candidate passage is adjusted according to the elapsed time between the query's target date and the passage's version timestamp (e.g., via a decaying function), while still leveraging its semantic similarity to the query from the base retriever. |
| Target system | Not recorded |
| Expected contribution | (1) A general framework for incorporating temporal dynamics into any document retriever for versioned collections; (2) A benchmark of regulatory documents with overlapping revisions and time-stamped queries to evaluate temporal-semantic retrieval approaches. |
| Independent variables | Retrieval method (baseline: semantic similarity only; proposed: temporal-semantic combination; other baselines: temporal-only, existing time-aware methods) |
| Dependent variables | Answer accuracy (Exact Match, F1) on the benchmark |
| Controls | Base retriever (e.g., BM25, DPR) kept constant when comparing methods, Benchmark dataset (regulatory documents with versions and timestamps), Query set |

**Assumptions**

- Each document version has a valid timestamp indicating when it was enacted or amended.
- Queries are associated with a target date (the time at which the question is asked).
- Semantic similarity (e.g., from a dense retriever) is a suitable baseline for relevance.
- The temporal relevance function can be modeled as a decaying function of time difference (e.g., exponential decay).
- The combination of temporal and semantic scores can be a simple weighted sum.

**Expected benefits / potential risks**

_None recorded._

**Ambiguities**

| Question | Resolution | Resolved by |
|---|---|---|
| What is the appropriate temporal relevance function (e.g., linear, exponential, step) for adjusting passage ranks based on time difference? | Literature suggests learned combinations (e.g., Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval, 2025) may outperform fixed functions, so this remains unresolved; we will treat it as a design choice to be evaluated. | literature |
| How should temporal and semantic scores be combined (e.g., weighted sum, product, learned)? | Recent work (e.g., Re3, 2025) learns to balance relevance and recency, indicating that a learned combination is promising; we will treat this as unresolved and plan to compare combination strategies. | literature |
| What baseline time-aware retrieval techniques exist for versioned documents to compare against? | Found work on time-travel phrase queries on versioned documents (Practical Index Framework for Efficient Time-Travel Phrase Queries on Versioned Documents, 2016) and time-aware random walk models for web archives; we will use these as baselines. | literature |
| Which metrics should be used to measure answer accuracy in the QA benchmark? | Standard QA metrics are Exact Match and F1; we will adopt these. | assumption |
| What regulatory documents should be used to construct the benchmark of overlapping revisions? | We assume publicly available corpora such as the US Code, EU regulations, or corporate policy histories; this remains an assumption to be verified during benchmark construction. | assumption |
| How to handle conflicting information across versions where an amendment supersedes a clause? | The idea assumes that the latest version's clause overrides earlier ones; we will treat this as a design principle for the temporal component (favoring newer versions for time-specific queries). | assumption |

## 4. Existing Research

Overlap values are heuristic signals assigned during analysis, not measurements of novelty.

| Paper | Relevance | Method | Problem / method / evaluation overlap | Read from |
|---|---|---|---|---|
| GRM: Generative Relevance Modeling Using Relevance-Aware Sample Estimation for Document Retrieval (2023) [3] | high | Generative Relevance Modeling (GRM) with Relevance-Aware Sample Estimation (RASE) that estimates relevance of generated documents via similarity to real documents in the collection, using a neural re-ranker to weight expansion terms. | 0.3 / 0.1 / 0.1 | full_text |
| Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval (2025) [2] | high | Re3 framework comprising Time Extraction, Time Encoding, and Time Enhancement modules, using a query-aware gating mechanism to dynamically balance semantic and temporal information during re-ranking. | 0.8 / 0.6 / 0.2 | full_text |
| A Question Answering System on Regulatory Documents (2018) [4] | high | Proposes a QA system specifically designed for regulatory documents, likely using semantic retrieval and possibly rule-based or machine learning approaches tailored to legal text. | 0.9 / 0.2 / 0.1 | abstract |
| Temporal Preference Optimization for Unsupervised Retrieval (2026) [5] | medium | TPOUR (Temporal Preference Optimization for Unsupervised Retriever) uses a novel training method Temporal Retrieval Preference Optimization (TRPO) that reinterprets preference learning in the temporal dimension to guide the retriever to favor temporally aligned documents, and generalizes to unseen t | 0.7 / 0.6 / 0.4 | full_text |
| Difficulty-Gated Fusion of Reasoning Views for Temporal Retrieval (2026) [6] | medium | Proposes difficulty-gated fusion of reasoning views for temporal retrieval, where query-specific weights are assigned to different query reformulations based on performance-prediction signatures. | 0.5 / 0.4 / 0.3 | abstract |
| Rank by Readability: Document Weighting for Information Retrieval (2010) [7] | medium | Proposes document weighting based on readability scores for information retrieval. | 0.1 / 0.1 / 0.1 | abstract |
| Extended structural relevance framework: a framework for evaluating structured document retrieval (2012) [8] | medium | Proposes an extended structural relevance framework for evaluating structured document retrieval. | 0.1 / 0.1 / 0.1 | abstract |
| Improving temporal question answering using temporal knowledge graph embedding (2023) [9] | medium | Uses temporal knowledge graph embeddings to improve temporal question answering. | 0.5 / 0.4 / 0.3 | abstract |
| Improved TFIDF weighting techniques in document Retrieval (2018) [10] | medium | Proposes improved TF-IDF weighting techniques for document retrieval. | 0.2 / 0.2 / 0.1 | abstract |
| Evaluating Temporal Information Understanding with Temporal Question Answering (2012) [11] | medium | Evaluates temporal information understanding using temporal question answering approaches. | 0.5 / 0.3 / 0.3 | abstract |
| Applying TF-IDF Weighting Method and BM-25 Algorithm in Myanmar News Retrieval (2025) [12] | medium | Applies TF-IDF weighting and BM-25 algorithm for Myanmar news retrieval. | 0.2 / 0.2 / 0.1 | abstract |
| Contextualized Offline Relevance Weighting for Efficient and Effective Neural Retrieval (2021) [13] | medium | Contextualized Offline Relevance Weighting (CORW) uses a powerful BERT ranker to weight neighbour documents collected by generated pseudo-queries for each document offline; online retrieval reduces to matching query to pseudo-query, making it efficient. | 0.2 / 0.1 / 0.1 | abstract |
| Phonetic confusion matrix based spoken document retrieval (2000) [14] | medium | Proposes a novel method for phonetic retrieval in the CueVideo system based on probabilistic term weighting using phone confusion data in a Bayesian framework to improve spoken document retrieval. | 0.1 / 0.1 / 0.1 | abstract |
| Temporal Question Answering in News Article Collections (2022) [15] | medium | Proposes temporal question answering approaches for news article collections. | 0.5 / 0.4 / 0.3 | abstract |
| ColBERT-PRF: Semantic Pseudo-Relevance Feedback for Dense Passage and Document Retrieval (2022) [16] | medium | Proposes ColBERT-PRF, a pseudo-relevance feedback technique for dense retrieval that enhances effectiveness by extracting representative feedback embeddings from pseudo-relevant documents and adding them to query representation. | 0.3 / 0.3 / 0.2 | abstract |
| Mitigating Semantic Bias in Multilingual Visual Document Retrieval via Language-Vision-Aware Late Interaction (2026) [17] | medium | Proposes Language-Vision-Aware Late Interaction (LVALI) to mitigate semantic bias in multilingual visual document retrieval via token-level weighting and visual alignment correction. | 0.1 / 0.1 / 0.1 | abstract |
| Document Retrieval by Relevance Terminological Logics (1995) [18] | medium | not stated in abstract | 0.1 / 0.1 / 0.1 | abstract |
| Metaknowledge Enhanced Open Domain Question Answering with Wiki Documents (2021) [19] | medium | Proposes a novel metaknowledge enhanced approach for open domain question answering: automatically extract metaknowledge and build metaknowledge network from Wiki documents, design a graph encoder GE4MK to model the network, and propose a metaknowledge enhanced graph reasoning model MEGr-Net for que | 0.4 / 0.2 / 0.1 | abstract |
| Error-tolerant question answering for spoken documents (2007) [20] | medium | not stated in abstract | 0.2 / 0.1 / 0.1 | abstract |
| Leveraging relevance cues for improved spoken document retrieval (2011) [21] | medium | not stated in abstract | 0.2 / 0.1 / 0.1 | abstract |
| Identification of LSA Data Retrieval Method and Temporal Graph for Document Retrieval (2025) [22] | medium | Uses LSA for dimensionality reduction and constructs a temporal graph based on citation and author occurrence to model document relevance over time. | 0.4 / 0.2 / 0.1 | abstract |
| Retrieval Augmented Generation for Question Answering in Financial Documents (2025) [23] | medium | not stated in abstract | 0.5 / 0.2 / 0.2 | abstract |
| On the Relevance of Query Expansion Using Parallel Corpora and Word Embeddings to Boost Text Document Retrieval Precision (2020) [24] | medium | Compares TF-IDF and BM25 weighting schemes, then expands queries using a comparable corpus (Wikipedia) and word embeddings to boost retrieval precision. | 0.1 / 0.1 / 0.1 | abstract |
| Question Answering over Linked Data with Vague Temporal Adverbials (2025) [25] | medium | not stated in abstract | 0.6 / 0.3 / 0.3 | abstract |

<details><summary>Full paper analyses</summary>

#### GRM: Generative Relevance Modeling Using Relevance-Aware Sample Estimation for Document Retrieval (2023) [3]

- **Problem:** Query expansion using Large Language Models (LLMs) can generate irrelevant content (hallucinations) that harms retrieval effectiveness.
- **Method:** Generative Relevance Modeling (GRM) with Relevance-Aware Sample Estimation (RASE) that estimates relevance of generated documents via similarity to real documents in the collection, using a neural re-ranker to weight expansion terms.
- **Main contribution:** GRM framework that improves query expansion effectiveness by reducing hallucination impact through relevance-aware weighting.
- **Key assumptions:** LLMs can generate documents covering subtopics of complex information needs.; Semantic similarity to real documents approximates the relevance of generated content.
- **Datasets / benchmarks:** TREC Robust04, CODEC, TREC Robust04, CODEC
- **Baselines:** BM25+RM3, GRF, GRF-News, SPLADE+RM3, CEQE, PCT+PRF
- **Metrics:** MAP, nDCG, Recall@1k
- **Results:** ["GRM improves MAP by 6-9% and Recall@1k by 2-4% over prior state-of-the-art expansion methods on TREC Robust04 and CODEC."]
- **Limitations:** Effectiveness depends on the quality of generated documents; requires a neural re-ranker for RASE.; Performance varies significantly across queries.; Reliance on external re-ranker adds complexity.
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** GRM focuses on query expansion via LLM-generated documents; our idea addresses temporal dynamics in versioned documents for QA, not query expansion. _(basis: not stated)_

#### Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval (2025) [2]

- **Problem:** Temporal Information Retrieval (TIR) requires balancing relevance (alignment with query's temporal constraints) and recency (preferring freshest version) which existing methods address in isolation.
- **Method:** Re3 framework comprising Time Extraction, Time Encoding, and Time Enhancement modules, using a query-aware gating mechanism to dynamically balance semantic and temporal information during re-ranking.
- **Main contribution:** (1) Re3, a unified lightweight framework for temporal-aware retrieval; (2) Re2Bench benchmark to disentangle relevance, recency, and their combination.
- **Key assumptions:** Explicit or reliably extractable timestamps are available for documents.; Semantic similarity and temporal signals can be combined via a learnable gate.
- **Datasets / benchmarks:** Re2Bench (including Re2-Rel from TSQA-Human, Re2-Rec from HoH, Re2-Hyb from NOAA), Re2Bench
- **Baselines:** BGE-M3 (semantic-only), tempRALM, TempRetriever, TSM
- **Metrics:** Recall@K, MRR, TimeVar@K, MFG@K
- **Results:** ["Re3 achieves state-of-the-art R@1 on all Re2Bench subsets: 0.920 on Re2-Rel, 0.649 on Re2-Rec, 0.742 on Re2-Hyb."]
- **Limitations:** Assumes explicit or reliably extractable timestamps.; Evaluation limited to three subsets; generalization to other domains (e.g., scientific literature, social media) needed.; Latency may increase with large candidate pools.
- **Future work:** Relax timestamp assumptions.; Optimize for low-latency retrieval.; Expand Re2Bench to broader domains and tasks.; Extend Re3 toward generative and multi-source datasets.; Add interpretability tools.
- **Code availability:** ["Available online at https://anonymous.4open.science/r/Re3-0C5A"]
- **Relation to idea:** Re3 focuses on general temporal IR benchmarks; our idea targets versioned regulatory documents for open-domain QA, proposing a retrieval-agnostic temporal relevance component adaptable to any retriever. _(basis: not stated)_

#### A Question Answering System on Regulatory Documents (2018) [4]

- **Problem:** Question answering over regulatory documents, which are often versioned and require up-to-date information.
- **Method:** Proposes a QA system specifically designed for regulatory documents, likely using semantic retrieval and possibly rule-based or machine learning approaches tailored to legal text.
- **Main contribution:** A question answering system tailored for regulatory documents, potentially incorporating document version handling.
- **Key assumptions:** Regulatory documents have a structure that can be exploited for QA.; Temporal aspects (versions) are important for regulatory QA.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** The paper focuses on a QA system for regulatory documents but does not explicitly address versioned texts with temporal retrieval; our idea adds a temporal relevance component to any retriever for versioned documents. _(basis: not stated)_

#### Temporal Preference Optimization for Unsupervised Retrieval (2026) [5]

- **Problem:** Unsupervised dense retrievers struggle to capture temporal relevance, retrieving semantically related but temporally misaligned documents when the collection spans multiple time periods, causing temporal ambiguity in queries like "Who is the president in 2019?".
- **Method:** TPOUR (Temporal Preference Optimization for Unsupervised Retriever) uses a novel training method Temporal Retrieval Preference Optimization (TRPO) that reinterprets preference learning in the temporal dimension to guide the retriever to favor temporally aligned documents, and generalizes to unseen time periods via interpolation in a learned time embedding.
- **Main contribution:** (1) TPOUR, a preference-based training method that injects temporal information into unsupervised dense retrievers via TRPO; (2) Demonstrates improved temporal alignment and generalization to unseen/intermediate time periods via time vector interpolation.
- **Key assumptions:** Temporal intent of queries can be detected (explicit or implicit).; Time vectors extracted from retrievers fine-tuned on specific periods can be interpolated for continuous temporal alignment.
- **Datasets / benchmarks:** SituatedQA (yearly temporal QA dataset, 2018-2021 subset), RealTimeQA (monthly temporal QA dataset), BEIR (general retrieval benchmark), SituatedQA, RealTimeQA, BEIR
- **Baselines:** Contriever, DPR, Nomic Embed v2 MoE, Qwen-Embedding-8B, Standard Retrievers, Temporal-Aware Retrievers, Mixture-of-TPOUR
- **Metrics:** nDCG@5, N@5, N@10
- **Results:** ["TPOUR Contriever improves average nDCG@5 by +4.04 (+12.15%) on explicit and +4.98 (+15.21%) on implicit queries compared to Qwen-Embedding-8B; outperforms both unsupervised and supervised baselines on temporal information retrieval; achieves better timestamp prediction and interpolation/extrapolation capabilities."]
- **Limitations:** Relies on temporally distributed document collections (e.g., Wikipedia dumps) for training; discrete temporal models limited in modeling continuous time; requires timestamp prediction or grounding for optimal performance.
- **Future work:** Relaxing requirement for temporally distributed corpora; further analysis of temporal grounding to enhance interpretability; time vector extrapolation for generalization beyond training period; applying TPOUR to other retrieval paradigms.
- **Code availability:** ["https://github.com/agwaBom/TPOUR"]
- **Relation to idea:** TPOUR focuses on improving temporal alignment in unsupervised dense retrievers via preference optimization and time embeddings for general retrieval tasks, while our idea proposes a retrieval-agnostic temporal relevance component that adjusts passage ranks based on version timestamp proximity for open-domain QA over versioned regulatory texts. _(basis: Based on abstract and full text analysis.)_

#### Difficulty-Gated Fusion of Reasoning Views for Temporal Retrieval (2026) [6]

- **Problem:** not stated in abstract
- **Method:** Proposes difficulty-gated fusion of reasoning views for temporal retrieval, where query-specific weights are assigned to different query reformulations based on performance-prediction signatures.
- **Main contribution:** Introduces difficulty-gated fusion that improves temporal retrieval performance across retrievers, with significant gains on weaker backbones.
- **Key assumptions:** Query difficulty can be predicted from score distribution signatures.; Fusing multiple reasoning views with adaptive weights improves temporal retrieval.
- **Datasets / benchmarks:** \textsc{Tempo} benchmark
- **Baselines:** Not recorded
- **Metrics:** nDCG@10
- **Results:** ["Strongest retrievers reach 0.297 and 0.303 nDCG@10; per-query gain significant under paired bootstrap (p<0.001)."]
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on adaptive fusion of reasoning views for temporal retrieval, while our idea focuses on temporal relevance weighting based on version timestamps for regulatory document QA. _(basis: Abstract describes difficulty-gated fusion method.)_

#### Rank by Readability: Document Weighting for Information Retrieval (2010) [7]

- **Problem:** not stated in abstract
- **Method:** Proposes document weighting based on readability scores for information retrieval.
- **Main contribution:** Introduces a readability-based weighting scheme for document retrieval.
- **Key assumptions:** Readability scores correlate with document usefulness or relevance.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on readability weighting for IR, unrelated to temporal dynamics or versioned documents. _(basis: Title suggests readability weighting.)_

#### Extended structural relevance framework: a framework for evaluating structured document retrieval (2012) [8]

- **Problem:** not stated in abstract
- **Method:** Proposes an extended structural relevance framework for evaluating structured document retrieval.
- **Main contribution:** Extends relevance evaluation frameworks to incorporate structural document features.
- **Key assumptions:** Structural aspects of documents affect relevance.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on structural relevance evaluation for document retrieval, unrelated to temporal versioning or QA. _(basis: Title indicates structural relevance framework.)_

#### Improving temporal question answering using temporal knowledge graph embedding (2023) [9]

- **Problem:** not stated in abstract
- **Method:** Uses temporal knowledge graph embeddings to improve temporal question answering.
- **Main contribution:** Applies temporal knowledge graph embeddings to enhance temporal QA performance.
- **Key assumptions:** Temporal knowledge graphs can capture temporal relations for QA.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on temporal knowledge graph embeddings for temporal QA, while our idea focuses on retrieval‑agnostic temporal relevance weighting for versioned regulatory documents in open‑domain QA. _(basis: Title suggests temporal KG embeddings for QA.)_

#### Improved TFIDF weighting techniques in document Retrieval (2018) [10]

- **Problem:** not stated in abstract
- **Method:** Proposes improved TF-IDF weighting techniques for document retrieval.
- **Main contribution:** Introduces improved TF-IDF weighting methods for better retrieval performance.
- **Key assumptions:** TF-IDF can be enhanced via alternative weighting schemes.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on TF-IDF weighting improvements for IR, unrelated to temporal versioning or regulatory QA. _(basis: Title indicates improved TF-IDF weighting.)_

#### Evaluating Temporal Information Understanding with Temporal Question Answering (2012) [11]

- **Problem:** not stated in abstract
- **Method:** Evaluates temporal information understanding using temporal question answering approaches.
- **Main contribution:** Provides evaluation frameworks for temporal QA systems.
- **Key assumptions:** Temporal QA can assess temporal information understanding.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on evaluation of temporal QA systems, while our idea proposes a temporal relevance component for retrieval in versioned regulatory document QA. _(basis: Title indicates evaluation of temporal information understanding with Temporal QA.)_

#### Applying TF-IDF Weighting Method and BM-25 Algorithm in Myanmar News Retrieval (2025) [12]

- **Problem:** not stated in abstract
- **Method:** Applies TF-IDF weighting and BM-25 algorithm for Myanmar news retrieval.
- **Main contribution:** Evaluates TF-IDF and BM-25 for improving relevance and precision in Myanmar news retrieval.
- **Key assumptions:** TF-IDF and BM-25 are effective for information retrieval in specific linguistic contexts.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on TF-IDF and BM-25 for Myanmar news retrieval, unrelated to temporal versioning or regulatory QA. _(basis: Title indicates TF-IDF and BM-25 application.)_

#### Contextualized Offline Relevance Weighting for Efficient and Effective Neural Retrieval (2021) [13]

- **Problem:** Online search latency is a major bottleneck when deploying large pre-trained language models (e.g., BERT) in retrieval applications.
- **Method:** Contextualized Offline Relevance Weighting (CORW) uses a powerful BERT ranker to weight neighbour documents collected by generated pseudo-queries for each document offline; online retrieval reduces to matching query to pseudo-query, making it efficient.
- **Main contribution:** CORW method that trades offline relevance weighting for online retrieval efficiency while maintaining effectiveness.
- **Key assumptions:** Generated pseudo-queries capture sufficient document context for relevance weighting.; Offline precomputation of neighbourhoods does not significantly degrade effectiveness.
- **Datasets / benchmarks:** MS MARCO (passage and document ranking), MS MARCO
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** ["Extensive experiments on MS MARCO demonstrate promising results in both online efficiency and effectiveness."]
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** CORW focuses on improving retrieval efficiency via offline pseudo-query weighting; our idea adds a temporal relevance component to adapt rankings based on version timestamps for QA over versioned texts. _(basis: not stated)_

#### Phonetic confusion matrix based spoken document retrieval (2000) [14]

- **Problem:** not stated in abstract
- **Method:** Proposes a novel method for phonetic retrieval in the CueVideo system based on probabilistic term weighting using phone confusion data in a Bayesian framework to improve spoken document retrieval.
- **Main contribution:** Introduces phonetic retrieval method that improves recall for out-of-vocabulary words and balances recall/precision for in-vocabulary words.
- **Key assumptions:** Phone confusion data can be used to improve term weighting for spoken document retrieval.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** ["Achieved average recall of 0.88 and average precision of 0.69 for out-of-vocabulary words; 17% improvement in recall over word-based retrieval for in-vocabulary words."]
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on phonetic retrieval for spoken documents, unrelated to temporal versioning or regulatory QA. _(basis: Abstract describes phonetic retrieval method.)_

#### Temporal Question Answering in News Article Collections (2022) [15]

- **Problem:** not stated in abstract
- **Method:** Proposes temporal question answering approaches for news article collections.
- **Main contribution:** Introduces methods for temporal QA over news collections.
- **Key assumptions:** Temporal aspects of news articles can be modeled for QA.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on temporal QA for news articles, while our idea focuses on versioned regulatory documents for open-domain QA with temporal relevance weighting. _(basis: Title suggests temporal QA in news.)_

#### ColBERT-PRF: Semantic Pseudo-Relevance Feedback for Dense Passage and Document Retrieval (2022) [16]

- **Problem:** not stated in abstract
- **Method:** Proposes ColBERT-PRF, a pseudo-relevance feedback technique for dense retrieval that enhances effectiveness by extracting representative feedback embeddings from pseudo-relevant documents and adding them to query representation.
- **Main contribution:** ColBERT-PRF improves MAP significantly on MSMARCO and TREC datasets; can be made more efficient with approximate scoring.
- **Key assumptions:** Pseudo-relevant documents contain useful feedback for query expansion.; Dense retrieval models like ColBERT can be improved with pseudo-relevance feedback.
- **Datasets / benchmarks:** MSMARCO passage ranking, MSMARCO document ranking, TREC Robust04 document ranking
- **Baselines:** ColBERT E2E model
- **Metrics:** MAP
- **Results:** ["MAP improved by up to 26% on TREC 2019 query set and 10% on TREC 2020 query set for passage ranking; up to 21% and 14% improvement for document ranking."]
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on pseudo-relevance feedback for dense retrieval, while our idea focuses on temporal relevance weighting based on version timestamps for regulatory document QA. _(basis: Abstract describes ColBERT-PRF method.)_

#### Mitigating Semantic Bias in Multilingual Visual Document Retrieval via Language-Vision-Aware Late Interaction (2026) [17]

- **Problem:** not stated in abstract
- **Method:** Proposes Language-Vision-Aware Late Interaction (LVALI) to mitigate semantic bias in multilingual visual document retrieval via token-level weighting and visual alignment correction.
- **Main contribution:** Introduces LVALI framework that improves robustness and cross-lingual consistency in multilingual visual document retrieval.
- **Key assumptions:** Semantic bias in multilingual VDR arises from heterogeneous token representations.; Language-aware weighting and visual alignment stability can mitigate bias.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on multilingual visual document retrieval bias mitigation, unrelated to temporal versioning or regulatory QA. _(basis: Title and abstract describe LVALI for VDR.)_

#### Document Retrieval by Relevance Terminological Logics (1995) [18]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** Not recorded
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on terminological logics for document retrieval, unrelated to temporal versioning or regulatory QA. _(basis: Title suggests relevance terminological logics.)_

#### Metaknowledge Enhanced Open Domain Question Answering with Wiki Documents (2021) [19]

- **Problem:** The commonly-used large-scale knowledge bases have been facing challenges in open domain question answering tasks which are caused by the loose knowledge association and weak structural logic of triplet-based knowledge.
- **Method:** Proposes a novel metaknowledge enhanced approach for open domain question answering: automatically extract metaknowledge and build metaknowledge network from Wiki documents, design a graph encoder GE4MK to model the network, and propose a metaknowledge enhanced graph reasoning model MEGr-Net for question answering that aggregates relational and neighboring interactions.
- **Main contribution:** (1) Metaknowledge enhanced approach for open domain QA; (2) Automatic extraction of metaknowledge from Wiki documents; (3) Graph encoder GE4MK for metaknowledge network modeling; (4) Metaknowledge enhanced graph reasoning model MEGr-Net for QA.
- **Key assumptions:** Metaknowledge extracted from Wiki documents can improve open domain question answering performance.; Graph reasoning models can effectively utilize metaknowledge for QA.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** "Experiments have proved the improvement of metaknowledge over main-stream triplet-based knowledge."
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on metaknowledge extraction from Wiki documents for general open-domain QA, while our idea focuses on temporal relevance weighting based on version timestamps for regulatory document QA. _(basis: Abstract describes metaknowledge enhanced QA approach.)_

#### Error-tolerant question answering for spoken documents (2007) [20]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** Not recorded
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on error-tolerant question answering for spoken documents, unrelated to temporal versioning or regulatory QA. _(basis: Title indicates error-tolerant QA for spoken documents.)_

#### Leveraging relevance cues for improved spoken document retrieval (2011) [21]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** Not recorded
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on leveraging relevance cues for spoken document retrieval, unrelated to temporal versioning or regulatory QA. _(basis: Title indicates relevance cues for spoken document retrieval.)_

#### Identification of LSA Data Retrieval Method and Temporal Graph for Document Retrieval (2025) [22]

- **Problem:** Identifying effective information retrieval methods for document retrieval using latent semantic analysis (LSA) and temporal graph approaches.
- **Method:** Uses LSA for dimensionality reduction and constructs a temporal graph based on citation and author occurrence to model document relevance over time.
- **Main contribution:** Demonstrates that LSA-based retrieval enhanced with temporal graph outperforms baseline keyword matching in expert finding tasks.
- **Key assumptions:** Temporal relationships captured by citation/author occurrence reflect document relevance.; LSA effectively captures semantic similarity for retrieval.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** precision@5 (p@5), mean average precision (MAP), mean reciprocal rank (MRR)
- **Results:** ["Achieves p@5 = 0.895, MAP = 0.839, MRR = 0.909, outperforming the baseline model."]
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** The paper uses temporal graph based on citation/author for expert finding; our idea focuses on versioned regulatory documents and uses temporal proximity between query date and version timestamp to adjust retrieval rankings. _(basis: not stated)_

#### Retrieval Augmented Generation for Question Answering in Financial Documents (2025) [23]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** Not recorded
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on retrieval-augmented generation for question answering in financial documents, while our idea focuses on temporal relevance weighting based on version timestamps for regulatory document QA. _(basis: Title indicates RAG for financial document QA.)_

#### On the Relevance of Query Expansion Using Parallel Corpora and Word Embeddings to Boost Text Document Retrieval Precision (2020) [24]

- **Problem:** Improving precision in text document retrieval via effective query expansion techniques.
- **Method:** Compares TF-IDF and BM25 weighting schemes, then expands queries using a comparable corpus (Wikipedia) and word embeddings to boost retrieval precision.
- **Main contribution:** Demonstrates that query expansion using word embeddings yields higher precision than TF-IDF and BM25 baselines.
- **Key assumptions:** Word embeddings capture semantic similarity useful for query expansion.; A comparable corpus like Wikipedia provides relevant expansion terms.
- **Datasets / benchmarks:** Not recorded
- **Baselines:** TF-IDF, BM25
- **Metrics:** precision
- **Results:** ["Query expansion with word embeddings achieves higher precision rates and retrieves more accurate documents compared to TF-IDF and BM25 alone."]
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** The paper focuses on query expansion with embeddings for general IR; our idea introduces a temporal relevance component to adjust rankings based on document version timestamps for QA over versioned regulatory texts. _(basis: not stated)_

#### Question Answering over Linked Data with Vague Temporal Adverbials (2025) [25]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** Not recorded
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** []
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** []
- **Relation to idea:** Focuses on question answering over linked data with vague temporal adverbials, which is related to temporal QA but not specifically on versioned regulatory documents or using temporal relevance weighting based on version timestamps. _(basis: Title indicates QA with vague temporal adverbials.)_

</details>

## 5. Research Landscape

```text
Temporal Information Retrieval for Versioned Texts in Question Answering
├── Query Expansion Techniques  [3] [24]
├── Temporal Information Retrieval  [2]
├── Efficient Retrieval  [13]
├── Temporal Graph / Expert Finding  [22]
└── Question Answering over Regulatory Documents  [4]
```

**Where the idea fits:** **[Inference]** Temporal Information Retrieval (specifically applied to versioned regulatory documents for open-domain QA)

**Dominant approaches**

- Learned gating mechanisms to dynamically balance semantic and temporal signals (e.g., Re3)
- Temporal graph modeling based on document relationships over time
- Offline precomputation of relevance weights for efficient retrieval
- Query expansion using embeddings or generated text

**Common assumptions**

- Each document version has a valid timestamp indicating enactment or amendment time.
- Queries are associated with a target date (the time the question is asked).
- Semantic similarity (e.g., from dense retrievers) provides a useful baseline for relevance.
- Temporal relevance can be modeled as a function of time difference (e.g., decaying function).
- Combining temporal and semantic signals can improve retrieval for time-sensitive queries.

**Common datasets**

- MS MARCO (passage and document ranking)
- TREC Robust04
- CODEC
- Re2Bench (Relevance & Recency Benchmark)

**Common benchmarks**

- MS MARCO
- TREC Robust04
- CODEC
- Re2Bench

**Common metrics**

- Recall@K
- Mean Reciprocal Rank (MRR)
- Mean Average Precision (MAP)
- Normalized Discounted Cumulative Gain (nDCG)
- Precision@K

**Underexplored combinations**

- **[Hypothesis]** Applying learned temporal relevance gating (like Re3) to versioned regulatory documents for QA
- **[Hypothesis]** Combining temporal graph methods with semantic retrieval for expert finding over regulatory versions
- **[Hypothesis]** Integrating query expansion with temporal relevance for handling hallucinations in versioned text QA
- **[Hypothesis]** Using offline precomputation (like CORW) to enable efficient temporal-semantic retrieval over large versioned corpora

**Limitations repeated across papers**

- Assumes explicit or reliably extractable timestamps, which may not hold in all settings. [2]
- Evaluation limited to specific domains (e.g., web, news), lacking generalization to other areas like scientific literature or regulatory texts. [2], [3]
- Reliance on external components (e.g., neural re-rankers) adds complexity and latency. [3]
- Latency may increase with large candidate pools when using re-ranking or complex temporal modeling. [2]

**Contradictions between papers**

_None recorded._

## 6. Closest Existing Work

**[Inference]** IndiaFinBench (2026) demonstrates existing work creating benchmarks for regulatory documents with temporal reasoning tasks that require identifying which version of a rule is in force at a given time, directly addressing the supersession problem. Re3 (2025) provides a framework for dynamically balancing semantic and temporal information. Together, they show that key aspects of our idea (regulatory-focused QA with temporal reasoning and semantic-temporal balancing) already exist, though not combined in exactly the same way.

- IndiaFinBench: An Evaluation Benchmark for Large Language Model Performance on Indian Financial Regulatory Text (2026) [1] (not analyzed in detail)
- Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval (2025) [2]: Re3 focuses on general temporal IR benchmarks; our idea targets versioned regulatory documents for open-domain QA, proposing a retrieval-agnostic temporal relevance component adaptable to any retriever.

## 7. Potential Overlap

**Overlap:** **[Inference]** Both our idea and existing work (IndiaFinBench, Re3) address temporal aspects of regulatory documents: IndiaFinBench creates benchmarks with temporal reasoning tasks for regulatory QA, while Re3 provides a framework for balancing semantic and temporal signals in retrieval. Our idea combines these threads by proposing a retrieval-agnostic temporal component for versioned regulatory document QA.

**Potential distinction:** **[Inference]** Our idea specifically proposes a retrieval-agnostic temporal component (designed to work with any base retriever) for open-domain QA over versioned regulatory texts, focusing on using version timestamps to adjust passage rankings. While IndiaFinBench shows regulatory QA benchmarks with temporal reasoning exist, and Re3 shows semantic-temporal balancing exists, the specific application of a learnable or adaptive temporal relevance component to any retriever for regulatory QA benchmarking may still offer novelty if shown to be effective.

**Novelty questions**

- **Has essentially the same idea been proposed under different terminology?** (high severity): IndiaFinBench (2026) demonstrates existing work creating regulatory QA benchmarks with temporal reasoning tasks that require identifying which version of a rule is in force at a given time. Re3 (2025) shows existing frameworks for dynamically balancing semantic and temporal information through query-aware gating mechanisms. _([1], [2]; [Evidence] claim C012; [Evidence] claim C013)_

## 8. Potential Research Gap

_Not recorded: this phase did not produce the required records._

## 9. Critique

| | |
|---|---|
| Strongest argument FOR | The idea addresses a significant problem: open-domain QA performance degrades when source texts are continuously amended (e.g., regulations), as existing time-aware retrieval treats versions as isolated snapshots and cannot determine which revision is valid for a time-specific query. Recent work like IndiaFinBench (2026) demonstrates that versioned regulatory QA benchmarks with temporal reasoning tasks are feasible and valuable, supporting the need for approaches that handle regulatory supersession. |
| Strongest argument AGAINST | Published work shows significant overlap with the proposed idea: IndiaFinBench (2026) already provides an evaluation benchmark for regulatory text that includes temporal reasoning tasks requiring models to identify which version of a rule was in force at a given time and addresses references chains of superseding circulars. Re3 (2025) proposes a unified framework that dynamically balances semantic and temporal information through a query-aware gating mechanism. Applying such temporal-semantic balancing to versioned regulatory documents may represent a straightforward extension rather than fundamental novelty. |
| Most important unresolved question | What specific novelty does our retrieval-agnostic temporal relevance component offer beyond existing approaches like Re3 when applied to versioned regulatory documents for open-domain QA, particularly regarding handling of supersession mechanisms, timestamp reliability in real regulatory corpora, and experimental isolation of temporal modeling effects from semantic matching improvements? |
| Most dangerous experimental confounder | Observed improvements in answer accuracy could be confounded by enhancements to semantic matching or query formulation rather than the temporal modeling itself, especially when using learned combination mechanisms that may absorb semantic improvements, making it difficult to isolate the true contribution of the temporal component. |
| Closest existing work | [1], [2] |
| Potential contribution | **[Hypothesis]** (1) A retrieval-agnostic framework that incorporates temporal dynamics based on version timestamps into any document retriever for regulatory texts; (2) Empirical validation of whether such temporal-semantic combination provides significant gains over existing baselines for open-domain QA over versioned regulatory texts; (3) Potential insights into optimal combination strategies and handling of supersession in regulatory contexts. |

**Technical validity**

- **What are the main technical risks or limitations in the proposed approach?** (high severity): Re3 assumes explicit or reliably extractable timestamps which may not hold in all settings, and its query-aware gating mechanism makes it challenging to isolate temporal modeling contributions from learned semantic weighting adjustments. _([2]; [Evidence] claim C003; [Inference] claim C006)_

**Experimental validity**

- **What confounders could produce the claimed result, and how are they addressed?** (high severity): Improvements in temporal-aware retrieval could be confounded by enhancements to semantic matching rather than temporal modeling, especially when using learned combinations that may absorb semantic improvements, posing challenges for ablation studies. _([2]; [Inference] claim C004; [Inference] claim C006)_

**Practicality**

- **Is the approach feasible given typical resources and constraints?** (moderate severity): The approach assumes document versions have valid timestamps, queries have target dates, semantic similarity is a suitable baseline, temporal relevance can be modeled as a decaying function, and scores can be combined via weighted sum - all of which may need empirical validation in the regulatory domain. _([Assumption] claim C007; [Assumption] claim C008; [Assumption] claim C009; [Assumption] claim C010; [Assumption] claim C011)_

## 10. Proposed Modifications

_Not recorded: this phase did not produce the required records._

## 11. Recommended Experimental Design

_Not recorded: this phase did not produce the required records._

## 12. Experimental Results

Experiment not performed. The designs in Section 11 are untested.

## 13. Remaining Uncertainty

- Literature coverage: searched 5 queries over arxiv, crossref, openalex, semantic_scholar. Work outside these queries and sources, very recent preprints, and non-English work may be missing; the absence of matching work here does not establish novelty.
- Some source requests failed and their results are missing: semantic_scholar (api.semanticscholar.org failed after 5 attempts (HTTP 429)).
- Metadata warning for Eukaryotic regulatory RNAs: an answer to the ‘genome complexity’ conundrum (2007) [26]: abstract (from openalex) never mentions 'Eukaryotic regulatory RNAs'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for The COMET Handbook: version 1.0 (2017) [27]: abstract (from openalex) never mentions 'The COMET Handbook'; it may belong to another work. Its abstract was not accepted as direct evidence.
- 21 of 24 analyses are based on abstracts only.
- Unresolved question: What specific novelty does our retrieval-agnostic temporal relevance component offer beyond existing approaches like Re3 when applied to versioned regulatory documents for open-domain QA, particularly regarding handling of supersession mechanisms, timestamp reliability in real regulatory corpora, and experimental isolation of temporal modeling effects from semantic matching improvements?
- Ambiguity (assumption): Which metrics should be used to measure answer accuracy in the QA benchmark?; assumed: Standard QA metrics are Exact Match and F1; we will adopt these.
- Ambiguity (assumption): What regulatory documents should be used to construct the benchmark of overlapping revisions?; assumed: We assume publicly available corpora such as the US Code, EU regulations, or corporate policy histories; this remains an assumption to be verified during benchmark construction.
- Ambiguity (assumption): How to handle conflicting information across versions where an amendment supersedes a clause?; assumed: The idea assumes that the latest version's clause overrides earlier ones; we will treat this as a design principle for the temporal component (favoring newer versions for time-specific queries).
- Claims without a verified source: C004, C016, C018, C019, C020, C021, C022, C023.
- Phases that did not complete: gaps, modifications, experiments.
- No hypothesis in this report has been tested experimentally.

**Uncertainty ledger**

| Id | Question | Category | Importance | Status | Evidence for / against | Resolution |
|---|---|---|---|---|---|---|
| U001 | What is the appropriate temporal relevance function (e.g., linear, exponential, step) for adjusting passage ranks based on time difference in the context of versioned regulatory texts? | validity | high | partially resolved | [2] / none | Literature shows learned combinations (like Re3's query-aware gating) may outperform fixed functions, but optimal approach for versioned regulatory QA remains unclear. |
| U002 | How should temporal and semantic scores be combined (e.g., weighted sum, product, learned) to optimize retrieval performance for time-specific queries over versioned documents? | validity | high | partially resolved | [2] / none | Re3 demonstrates that a learned query-aware gating mechanism can effectively balance semantic and temporal information, but optimal combination strategy for versioned regulatory QA needs investigation. |
| U005 | What regulatory documents should be used to construct the benchmark of overlapping revisions with time-stamped queries? | feasibility | high | open | none / none | Not recorded |
| U006 | How to handle conflicting information across versions where an amendment supersedes a clause, especially when the temporal component may still retrieve outdated versions? | confounder | high | open | none / none | The idea assumes latest version's clause overrides earlier ones, but we need to verify how supersession works in different regulatory systems and whether temporal proximity alone correctly captures validity. |
| U008 | Which existing time-aware retrieval techniques for versioned documents (e.g., time-travel phrase queries, temporal indexing) are the strongest baselines, and how does our proposed temporal-semantic combination differ in mechanism and assumptions? | overlap | high | partially resolved | [2], [22], [13] / none | The strongest baselines for time-aware retrieval of versioned documents include Re3 (a retrieval-agnostic framework balancing semantic and temporal signals), time-travel phrase query frameworks (focused on efficient indexing), and temporal random walk models (for importance scoring). Our idea differs by specifically targeting open-domain QA over versioned regulatory documents, focusing on the semantic overlap from superseding amendments, and aiming to construct a regulatory-specific benchmark with time-stamped queries. |
| U009 | What is the most effective way to combine temporal relevance and semantic similarity scores (e.g., learned weighting, gating, product) for improving retrieval accuracy in versioned document QA? | validity | high | open | none / none | Not recorded |
| U010 | Is it feasible to construct a benchmark of regulatory documents (e.g., US Code, EU regulations) with version histories, timestamps, and time-stamped question-answer pairs that reflect real-world information needs? | feasibility | high | open | none / none | Not recorded |
| U011 | What specific sources of versioned regulatory texts (e.g., US Code, EU regulations, national legislation) are publicly available with sufficient version history and timestamps to construct a meaningful benchmark for temporal-semantic QA evaluation? | feasibility | high | open | none / none | Not recorded |
| U012 | Does applying a temporal-semantic balance mechanism like Re3's query-aware gating to versioned regulatory documents for open-domain QA constitute a sufficient novelty, or is it a straightforward extension of existing temporal IR methods? | novelty | high | partially resolved | [1], [2] / none | Published work shows that key aspects exist: IndiaFinBench (2026) demonstrates regulatory QA benchmarks with temporal reasoning tasks addressing supersession, and Re3 (2025) shows semantic-temporal balancing frameworks. The novelty may lie in the specific combination and empirical validation for open-domain QA. |
| U013 | To what extent do versioned regulatory documents (statutes, codes, regulations) provide reliable, extractable timestamps for each version that can be used for temporal relevance modeling, and how do we handle cases where timestamps are missing, ambiguous, or follow complex versioning schemes? | validity | high | open | none / none | Not recorded |
| U014 | How can we design experiments to isolate the effect of temporal relevance modeling from confounding factors such as semantic matching improvements, query formulation changes, or retrieval strategy alterations when evaluating our temporal-semantic framework for regulatory QA? | validity | high | open | none / none | Not recorded |
| U015 | How feasible is it to construct a benchmark of regulatory documents with version histories, reliable timestamps, and time-stamped question-answer pairs that reflect realistic information needs across different time points, and what resources would be required for annotation and validation? | feasibility | high | open | none / none | Not recorded |
| U016 | Does adding a temporal relevance component to a standard document retriever provide statistically significant improvements in answer accuracy (Exact Match/F1) for open-domain QA over versioned regulatory texts compared to strong baselines including semantic-only retrievers and existing temporal-aware methods? | evaluation | high | open | none / none | Not recorded |
| U018 | The conclusion behind U017 was weakened by contradicting work; how should the direction change? (raised by ResearchForge) | direction | high | open | none / none | Not recorded |
| U019 | Does Re3's query-aware gating mechanism effectively handle the specific challenge of versioned regulatory documents where amendments supersede earlier clauses (creating semantic overlap), or is a specialized temporal relevance function needed for this use case? | validity | high | open | none / none | Not recorded |
| U020 | What are the most appropriate baseline methods for evaluating a temporal-semantic retrieval framework for open-domain QA over versioned regulatory documents, considering both general temporal IR approaches (like Re3) and domain-specific regulatory QA approaches? | overlap | high | open | none / none | Not recorded |
| U003 | What baseline time-aware retrieval techniques exist for versioned documents that we should compare against in our evaluation? | overlap | medium | partially resolved | [2], [22] / none | Identified baselines include Re3 (learned gating), tempRALM, TempRetriever, TSM (heuristic fusion), and temporal graph-based methods. Need to determine which are most appropriate for versioned regulatory QA comparison. |
| U007 | Does a retrieval-agnostic framework that combines temporal relevance with semantic similarity for versioned documents already exist under different terminology (e.g., temporal relevance models, time-aware retrievers)? | novelty | high | resolved | [2] / none | Yes, a retrieval-agnostic framework that combines temporal relevance with semantic similarity for versioned documents already exists: Re3 (2025) is explicitly described as a "universal, plug-and-play, and lightweight framework for TIR" that "can be seamlessly integrated with existing dense retrievers" and is designed to be a "lightweight, plug-and-play retriever" that dynamically balances semantic and temporal information through a query-aware gating mechanism. |
| U017 | Does published work contradict the current assessment: Our idea specifically targets versioned regulatory documents for open-domain question answering (not general IR), focuses on the problem where amendments supersede earlier clauses creating semantic overlap, proposes a retrieval-agnostic temporal component designed to work with any base retriever, and aims to construct a domain-specific benchmark with regulatory texts and time-stamped queries.? (raised by ResearchForge) | contradiction | high | resolved (weakened) | none / [1], [2] | Published work shows that aspects of the idea are not novel: IndiaFinBench (2026) demonstrates existing work targeting versioned regulatory documents for QA-related tasks, addressing the supersession problem, and constructing domain-specific benchmarks with temporal reasoning tasks. Re3 (2025) shows existing frameworks for dynamically balancing semantic and temporal information. However, the specific combination of a retrieval-agnostic temporal component for open-domain QA over versioned regulatory texts may still offer novelty. |
| U004 | Which metrics should be used to measure answer accuracy in the QA benchmark for evaluating temporal-semantic retrieval? | evaluation | low | resolved | none / none | Standard QA metrics Exact Match and F1 are appropriate for measuring answer accuracy in the benchmark, supplemented by retrieval metrics like Recall@k and MRR to evaluate the retrieval component. |

## 14. Suggested Next Steps

1. Resolve: What specific novelty does our retrieval-agnostic temporal relevance component offer beyond existing approaches like Re3 when applied to versioned regulatory documents for open-domain QA, particularly regarding handling of supersession mechanisms, timestamp reliability in real regulatory corpora, and experimental isolation of temporal modeling effects from semantic matching improvements?
2. Design a control for the confounder: Observed improvements in answer accuracy could be confounded by enhancements to semantic matching or query formulation rather than the temporal modeling itself, especially when using learned combination mechanisms that may absorb semantic improvements, making it difficult to isolate the true contribution of the temporal component.
3. Search for work newer than the most recent retrieved paper (2026) before claiming a distinction.

## 15. References

1. Rajveer Singh Pall. **IndiaFinBench: An Evaluation Benchmark for Large Language Model Performance on Indian Financial Regulatory Text**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2604.19298> (id `arxiv:2604.19298`; retrieved from arxiv)
2. Jiawei Cao, Jie Ouyang, Zhaomeng Zhou et al.. **Re3: Learning to Balance Relevance & Recency for Temporal Information Retrieval**. _arXiv.org_, 2025. <https://www.semanticscholar.org/paper/663074e8a1dcdf751c7d517f55f50c1d629376e0> doi:10.48550/arxiv.2509.01306 (id `arxiv:2509.01306`; retrieved from semantic_scholar; 0 citations per semantic_scholar)
3. Iain Mackie, Ivan Sekulic, Shubham Chatterjee et al.. **GRM: Generative Relevance Modeling Using Relevance-Aware Sample Estimation for Document Retrieval**. _arXiv.org_, 2023. <https://www.semanticscholar.org/paper/0b8eaf52001bafa01dda642a0358ce3355318bc9> doi:10.48550/arxiv.2306.09938 (id `arxiv:2306.09938`; retrieved from semantic_scholar; 3 citations per semantic_scholar)
4. Collarana Diego, Heuss Timm, Lehmann Jens et al.. **A Question Answering System on Regulatory Documents**. _Frontiers in Artificial Intelligence and Applications_, 2018. <https://doi.org/10.3233/978-1-61499-935-5-41> (id `doi:10.3233/978-1-61499-935-5-41`; retrieved from crossref; 7 citations per crossref)
5. Hyunjin Kim, Jaejun Shim, Young Jin Kim et al.. **Temporal Preference Optimization for Unsupervised Retrieval**. _arXiv.org_, 2026. <https://www.semanticscholar.org/paper/3b5514cd6f7f9307dea5bd922db840ce3d5915a2> doi:10.48550/arxiv.2606.17664 (id `arxiv:2606.17664`; retrieved from semantic_scholar; 0 citations per semantic_scholar)
6. Jamie Holdcroft, Abdelrahman Abdallah, Adam Jatowt. **Difficulty-Gated Fusion of Reasoning Views for Temporal Retrieval**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2608.08940> (id `arxiv:2608.08940`; retrieved from arxiv)
7. Neil Newbold, Harry McLaughlin, Lee Gillam. **Rank by Readability: Document Weighting for Information Retrieval**. _Lecture Notes in Computer Science_, 2010. <https://doi.org/10.1007/978-3-642-13084-7_3> (id `doi:10.1007/978-3-642-13084-7_3`; retrieved from crossref; 4 citations per crossref)
8. M. Sadek Ali, Mariano Consens, Mounia Lalmas. **Extended structural relevance framework: a framework for evaluating structured document retrieval**. _Information Retrieval_, 2012. <https://doi.org/10.1007/s10791-012-9192-1> (id `doi:10.1007/s10791-012-9192-1`; retrieved from crossref; 3 citations per crossref)
9. Jiabao Chen, Yongquan Fan. **Improving temporal question answering using temporal knowledge graph embedding**. _2023 4th International Conference on Computer Engineering and Application (ICCEA)_, 2023. <https://doi.org/10.1109/iccea58433.2023.10135342> (id `doi:10.1109/iccea58433.2023.10135342`; retrieved from crossref; 1 citations per crossref)
10. Fadi Yamout, Rachad Lakkis. **Improved TFIDF weighting techniques in document Retrieval**. _2018 Thirteenth International Conference on Digital Information Management (ICDIM)_, 2018. <https://doi.org/10.1109/icdim.2018.8847156> (id `doi:10.1109/icdim.2018.8847156`; retrieved from crossref; 11 citations per crossref)
11. Naushad UzZaman, Hector Llorens, James Allen. **Evaluating Temporal Information Understanding with Temporal Question Answering**. _2012 IEEE Sixth International Conference on Semantic Computing_, 2012. <https://doi.org/10.1109/icsc.2012.34> (id `doi:10.1109/icsc.2012.34`; retrieved from crossref; 7 citations per crossref)
12. Mayme Moon Zin, Myo Thida, S. Phithakkitnukoon. **Applying TF-IDF Weighting Method and BM-25 Algorithm in Myanmar News Retrieval**. _2025 20th International Joint Symposium on Artificial Intelligence and Natural Language Processing (iSAI-NLP)_, 2025. <https://www.semanticscholar.org/paper/4faff61455a9197f3626b5feda9da18a9c0868e1> doi:10.1109/isai-nlp66160.2025.11320529 (id `doi:10.1109/isai-nlp66160.2025.11320529`; retrieved from semantic_scholar; 1 citations per semantic_scholar)
13. Xuanang Chen, Ben He, Kai Hui et al.. **Contextualized Offline Relevance Weighting for Efficient and Effective Neural Retrieval**. _Annual International ACM SIGIR Conference on Research and Development in Information Retrieval_, 2021. <https://www.semanticscholar.org/paper/9555077e9b2191d9ada157ed31aa976258924009> doi:10.1145/3404835.3463073 (id `doi:10.1145/3404835.3463073`; retrieved from semantic_scholar; 7 citations per semantic_scholar)
14. Savitha Srinivasan, Dragutin Petković. **Phonetic confusion matrix based spoken document retrieval**. 2000. <https://doi.org/10.1145/345508.345552> (id `doi:10.1145/345508.345552`; retrieved from openalex; 77 citations per openalex)
15. Adam Jatowt. **Temporal Question Answering in News Article Collections**. _Companion Proceedings of the Web Conference 2022_, 2022. <https://doi.org/10.1145/3487553.3526023> (id `doi:10.1145/3487553.3526023`; retrieved from crossref; 3 citations per crossref)
16. Xiao Wang, Craig Macdonald, N. Tonellotto et al.. **ColBERT-PRF: Semantic Pseudo-Relevance Feedback for Dense Passage and Document Retrieval**. _ACM Transactions on the Web_, 2022. <https://www.semanticscholar.org/paper/5537feedc97256e81c6f1af66664dbcd19621d11> doi:10.1145/3572405 (id `doi:10.1145/3572405`; retrieved from semantic_scholar; 83 citations per semantic_scholar)
17. Hao-Wei Li, Hao-Jie Wu, Jie Bao et al.. **Mitigating Semantic Bias in Multilingual Visual Document Retrieval via Language-Vision-Aware Late Interaction**. _International Conference on Multimedia Retrieval_, 2026. <https://www.semanticscholar.org/paper/47137a5aff2f93d10ca13d3227d69433102051d9> doi:10.1145/3805622.3810802 (id `doi:10.1145/3805622.3810802`; retrieved from semantic_scholar; 0 citations per semantic_scholar)
18. Umberto Straccia. **Document Retrieval by Relevance Terminological Logics**. _Electronic Workshops in Computing_, 1995. <https://doi.org/10.14236/ewic/miro1995.16> (id `doi:10.14236/ewic/miro1995.16`; retrieved from crossref; 1 citations per crossref)
19. Shukan Liu, Ruilin Xu, Li Duan et al.. **Metaknowledge Enhanced Open Domain Question Answering with Wiki Documents**. _Sensors_, 2021. <https://doi.org/10.20944/preprints202110.0220.v1> (id `doi:10.20944/preprints202110.0220.v1`; retrieved from crossref; 0 citations per crossref)
20. Tomoyosi Akiba, Hirofumi Tsujimura. **Error-tolerant question answering for spoken documents**. _Interspeech 2007_, 2007. <https://doi.org/10.21437/interspeech.2007-177> (id `doi:10.21437/interspeech.2007-177`; retrieved from crossref; 0 citations per crossref)
21. Pei-Ning Chen, Kuan-Yu Chen, Berlin Chen. **Leveraging relevance cues for improved spoken document retrieval**. _Interspeech 2011_, 2011. <https://doi.org/10.21437/interspeech.2011-373> (id `doi:10.21437/interspeech.2011-373`; retrieved from crossref; 3 citations per crossref)
22. Shahla Rezvani, N. Naghshineh, Ahmad Khalilijafarabad. **Identification of LSA Data Retrieval Method and Temporal Graph for Document Retrieval**. _Tehnički glasnik_, 2025. <https://www.semanticscholar.org/paper/7c79931e45b9e678480f53b11ba2d7ee05e9e269> doi:10.31803/tg-20230715000112 (id `doi:10.31803/tg-20230715000112`; retrieved from semantic_scholar; 1 citations per semantic_scholar)
23. S. Sharon Benita, V. Srividhya. **Retrieval Augmented Generation for Question Answering in Financial Documents**. _Journal of Advanced Database Management & Systems_, 2025. <https://doi.org/10.37591/joadms.v12i02.226214> (id `doi:10.37591/joadms.v12i02.226214`; retrieved from crossref; 0 citations per crossref)
24. Alaidine Ben Ayed, Ismaïl Biskri. **On the Relevance of Query Expansion Using Parallel Corpora and Word Embeddings to Boost Text Document Retrieval Precision**. 2020. <https://www.semanticscholar.org/paper/2c81b8f7eb2aeb556a2e3609bbeff4570465fb52> doi:10.5121/ijnlc.2020.9101 (id `doi:10.5121/ijnlc.2020.9101`; retrieved from semantic_scholar; 1 citations per semantic_scholar)
25. David Schmidt, Svenja Kenneweg, Julian Eggert et al.. **Question Answering over Linked Data with Vague Temporal Adverbials**. _Proceedings of the 17th International Joint Conference on Knowledge Discovery, Knowledge Engineering and Knowledge Management_, 2025. <https://doi.org/10.5220/0013778400004000> (id `doi:10.5220/0013778400004000`; retrieved from crossref; 0 citations per crossref)
26. Kannanganattu V. Prasanth, David L. Spector. **Eukaryotic regulatory RNAs: an answer to the ‘genome complexity’ conundrum**. _Genes & Development_, 2007. <https://doi.org/10.1101/gad.1484207> (id `doi:10.1101/gad.1484207`; retrieved from openalex; 399 citations per openalex)
27. Paula Ruth Williamson, Douglas G. Altman, Heather Bagley et al.. **The COMET Handbook: version 1.0**. _Trials_, 2017. <https://doi.org/10.1186/s13063-017-1978-4> (id `doi:10.1186/s13063-017-1978-4`; retrieved from openalex; 2086 citations per openalex)
28. Chun-Ting Kuo, Wing-Kai Hon. **Practical Index Framework for Efficient Time-Travel Phrase Queries on Versioned Documents**. _2016 Data Compression Conference (DCC)_, 2016. <https://doi.org/10.1109/dcc.2016.52> (id `doi:10.1109/dcc.2016.52`; retrieved from crossref; 2 citations per crossref)
29. Tu Ngoc Nguyen, Nattiya Kanhabua, Claudia Niederée et al.. **A Time-aware Random Walk Model for Finding Important Documents in Web Archives**. _Proceedings of the 38th International ACM SIGIR Conference on Research and Development in Information Retrieval_, 2015. <https://doi.org/10.1145/2766462.2767832> (id `doi:10.1145/2766462.2767832`; retrieved from crossref; 9 citations per crossref)

<details><summary>Other retrieved papers (not cited in this report)</summary>

- An Eigensystem for Topic Term Weighting yields Fair and Effective Document Rankings (2025) <https://www.semanticscholar.org/paper/905e0de7c0e24f0c3ab8bb1ed0ed672b960ac46b> `doi:10.54195/irrj.23480`
- Web Document Retrieval Using Passage Retrieval, Connectivity Information, and Automatic Link Weighting–TREC-9 Report (2000) <https://doi.org/10.6028/nist.sp.500-249.padova> `doi:10.6028/nist.sp.500-249.padova`
- Question Answering Using XML-Tagged Documents (2002) <https://doi.org/10.6028/nist.sp.500-251.qa-clresearch> `doi:10.6028/nist.sp.500-251.qa-clresearch`
- Document Listing on Versioned Documents (2013) <https://doi.org/10.1007/978-3-319-02432-5_12> `doi:10.1007/978-3-319-02432-5_12`
- Continuous Temporal Top-k Query over Versioned Documents (2014) <https://doi.org/10.1007/978-3-319-08010-9_55> `doi:10.1007/978-3-319-08010-9_55`
- Versioned Documents in a Technical Document Management System (1990) <https://doi.org/10.1007/978-94-009-0705-8_43> `doi:10.1007/978-94-009-0705-8_43`
- Improving document clustering using Okapi BM25 feature weighting (2011) <https://doi.org/10.1007/s10791-011-9163-y> `doi:10.1007/s10791-011-9163-y`
- Regulatory focus theory and sustainable entrepreneurship (2017) <https://doi.org/10.1108/ijebr-12-2015-0269> `doi:10.1108/ijebr-12-2015-0269`
- An LDA-smoothed relevance model for document expansion (2013) <https://doi.org/10.1145/2484028.2484110> `doi:10.1145/2484028.2484110`
- Relevance feedback retrieval of time series data (1999) <https://doi.org/10.1145/312624.312676> `doi:10.1145/312624.312676`
- Searching for studies: a guide to information retrieval for Campbell systematic reviews (2017) <https://doi.org/10.4073/cmg.2016.1> `doi:10.4073/cmg.2016.1`
- From document retrieval to question answering (2003) <https://research.utwente.nl/en/publications/3c5b1ae9-93f7-4a7c-8b8b-a0f894a87a17> `openalex:W2111572281`
- A Statistical Approach For Open Domain Question Answering (2008) <https://doi.org/10.1007/978-1-4020-4746-6_2> `doi:10.1007/978-1-4020-4746-6_2`
- Relation Extraction for Open and Closed Domain Question Answering (2011) <https://doi.org/10.1007/978-3-642-17525-1_8> `doi:10.1007/978-3-642-17525-1_8`
- Experiments adapting an open-domain question answering system to the geographical domain using scope-based resources (2006) <https://doi.org/10.3115/1708097.1708111> `doi:10.3115/1708097.1708111`
- The Power of Noise: Redefining Retrieval for RAG Systems (2024) <https://doi.org/10.1145/3626772.3657834> `arxiv:2401.14887`
- Supporting information retrieval from electronic health records: A report of University of Michigan’s nine-year experience in developing and using the Electronic Medical Record Search Engine (EMERSE) (2015) <https://doi.org/10.1016/j.jbi.2015.05.003> `doi:10.1016/j.jbi.2015.05.003`
- Information filtering and information retrieval (1992) <https://doi.org/10.1145/138859.138861> `doi:10.1145/138859.138861`
- Automatic Indexing and Abstracting of Document Texts (2002) <https://doi.org/10.1007/b116177> `doi:10.1007/b116177`
- Temporal and multi-versioned XML documents: A survey (2014) <https://doi.org/10.1016/j.ipm.2013.08.003> `doi:10.1016/j.ipm.2013.08.003`
- Retrieval of historical documents by word spotting (2009) <https://doi.org/10.1117/12.805602> `doi:10.1117/12.805602`
- Indexing and Retrieval of Handwritten Documents (2014) <https://doi.org/10.1142/9789814368711_0005> `doi:10.1142/9789814368711_0005`
- Faster temporal range queries over versioned text (2011) <https://doi.org/10.1145/2009916.2009993> `doi:10.1145/2009916.2009993`
- Optimizing positional index structures for versioned document collections (2012) <https://doi.org/10.1145/2348283.2348319> `doi:10.1145/2348283.2348319`
- Open-Domain Question–Answering (2006) <https://doi.org/10.1561/9781601980533> `doi:10.1561/9781601980533`
- Open-domain Factoid Question Answering via Knowledge Graph Search (2016) <https://doi.org/10.18653/v1/w16-0104> `doi:10.18653/v1/w16-0104`
- Textpresso: An Ontology-Based Information Retrieval and Extraction System for Biological Literature (2004) <https://doi.org/10.1371/journal.pbio.0020309> `doi:10.1371/journal.pbio.0020309`
- Recurrent Coupled Topic Modeling over Sequential Documents (2021) <https://arxiv.org/abs/2106.13732> `arxiv:2106.13732`
- On the concept of relevance in legal information retrieval (2017) <https://doi.org/10.1007/s10506-017-9195-8> `doi:10.1007/s10506-017-9195-8`
- Safety and recommendations for TMS use in healthy subjects and patient populations, with updates on training, ethical and regulatory issues: Expert Guidelines (2020) <https://doi.org/10.1016/j.clinph.2020.10.003> `doi:10.1016/j.clinph.2020.10.003`
- Intelligent Indexing and Semantic Retrieval of Multimodal Documents (2000) <https://doi.org/10.1023/a:1009962928226> `doi:10.1023/a:1009962928226`
- When prevention promotes creativity: The role of mood, regulatory focus, and regulatory closure. (2011) <https://doi.org/10.1037/a0022981> `doi:10.1037/a0022981`
- High resolution temporal profiles in the Emissions Database for Global Atmospheric Research (2020) <https://doi.org/10.1038/s41597-020-0462-2> `doi:10.1038/s41597-020-0462-2`
- Topical N-Grams: Phrase and Topic Discovery, with an Application to Information Retrieval (2007) <https://doi.org/10.1109/icdm.2007.86> `doi:10.1109/icdm.2007.86`
- How do Regulatory T Cells Work? (2009) <https://doi.org/10.1111/j.1365-3083.2009.02308.x> `doi:10.1111/j.1365-3083.2009.02308.x`
- Rank and relevance in novelty and diversity metrics for recommender systems (2011) <https://doi.org/10.1145/2043932.2043955> `doi:10.1145/2043932.2043955`
- Recommender systems for contextually-aware, versioned items (2019) <https://doi.org/10.1145/3298689.3346955> `doi:10.1145/3298689.3346955`
- Information retrieval on the web (2000) <https://doi.org/10.1145/358923.358934> `doi:10.1145/358923.358934`
- A comparison of search term weighting (1981) <https://doi.org/10.1145/511754.511759> `doi:10.1145/511754.511759`
- If Cumulative Risk Assessment Is the Answer, What Is the Question? (2007) <https://doi.org/10.1289/ehp.9330> `doi:10.1289/ehp.9330`
- COIL: Revisit Exact Lexical Match in Information Retrieval with Contextualized Inverted List (2021) <https://doi.org/10.18653/v1/2021.naacl-main.241> `doi:10.18653/v1/2021.naacl-main.241`
- Mobile medical and health apps: state of the art, concerns, regulatory control and certification (2014) <https://doi.org/10.5210/ojphi.v5i3.4814> `doi:10.5210/ojphi.v5i3.4814`
- OmicsLake: Versioned, Agent-Aware Data Lineage for R/Bioconductor Workflows (2026) <https://doi.org/10.64898/2026.07.17.739088> `doi:10.64898/2026.07.17.739088`
- Evaluating Question Answering System Performance (2008) <https://doi.org/10.1007/978-1-4020-4746-6_13> `doi:10.1007/978-1-4020-4746-6_13`
- Evaluating Interactive Question Answering (2008) <https://doi.org/10.1007/978-1-4020-4746-6_14> `doi:10.1007/978-1-4020-4746-6_14`
- New Directions In Question Answering (2008) <https://doi.org/10.1007/978-1-4020-4746-6_18> `doi:10.1007/978-1-4020-4746-6_18`
- A Review on Large Language Models: Architectures, Applications, Taxonomies, Open Issues and Challenges (2024) <https://doi.org/10.1109/access.2024.3365742> `doi:10.1109/access.2024.3365742`
- miR2Disease: a manually curated database for microRNA deregulation in human disease (2008) <https://doi.org/10.1093/nar/gkn714> `doi:10.1093/nar/gkn714`
- 31. Similar, more detail, document with Council's replies, March–April 1261 (1973) <https://doi.org/10.1093/oseo/instance.00256906> `doi:10.1093/oseo/instance.00256906`
- Measuring the temporal dynamics of policy mixes – An empirical analysis of renewable energy policy mixes’ balance and design features in nine countries (2018) <https://doi.org/10.1016/j.respol.2018.03.012> `doi:10.1016/j.respol.2018.03.012`
- A systematic literature review of blockchain-based applications: Current status, classification and open issues (2018) <https://doi.org/10.1016/j.tele.2018.11.006> `doi:10.1016/j.tele.2018.11.006`
- 2017 ESC Guidelines on the Diagnosis and Treatment of Peripheral Arterial Diseases, in collaboration with the European Society for Vascular Surgery (ESVS) (2017) <https://doi.org/10.1093/eurheartj/ehx095> `doi:10.1093/eurheartj/ehx095`
- LightRAG: Simple and Fast Retrieval-Augmented Generation (2025) <https://doi.org/10.18653/v1/2025.findings-emnlp.568> `doi:10.18653/v1/2025.findings-emnlp.568`
- Adverse outcome pathways: opportunities, limitations and open questions (2017) <https://doi.org/10.1007/s00204-017-2045-3> `doi:10.1007/s00204-017-2045-3`
- High-Throughput Metagenomic Technologies for Complex Microbial Community Analysis: Open and Closed Formats (2015) <https://doi.org/10.1128/mbio.02288-14> `doi:10.1128/mbio.02288-14`
- CONSORT 2010 Explanation and Elaboration: updated guidelines for reporting parallel group randomised trials (2010) <https://doi.org/10.1136/bmj.c869> `doi:10.1136/bmj.c869`
- Text Algorithms in Economics (2023) <https://doi.org/10.1146/annurev-economics-082222-074352> `doi:10.1146/annurev-economics-082222-074352`
- Setting the future of digital and social media marketing research: Perspectives and research propositions (2020) <https://doi.org/10.1016/j.ijinfomgt.2020.102168> `doi:10.1016/j.ijinfomgt.2020.102168`
- A field study of the software design process for large systems (1988) <https://doi.org/10.1145/50087.50089> `doi:10.1145/50087.50089`
- Vertically Integrated Architectures (2019) <https://doi.org/10.1007/978-1-4842-4252-0> `doi:10.1007/978-1-4842-4252-0`
- The Problem (2018) <https://doi.org/10.1007/978-1-4842-4252-0_1> `doi:10.1007/978-1-4842-4252-0_1`
- Implicit Services (2018) <https://doi.org/10.1007/978-1-4842-4252-0_8> `doi:10.1007/978-1-4842-4252-0_8`
- Persistence-Aware Programming (2018) <https://doi.org/10.1007/978-1-4842-4252-0_9> `doi:10.1007/978-1-4842-4252-0_9`
- Management of Statin Intolerance in 2018: Still More Questions Than Answers (2018) <https://doi.org/10.1007/s40256-017-0259-7> `doi:10.1007/s40256-017-0259-7`
- 2012 ACCF/AATS/SCAI/STS Expert Consensus Document on Transcatheter Aortic Valve Replacement (2012) <https://doi.org/10.1016/j.jacc.2012.01.001> `doi:10.1016/j.jacc.2012.01.001`
- A survey of socially interactive robots (2003) <https://doi.org/10.1016/s0921-8890(02)00372-x> `doi:10.1016/s0921-8890(02)00372-x`
- Minimal information for studies of extracellular vesicles 2018 (MISEV2018): a position statement of the International Society for Extracellular Vesicles and update of the MISEV2014 guidelines (2018) <https://doi.org/10.1080/20013078.2018.1535750> `doi:10.1080/20013078.2018.1535750`
- Text mining and ontologies in biomedicine: Making sense of raw text (2005) <https://doi.org/10.1093/bib/6.3.239> `doi:10.1093/bib/6.3.239`
- Deep learning for healthcare: review, opportunities and challenges (2017) <https://doi.org/10.1093/bib/bbx044> `doi:10.1093/bib/bbx044`
- Microdosing psychedelics: More questions than answers? An overview and suggestions for future research (2019) <https://doi.org/10.1177/0269881119857204> `doi:10.1177/0269881119857204`
- The PRISMA Statement for Reporting Systematic Reviews and Meta-Analyses of Studies That Evaluate Health Care Interventions: Explanation and Elaboration (2009) <https://doi.org/10.1371/journal.pmed.1000100> `doi:10.1371/journal.pmed.1000100`
- Distributional Semantics Resources for Biomedical Text Processing (2013) <https://research.manchester.ac.uk/en/publications/8b865ebe-417a-41fb-acb7-241efe6a5490> `openalex:W2527896214`

</details>

## Appendix A. Evidence Ledger

### [Evidence] claims (5)

- **[Evidence]** Re3 (2025) proposes a unified framework that dynamically balances semantic and temporal information through a query-aware gating mechanism for temporal information retrieval, achieving state-of-the-art results on Re2Bench benchmark. _(claim C001, confidence: high)_
  - [2], abstract (direct support, verified) "To address this gap, we introduce Re2Bench, a benchmark specifically designed to disentangle and evaluate Relevance, Recency, and their hybrid combination. Building on this foundation, we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism."
- **[Evidence]** Re3 assumes explicit or reliably extractable timestamps, which may not hold in all settings, limiting its applicability to domains where document version timestamps are unavailable or unreliable. _(claim C003, confidence: high)_
  - [2], limitations (direct support, verified) "Assumes explicit or reliably extractable timestamps, which may not hold in all settings."
- **[Evidence]** IndiaFinBench (2026) is an evaluation benchmark for Indian financial regulatory text that includes temporal reasoning tasks requiring models to "identify which version of a rule was in force at a given time" and explicitly addresses challenges posed by "references chains of superseding circulars that require temporal reasoning to untangle." _(claim C012, confidence: high)_
  - [1], p. 2 (direct support, verified) "references chains of superseding circulars that require temporal reasoning to untangle"
  - [1], p. 4 (direct support, verified) "identify which version of a rule was in force at a given time"
- **[Evidence]** Re3 (2025) proposes a unified framework that dynamically balances semantic and temporal information through a query-aware gating mechanism for temporal information retrieval, achieving state-of-the-art results on temporal IR benchmarks. _(claim C013, confidence: high)_
  - [2], abstract (direct support, verified) "we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism"
  - [2], abstract (direct support, verified) "On Re2Bench, Re3 achieves state-of-the-art results, leading in R@1 across all three subsets"
- **[Evidence]** Re3 (2025) is explicitly described as a "universal, plug-and-play, and lightweight framework for TIR" that "can be seamlessly integrated with existing dense retrievers" and is designed to be a "lightweight, plug-and-play retriever". _(claim C014, confidence: high)_
  - [2], p. 2 (direct support, verified) "universal, plug-and-play, and lightweight framework for TIR"
  - [2], p. 2 (direct support, verified) "can be seamlessly integrated with existing dense retrievers"
  - [2], p. 9 (direct support, verified) "designed to be a lightweight, plug-and-play retriever"

### [Inference] claims (13)

- **[Inference]** The effectiveness of temporal relevance modeling depends heavily on the choice of temporal function (e.g., linear, exponential) and its parameters, which may not generalize across different document versioning patterns and amendment frequencies. _(claim C002, confidence: medium)_
  - [2], limitations (indirect support, verified) "Assumes explicit or reliably extractable timestamps, which may not hold in all settings."
  - [2], future_work (indirect support, unverified) "Relax timestamp assumptions."
- **[Inference]** Observed improvements in temporal-aware retrieval could be confounded by enhancements to semantic matching components rather than the temporal modeling itself, especially when using learned combinations that may absorb semantic improvements. _(claim C004, confidence: medium)_
  - [2], relation_to_idea (indirect support, unverified) "Re3 focuses on general temporal IR benchmarks; our idea targets versioned regulatory documents for open-domain QA, proposing a retrieval-agnostic temporal relevance component adaptable to any retriever."
- **[Inference]** When using learned mechanisms to combine semantic and temporal signals (like Re3's query-aware gating), it becomes difficult to disentangle whether performance gains come from better temporal modeling or from the learned mechanism's ability to adjust semantic weighting, posing a challenge for ablation studies. _(claim C005, confidence: medium)_
  - [2], method (direct support, verified) "we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism."
  - [2], future_work (indirect support, unverified) "Add interpretability tools."
- **[Inference]** Re3 uses a query-aware gating mechanism to dynamically balance semantic and temporal information during re-ranking, which makes it challenging to isolate the contribution of temporal modeling from the learned gating function's effect on semantic weighting. _(claim C006, confidence: medium)_
  - [2], method (direct support, verified) "we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism."
- **[Inference]** Re3 (2025) demonstrates that a retrieval-agnostic framework combining temporal relevance with semantic similarity for versioned documents already exists, as it is described as a universal, plug-and-play framework that dynamically balances semantic and temporal information through a query-aware gating mechanism and can be integrated with existing dense retrievers. _(claim C015, confidence: high)_
  - [2], p. 1 (direct support, verified) "we propose Re3, a unified and lightweight framework that dynamically balances semantic and temporal information through a query-aware gating mechanism"
  - [2], p. 2 (direct support, verified) "universal, plug-and-play, and lightweight framework for TIR"
  - [2], p. 2 (direct support, verified) "can be seamlessly integrated with existing dense retrievers"
  - [2], p. 9 (direct support, verified) "designed to be a lightweight, plug-and-play retriever"
- **[Inference]** While Re3 (2025) provides a retrieval-agnostic framework for balancing semantic and temporal information, our idea specifically targets versioned regulatory documents for open-domain question answering, focusing on the problem where amendments supersede earlier clauses creating semantic overlap, and aims to construct a domain-specific benchmark with regulatory texts and time-stamped queries. _(claim C016, confidence: medium)_
  - [2], relation_to_idea (indirect support, unverified) "Re3 focuses on general temporal IR benchmarks; our idea targets versioned regulatory documents for open-domain QA, proposing a retrieval-agnostic temporal relevance component adaptable to any retriever."
- **[Inference]** Re3 (2025) focuses on general temporal IR benchmarks (Re2Bench) to disentangle and evaluate Relevance, Recency, and their hybrid combination, while our idea specifically targets versioned regulatory documents for open-domain QA, focusing on the problem where amendments supersede earlier clauses creating semantic overlap, and aims to construct a domain-specific benchmark with regulatory texts and time-stamped queries. _(claim C017, confidence: medium)_
  - [2], p. 1 (direct support, verified) "we introduce Re2Bench"
  - [2], p. 1 (direct support, verified) "a benchmark specifically designed"
- **[Inference]** The Practical Index Framework for Efficient Time-Travel Phrase Queries on Versioned Documents (2016) focuses on enabling efficient time-travel phrase queries through specialized indexing structures, rather than combining temporal relevance with semantic similarity for ranking adjustments. _(claim C018, confidence: medium)_
  - [28], title (indirect support, unverified) "Practical Index Framework for Efficient Time-Travel Phrase Queries on Versioned Documents"
- **[Inference]** The Time-aware Random Walk Model for Finding Important Documents in Web Archives (2015) applies random walk models with temporal awareness to identify important documents in web archives, focusing on importance scoring rather than combining temporal and semantic relevance for query-specific retrieval. _(claim C019, confidence: medium)_
  - [29], title (indirect support, unverified) "A Time-aware Random Walk Model for Finding Important Documents in Web Archives"
- **[Inference]** While Re3 (2025) provides a retrieval-agnostic framework that dynamically balances semantic and temporal information through a query-aware gating mechanism for general temporal information retrieval, our idea specifically targets versioned regulatory documents for open-domain question answering, focusing on the semantic overlap problem created by superseding amendments and aiming to construct a domain-specific benchmark with regulatory texts and time-stamped queries. _(claim C020, confidence: high)_
  - [2], relation_to_idea (indirect support, unverified) "Re3 focuses on general temporal IR benchmarks; our idea targets versioned regulatory documents for open-domain QA, proposing a retrieval-agnostic temporal relevance component adaptable to any retriever."
  - [4], problem (indirect support, unverified) "Question answering over regulatory documents, which are often versioned and require up-to-date information."
- **[Inference]** The temporal graph approach based on LSA and citation/author occurrence (doi:10.31803/tg-20230715000112) models document relevance over time through temporal relationships in expert finding tasks, whereas our idea uses temporal proximity between query timestamps and version timestamps to adjust retrieval rankings for open-domain QA over versioned regulatory texts. _(claim C021, confidence: medium)_
  - [22], relation_to_idea (indirect support, unverified) "The paper uses temporal graph based on citation/author for expert finding; our idea focuses on versioned regulatory documents and uses temporal proximity between query date and version timestamp to adjust retrieval rankings."
- **[Inference]** Contextualized Offline Relevance Weighting (doi:10.1145/3404835.3463073) improves retrieval efficiency by precomputing relevance weights using pseudo-queries, focusing on online latency reduction rather than incorporating temporal dynamics based on version timestamps for regulatory document QA. _(claim C022, confidence: medium)_
  - [13], relation_to_idea (indirect support, unverified) "CORW focuses on improving retrieval efficiency via offline pseudo-query weighting; our idea adds a temporal relevance component to adapt rankings based on version timestamps for QA over versioned texts."
- **[Inference]** The strongest baselines for time-aware retrieval of versioned documents include Re3 (a retrieval-agnostic framework balancing semantic and temporal signals), time-travel phrase query frameworks (focused on efficient indexing), and temporal random walk models (for importance scoring). Our idea differs by specifically targeting open-domain QA over versioned regulatory documents, focusing on the semantic overlap from superseding amendments, and aiming to construct a regulatory-specific benchmark with time-stamped queries. _(claim C023, confidence: high)_
  - [2], relation_to_idea (indirect support, unverified) "Re3 focuses on general temporal IR benchmarks; our idea targets versioned regulatory documents for open-domain QA, proposing a retrieval-agnostic temporal relevance component adaptable to any retriever."
  - [22], relation_to_idea (indirect support, unverified) "The paper uses temporal graph based on citation/author for expert finding; our idea focuses on versioned regulatory documents and uses temporal proximity between query date and version timestamp to adjust retrieval rankings."
  - [13], relation_to_idea (indirect support, unverified) "CORW focuses on improving retrieval efficiency via offline pseudo-query weighting; our idea adds a temporal relevance component to adapt rankings based on version timestamps for QA over versioned texts."

### [Assumption] claims (5)

- **[Assumption]** Each document version has a valid timestamp indicating when it was enacted or amended. _(claim C007, confidence: medium)_
- **[Assumption]** Queries are associated with a target date (the time at which the question is asked). _(claim C008, confidence: medium)_
- **[Assumption]** Semantic similarity (e.g., from a dense retriever) is a suitable baseline for relevance. _(claim C009, confidence: high)_
- **[Assumption]** The temporal relevance function can be modeled as a decaying function of time difference (e.g., exponential decay). _(claim C010, confidence: medium)_
- **[Assumption]** The combination of temporal and semantic scores can be a simple weighted sum. _(claim C011, confidence: low)_

## Appendix B. Search Log

| Query | Sources (status: results) | Papers |
|---|---|---|
| temporal document retrieval versioned documents regulatory texts | arxiv (ok: 0), openalex (ok: 10), semantic_scholar (error: 0), crossref (ok: 10) | 20 |
| temporal question answering regulatory documents | arxiv (ok: 1), openalex (ok: 10), semantic_scholar (error: 0), crossref (ok: 10) | 20 |
| temporal relevance weighting document retrieval | arxiv (ok: 2), openalex (ok: 10), semantic_scholar (ok: 10), crossref (ok: 10) | 31 |
| time-aware retrieval versioned documents regulatory | arxiv (ok: 0), openalex (ok: 10), semantic_scholar (error: 0), crossref (ok: 10) | 19 |
| open domain question answering regulatory documents versioned temporal | arxiv (ok: 0), openalex (ok: 10), semantic_scholar (error: 0), crossref (ok: 10) | 19 |

## Appendix C. Investigation Log

Each step was chosen by the ResearchForge controller from the recorded research state.

| Step | Phase | Action | Why | Alternatives considered | Outcome | Information gain |
|---|---|---|---|---|---|---|
| 0 | INTAKE | INTAKE | Research idea received. | none | idea stored in the workspace | n/a |
| 1 | FORMALIZE | FORMALIZE | The idea has not been formalized into a testable research question. | none | +85 papers; +4 searches; +6 uncertainties; idea formalized | 3 |
| 2 | PLAN | PLAN | No investigation plan exists yet, so it is unclear what must be determined. | none | +4 uncertainties; investigation plan recorded | 1 |
| 3 | INVESTIGATE | READ | Retrieved papers have not been analyzed enough to judge overlap. | none | +6 analyses | 3 |
| 4 | SYNTHESIZE | SYNTHESIZE | Analyses exist but the field has not been mapped. | none | landscape recorded | 1 |
| 5 | CRITIQUE | CRITIQUE | The idea has not been challenged yet. | none | +11 claims; +5 verified claims; +6 uncertainties; +1 resolved uncertainties; critique recorded; uncertainties updated: U001, U002, U003, U004 | 8 |
| 6 | CHALLENGE | CHALLENGE (U017: Does published work contradict the current assessment: Our idea specifical) | The critique's assessment has not been challenged yet (U017); look for published work that contradicts it before investing in anything that builds on it. | none | +16 papers; +1 searches; +2 claims; +2 verified claims; +1 contradicted conclusions; +1 resolved uncertainties; uncertainties updated: U017 | 8 |
| 7 | CRITIQUE | CRITIQUE (Does published work contradict the current assessment: Our idea specifically tar) | The current critique predates contradicting evidence (U017 weakened); the assessment must be revised before continuing. | none | critique recorded; uncertainties updated: U012 | 1 |
| 8 | UNCERTAINTY | COMPARE (U007: Does a retrieval-agnostic framework that combines temporal relevance with ) | Most valuable next step for high-importance novelty question U007: score 1.2 = importance 3 x expected gain 0.6 x relevance 1 x evidence deficiency 1 / cost 1.5. Next best: COMPARE on U008 (1.2). | COMPARE U008 (1.2); READ U007 (1.125) | +4 claims; +3 verified claims; +2 uncertainties; +1 resolved uncertainties; uncertainties updated: U007 | 5 |
| 9 | UNCERTAINTY | COMPARE (U008: Which existing time-aware retrieval techniques for versioned documents (e.) | Most valuable next step for high-importance overlap question U008: score 1.6 = importance 3 x expected gain 0.8 x relevance 1 x evidence deficiency 1 / cost 1.5. Next best: COMPARE on U020 (1.6). | COMPARE U020 (1.6); COMPARE U006 (1.44) | +6 claims; uncertainties updated: U008 | 0 |
| 10 | UNCERTAINTY | READ (U020: What are the most appropriate baseline methods for evaluating a temporal-s) | Most valuable next step for high-importance overlap question U020: score 1.125 = importance 3 x expected gain 0.75 x relevance 1 x evidence deficiency 1 / cost 2. Next best: PLAN_EXPERIMENT on U014 (1.08). | PLAN_EXPERIMENT U014 (1.08); COMPARE U020 (1.066) | +6 analyses | 3 |
| 11 | UNCERTAINTY | READ (U006: How to handle conflicting information across versions where an amendment s) | Most valuable next step for high-importance confounder question U006: score 1.125 = importance 3 x expected gain 0.833 x relevance 0.9 x evidence deficiency 1 / cost 2. Next best: READ on U009 (1.125). | READ U009 (1.125); READ U013 (1.125) | +6 analyses | 3 |
| 12 | UNCERTAINTY | READ (U009: What is the most effective way to combine temporal relevance and semantic ) | Most valuable next step for high-importance validity question U009: score 1.181 = importance 3 x expected gain 0.875 x relevance 0.9 x evidence deficiency 1 / cost 2. Next best: READ on U013 (1.181). | READ U013 (1.181); READ U014 (1.181) | +6 analyses | 3 |
| 13 | UNCERTAINTY | READ (U013: To what extent do versioned regulatory documents (statutes, codes, regulat) | Most valuable next step for high-importance validity question U013: score 1.215 = importance 3 x expected gain 0.9 x relevance 0.9 x evidence deficiency 1 / cost 2. Next best: READ on U014 (1.215). | READ U014 (1.215); READ U019 (1.215) | no recorded change; runtime note: phase exceeded 1200.0s and was stopped | 0 |
| 14 | FINALIZE | FINALIZE | Stopping: time budget reached (3600 s). | none | finalizing | n/a |
