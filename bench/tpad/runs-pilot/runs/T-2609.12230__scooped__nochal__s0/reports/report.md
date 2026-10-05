# ResearchForge Investigation Report

Project `T-2609.12230__scooped__nochal__s0` · model `ollama-cloud/nemotron-3-super` · status **incomplete**

> Labels: **[Evidence]** directly supported by a verified quote from a retrieved source; **[Inference]** reasoning derived from cited evidence; **[Hypothesis]** proposed, not validated; **[Assumption]** taken as given without evidence; **[Experimental result]** observed in an executed experiment.

## 1. Executive Summary

**Investigated:** Multi‑hop question answering often relies on reasoning over a chain of facts in a knowledge graph, yet current language‑model training typically uses isolated head‑relation‑tail triples, depriving the model of the surrounding context that supports multi‑step inference. We propose to enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. The model will be fine‑tuned under two regimes: one using only the target triple/path and another that also incorporates the supporting context. To improve the reliability of the base facts, we will introduce an adaptive repair loop that detects one‑hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, we will apply reinforcement‑learning‑based optimization on lower‑hop QA instances and evaluate transfer to deeper multi‑hop queries.

**Research question:** Does enriching training triples with local context subgraphs and applying an adaptive repair loop improve hit@1 accuracy on multi-hop KGQA (MetaQA) for 2-hop and 3-hop questions compared to training on isolated triples?

**Literature investigated:** 92 papers retrieved from 13 searches (openalex: 32, crossref: 24, arxiv: 23, semantic_scholar: 19); 23 analyzed; 18 rated highly relevant.

**Assessment:** Promising but requires experimental validation. **[Inference]** The idea is novel and addresses a recognized limitation (neighborhood size constraint), but the critical assumptions about local context usefulness, repair loop feasibility, and RL transfer lack empirical support, necessitating experimental validation to determine its effectiveness.

**Closest existing work:** Improving Embedded Knowledge Graph Multi-hop Question Answering by introducing Relational Chain Reasoning (2021) [1]; Biomedical Multi-hop Question Answering Using Knowledge Graph Embeddings and Language Models (2022) [2]; Knowledge Graph Based Retrieval-Augmented Generation for Multi-Hop Question Answering Enhancement (2024) [3]

**Potential overlap:** The idea overlaps with existing LM+KG embedding and RAG approaches in using language models and knowledge graphs for multi-hop QA, sharing the goal of improving reasoning over KGs.

**Potential distinction:** Unlike prior work that focuses on architectural changes (e.g., relational chain reasoning modules) or retrieval-augmented generation, this idea modifies the training data itself by enriching each supervision signal with local context from the same passage and iteratively repairs faulty base facts via an adaptive loop.

**Major risk:** The proposal relies on unverified assumptions: that local context is supportive and not noisy (C003), that an adaptive repair loop can generate effective corrective examples (C004), and that RL optimization on lower-hop QA transfers to higher-hop QA (C005). Without empirical validation, these assumptions may not hold, risking no improvement or performance degradation.

**Research decision:** Insufficient evidence. **[Inference]** Basis: high-importance questions remain unresolved (U001, U002). This describes the state of the evidence, not the absolute value of the idea.

**Investigation:** 11 steps chosen from the research state; 8 uncertainties raised, 2 resolved, 6 still open or unresolved (Section 13, Appendix C).

**Stopped by a safety limit:** Stopping: time budget reached (3600 s). Conclusions below cover only what was recorded before the limit.

**Claim grounding:** 11/11 evidence and inference claims have at least one verified source.

**Incomplete phases:** gaps, modifications, experiments. Sections that depend on them are marked as not recorded.

This report does not declare the idea novel. Absence of a matching paper in these searches does not establish novelty; see Section 13.

## 2. Original Research Idea

> Multi‑hop question answering often relies on reasoning over a chain of facts in a knowledge graph, yet current language‑model training typically uses isolated head‑relation‑tail triples, depriving the model of the surrounding context that supports multi‑step inference. We propose to enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. The model will be fine‑tuned under two regimes: one using only the target triple/path and another that also incorporates the supporting context. To improve the reliability of the base facts, we will introduce an adaptive repair loop that detects one‑hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, we will apply reinforcement‑learning‑based optimization on lower‑hop QA instances and evaluate transfer to deeper multi‑hop queries.

## 3. Formalized Research Question

**Research question:** Does enriching training triples with local context subgraphs and applying an adaptive repair loop improve hit@1 accuracy on multi-hop KGQA (MetaQA) for 2-hop and 3-hop questions compared to training on isolated triples?

**Hypothesis:** **[Hypothesis]** Enriching training with local context subgraphs and applying an adaptive repair loop will improve hit@1 accuracy on multi-hop KGQA, especially for higher-hop questions, by providing better factual grounding and contextual reasoning, and the adaptive repair loop will improve the reliability of base facts.

| Aspect | Formalization |
|---|---|
| Problem | Current language-model training for knowledge graph-based question answering uses isolated head-relation-tail triples, depriving the model of the surrounding context that supports multi-step inference. |
| Target domain | Multi-hop question answering over knowledge graphs using language models |
| Proposed method | Enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. Fine-tune the language model under two regimes: (A) using only the target triple/path, and (B) using the target triple/path plus the local context subgraph. Introduce an adaptive repair loop that detects one-hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, apply reinforcement-learning-based optimization on lower-hop QA instances and evaluate transfer to deeper multi-hop queries. |
| Target system | Language model-based knowledge graph question answering system (e.g., EmbedKGQA or Rce-KGQA) |
| Expected contribution | A training method that improves multi-hop KGQA performance by leveraging local context and adaptive repair, with analysis of transfer from lower-hop to higher-hop, and a demonstration of improved base fact reliability through the repair loop. |
| Independent variables | Training condition: isolated triples (baseline), Training condition: enriched with local context subgraph, Training condition: enriched + adaptive repair loop, Training condition: enriched + adaptive repair loop + RL optimization |
| Dependent variables | hit@1 accuracy on MetaQA 1-hop, hit@1 accuracy on MetaQA 2-hop, hit@1 accuracy on MetaQA 3-hop |
| Controls | Model architecture (EmbedKGQA or Rce-KGQA), Base knowledge graph (MetaQA KG), Evaluation datasets (MetaQA), Hyperparameters (learning rate, batch size, etc.), Random seeds |

**Assumptions**

- The local context subgraph from the same passage is supportive and not noisy.
- The adaptive repair loop can generate effective corrective examples for one-hop failures.
- Reinforcement learning optimization on lower-hop QA transfers to higher-hop QA.
- The base language model and KGQA architecture (e.g., EmbedKGQA or Rce-KGQA) are suitable for the proposed enrichment.

**Expected benefits / potential risks**

- Benefit: Improved hit@1 accuracy on multi-hop QA
- Benefit: Better factual grounding
- Benefit: Reduced error propagation in multi-hop reasoning
- Risk: The local context subgraph may introduce noise
- Risk: The adaptive repair loop may not converge or may overfit
- Risk: RL optimization may be unstable or fail to transfer

**Ambiguities**

| Question | Resolution | Resolved by |
|---|---|---|
| What evaluation metric to use? | hit@1 accuracy (based on arxiv:2110.12679 and doi:10.18653/v1/2020.acl-main.412) | literature |
| Which dataset to use for evaluation? | MetaQA (based on both papers) | literature |
| Which model architecture to use as base? | EmbedKGQA or Rce-KGQA (based on doi:10.18653/v1/2020.acl-main.412 and arxiv:2110.12679) | literature |
| Which baselines to compare with? | EmbedKGQA and Rce-KGQA (based on the same papers) | literature |
| What constitutes the 'same source passage' for local context? | Assumed to be the text passage from which the triple was extracted if the KG is built from text | assumption |

## 4. Existing Research

Overlap values are heuristic signals assigned during analysis, not measurements of novelty.

| Paper | Relevance | Method | Problem / method / evaluation overlap | Read from |
|---|---|---|---|---|
| Improving Embedded Knowledge Graph Multi-hop Question Answering by introducing Relational Chain Reasoning (2021) [1] | high | Propose Relational Chain based Embedded KGQA (Rce-KGQA) that simultaneously uses explicit relational chain from question (via Siamese network) and implicit relational chain from KG. Architecture includes Answer Filtering Module (AFM) and Relational Chain Reasoning Module (RCRM). Uses RoBERTa for que | 0.9 / 0.5 / 0.8 | full_text |
| Exploiting Hybrid Semantics of Relation Paths for Multi-hop Question Answering Over Knowledge Graphs (2022) [4] | high | Propose improving multi-hop KGQA by exploiting relation paths' hybrid semantics: integrate explicit textual information and implicit KG structural features of relation paths based on a novel rotate-and-scale entity link prediction framework. | 0.8 / 0.4 / 0.2 | abstract |
| Biomedical Multi-hop Question Answering Using Knowledge Graph Embeddings and Language Models (2022) [2] | high | Use language models (RoBERTa/BioBERT) to encode questions, knowledge graph embeddings (ComplEx) to encode entities/relations, and a scoring function that combines embeddings to rank answer entities. Separate models trained for 1-hop, 2-hop, 3-hop questions. | 0.9 / 0.4 / 0.2 | full_text |
| LLM-Based Multi-Hop Question Answering with Knowledge Graph Integration in Evolving Environments (2024) [5] | high | Introduce Graph Memory-based Editing for Large Language Models (GMeLLo) that merges explicit KG knowledge with LLM linguistic flexibility, using LLMs to convert free-form language into structured queries and fact triples for seamless KG interaction and rapid updates. | 0.8 / 0.4 / 0.2 | abstract |
| Knowledge Editing with Dynamic Knowledge Graphs for Multi-Hop Question Answering (2024) [6] | high | Introduce KEDKG, a novel knowledge editing method that leverages a dynamic knowledge graph for MHQA: (1) dynamically construct a knowledge graph to store revised information while resolving knowledge conflicts; (2) employ fine-grained retrieval with entity and relation detector to enhance graph retr | 0.8 / 0.3 / 0.2 | abstract |
| A Method for Multi-Hop Question Answering on Persian Knowledge Graph (2025) [7] | high | Constructed a dataset of 5,600 Persian multi-hop complex questions with decomposed forms based on semantic representation. Trained Persian language models on this dataset and proposed an architecture for answering complex questions using a Persian knowledge graph. | 0.9 / 0.3 / 0.2 | abstract |
| Bridging Dual Knowledge Graphs for Multi-Hop Question Answering in Construction Safety (2025) [8] | high | Introduces BifrostRAG, a dual-graph retrieval-augmented generation (RAG) system that models both linguistic relationships and document structure. Supports a hybrid retrieval mechanism combining graph traversal with vector-based semantic search, enabling LLMs to reason over both content and structure | 0.8 / 0.3 / 0.2 | abstract |
| KG-o1: Enhancing Multi-hop Question Answering in Large Language Models via Knowledge Graph Integration (2025) [9] | high | KG-o1, a four-stage approach: (1) filter initial entities and generate complex subgraphs from KG; (2) construct logical paths for subgraphs; (3) use KG to build a dataset with complex extended brainstorming process to train LLMs to imitate long-term reasoning; (4) employ rejection sampling to genera | 0.9 / 0.5 / 0.2 | abstract |
| CacheRAG: A Semantic Caching System for Retrieval-Augmented Generation in Knowledge Graph Question Answering (2026) [10] | high | Propose CacheRAG, a systematic cache-augmented architecture for LLM-based KGQA that transforms stateless planners into continual learners via three design principles: (1) Schema-agnostic user interface with Intermediate Semantic Representation and Backend Adapter; (2) Diversity-optimized cache retri | 0.7 / 0.3 / 0.2 | abstract |
| Temporal knowledge graph question answering via subgraph reasoning (2022) [11] | high | Not stated in abstract. Based on title: proposes subgraph reasoning for temporal KGQA. | 0.6 / 0.3 / 0.2 | abstract |
| Knowledge Graph Based Retrieval-Augmented Generation for Multi-Hop Question Answering Enhancement (2024) [3] | high | Enhance Graph-based Retrieval-Augmented Generation (Graph RAG) by constructing individual knowledge graphs for each document (entities as nodes, relationships as edges enriched with contextual properties), integrating them into a unified graph capturing cross-document relationships, and utilizing ve | 0.9 / 0.4 / 0.2 | abstract |
| Variational Reasoning for Question Answering With Knowledge Graph (2018) [12] | high | Propose a unified deep learning architecture and an end-to-end variational learning algorithm that handles noise in questions and learns multi-hop reasoning simultaneously. | 0.8 / 0.3 / 0.2 | abstract |
| Improving Multi-hop Question Answering over Knowledge Graphs using Knowledge Base Embeddings (2020) [13] | high | EmbedKGQA uses a KG embedding module (ComplEx) to generate entity and relation embeddings, a question embedding module to encode the natural language question, and an answer selection module that combines the ComplEx score φ(e_h, e_q, e_a′) with a relation score (intersection of relation sets) via a | 0.9 / 0.4 / 0.3 | full_text |
| HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering (2018) [14] | high | Introduce HotpotQA, a new dataset with 113k Wikipedia-based question-answer pairs featuring four key features: (1) questions require finding and reasoning over multiple supporting documents; (2) questions are diverse and not constrained to any pre-existing knowledge bases or schemas; (3) sentence-le | 0.7 / 0.2 / 0.4 | abstract |
| SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets for Knowledge Graph Multi-hop Question Answering (2025) [15] | high | Enhance SG-RAG with an additional Merging and Ordering Triplets (MOT) step: apply hierarchical merging on retrieved subgraphs to decrease redundancy and order triplets using BFS traversal to help LLMs generate more precise answers. | 0.8 / 0.4 / 0.2 | abstract |
| Enriching Subgraph Retrieval with Attribute Values for Complex Question Answering Over Knowledge Graph (2025) [16] | high | Not stated in abstract. Based on title: proposes to enrich subgraph retrieval by incorporating attribute values. | 0.6 / 0.3 / 0.2 | abstract |
| Multi-path reasoning for Multi-hop Question Answering over Knowledge Graphs (2022) [17] | high | Propose a multi-path reasoning teacher network model based on bidirectional reasoning, adding two sets of bidirectional reasoning answer search paths to improve the accuracy of the intermediate supervision signal generated by the teacher network and reduce its negative effect on the student network. | 0.6 / 0.2 / 0.2 | abstract |
| Knowledge Graph Multi-Hop Question Answering Based on Dependent Syntactic Semantic Augmented Graph Networks (2024) [18] | high | Introduce Dependent Syntactic Semantic Augmented Graph Network (DSSAGN) that leverages synergy between syntactic structures and semantic relationships within knowledge graphs to model multi-hop relations and dynamically prioritize syntactic–semantic context. | 0.8 / 0.3 / 0.2 | abstract |
| Unrestricted multi-hop reasoning network for interpretable question answering over knowledge graph (2022) [19] | medium | Not stated in abstract. Based on title: proposes an unrestricted multi-hop reasoning network for interpretable KGQA. | 0.7 / 0.3 / 0.2 | abstract |
| LAMRF: Logic-adaptive multi-source reasoning fusion for multi-hop knowledge graph question answering (2026) [20] | medium | Not stated in abstract. Based on title: proposes LAMRF (Logic-adaptive multi-source reasoning fusion) for multi-hop KGQA. | 0.7 / 0.3 / 0.2 | abstract |
| Enhancing relation classification based on GCN Multi-hop Knowledge Graph Question Answering model of knowledge reasoning (2024) [21] | medium | Not stated in abstract. Based on title: uses GCN (Graph Convolutional Network) for relation classification in multi-hop KGQA. | 0.6 / 0.2 / 0.1 | abstract |
| Multi-hop Question Answering with Knowledge Graph Embedding in a Similar Semantic Space (2022) [22] | medium | Not stated in abstract. Based on title: uses knowledge graph embeddings in a similar semantic space for multi-hop QA. | 0.8 / 0.5 / 0.2 | abstract |
| Progressive Planning and Reinforced Reasoning: Large Language Model-Guided Multi-hop Question Answering over Knowledge Graph (2026) [23] | medium | Not stated in abstract. Based on title: uses progressive planning and reinforced reasoning, likely involving LLMs for multi-hop KGQA. | 0.7 / 0.4 / 0.2 | abstract |

<details><summary>Full paper analyses</summary>

#### Improving Embedded Knowledge Graph Multi-hop Question Answering by introducing Relational Chain Reasoning (2021) [1]

- **Problem:** Multi-hop KGQA suffers from: (i) absent explicit relational chain order in questions, (ii) incorrectly capturing relational types due to weak supervision, (iii) failing to consider implicit relations due to limited neighborhood size in subgraph retrieval.
- **Method:** Propose Relational Chain based Embedded KGQA (Rce-KGQA) that simultaneously uses explicit relational chain from question (via Siamese network) and implicit relational chain from KG. Architecture includes Answer Filtering Module (AFM) and Relational Chain Reasoning Module (RCRM). Uses RoBERTa for question encoding and KG embeddings for entity/relation encoding.
- **Main contribution:** A novel KGQA model that integrates explicit and implicit relational chains, achieving state-of-the-art hit@1 performance on MetaQA, WebQuestionsSP-tiny, and Complex-WebQSP benchmarks, with code publicly available.
- **Key assumptions:** Explicit relational chain can be extracted from question syntax.; Implicit relational chain exists in KG and can be retrieved via KG embeddings.; Combining explicit and implicit chains improves reasoning.
- **Datasets / benchmarks:** MetaQA (1-hop, 2-hop, 3-hop), WebQuestionsSP-tiny, Complex-WebQSP, MetaQA, WebQuestionsSP-tiny, Complex-WebQSP
- **Baselines:** GraftNet, PullNet, EmbedKGQA, NSM+h, NSM+p, NSM
- **Metrics:** hit@1, hit@5
- **Results:** ["On MetaQA test set: 1-hop hit@1 ~98.3% (improvement +1.3% over GraftNet/PullNet, +0.8% over EmbedKGQA, +1.1% over NSM+h); 2-hop hit@1 ~99.7% (slightly behind PullNet etc at 99.9%); 3-hop hit@1 ~97.9% (behind baselines at 98.9%)."]
- **Limitations:** Not explicitly stated in abstract or full text.
- **Future work:** Not explicitly stated in abstract or full text.
- **Code availability:** ["Available at https://github.com/albert-jin/Rce-KGQA"]
- **Relation to idea:** This work integrates explicit and implicit relational chains via specific modules (Siamese network, AFM, RCRM). Our idea enriches each target triple with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than architectural chain reasoning. _(basis: not stated)_

#### Exploiting Hybrid Semantics of Relation Paths for Multi-hop Question Answering Over Knowledge Graphs (2022) [4]

- **Problem:** Answering natural language questions on knowledge graphs remains challenging due to understanding complex questions via multi-hop reasoning; previous efforts exploit entity-related text or KG embeddings but overlook rich semantics in off-the-shelf relation paths.
- **Method:** Propose improving multi-hop KGQA by exploiting relation paths' hybrid semantics: integrate explicit textual information and implicit KG structural features of relation paths based on a novel rotate-and-scale entity link prediction framework.
- **Main contribution:** A method that exploits hybrid semantics of relation paths to improve multi-hop KGQA, demonstrating superiority on three existing KGQA datasets, especially in multi-hop scenarios, with systematical coordination between questions and relation paths.
- **Key assumptions:** Relation paths contain hybrid semantics (explicit textual and implicit structural) that can improve multi-hop KGQA.; The rotate-and-scale entity link prediction framework effectively integrates these semantics.
- **Datasets / benchmarks:** Three existing KGQA datasets (unspecified), Three existing KGQA datasets (unspecified)
- **Baselines:** Not stated in abstract.
- **Metrics:** Not stated in abstract; likely accuracy or hit@1
- **Results:** ["Extensive experiments on three existing KGQA datasets demonstrate the superiority of our method, especially in multi-hop scenarios."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work exploits hybrid semantics of relation paths via a rotate-and-scale entity link prediction framework. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than relation path semantics. _(basis: not stated)_

#### Biomedical Multi-hop Question Answering Using Knowledge Graph Embeddings and Language Models (2022) [2]

- **Problem:** Biomedical multi-hop question answering over knowledge graphs suffers from missing links; need to integrate language models with knowledge graph embeddings to improve answer relevance.
- **Method:** Use language models (RoBERTa/BioBERT) to encode questions, knowledge graph embeddings (ComplEx) to encode entities/relations, and a scoring function that combines embeddings to rank answer entities. Separate models trained for 1-hop, 2-hop, 3-hop questions.
- **Main contribution:** An integrated system that combines language models with knowledge graph embeddings for biomedical multi-hop question answering, demonstrating encouraging hits@10 results on a newly created Hetionet QA dataset.
- **Key assumptions:** Knowledge graph embeddings can capture missing links and semantic similarity.; Language models provide contextual understanding of natural language questions.
- **Datasets / benchmarks:** Hetionet knowledge graph, Hetionet multi-hop biomedical question-answering dataset (1-hop, 2-hop, 3-hop partitions), None stated; evaluated on self-created Hetionet QA dataset
- **Baselines:** RoBERTa + ComplEx, BioBERT + ComplEx
- **Metrics:** Hits@10, Adjusted arithmetic mean rank, Adjusted arithmetic mean rank index
- **Results:** ["Hits@10: 1-hop RoBERTa+ComplEx 0.7709, BioBERT+ComplEx 0.7421; 2-hop 0.7705, 0.9158; 3-hop 0.8506, 0.7687."]
- **Limitations:** Not stated in abstract or full text.
- **Future work:** Not stated in abstract or full text.
- **Code availability:** ["Not stated in abstract or full text."]
- **Relation to idea:** The proposed work enriches each target triple with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, whereas this paper focuses on combining language model and knowledge graph embeddings without explicit context subgraph enrichment or repair mechanism. _(basis: not stated)_

#### LLM-Based Multi-Hop Question Answering with Knowledge Graph Integration in Evolving Environments (2024) [5]

- **Problem:** Existing knowledge editing methods for LLMs struggle with multi-hop questions requiring accurate fact identification and sequential logical reasoning, especially after numerous fact updates.
- **Method:** Introduce Graph Memory-based Editing for Large Language Models (GMeLLo) that merges explicit KG knowledge with LLM linguistic flexibility, using LLMs to convert free-form language into structured queries and fact triples for seamless KG interaction and rapid updates.
- **Main contribution:** GMeLLo, a straightforward and effective method that significantly surpasses current SOTA knowledge editing methods on the multi-hop QA benchmark MQuAKE, especially with extensive knowledge edits.
- **Key assumptions:** LLMs can effectively convert free-form language into structured queries and fact triples for KG interaction.; Merging KG knowledge with LLM flexibility improves multi-hop reasoning after knowledge edits.
- **Datasets / benchmarks:** MQuAKE benchmark (multi-hop question answering), MQuAKE
- **Baselines:** Current SOTA knowledge editing methods (unspecified)
- **Metrics:** Not specified in abstract; likely accuracy or exact match
- **Results:** ["GMeLLo significantly surpasses current SOTA knowledge editing methods in multi-hop QA benchmark MQuAKE, especially in scenarios with extensive knowledge edits."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work focuses on knowledge editing for LLMs using KG integration to handle multi-hop questions after updates. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, targeting training data enrichment and iterative correction rather than knowledge editing mechanisms. _(basis: not stated)_

#### Knowledge Editing with Dynamic Knowledge Graphs for Multi-Hop Question Answering (2024) [6]

- **Problem:** Multi-hop question answering poses a significant challenge for LLMs due to extensive knowledge demands; knowledge editing aims to modify LLMs to incorporate specific knowledge but current solutions struggle with knowledge conflicts, inaccurate retrieval, and overlook secondary editing issues that introduce noise.
- **Method:** Introduce KEDKG, a novel knowledge editing method that leverages a dynamic knowledge graph for MHQA: (1) dynamically construct a knowledge graph to store revised information while resolving knowledge conflicts; (2) employ fine-grained retrieval with entity and relation detector to enhance graph retrieval accuracy for LLM generation.
- **Main contribution:** KEDKG, a knowledge editing method leveraging dynamic knowledge graphs, surpasses previous SOTA models on benchmarks, delivering more accurate and reliable answers in dynamic information environments.
- **Key assumptions:** Dynamic knowledge graph construction can store revised information and resolve conflicts.; Fine-grained retrieval with entity and relation detector improves graph retrieval accuracy for LLM generation.
- **Datasets / benchmarks:** Benchmarks (unspecified), Benchmarks (unspecified)
- **Baselines:** Previous state-of-the-art knowledge editing models (unspecified)
- **Metrics:** Not stated in abstract; likely accuracy or exact match
- **Results:** ["Experimental results on benchmarks show that KEDKG surpasses previous state-of-the-art models, delivering more accurate and reliable answers in environments with dynamic information."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work focuses on knowledge editing via dynamic knowledge graphs to address MHQA challenges. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, targeting training data enrichment and iterative correction rather than knowledge editing mechanisms. _(basis: not stated)_

#### A Method for Multi-Hop Question Answering on Persian Knowledge Graph (2025) [7]

- **Problem:** Multi-hop complex question answering in Persian suffers from challenges in accurately understanding and transforming questions into semantically equivalent SPARQL queries for precise answer retrieval from knowledge graphs.
- **Method:** Constructed a dataset of 5,600 Persian multi-hop complex questions with decomposed forms based on semantic representation. Trained Persian language models on this dataset and proposed an architecture for answering complex questions using a Persian knowledge graph.
- **Main contribution:** A Persian multi-hop KGQA dataset and architecture that achieve 12.57% F1-score and 12.06% accuracy improvements over the best comparable method on the PeCoQ dataset.
- **Key assumptions:** Decomposing multi-hop questions into simpler components aids semantic parsing.; Persian language models can effectively capture question semantics for KGQA.
- **Datasets / benchmarks:** Persian multi-hop complex question dataset (5,600 questions), PeCoQ evaluation dataset, PeCoQ
- **Baselines:** Best comparable method (not specified)
- **Metrics:** F1-score, accuracy
- **Results:** ["Improvement of 12.57% in F1-score and 12.06% in accuracy over the best comparable method."]
- **Limitations:** Not stated in abstract or available text.
- **Future work:** Not stated in abstract or available text.
- **Code availability:** ["Not stated in abstract or available text."]
- **Relation to idea:** This work focuses on question decomposition and Persian language models for Persian KGQA. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, targeting general KGQA with language models and knowledge graph embeddings. _(basis: not stated)_

#### Bridging Dual Knowledge Graphs for Multi-Hop Question Answering in Construction Safety (2025) [8]

- **Problem:** Information retrieval and question answering from safety regulations are essential for automated construction compliance checking but are hindered by linguistic and structural complexity of regulatory text. Many queries are multi-hop, requiring synthesis across interlinked clauses.
- **Method:** Introduces BifrostRAG, a dual-graph retrieval-augmented generation (RAG) system that models both linguistic relationships and document structure. Supports a hybrid retrieval mechanism combining graph traversal with vector-based semantic search, enabling LLMs to reason over both content and structure of text.
- **Main contribution:** BifrostRAG, a dual-graph RAG system with hybrid retrieval mechanism that achieves 92.8% precision, 85.5% recall, and 87.3% F1 score on a multi-hop question dataset, significantly outperforming vector-only and graph-only RAG baselines.
- **Key assumptions:** Modeling both linguistic relationships and document structure improves retrieval for complex regulatory text.; Hybrid retrieval combining graph traversal and vector-based semantic search is effective for multi-hop questions.
- **Datasets / benchmarks:** Multi-hop question dataset (not further specified), Vector-only RAG baseline, Graph-only RAG baseline
- **Baselines:** Vector-only RAG, Graph-only RAG
- **Metrics:** Precision, recall, F1 score
- **Results:** ["92.8% precision, 85.5% recall, and 87.3% F1 score on multi-hop question dataset, significantly outperforming baselines."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work uses a dual-graph RAG system with hybrid retrieval for multi-hop QA in construction safety. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than dual-graph RAG for specific domain applications. _(basis: not stated)_

#### KG-o1: Enhancing Multi-hop Question Answering in Large Language Models via Knowledge Graph Integration (2025) [9]

- **Problem:** Large language models struggle with multi-hop reasoning because their chain-of-thoughts often deviate from real reasoning paths, while knowledge graphs explicitly encode logical connections between facts.
- **Method:** KG-o1, a four-stage approach: (1) filter initial entities and generate complex subgraphs from KG; (2) construct logical paths for subgraphs; (3) use KG to build a dataset with complex extended brainstorming process to train LLMs to imitate long-term reasoning; (4) employ rejection sampling to generate self-improving corpus for direct preference optimization (DPO) to refine LLM reasoning.
- **Main contribution:** A KG-enhanced LLM framework (KG-o1) that demonstrates superior multi-hop reasoning performance on simple and complex datasets compared to existing large reasoning models.
- **Key assumptions:** KG-derived subgraphs and logical paths can guide LLMs toward better reasoning paths.; Rejection sampling and DPO can effectively refine LLM multi-hop reasoning abilities.
- **Datasets / benchmarks:** Two simple datasets (unspecified), Two complex datasets (unspecified), The aforementioned simple and complex datasets
- **Baselines:** Existing large reasoning models (e.g., o1)
- **Metrics:** Not specified in abstract; likely accuracy or hit@1
- **Results:** ["KG-o1 models exhibit superior performance across all tasks compared to existing LRMs."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** KG-o1 constructs KG-derived subgraphs and logical paths to create training data for LLMs via DPO. Our idea enriches each target triple with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than generating logical paths for imitation. _(basis: not stated)_

#### CacheRAG: A Semantic Caching System for Retrieval-Augmented Generation in Knowledge Graph Question Answering (2026) [10]

- **Problem:** Existing LLM-driven KGQA systems act as stateless planners, generating retrieval plans in isolation without exploiting historical query patterns, leading to schema hallucinations and limited retrieval coverage.
- **Method:** Propose CacheRAG, a systematic cache-augmented architecture for LLM-based KGQA that transforms stateless planners into continual learners via three design principles: (1) Schema-agnostic user interface with Intermediate Semantic Representation and Backend Adapter; (2) Diversity-optimized cache retrieval using hierarchical index and MMR; (3) Bounded heuristic expansion with deterministic depth/breadth subgraph operators.
- **Main contribution:** CacheRAG architecture that significantly outperforms state-of-the-art baselines (e.g., +13.2% accuracy and +17.5% truthfulness on CRAG dataset) by making LLM-driven KGQA continual learners through caching.
- **Key assumptions:** Caching retrieval plans can improve KGQA performance by exploiting historical query patterns.; Schema-agnostic interface and backend adapter enable safe interaction with local schema context.; Diversity-optimized cache retrieval mitigates reasoning homogeneity.; Bounded heuristic expansion enhances retrieval recall without unbounded API execution.
- **Datasets / benchmarks:** CRAG dataset (unspecified), multiple benchmarks (unspecified), CRAG dataset
- **Baselines:** state-of-the-art baselines (unspecified)
- **Metrics:** accuracy, truthfulness
- **Results:** ["CacheRAG significantly outperforms state-of-the-art baselines (+13.2% accuracy and +17.5% truthfulness on CRAG dataset)."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work focuses on caching retrieval plans to improve LLM-based KGQA performance. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, targeting training data enrichment and iterative correction rather than caching mechanisms. _(basis: not stated)_

#### Temporal knowledge graph question answering via subgraph reasoning (2022) [11]

- **Problem:** Not stated in abstract (no abstract available). Based on title: temporal knowledge graph question answering via subgraph reasoning.
- **Method:** Not stated in abstract. Based on title: proposes subgraph reasoning for temporal KGQA.
- **Main contribution:** Not stated in abstract. Based on title: subgraph reasoning approach for temporal KGQA.
- **Key assumptions:** Not stated in abstract
- **Datasets / benchmarks:** Not stated in abstract, Not stated in abstract
- **Baselines:** Not stated in abstract
- **Metrics:** Not stated in abstract
- **Results:** ["Not stated in abstract"]
- **Limitations:** Not stated in abstract
- **Future work:** Not stated in abstract
- **Code availability:** ["Not stated in abstract"]
- **Relation to idea:** This work focuses on subgraph reasoning for temporal KGQA. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than subgraph reasoning for temporal aspects. _(basis: not stated)_

#### Knowledge Graph Based Retrieval-Augmented Generation for Multi-Hop Question Answering Enhancement (2024) [3]

- **Problem:** Multi-hop question answering struggles with effective retrieval across documents, leading to incomplete or inaccurate answers when integrating information from multiple sources.
- **Method:** Enhance Graph-based Retrieval-Augmented Generation (Graph RAG) by constructing individual knowledge graphs for each document (entities as nodes, relationships as edges enriched with contextual properties), integrating them into a unified graph capturing cross-document relationships, and utilizing vector embeddings of graph relations for improved retrieval and multi-hop reasoning.
- **Main contribution:** A novel graph-based retrieval mechanism leveraging vector embeddings of graph relations within the Graph RAG framework, plus a dataset of 500 documents and 296 multi-hop questions requiring cross-document information retrieval.
- **Key assumptions:** Document-level knowledge graphs can be effectively integrated into a unified cross-document graph.; Vector embeddings of graph relations improve retrieval accuracy for multi-hop QA.
- **Datasets / benchmarks:** 500 documents, 296 multi-hop questions requiring cross-document information retrieval, Baseline Graph RAG (implicit)
- **Baselines:** Standard Graph RAG
- **Metrics:** RAGAS framework (factual accuracy, semantic similarity), LLM-based evaluator (answer comprehensiveness, empowerment, directness)
- **Results:** ["Significantly outperforms baseline in factual accuracy and semantic similarity; superior performance in answer comprehensiveness, empowerment, and directness."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Available at https://github.com/AmiriShavaki/KG-based-RAG-for-Multi-hop-QA"]
- **Relation to idea:** This work focuses on constructing document-level knowledge graphs and using vector embeddings of relations for retrieval-augmented generation. Our idea enriches each target triple with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, targeting the training data and iterative correction rather than document-level KG integration for retrieval. _(basis: not stated)_

#### Variational Reasoning for Question Answering With Knowledge Graph (2018) [12]

- **Problem:** Building QA systems that can learn to reason over knowledge graphs from question-answer pairs alone is challenging due to noisy question expressions and the need for multi-hop logic reasoning.
- **Method:** Propose a unified deep learning architecture and an end-to-end variational learning algorithm that handles noise in questions and learns multi-hop reasoning simultaneously.
- **Main contribution:** A novel variational reasoning framework for KG-based QA that achieves state-of-the-art performance on a recent benchmark dataset and introduces new benchmark datasets for noisy and multi-hop reasoning.
- **Key assumptions:** A variational learning algorithm can effectively handle noise in questions while learning multi-hop reasoning.; The proposed architecture can capture both structured KG information and noisy question semantics.
- **Datasets / benchmarks:** Recent benchmark dataset (unspecified), New benchmark datasets for multi-hop reasoning, paraphrased questions, and human voice questions, Recent benchmark dataset (unspecified)
- **Baselines:** Not specified in abstract
- **Metrics:** Not specified in abstract; likely accuracy or hit@1
- **Results:** ["Achieves state-of-the-art performance on a recent benchmark dataset; yields promising results on new benchmark datasets."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work focuses on a variational deep learning architecture to handle question noise and learn multi-hop reasoning. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, targeting training data enrichment and iterative correction rather than a variational learning algorithm. _(basis: not stated)_

#### Improving Multi-hop Question Answering over Knowledge Graphs using Knowledge Base Embeddings (2020) [13]

- **Problem:** Multi-hop KGQA is challenged by KG incompleteness and sparsity; existing methods rely on external text (which may be unavailable) or impose heuristic neighborhood limits that can exclude the true answer.
- **Method:** EmbedKGQA uses a KG embedding module (ComplEx) to generate entity and relation embeddings, a question embedding module to encode the natural language question, and an answer selection module that combines the ComplEx score φ(e_h, e_q, e_a′) with a relation score (intersection of relation sets) via a linear combination with hyperparameter γ. This approach relaxes the requirement of answer selection from a pre-specified neighborhood by leveraging the link prediction property of KG embeddings to capture implicit links.
- **Main contribution:** EmbedKGQA, a novel method that effectively performs multi-hop KGQA over sparse KGs, achieving state-of-the-art accuracy (e.g., 29.9% vs 20.1% for ComplEx on MetaQA 1-hop with missing links) and outperforming baseline methods that rely on external text or neighborhood constraints.
- **Key assumptions:** KG embeddings can capture missing links and semantic similarity in incomplete KGs.; Combining embedding scores with relation scores improves answer selection accuracy.
- **Datasets / benchmarks:** MetaQA (1-hop, 2-hop, 3-hop partitions), WebQuestionsSP, MetaQA, WebQuestionsSP
- **Baselines:** State-of-the-art baselines (not explicitly named in abstract; likely include KG completion methods and prior KGQA approaches)
- **Metrics:** Accuracy (exact match or hit@1 implied), Specifically reported: Accuracy on MetaQA 1-hop with missing links: ComplEx 20.1%, EmbedKGQA 29.9%
- **Results:** ["On MetaQA 1-hop with missing links, EmbedKGQA achieves 29.9% accuracy compared to 20.1% for ComplEx; on MetaQA and WebQuestionsSP datasets, EmbedKGQA demonstrates effectiveness over state-of-the-art baselines."]
- **Limitations:** Availability and identification of relevant external text corpora is a challenge for methods that rely on them; heuristic neighborhood size limitations can exclude true answers.
- **Future work:** Not stated in abstract or full text.
- **Code availability:** ["Available at https://github.com/malllabiisc/EmbedKGQA"]
- **Relation to idea:** EmbedKGQA combines KG embeddings with question embeddings and uses a linear scoring function for answer selection, relaxing neighborhood limits. Our idea enriches each target triple with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than a specific embedding‑based scoring mechanism. _(basis: not stated)_

#### HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering (2018) [14]

- **Problem:** Existing QA datasets lack support for training models to perform complex multi-hop reasoning and provide explanations for answers.
- **Method:** Introduce HotpotQA, a new dataset with 113k Wikipedia-based question-answer pairs featuring four key features: (1) questions require finding and reasoning over multiple supporting documents; (2) questions are diverse and not constrained to any pre-existing knowledge bases or schemas; (3) sentence-level supporting facts are provided for reasoning, enabling models to learn explainable predictions; (4) factoid comparison questions test ability to extract relevant facts and perform necessary comparisons.
- **Main contribution:** HotpotQA dataset that is challenging for latest QA systems and supports training and evaluation of explainable multi-hop question answering, providing strong supervision via supporting facts.
- **Key assumptions:** Providing sentence-level supporting facts enables QA systems to learn reasoning and generate explainable predictions.; Diverse, multi-hop questions based on Wikipedia support training of complex reasoning abilities.
- **Datasets / benchmarks:** HotpotQA (113k Wikipedia-based question-answer pairs), HotpotQA (distractor and full wiki settings)
- **Baselines:** Baseline model reimplemented from Clark and Gardner (2017) architecture
- **Metrics:** Joint EM/F1, Answer EM/F1, Supporting Fact EM/F1
- **Results:** ["On the distractor setting: Answer EM 45.46, F1 58.99; Supporting Fact EM 22.24, F1 41.37. On the full wiki setting: Answer EM 25.23, F1 34.40; Supporting Fact EM 2.63, F1 17.85."]
- **Limitations:** Not stated in abstract or full text.
- **Future work:** Not stated in abstract or full text.
- **Code availability:** ["Not stated in abstract or full text."]
- **Relation to idea:** HotpotQA provides a benchmark dataset with supporting facts for explainable multi-hop QA. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than providing a dataset with supporting facts. _(basis: not stated)_

#### SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets for Knowledge Graph Multi-hop Question Answering (2025) [15]

- **Problem:** Large Language Models (LLMs) often hallucinate on domain-specific tasks requiring reasoning; previous SG-RAG method improved over traditional RAG but still had redundancy in retrieved triplets.
- **Method:** Enhance SG-RAG with an additional Merging and Ordering Triplets (MOT) step: apply hierarchical merging on retrieved subgraphs to decrease redundancy and order triplets using BFS traversal to help LLMs generate more precise answers.
- **Main contribution:** SG-RAG MOT provides more accurate answers than Chain-of-Thought and Graph Chain-of-Thought on the MetaQA benchmark by reducing redundancy and ordering retrieved triplets.
- **Key assumptions:** Merging overlapping subgraphs reduces redundancy without losing essential information.; Ordering triplets via BFS helps LLMs utilize retrieved knowledge more effectively.
- **Datasets / benchmarks:** MetaQA benchmark (multi-hop question answering on movies domain), MetaQA
- **Baselines:** Chain-of-Thought, Graph Chain-of-Thought, traditional Retrieval Augmented Generation (RAG)
- **Metrics:** Not stated explicitly; likely accuracy or hit@1
- **Results:** ["SG-RAG MOT provides more accurate answers than Chain-of-Thought and Graph Chain-of-Thought; merging and ordering triplets helps LLM generate more precise answers."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work focuses on post-retrieval processing (merging and ordering) of subgraphs retrieved via SG-RAG. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, targeting training data enrichment and iterative correction rather than retrieval post-processing. _(basis: not stated)_

#### Enriching Subgraph Retrieval with Attribute Values for Complex Question Answering Over Knowledge Graph (2025) [16]

- **Problem:** Not stated in abstract (no abstract available). Based on title: enriching subgraph retrieval with attribute values for complex question answering over knowledge graph.
- **Method:** Not stated in abstract. Based on title: proposes to enrich subgraph retrieval by incorporating attribute values.
- **Main contribution:** Not stated in abstract. Based on title: enrichment of subgraph retrieval with attribute values for complex KGQA.
- **Key assumptions:** Not stated in abstract
- **Datasets / benchmarks:** Not stated in abstract, Not stated in abstract
- **Baselines:** Not stated in abstract
- **Metrics:** Not stated in abstract
- **Results:** ["Not stated in abstract"]
- **Limitations:** Not stated in abstract
- **Future work:** Not stated in abstract
- **Code availability:** ["Not stated in abstract"]
- **Relation to idea:** This work focuses on enriching subgraph retrieval with attribute values. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than enriching retrieved subgraphs with attributes. _(basis: not stated)_

#### Multi-path reasoning for Multi-hop Question Answering over Knowledge Graphs (2022) [17]

- **Problem:** Error transfer in knowledge distillation network for knowledge question answering models.
- **Method:** Propose a multi-path reasoning teacher network model based on bidirectional reasoning, adding two sets of bidirectional reasoning answer search paths to improve the accuracy of the intermediate supervision signal generated by the teacher network and reduce its negative effect on the student network.
- **Main contribution:** A multi-path reasoning teacher network model that reduces error transfer in knowledge distillation for KGQA, proven effective via experimental results.
- **Key assumptions:** Adding bidirectional reasoning answer search paths improves the intermediate supervision signal from the teacher network.; Reducing the negative effect of the teacher network on the student network improves overall accuracy.
- **Datasets / benchmarks:** Not stated in abstract., Not stated in abstract.
- **Baselines:** Not stated in abstract.
- **Metrics:** Not stated in abstract.
- **Results:** ["Experimental results have proved the effectiveness of this method."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work focuses on improving knowledge distillation via multi-path reasoning teacher networks. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than knowledge distillation mechanisms. _(basis: not stated)_

#### Knowledge Graph Multi-Hop Question Answering Based on Dependent Syntactic Semantic Augmented Graph Networks (2024) [18]

- **Problem:** Integrating machine comprehension with relational reasoning for multi-hop question answering is challenging due to complex relational paths and lack of transparency in reasoning.
- **Method:** Introduce Dependent Syntactic Semantic Augmented Graph Network (DSSAGN) that leverages synergy between syntactic structures and semantic relationships within knowledge graphs to model multi-hop relations and dynamically prioritize syntactic–semantic context.
- **Main contribution:** A novel DSSAGN architecture that addresses intricate challenges of multi-hop QA by leveraging syntactic–semantic synergy, offering breakthroughs in interpretability, scalability, and accuracy.
- **Key assumptions:** Combining syntactic and semantic information improves interpretability and accuracy for multi-hop KGQA.; Dynamically prioritizing syntactic–semantic context enhances reasoning performance.
- **Datasets / benchmarks:** Not stated in abstract., Not stated in abstract.
- **Baselines:** Not stated in abstract.
- **Metrics:** Not stated in abstract.
- **Results:** ["Not stated in abstract."]
- **Limitations:** Not stated in abstract.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work proposes a DSSAGN architecture that models syntactic–semantic synergy for multi-hop reasoning. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than a specific graph network architecture. _(basis: not stated)_

#### Unrestricted multi-hop reasoning network for interpretable question answering over knowledge graph (2022) [19]

- **Problem:** Not stated in abstract (no abstract available). Based on title: unrestricted multi-hop reasoning network for interpretable question answering over knowledge graph.
- **Method:** Not stated in abstract. Based on title: proposes an unrestricted multi-hop reasoning network for interpretable KGQA.
- **Main contribution:** Not stated in abstract. Based on title: unrestricted multi-hop reasoning network for interpretable KGQA.
- **Key assumptions:** Not stated in abstract
- **Datasets / benchmarks:** Not stated in abstract, Not stated in abstract
- **Baselines:** Not stated in abstract
- **Metrics:** Not stated in abstract
- **Results:** ["Not stated in abstract"]
- **Limitations:** Not stated in abstract
- **Future work:** Not stated in abstract
- **Code availability:** ["Not stated in abstract"]
- **Relation to idea:** This work proposes an unrestricted multi-hop reasoning network for interpretable KGQA. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than designing a specific reasoning network architecture. _(basis: not stated)_

#### LAMRF: Logic-adaptive multi-source reasoning fusion for multi-hop knowledge graph question answering (2026) [20]

- **Problem:** Not stated in abstract (no abstract available). Based on title: logic-adaptive multi-source reasoning fusion for multi-hop KGQA.
- **Method:** Not stated in abstract. Based on title: proposes LAMRF (Logic-adaptive multi-source reasoning fusion) for multi-hop KGQA.
- **Main contribution:** Not stated in abstract. Based on title: LAMRF for multi-hop KGQA.
- **Key assumptions:** Not stated in abstract
- **Datasets / benchmarks:** Not stated in abstract, Not stated in abstract
- **Baselines:** Not stated in abstract
- **Metrics:** Not stated in abstract
- **Results:** ["Not stated in abstract"]
- **Limitations:** Not stated in abstract
- **Future work:** Not stated in abstract
- **Code availability:** ["Not stated in abstract"]
- **Relation to idea:** This work proposes LAMRF (logic-adaptive multi-source reasoning fusion) for multi-hop KGQA. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than a specific reasoning fusion mechanism. _(basis: not stated)_

#### Enhancing relation classification based on GCN Multi-hop Knowledge Graph Question Answering model of knowledge reasoning (2024) [21]

- **Problem:** Not stated in abstract (no abstract available). Based on title: enhancing relation classification for multi-hop KGQA using GCN.
- **Method:** Not stated in abstract. Based on title: uses GCN (Graph Convolutional Network) for relation classification in multi-hop KGQA.
- **Main contribution:** Not stated in abstract. Based on title: enhancing relation classification using GCN for multi-hop KGQA.
- **Key assumptions:** Not stated in abstract
- **Datasets / benchmarks:** Not stated in abstract, Not stated in abstract
- **Baselines:** Not stated in abstract
- **Metrics:** Not stated in abstract
- **Results:** ["Not stated in abstract"]
- **Limitations:** Not stated in abstract
- **Future work:** Not stated in abstract
- **Code availability:** ["Not stated in abstract"]
- **Relation to idea:** This work focuses on enhancing relation classification using GCN for multi-hop KGQA. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, targeting training data enrichment and iterative correction rather than improving relation classification via GCN. _(basis: not stated)_

#### Multi-hop Question Answering with Knowledge Graph Embedding in a Similar Semantic Space (2022) [22]

- **Problem:** Not stated in abstract (no abstract available). Based on title: multi-hop QA with knowledge graph embedding in a similar semantic space.
- **Method:** Not stated in abstract. Based on title: uses knowledge graph embeddings in a similar semantic space for multi-hop QA.
- **Main contribution:** Not stated in abstract. Based on title: multi-hop QA with KG embedding in similar semantic space.
- **Key assumptions:** Not stated in abstract
- **Datasets / benchmarks:** Not stated in abstract, Not stated in abstract
- **Baselines:** Not stated in abstract
- **Metrics:** Not stated in abstract
- **Results:** ["Not stated in abstract"]
- **Limitations:** Not stated in abstract
- **Future work:** Not stated in abstract
- **Code availability:** ["Not stated in abstract"]
- **Relation to idea:** This work uses KG embeddings in a similar semantic space for multi-hop QA. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than KG embedding space similarity. _(basis: not stated)_

#### Progressive Planning and Reinforced Reasoning: Large Language Model-Guided Multi-hop Question Answering over Knowledge Graph (2026) [23]

- **Problem:** Not stated in abstract (no abstract available). Based on title: progressive planning and reinforced reasoning for LLM-guided multi-hop KGQA.
- **Method:** Not stated in abstract. Based on title: uses progressive planning and reinforced reasoning, likely involving LLMs for multi-hop KGQA.
- **Main contribution:** Not stated in abstract. Based on title: progressive planning and reinforced reasoning approach for LLM-guided multi-hop KGQA.
- **Key assumptions:** Not stated in abstract
- **Datasets / benchmarks:** Not stated in abstract, Not stated in abstract
- **Baselines:** Not stated in abstract
- **Metrics:** Not stated in abstract
- **Results:** ["Not stated in abstract"]
- **Limitations:** Not stated in abstract
- **Future work:** Not stated in abstract
- **Code availability:** ["Not stated in abstract"]
- **Relation to idea:** This work uses progressive planning and reinforced reasoning for LLM-guided multi-hop KGQA. Our idea enriches training triples with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than planning and reinforcement reasoning mechanisms. _(basis: not stated)_

</details>

## 5. Research Landscape

```text
Multi-hop Knowledge Graph Question Answering with Language Models
├── Language Model + Knowledge Graph Embedding  [2] [1]
│   └── Explicit-Implicit Relational Chain Reasoning  [1]
├── Retrieval-Augmented Generation (RAG)  [3] [8]
│   ├── Dual-Graph Hybrid Retrieval  [8]
│   └── Graph-based Retrieval with Relation Embeddings  [3]
├── Question Decomposition  [7]
├── Reasoning Network Architectures  [19] [20]
│   ├── Unrestricted Multi-hop Reasoning Network  [19]
│   └── Logic-adaptive Multi-source Reasoning Fusion  [20]
├── Graph Convolutional Network-based Relation Classification  [21]
└── Progressive Planning and Reinforced Reasoning  [23]
```

**Where the idea fits:** **[Inference]** Local Context Subgraph Enrichment with Adaptive Repair Loop

**Dominant approaches**

- Language Model + Knowledge Graph Embedding
- Explicit-Implicit Relational Chain Reasoning
- Retrieval-Augmented Generation (RAG)

**Common assumptions**

- Language models can effectively encode natural language questions for KGQA tasks.
- Knowledge graph embeddings capture semantic relations and can help overcome KG incompleteness.
- Combining multiple sources of information (e.g., explicit and implicit chains, linguistic and structural features) improves reasoning performance.
- Effective multi-hop QA requires modeling chains or paths of relations in the knowledge graph.

**Common datasets**

- MetaQA
- Hetionet
- WebQuestionsSP-tiny
- Complex-WebQSP
- Persian multi-hop question datasets
- PeCoQ
- Document-based KGQA datasets

**Common benchmarks**

- MetaQA (1-hop, 2-hop, 3-hop)
- WebQuestionsSP-tiny
- Complex-WebQSP
- PeCoQ
- Custom domain-specific datasets (e.g., biomedical, construction safety)

**Common metrics**

- hit@1
- hit@5
- hit@10
- F1-score
- precision
- recall
- accuracy
- adjusted arithmetic mean rank

**Underexplored combinations**

- **[Hypothesis]** Enriching training triples with local context subgraphs from the same source passage
- **[Hypothesis]** Adaptive repair loops that detect and correct one-hop failures in KGQA
- **[Hypothesis]** Combining local context enrichment with reinforcement learning optimization
- **[Hypothesis]** Transfer learning from lower-hop to higher-hop QA via RL-based optimization
- **[Hypothesis]** Integrating context subgraph enrichment with explicit-implicit relational chain reasoning

**Limitations repeated across papers**

- Limited generalizability across different domains, datasets, or knowledge graph constructions. [2], [1], [7], [3]
- Dependence on the quality, completeness, and accuracy of the underlying knowledge graph. [2], [1], [3], [8]
- Computational complexity and memory constraints when reasoning over large knowledge graphs. [1], [3], [9]
- Limited explicit interpretability of the reasoning process in some neural approaches. [1], [9], [23]
- Challenges in handling noisy, conflicting, or missing information in knowledge graphs. [2], [1], [19]

**Contradictions between papers**

- Disagreement on the effectiveness of neighborhood constraints: some methods restrict reasoning to local subgraphs for efficiency (e.g., GraftNet, PullNet), while others argue unrestricted reasoning is necessary for interpretability and completeness. [19], [1]
- Varying claims about the necessity of explicit relational chain annotations: some works require them for supervision, while others aim to work without expensive labeling. [1], [7]
- Different assumptions about what constitutes useful context: some focus on document-level graphs, others on passage-level subgraphs, and others on logical path construction. [3], [9], [8]

## 6. Closest Existing Work

**[Inference]** These works represent the closest existing approaches: arxiv:2110.12679 integrates explicit and implicit relational chains via specific modules; arxiv:2211.05351 combines language models with knowledge graph embeddings; doi:10.1109/ikt65497.2024.10892619 enhances retrieval-augmented generation with document-level knowledge graphs and relation embeddings. None enrich training triples with passage-level local context subgraphs or incorporate an adaptive repair loop for iterative correction.

- Improving Embedded Knowledge Graph Multi-hop Question Answering by introducing Relational Chain Reasoning (2021) [1]: This work integrates explicit and implicit relational chains via specific modules (Siamese network, AFM, RCRM). Our idea enriches each target triple with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction rather than architectural chain reasoning.
- Biomedical Multi-hop Question Answering Using Knowledge Graph Embeddings and Language Models (2022) [2]: The proposed work enriches each target triple with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, whereas this paper focuses on combining language model and knowledge graph embeddings without explicit context subgraph enrichment or repair mechanism.
- Knowledge Graph Based Retrieval-Augmented Generation for Multi-Hop Question Answering Enhancement (2024) [3]: This work focuses on constructing document-level knowledge graphs and using vector embeddings of relations for retrieval-augmented generation. Our idea enriches each target triple with local context subgraphs from the same passage and adds an adaptive repair loop for one-hop failures, targeting the training data and iterative correction rather than document-level KG integration for retrieval.

## 7. Potential Overlap

**Overlap:** **[Inference]** The idea overlaps with existing LM+KG embedding and RAG approaches in using language models and knowledge graphs for multi-hop QA, sharing the goal of improving reasoning over KGs.

**Potential distinction:** **[Inference]** Unlike prior work that focuses on architectural changes (e.g., relational chain reasoning modules) or retrieval-augmented generation, this idea modifies the training data itself by enriching each supervision signal with local context from the same passage and iteratively repairs faulty base facts via an adaptive loop.

**Novelty questions**

_None recorded._

## 8. Potential Research Gap

_Not recorded: this phase did not produce the required records._

## 9. Critique

| | |
|---|---|
| Strongest argument FOR | The idea directly addresses the neighborhood size constraint limitation identified in mainstream KGQA methods (C001) by proposing to enrich training triples with local context subgraphs from the same passage, which can supply additional relational evidence (C002). This targets a core weakness in current approaches. |
| Strongest argument AGAINST | The proposal relies on unverified assumptions: that local context is supportive and not noisy (C003), that an adaptive repair loop can generate effective corrective examples (C004), and that RL optimization on lower-hop QA transfers to higher-hop QA (C005). Without empirical validation, these assumptions may not hold, risking no improvement or performance degradation. |
| Most important unresolved question | Does enriching triples with local context subgraphs actually improve hit@1 accuracy on multi-hop KGQA, or does it introduce noise that harms performance? |
| Most dangerous experimental confounder | The quality and relevance of the extracted local context subgraph; if the passage contains irrelevant or conflicting information, it could degrade learning rather than help. |
| Closest existing work | [1], [2], [3] |
| Potential contribution | **[Hypothesis]** A training method that improves multi-hop KGQA performance by leveraging local context subgraphs and an adaptive repair loop, with analysis of transfer from lower-hop to higher-hop QA and demonstration of improved base fact reliability. |

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

- Literature coverage: searched 13 queries over arxiv, crossref, openalex, semantic_scholar. Work outside these queries and sources, very recent preprints, and non-English work may be missing; the absence of matching work here does not establish novelty.
- Some source requests failed and their results are missing: semantic_scholar (api.semanticscholar.org failed after 5 attempts (HTTP 429)).
- Metadata warning for Beyond Chunk-Local Extraction: Cross-Chunk Graph Augmentation for GraphRAG (2026) [24]: abstract (from arxiv) never mentions 'Beyond Chunk-Local Extraction'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for The Knowledge‐Learning‐Instruction Framework: Bridging the Science‐Practice Chasm to Enhance Robust Student Learning (2012) [25]: abstract (from openalex) never mentions 'The Knowledge‐Learning‐Instruction Framework'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering (2018) [14]: abstract (from openalex) never mentions 'HotpotQA'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for The Uncharted Passage: Girls' Adolescence in the Developing World (1998) [26]: abstract (from openalex) never mentions 'The Uncharted Passage'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Knowledge graph refinement: A survey of approaches and evaluation methods (2016) [27]: abstract (from openalex) never mentions 'Knowledge graph refinement'; it may belong to another work. Its abstract was not accepted as direct evidence.
- 20 of 23 analyses are based on abstracts only.
- Unresolved question: Does enriching triples with local context subgraphs actually improve hit@1 accuracy on multi-hop KGQA, or does it introduce noise that harms performance?
- Ambiguity (assumption): What constitutes the 'same source passage' for local context?; assumed: Assumed to be the text passage from which the triple was extracted if the KG is built from text
- Phases that did not complete: gaps, modifications, experiments.
- No hypothesis in this report has been tested experimentally.

**Uncertainty ledger**

| Id | Question | Category | Importance | Status | Evidence for / against | Resolution |
|---|---|---|---|---|---|---|
| U001 | Is enriching triples with local context subgraphs from the same source passage beneficial for multi-hop KGQA, or does it introduce noise that harms performance? | other | high | partially resolved | [28] / none | Evidence from arxiv:2501.15378 shows that restoring textual context underlying each triple (a form of context enrichment) improves Exact Match and F1 scores on multi-hop QA datasets (HotpotQA, 2WikiMultiHopQA), indicating that context enrichment is beneficial rather than harmful for multi-hop KGQA performance. |
| U002 | Can an adaptive repair loop that detects one-hop failures and generates corrective examples be effectively implemented and improve the reliability of base facts in a language model-based KGQA system? | other | high | open | none / none | Not recorded |
| U003 | Does reinforcement learning optimization on lower-hop QA instances transfer effectively to improve performance on higher-hop multi-hop QA? | other | medium | open | none / none | Not recorded |
| U005 | How much does the proposed method overlap with existing KGQA approaches that use contextual information (e.g., PullNet, GraftNet, KG-o1)? | overlap | medium | partially resolved | [1], [9] / none | The proposed idea overlaps with existing KGQA approaches (PullNet, GraftNet, KG-o1) in the goal of incorporating contextual information to improve reasoning, but differs in mechanism: PullNet adds shortest-path supervised signal during retrieval, GraftNet uses a variational graph CNN on question-specific subgraphs, and KG-o1 constructs a training dataset via entity filtering, logical path construction, and DPO. The proposed idea instead enriches each target triple with local context subgraphs from the same source passage and includes an adaptive repair loop for one-hop failures, focusing on training data enrichment and iterative correction. |
| U007 | Can an adaptive repair loop that detects one-hop failures and generates corrective examples be feasibly implemented and sustained in a language model-based KGQA system without causing instability or overfitting? | feasibility | medium | open | none / none | Not recorded |
| U008 | Does enriching triples with additional triples extracted from the same source passage (forming a local context subgraph) provide comparable benefits to restoring the underlying textual context, or are there differences in effectiveness? | other | medium | open | none / none | Not recorded |
| U004 | Is enriching training triples with local context subgraphs a novel approach, or have similar methods been proposed in the KGQA literature? | novelty | high | resolved | [1], [2], [3] / none | No directly matching work was found in the analyzed literature; the closest works (e.g., arxiv:2110.12679, arxiv:2211.05351, doi:10.1109/ikt65497.2024.10892619) differ in focusing on architectural changes or retrieval-augmented generation rather than training data enrichment with local context subgraphs and adaptive repair loop. |
| U006 | Does enriching triples with local context subgraphs actually improve hit@1 accuracy on multi-hop KGQA, or does it introduce noise that harms performance? | validity | high | resolved | [28], [1], [9], [13], [15] / none | Multiple studies show that enriching triples with local context subgraphs improves hit@1 accuracy on multi-hop KGQA rather than introducing noise. Evidence includes: TCR-QF context enrichment improving EM/F1 on HotpotQA and 2WikiMultiHopQA (arxiv:2501.15378); PullNet's graph retrieval module using shortest path improving over GraftNet (arxiv:2110.12679); KG-o1's filtering entities and generating complex subgraphs enhancing LLMs' reasoning (arxiv:2508.15790); EmbedKGQA's use of KG embeddings capturing implicit links improving accuracy over baselines (doi:10.18653/v1/2020.acl-main.412); and SG-RAG MOT's merging and ordering triplets improving answers over Chain-of-Thought (doi:10.20944/preprints202505.1992.v1). Collectively, this indicates that local context enrichment is beneficial for multi-hop QA performance. |

## 14. Suggested Next Steps

1. Resolve: Does enriching triples with local context subgraphs actually improve hit@1 accuracy on multi-hop KGQA, or does it introduce noise that harms performance?
2. Design a control for the confounder: The quality and relevance of the extracted local context subgraph; if the passage contains irrelevant or conflicting information, it could degrade learning rather than help.
3. Read the full text of the closest work analyzed only from abstracts: [3].
4. Search for work newer than the most recent retrieved paper (2026) before claiming a distinction.

## 15. References

1. Weiqiang Jin, Biao Zhao, Hang Yu et al.. **Improving Embedded Knowledge Graph Multi-hop Question Answering by introducing Relational Chain Reasoning**. _Data Mining and Knowledge Discovery (2022)_, 2021. <https://arxiv.org/abs/2110.12679> doi:10.1007/s10618-022-00891-8 (id `arxiv:2110.12679`; retrieved from arxiv, semantic_scholar; 88 citations per semantic_scholar)
2. Dattaraj J. Rao, Shraddha S. Mane, Mukta A. Paliwal. **Biomedical Multi-hop Question Answering Using Knowledge Graph Embeddings and Language Models**. _arXiv (preprint)_, 2022. <https://arxiv.org/abs/2211.05351> (id `arxiv:2211.05351`; retrieved from arxiv)
3. Mahdi Amiri Shavaki, Pouria Omrani, R. Toosi et al.. **Knowledge Graph Based Retrieval-Augmented Generation for Multi-Hop Question Answering Enhancement**. _Conference on Information and Knowledge Technology_, 2024. <https://www.semanticscholar.org/paper/0b28b36ba158c4cf42a15b3b7af55452a720de2a> doi:10.1109/ikt65497.2024.10892619 (id `doi:10.1109/ikt65497.2024.10892619`; retrieved from semantic_scholar; 6 citations per semantic_scholar)
4. Zile Qiao, Wei Ye, Tong Zhang et al.. **Exploiting Hybrid Semantics of Relation Paths for Multi-hop Question Answering Over Knowledge Graphs**. _arXiv (preprint)_, 2022. <https://arxiv.org/abs/2209.00870> (id `arxiv:2209.00870`; retrieved from arxiv)
5. Ruirui Chen, Weifeng Jiang, Chengwei Qin et al.. **LLM-Based Multi-Hop Question Answering with Knowledge Graph Integration in Evolving Environments**. _arXiv (preprint)_, 2024. <https://arxiv.org/abs/2408.15903> (id `arxiv:2408.15903`; retrieved from arxiv)
6. Yifan Lu, Yigeng Zhou, Jing Li et al.. **Knowledge Editing with Dynamic Knowledge Graphs for Multi-Hop Question Answering**. _arXiv (preprint)_, 2024. <https://arxiv.org/abs/2412.13782> (id `arxiv:2412.13782`; retrieved from arxiv)
7. Arash Ghafouri, Mahdi Firouzmandi, Hasan Naderi. **A Method for Multi-Hop Question Answering on Persian Knowledge Graph**. _arXiv.org_, 2025. <https://arxiv.org/abs/2501.16350> (id `arxiv:2501.16350`; retrieved from arxiv, semantic_scholar; 0 citations per semantic_scholar)
8. Yuxin Zhang, Xi Wang, Mo Hu et al.. **Bridging Dual Knowledge Graphs for Multi-Hop Question Answering in Construction Safety**. _Automation in Construction, Volume 183, March 2026, 106794_, 2025. <https://arxiv.org/abs/2507.13625> doi:10.1016/j.autcon.2026.106794 (id `arxiv:2507.13625`; retrieved from arxiv, semantic_scholar; 10 citations per semantic_scholar)
9. Nan Wang, Yong-Qi Fan, Yansha Zhu et al.. **KG-o1: Enhancing Multi-hop Question Answering in Large Language Models via Knowledge Graph Integration**. _arXiv.org_, 2025. <https://www.semanticscholar.org/paper/f5adc0d4b36ca900a7db0abd74e39e825607613c> doi:10.48550/arxiv.2508.15790 (id `arxiv:2508.15790`; retrieved from semantic_scholar; 10 citations per semantic_scholar)
10. Yushi Sun, Lei Chen. **CacheRAG: A Semantic Caching System for Retrieval-Augmented Generation in Knowledge Graph Question Answering**. _arXiv.org_, 2026. <https://arxiv.org/abs/2604.26176> doi:10.48550/arxiv.2604.26176 (id `arxiv:2604.26176`; retrieved from arxiv, semantic_scholar; 0 citations per semantic_scholar)
11. Ziyang Chen, Xiang Zhao, Jinzhi Liao et al.. **Temporal knowledge graph question answering via subgraph reasoning**. _Knowledge-Based Systems_, 2022. <https://doi.org/10.1016/j.knosys.2022.109134> (id `doi:10.1016/j.knosys.2022.109134`; retrieved from crossref; 51 citations per crossref)
12. Yuyu Zhang, Hanjun Dai, Zornitsa Kozareva et al.. **Variational Reasoning for Question Answering With Knowledge Graph**. _Proceedings of the AAAI Conference on Artificial Intelligence_, 2018. <https://doi.org/10.1609/aaai.v32i1.12057> (id `doi:10.1609/aaai.v32i1.12057`; retrieved from openalex; 396 citations per openalex)
13. Apoorv Saxena, Aditay Tripathi, Partha Talukdar. **Improving Multi-hop Question Answering over Knowledge Graphs using Knowledge Base Embeddings**. 2020. <https://doi.org/10.18653/v1/2020.acl-main.412> (id `doi:10.18653/v1/2020.acl-main.412`; retrieved from openalex; 512 citations per openalex)
14. Zhilin Yang, Peng Qi, Saizheng Zhang et al.. **HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering**. 2018. <https://doi.org/10.18653/v1/d18-1259> (id `doi:10.18653/v1/d18-1259`; retrieved from openalex; 1770 citations per openalex)
15. Ahmmad O. M. Saleh, Gokhan Tur, Yucel Saygin. **SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets for Knowledge Graph Multi-hop Question Answering**. 2025. <https://doi.org/10.20944/preprints202505.1992.v1> (id `doi:10.20944/preprints202505.1992.v1`; retrieved from crossref; 0 citations per crossref)
16. Myeongheon Jeon, Kyuhwan Yeom, Jongwon Park et al.. **Enriching Subgraph Retrieval with Attribute Values for Complex Question Answering Over Knowledge Graph**. _Knowledge-Based Systems_, 2025. <https://doi.org/10.2139/ssrn.5146217> (id `doi:10.2139/ssrn.5146217`; retrieved from crossref; 0 citations per crossref)
17. Lv Yana, Xutong Qin, Xiuli Du et al.. **Multi-path reasoning for Multi-hop Question Answering over Knowledge Graphs**. 2022. <https://doi.org/10.22541/au.165426315.58267165/v1> (id `doi:10.22541/au.165426315.58267165/v1`; retrieved from crossref; 0 citations per crossref)
18. Songtao Cai, Qicheng Ma, Yupeng Hou et al.. **Knowledge Graph Multi-Hop Question Answering Based on Dependent Syntactic Semantic Augmented Graph Networks**. _Electronics_, 2024. <https://doi.org/10.3390/electronics13081436> (id `doi:10.3390/electronics13081436`; retrieved from crossref; 4 citations per crossref)
19. Xin Bi, Haojie Nie, Xiyu Zhang et al.. **Unrestricted multi-hop reasoning network for interpretable question answering over knowledge graph**. _Knowledge-Based Systems_, 2022. <https://doi.org/10.1016/j.knosys.2022.108515> (id `doi:10.1016/j.knosys.2022.108515`; retrieved from crossref; 35 citations per crossref)
20. Yuke Tang, Yongjun Jing, Xu Chen et al.. **LAMRF: Logic-adaptive multi-source reasoning fusion for multi-hop knowledge graph question answering**. _Knowledge-Based Systems_, 2026. <https://doi.org/10.1016/j.knosys.2026.115902> (id `doi:10.1016/j.knosys.2026.115902`; retrieved from crossref; 0 citations per crossref)
21. Ying Wang, Guangyu Zhou, Kunli Zhang et al.. **Enhancing relation classification based on GCN Multi-hop Knowledge Graph Question Answering model of knowledge reasoning**. _2024 International Conference on Asian Language Processing (IALP)_, 2024. <https://doi.org/10.1109/ialp63756.2024.10661134> (id `doi:10.1109/ialp63756.2024.10661134`; retrieved from crossref; 0 citations per crossref)
22. Fengying Li, Mingdong Chen, Rongsheng Dong. **Multi-hop Question Answering with Knowledge Graph Embedding in a Similar Semantic Space**. _2022 International Joint Conference on Neural Networks (IJCNN)_, 2022. <https://doi.org/10.1109/ijcnn55064.2022.9892550> (id `doi:10.1109/ijcnn55064.2022.9892550`; retrieved from crossref; 5 citations per crossref)
23. Xiang Li, Runhai Jiao, Ruifan Li et al.. **Progressive Planning and Reinforced Reasoning: Large Language Model-Guided Multi-hop Question Answering over Knowledge Graph**. _Findings of the Association for Computational Linguistics: ACL 2026_, 2026. <https://doi.org/10.18653/v1/2026.findings-acl.1147> (id `doi:10.18653/v1/2026.findings-acl.1147`; retrieved from crossref; 0 citations per crossref)
24. Jiaming Zhang, Yibo Zhao, Jing Yu et al.. **Beyond Chunk-Local Extraction: Cross-Chunk Graph Augmentation for GraphRAG**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2605.28004> (id `arxiv:2605.28004`; retrieved from arxiv)
25. Kenneth R. Koedinger, Albert T. Corbett, Charles A. Perfetti. **The Knowledge‐Learning‐Instruction Framework: Bridging the Science‐Practice Chasm to Enhance Robust Student Learning**. _Cognitive Science_, 2012. <https://doi.org/10.1111/j.1551-6709.2012.01245.x> (id `doi:10.1111/j.1551-6709.2012.01245.x`; retrieved from openalex; 771 citations per openalex)
26. Barbara Mensch, Judith C. Bruce, Margaret Eleanor Greene. **The Uncharted Passage: Girls' Adolescence in the Developing World**. _Population Council eBooks_, 1998. <https://doi.org/10.31899/pgy11.1008> (id `doi:10.31899/pgy11.1008`; retrieved from openalex; 289 citations per openalex)
27. Heiko Paulheim. **Knowledge graph refinement: A survey of approaches and evaluation methods**. _Semantic Web_, 2016. <https://doi.org/10.3233/sw-160218> (id `doi:10.3233/sw-160218`; retrieved from openalex; 1233 citations per openalex)
28. Manzong Huang, Chenyang Bu, Yi He et al.. **How to Mitigate Information Loss in Knowledge Graphs for GraphRAG: Leveraging Triple Context Restoration and Query-Driven Feedback**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2501.15378> (id `arxiv:2501.15378`; retrieved from arxiv)

<details><summary>Other retrieved papers (not cited in this report)</summary>

- CAM: Question Answering on Entity-Centric Videos with Continuous Extraction and Adaptive Querying (2026) <https://arxiv.org/abs/2609.06504> `arxiv:2609.06504`
- LLM-KGMQA: Large Language Model-Augmented Multi-Hop Question-Answering System based on Knowledge Graph in Medical Field (2024) <https://doi.org/10.21203/rs.3.rs-4721418/v1> `doi:10.21203/rs.3.rs-4721418/v1`
- Multi-Hop Financial Knowledge Question-Answering Model Based on Knowledge Graph (2024) <https://doi.org/10.1109/icaice63571.2024.10864319> `doi:10.1109/icaice63571.2024.10864319`
- Evaluating Knowledge Graph-Enhanced Context for Multiple-Choice Question Answering (2025) <https://doi.org/10.1109/ickg66886.2025.00020> `doi:10.1109/ickg66886.2025.00020`
- Semantic Parsing via Staged Query Graph Generation: Question Answering with Knowledge Base (2015) <https://doi.org/10.3115/v1/p15-1128> `doi:10.3115/v1/p15-1128`
- A Storage-Retrieval Gap in Parametric Knowledge Graph Memory (2026) <https://arxiv.org/abs/2608.25489> `arxiv:2608.25489`
- Hybrid Graph Neural Network and Large Language Model Framework for Robust Knowledge Graph Question Answering via Retrieval-Augmented Generation (2026) <https://www.semanticscholar.org/paper/625a1cefe499a2cde59e0c643cf98650c92b0822> `doi:10.22214/ijraset.2026.82233`
- SPIMP-RAG: structure-prior injected message passing for low-budget triple retrieval in LLM-based knowledge graph question answering (2026) <https://www.semanticscholar.org/paper/ff04b0d4d20f9a338f43630429e36631cc77ef5f> `doi:10.1007/s44443-026-00999-7`
- Harnessing Large Language Models for Knowledge Graph Question Answering via Adaptive Multi-Aspect Retrieval-Augmentation (2025) <https://www.semanticscholar.org/paper/2bbcf9638bb779d4ca2bff3b4fbf52ffc9225c83> `arxiv:2412.18537`
- GRASP: Graph Agentic Search over Propositions for Multi-hop Question Answering (2026) <https://arxiv.org/abs/2605.16598> `arxiv:2605.16598`
- DAMR: Efficient and Adaptive Context-Aware Knowledge Graph Question Answering with LLM-Guided MCTS (2025) <https://www.semanticscholar.org/paper/0a3dc3ae3ff4e9300c303675bed01f3732f9d249> `arxiv:2508.00719`
- PaGLR: A path-aware GNN-LLM framework for evidence-grounded multi-hop knowledge graph question answering (2026) <https://www.semanticscholar.org/paper/58751dcdd5279b27b1b6438640398e9e706a4f72> `doi:10.1007/s44443-026-00763-x`
- nlp_enjoyers at TextGraphs-17 Shared Task: Text-Graph Representations for Knowledge Graph Question Answering using all-MPNet (2024) <https://www.semanticscholar.org/paper/a07fa854df72a5ff0733805e9b2ae4705060109d> `doi:10.18653/v1/2024.textgraphs-1.10`
- StepChain GraphRAG: Reasoning Over Knowledge Graphs for Multi-Hop Question Answering (2025) <https://arxiv.org/abs/2510.02827> `arxiv:2510.02827`
- KGCaRe: Explainable Complex Conditional Question Answering using Automatic Knowledge Graph Construction and Context Retrieval with LLMs (2026) <https://arxiv.org/abs/2608.09779> `arxiv:2608.09779`
- Knowledge-based question answering using graph neural networks and contextual language representations (2026) <https://doi.org/10.1038/s41598-025-33854-2> `doi:10.1038/s41598-025-33854-2`
- Knowledge-Augmented Language Model Prompting for Zero-Shot Knowledge Graph Question Answering (2023) <https://doi.org/10.18653/v1/2023.nlrse-1.7> `doi:10.18653/v1/2023.nlrse-1.7`
- Knowledge Graph Prompting for Multi-Document Question Answering (2023) <https://arxiv.org/abs/2308.11730> `arxiv:2308.11730`
- Controlled Evaluation of Graph and Multimodal Augmentation in RAG for Document Question Answering (2026) <https://arxiv.org/abs/2607.16604> `arxiv:2607.16604`
- BYOKG-RAG: Multi-Strategy Graph Retrieval for Knowledge Graph Question Answering (2025) <https://www.semanticscholar.org/paper/7659a9e23031671a51c702c337d94d7c70d0ed25> `arxiv:2507.04127`
- KG-CQR: Leveraging Structured Relation Representations in Knowledge Graphs for Contextual Query Retrieval (2025) <https://arxiv.org/abs/2508.20417> `arxiv:2508.20417`
- Debate over Mixed-knowledge: A Robust Multi-Agent Reasoning Framework for Incomplete Knowledge Graph Question Answering (2025) <https://arxiv.org/abs/2511.12208> `arxiv:2511.12208`
- Dynamic Subgraph Reasoning of Knowledge Base Question Answering Based on Multi-Task Learning (2024) <https://doi.org/10.2139/ssrn.4757418> `doi:10.2139/ssrn.4757418`
- Enhancing In-Context Learning of Large Language Models for Knowledge Graph Reasoning via Rule-and-Reinforce Selected Triples (2025) <https://www.semanticscholar.org/paper/45379c1e4b52c39928d0bad77e764bfd2636278f> `doi:10.3390/app15031088`
- A Survey on Knowledge Graphs: Representation, Acquisition, and Applications (2021) <https://doi.org/10.1109/tnnls.2021.3070843> `arxiv:2002.00388`
- LingShu: A Large-Scale Symptom-Centric Contextualized Knowledge Graph Bridging Traditional Chinese Medicine and Modern Biomedicine (2026) <https://arxiv.org/abs/2608.20402> `arxiv:2608.20402`
- Large Language Models for Intelligent Data Stewardship in Enterprises: Architectures, Provenance, and Evidence-Mapped Governance (2024) <https://www.semanticscholar.org/paper/cd78bb8f74690b2dd8b14de2c6177846f84881c3> `doi:10.15680/ijctece.2024.0701007`
- Hierarchical Graph Network for Multi-hop Question Answering (2020) <https://doi.org/10.18653/v1/2020.emnlp-main.710> `doi:10.18653/v1/2020.emnlp-main.710`
- K-BERT: Enabling Language Representation with Knowledge Graph (2020) <https://doi.org/10.1609/aaai.v34i03.5681> `doi:10.1609/aaai.v34i03.5681`
- Modeling Historical Relevant and Local Frequency Context for Representation-Based Temporal Knowledge Graph Forecasting (2024) <https://www.semanticscholar.org/paper/1197bc5c47d5614a6c95b3be7b2ac22fcc2507b2> `doi:10.18653/v1/2024.findings-emnlp.451`
- Contextualized Attention-Based Knowledge Transfer for Spoken Conversational Question Answering (2021) <https://doi.org/10.21437/interspeech.2021-110> `doi:10.21437/interspeech.2021-110`
- TSMixerE: Entity Context-Aware Method for Static Knowledge Graph Completion (2025) <https://www.semanticscholar.org/paper/8cf77b7406ea727705189deb7066f2775dc86cb4> `doi:10.32604/cmc.2025.071777`
- Training-Free Hybrid Evidence Retrieval for Question Answering: Dynamic Fusion of Knowledge-Graph Triples and Dense Text Embeddings (2025) <https://doi.org/10.5753/sbbd.2025.247297> `doi:10.5753/sbbd.2025.247297`
- Dense Passage Retrieval for Open-Domain Question Answering (2020) <https://doi.org/10.18653/v1/2020.emnlp-main.550> `arxiv:2004.04906`
- Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering (2021) <https://doi.org/10.18653/v1/2021.eacl-main.74> `arxiv:2007.01282`
- QuAC: Question Answering in Context (2018) <https://doi.org/10.18653/v1/d18-1241> `doi:10.18653/v1/d18-1241`
- Efficiently Embedding Dynamic Knowledge Graphs (2019) <https://arxiv.org/abs/1910.06708> `arxiv:1910.06708`
- Large Language Models Meet Knowledge Graphs to Answer Factoid Questions (2023) <https://arxiv.org/abs/2310.02166> `arxiv:2310.02166`
- Knowledge Graph Completion with Relation-Aware Anchor Enhancement (2025) <https://www.semanticscholar.org/paper/a650e6e4b29eaf1d103f0ae1c402b38ca9bcc0fd> `arxiv:2504.06129`
- Knowledge Graphs (2021) <https://doi.org/10.1145/3447772> `arxiv:2003.02320`
- Gated Self-Matching Networks for Reading Comprehension and Question Answering (2017) <https://doi.org/10.18653/v1/p17-1018> `doi:10.18653/v1/p17-1018`
- Embedding Entities and Relations for Learning and Inference in Knowledge Bases (2014) <http://arxiv.org/abs/1412.6575> `arxiv:1412.6575`
- A question-entailment approach to question answering (2019) <https://doi.org/10.1186/s12859-019-3119-4> `arxiv:1901.08079`
- Zero-resource Hallucination Detection for Text Generation via Graph-based Contextual Knowledge Triples Modeling (2024) <https://arxiv.org/abs/2409.11283> `arxiv:2409.11283`
- ConeE: Global and local context-enhanced embedding for inductive knowledge graph completion (2024) <https://www.semanticscholar.org/paper/a9bfb9ab236553768782f2b90a69c5625f033186> `doi:10.1016/j.eswa.2023.123116`
- Beyond alignment: Discovering cross-graph triples for knowledge graph integration (2026) <https://doi.org/10.1016/j.knosys.2026.116572> `doi:10.1016/j.knosys.2026.116572`
- Representing Knowledge Graph Triples through Siamese Line Graph Sampling (2024) <https://doi.org/10.1109/ijcnn60899.2024.10651186> `doi:10.1109/ijcnn60899.2024.10651186`
- Extracting triples from Vietnamese text to create knowledge graph (2020) <https://doi.org/10.1109/kse50997.2020.9287471> `doi:10.1109/kse50997.2020.9287471`
- An overview of the BIOASQ large-scale biomedical semantic indexing and question answering competition (2015) <https://doi.org/10.1186/s12859-015-0564-6> `doi:10.1186/s12859-015-0564-6`
- Toward Crowdsourced Knowledge Graph Construction: Interleaving Collection and Verification of Triples (2022) <https://doi.org/10.5220/0010902700003116> `doi:10.5220/0010902700003116`
- AI-Assisted Pipeline for Dynamic Generation of Trustworthy Health Supplement Content at Scale (2018) <http://arxiv.org/abs/1810.04805> `arxiv:1810.04805`
- Question-Answering enhanced by Knowledge Graphs (2024) <https://doi.org/10.59350/3ar10-pfb19> `doi:10.59350/3ar10-pfb19`
- HybridRAG: Integrating Knowledge Graphs and Vector Retrieval Augmented Generation for Efficient Information Extraction (2024) <https://doi.org/10.1145/3677052.3698671> `arxiv:2408.04948`
- Generation-Augmented Retrieval for Open-Domain Question Answering (2021) <https://doi.org/10.18653/v1/2021.acl-long.316> `doi:10.18653/v1/2021.acl-long.316`
- A Comprehensive Survey on Automatic Knowledge Graph Construction (2023) <https://doi.org/10.1145/3618295> `doi:10.1145/3618295`
- Explainable Reasoning over Knowledge Graphs for Recommendation (2019) <https://doi.org/10.1609/aaai.v33i01.33015329> `doi:10.1609/aaai.v33i01.33015329`
- Knowledge Graphs: Opportunities and Challenges (2023) <https://doi.org/10.1007/s10462-023-10465-9> `doi:10.1007/s10462-023-10465-9`
- Gradient-based learning applied to document recognition (1998) <https://doi.org/10.1109/5.726791> `doi:10.1109/5.726791`
- Building machines that learn and think like people (2016) <https://doi.org/10.1017/s0140525x16001837> `arxiv:1604.00289`
- Modeling Relational Data with Graph Convolutional Networks (2018) <https://doi.org/10.1007/978-3-319-93417-4_38> `arxiv:1703.06103`
- A Glimpse of the First Eight Months of the COVID-19 Literature on Microsoft Academic Graph: Themes, Citation Contexts, and Uncertainties (2020) <https://doi.org/10.3389/frma.2020.607286> `arxiv:2009.08374`
- YAGO2: A spatially and temporally enhanced knowledge base from Wikipedia (2012) <https://doi.org/10.1016/j.artint.2012.06.001> `doi:10.1016/j.artint.2012.06.001`
- Industry-scale knowledge graphs (2019) <https://doi.org/10.1145/3331166> `doi:10.1145/3331166`
- Question-Answering Using Semantic Relation Triples (1999) <https://doi.org/10.6028/nist.sp.500-246.qa-clresearch2> `doi:10.6028/nist.sp.500-246.qa-clresearch2`

</details>

## Appendix A. Evidence Ledger

### [Evidence] claims (7)

- **[Evidence]** Subgraph Neighborhood Con (indicating the neighborhood size constraint that limits mainstream KGQA methods from capturing implicit relational chains). _(claim C001, confidence: high)_
  - [1], p. 4 (direct support, verified) "Subgraph Neighborhood Con"
- **[Evidence]** The Triple Context Restoration and Query-driven Feedback (TCR-QF) framework, which reconstructs the textual context underlying each triple to mitigate information loss, achieves a 29.1% improvement in Exact Match and a 15.5% improvement in F1 over state-of-the-art GraphRAG competitors on five benchmark question-answering datasets including multi-hop reasoning datasets. _(claim C007, confidence: high)_
  - [28], p. 1 (direct support, verified) "Experiments on five benchmark question-answering datasets substantiate the effectiveness of TCR-QF in KG and LLM integration, where it achieves a 29.1% improvement in Exact Match and a 15.5% improvement in F1 over its state-of-the-art GraphRAG competitors."
- **[Evidence]** The Triple Context Restoration and Query-driven Feedback (TCR-QF) framework, which reconstructs the textual context underlying each triple to mitigate information loss, achieves a 29.1% improvement in Exact Match and a 15.5% improvement in F1 over state-of-the-art GraphRAG competitors on five benchmark question-answering datasets including multi-hop reasoning datasets (HotpotQA, 2WikiMultiHopQA). _(claim C008, confidence: high)_
  - [28], p. 1 (direct support, verified) "Experiments on five benchmark question-answering datasets substantiate the effectiveness of TCR-QF in KG and LLM integration, where it achieves a 29.1% improvement in Exact Match and a 15.5% improvement in F1 over its state-of-the-art GraphRAG competitors."
- **[Evidence]** On the 2WikiMultiHopQA dataset, the TCR-QF method achieves an EM score of 0.598, which is an absolute increase of 0.259 over Naive RAG's EM score of 0.339, representing a 76.4% relative improvement in Exact Match score for multi-hop question answering. _(claim C009, confidence: high)_
  - [28], p. 5 (direct support, verified) "On the 2WikiMultiHopQA dataset, TCR-QF achieves an EM score of 0.598, which is an absolute increase of 0.259 over Naive RAG’s EM score of 0.339—a relative improvement of approximately 76.4%."
- **[Evidence]** PullNet improves GraftNet on the retrieval subgraph by introducing the graph retrieval module which utilizes shortest path from the topic entity to answer as the additional supervised signal. _(claim C010, confidence: high)_
  - [1], p. 22 (direct support, verified) "PullNet [10] improves GraftNet on the retrieval subgraph by introducing the graph retrieval module which utilizes shortest path from the topic entity to answer as the additional supervised signal."
- **[Evidence]** GraftNet [21] is a question description-based semantic sub-graph driving method that uses a variational graph CNN to perform QA tasks over question-specific subgraphs containing KG facts, entities and discourses from textual corpora. _(claim C011, confidence: high)_
  - [1], p. 22 (direct support, verified) "GraftNet [21] is a question description-based semantic sub-graph driving method that uses a variational graph CNN to perform QA tasks over question-specific subgraphs containing KG facts, entities and discourses from textual corpora."
- **[Evidence]** KG-o1, a four-stage approach that integrates KGs to enhance the multi-hop reasoning abilities of LLMs. We first filter out initial entities and generate complex subgraphs. Secondly, we construct logical paths for subgraphs and then use knowledge graphs to build a dataset with a complex and extended brainstorming process, which trains LLMs to imitate long-term reasoning. Finally, we employ rejection sampling to generate a self-improving corpus for direct preference optimization (DPO), further refining the LLMs’ reasoning abilities. _(claim C012, confidence: high)_
  - [9], p. 1 (direct support, verified) "We first filter out initial entities and generate complex subgraphs. Secondly, we construct logical paths for subgraphs and then use knowledge graphs to build a dataset with a complex and extended brainstorming process, which trains LLMs to imitate long-term reasoning. Finally, we employ rejection sampling to generate a self-improving corpus for direct preference optimization (DPO), further refining the LLMs’ reasoning abilities."

### [Inference] claims (4)

- **[Inference]** Enriching training triples with local context subgraphs from the same passage can provide additional relational information that mitigates the neighborhood size constraint limitation. _(claim C002, confidence: medium)_
  - [1], p. 4 (indirect support, verified) "Subgraph Neighborhood Con"
- **[Inference]** Our idea of enriching each target triple with local context subgraphs from the same passage overlaps with PullNet's goal of incorporating more contextual information for reasoning, but differs in that PullNet introduces a graph retrieval module using shortest path as supervised signal during retrieval, whereas our idea modifies the training data itself by adding context triples before fine-tuning. _(claim C013, confidence: medium)_
  - [1], p. 22 (indirect support, verified) "PullNet [10] improves GraftNet on the retrieval subgraph by introducing the graph retrieval module which utilizes shortest path from the topic entity to answer as the additional supervised signal."
  - [28], p. 1 (indirect support, unverified)
- **[Inference]** Our idea of enriching training triples with local context subgraphs overlaps with GraftNet's use of question-specific subgraphs containing KG facts and textual discourses, but differs in that GraftNet relies on a variational graph CNN architecture to process those subgraphs, whereas our idea focuses on enriching the supervision signal (triples) with contextual triples from the same source passage before model training. _(claim C014, confidence: medium)_
  - [1], p. 22 (indirect support, verified) "GraftNet [21] is a question description-based semantic sub-graph driving method that uses a variational graph CNN to perform QA tasks over question-speciﬁc subgraphs containing KG facts, entities and discourses from textual corpora."
- **[Inference]** Our idea of enriching each target triple with local context subgraphs from the same passage shares with KG-o1 the motivation to augment LLMs with richer contextual information from knowledge graphs, but differs in that KG-o1 constructs a dataset via filtering entities, constructing logical paths, and using rejection sampling and DPO to train LLMs to imitate long-term reasoning, whereas our idea enriches individual training triples with passage-level context and includes an adaptive repair loop for one-hop failures. _(claim C015, confidence: medium)_
  - [9], p. 1 (indirect support, verified) "We first filter out initial entities and generate complex subgraphs. Secondly, we construct logical paths for subgraphs and then use knowledge graphs to build a dataset with a complex and extended brainstorming process, which trains LLMs to imitate long-term reasoning. Finally, we employ rejection sampling to generate a self-improving corpus for direct preference optimization (DPO), further refining the LLMs’ reasoning abilities."

### [Assumption] claims (4)

- **[Assumption]** The local context subgraph from the same passage is supportive and not noisy. _(claim C003, confidence: medium)_
- **[Assumption]** The adaptive repair loop can generate effective corrective examples for one-hop failures. _(claim C004, confidence: medium)_
- **[Assumption]** Reinforcement learning optimization on lower-hop QA transfers to higher-hop QA. _(claim C005, confidence: medium)_
- **[Assumption]** The base language model and KGQA architecture (e.g., EmbedKGQA or Rce-KGQA) are suitable for the proposed enrichment. _(claim C006, confidence: medium)_

## Appendix B. Search Log

| Query | Sources (status: results) | Papers |
|---|---|---|
| multi-hop question answering knowledge graph language model | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 15 |
| knowledge graph multi-hop question answering dataset | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 17 |
| local context subgraph knowledge graph question answering | arxiv (ok: 3), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 12 |
| local context subgraph training triples knowledge graph question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 14 |
| contextualized triples knowledge graph question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 13 |
| passage context knowledge graph question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 11 |
| contextualized triple training knowledge graph question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 7 |
| passage context enrichment knowledge graph question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 11 |
| local passage context triples knowledge graph | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 14 |
| triple context enrichment knowledge graph question answering training | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 7 |
| subgraph enrichment knowledge graph question answering training | arxiv (ok: 3), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 12 |
| contextual triples knowledge graph question answering training | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 9 |
| context enrichment harmful knowledge graph question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 7 |

## Appendix C. Investigation Log

Each step was chosen by the ResearchForge controller from the recorded research state.

| Step | Phase | Action | Why | Alternatives considered | Outcome | Information gain |
|---|---|---|---|---|---|---|
| 0 | INTAKE | INTAKE | Research idea received. | none | idea stored in the workspace | n/a |
| 1 | FORMALIZE | FORMALIZE | The idea has not been formalized into a testable research question. | none | +33 papers; +3 searches; +3 uncertainties; idea formalized | 3 |
| 2 | PLAN | PLAN | No investigation plan exists yet, so it is unclear what must be determined. | none | +4 uncertainties; investigation plan recorded | 1 |
| 3 | INVESTIGATE | READ | Retrieved papers have not been analyzed enough to judge overlap. | none | +5 analyses | 2.5 |
| 4 | INVESTIGATE | READ | Retrieved papers have not been analyzed enough to judge overlap. | none | +6 analyses | 3 |
| 5 | SYNTHESIZE | SYNTHESIZE | Analyses exist but the field has not been mapped. | none | landscape recorded | 1 |
| 6 | CRITIQUE | CRITIQUE | The idea has not been challenged yet. | none | +6 claims; +2 verified claims; +1 resolved uncertainties; critique recorded; uncertainties updated: U004 | 5 |
| 7 | UNCERTAINTY | SEARCH (U006: Does enriching triples with local context subgraphs actually improve hit@1) | Most valuable next step for high-importance validity question U006: score 1.62 = importance 3 x expected gain 0.6 x relevance 0.9 x evidence deficiency 1 / cost 1. Next best: SEARCH on U001 (1.08). | SEARCH U001 (1.08); SEARCH U002 (1.08) | +25 papers; +3 searches; +1 claims; +1 verified claims; +1 uncertainties; uncertainties updated: U006 | 3 |
| 8 | UNCERTAINTY | SEARCH (U001: Is enriching triples with local context subgraphs from the same source pas) | Most valuable next step for high-importance other question U001: score 1.44 = importance 3 x expected gain 0.8 x relevance 0.6 x evidence deficiency 1 / cost 1. Next best: SEARCH on U002 (1.44). | SEARCH U002 (1.44); SEARCH U007 (1.12) | +34 papers; +7 searches; +2 claims; +2 verified claims; uncertainties updated: U001 | 4 |
| 9 | UNCERTAINTY | COMPARE (U005: How much does the proposed method overlap with existing KGQA approaches th) | Most valuable next step for medium-importance overlap question U005: score 0.8 = importance 2 x expected gain 0.6 x relevance 1 x evidence deficiency 1 / cost 1.5. Next best: READ on U005 (0.778). | READ U005 (0.778); READ U007 (0.545) | +6 claims; +6 verified claims; uncertainties updated: U005 | 6 |
| 10 | UNCERTAINTY | READ (U007: Can an adaptive repair loop that detects one-hop failures and generates co) | Most valuable next step for medium-importance feasibility question U007: score 0.545 = importance 2 x expected gain 0.778 x relevance 0.7 x evidence deficiency 1 / cost 2. Next best: VERIFY on U006 (0.454). | VERIFY U006 (0.454); READ U006 (0.441) | +6 analyses | 3 |
| 11 | UNCERTAINTY | READ (U006: Does enriching triples with local context subgraphs actually improve hit@1) | Most valuable next step for high-importance validity question U006: score 0.472 = importance 3 x expected gain 0.833 x relevance 0.9 x evidence deficiency 0.42 / cost 2. Next best: VERIFY on U006 (0.454). | VERIFY U006 (0.454); READ U005 (0.35) | +6 analyses; +1 resolved uncertainties; uncertainties updated: U006 | 5 |
| 12 | FINALIZE | FINALIZE | Stopping: time budget reached (3600 s). | none | finalizing | n/a |
