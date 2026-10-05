# ResearchForge Investigation Report

Project `T-2609.12230__scooped__full__s0` · model `ollama-cloud/nemotron-3-super` · status **incomplete**

> Labels: **[Evidence]** directly supported by a verified quote from a retrieved source; **[Inference]** reasoning derived from cited evidence; **[Hypothesis]** proposed, not validated; **[Assumption]** taken as given without evidence; **[Experimental result]** observed in an executed experiment.

## 1. Executive Summary

**Investigated:** Multi‑hop question answering often relies on reasoning over a chain of facts in a knowledge graph, yet current language‑model training typically uses isolated head‑relation‑tail triples, depriving the model of the surrounding context that supports multi‑step inference. We propose to enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. The model will be fine‑tuned under two regimes: one using only the target triple/path and another that also incorporates the supporting context. To improve the reliability of the base facts, we will introduce an adaptive repair loop that detects one‑hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, we will apply reinforcement‑learning‑based optimization on lower‑hop QA instances and evaluate transfer to deeper multi‑hop queries.

**Research question:** Does fine-tuning language models on context-enriched triple subgraphs (with adaptive repair) yield significantly higher multi-hop QA EM/F1 scores on benchmarks like HotpotQA compared to training on isolated triples, and does it improve transfer to deeper multi-hop queries?

**Literature investigated:** 93 papers retrieved from 11 searches (openalex: 43, crossref: 30, arxiv: 19, semantic_scholar: 7); 6 analyzed; 5 rated highly relevant.

**Assessment:** Substantial overlap with existing work. **[Inference]** The retrieved work arXiv:2609.12230 already demonstrates a context‑augmented training framework with adaptive repair and RL transfer, showing positive results on disease‑specific KGs. This indicates the core idea is not novel, though further validation on open‑domain benchmarks could still be useful.

**Closest existing work:** UniKGQA: Unified Retrieval and Reasoning for Solving Multi-hop Question Answering Over Knowledge Graph (2022) [1]; Co-Evolving Graph and Text Memory for Training-Free Multi-Hop Question Answering (2026) [2]; Repair Before Reinforce: Context-Augmented Knowledge Graph Reasoning for Multi-Hop Question Answering (2026) [3]

**Potential overlap:** Overlaps with UniKGQA in seeking better integration of retrieval and reasoning, with Co‑E in leveraging graph‑text interactions, and with arXiv:2609.12230 in the specific combination of context‑augmented training, adaptive repair, and RL transfer.

**Potential distinction:** Unlike UniKGQA (which unifies via shared architecture/pre‑training) and Co‑E (which synchronizes memory at inference), and unlike arXiv:2609.12230 (which evaluates on disease‑specific KGs), the proposed idea aims to be general across open‑domain KGs and may differ in implementation details of the adaptive repair loop and RL scheme, but the core is substantially overlapping.

**Major risk:** The main technical risk is that context enrichment may introduce noise from imperfect triple extraction, leading to overfitting or incorrect facts. Moreover, the closely related work arXiv:2609.12230 already proposes essentially the same idea (context‑augmented training, adaptive repair, RL transfer), indicating limited novelty.

**Potential gap:** **[Hypothesis]** Lack of evaluation of context‑enriched triple training with adaptive repair and RL transfer on standard open‑domain multi-hop QA benchmarks (e.g., HotpotQA, MuSiQue, WebQSP, CWQ). (confidence: high; 1 gap(s) recorded)

**Recommended modification:** **[Hypothesis]** Cross‑passage context subgraph enrichment: Instead of restricting supporting triples to the same source text chunk, collect triples from multiple related passages (e.g., via TF‑IDF or dense retrieval) that share entities with the target triple, forming a broader context subgraph that captures multi‑document evidence.

**Recommended experiment:** Evaluating Cross-Passage Context Enrichment with External KG-Verified Adaptive Repair and Staged RL Transfer for Multi-Hop QA (E001)

**Research decision:** Already well explored. **[Inference]** Basis: the direction was rejected or the critique found substantial overlap with existing work. This describes the state of the evidence, not the absolute value of the idea.

**Current research direction (modify method, medium confidence):** **[Hypothesis]** Modify the method to incorporate cross-passage context enrichment and external knowledge-base verification for the adaptive repair loop, and evaluate on open-domain multi-hop QA benchmarks. (the original idea is kept in Section 2)

**Investigation:** 15 steps chosen from the research state; 11 uncertainties raised, 6 resolved, 5 still open or unresolved (Section 13, Appendix C).

**Stopped by a safety limit:** Stopping: time budget reached (3600 s). Conclusions below cover only what was recorded before the limit.

**Claim grounding:** 6/10 evidence and inference claims have at least one verified source.

This report does not declare the idea novel. Absence of a matching paper in these searches does not establish novelty; see Section 13.

## 2. Original Research Idea

> Multi‑hop question answering often relies on reasoning over a chain of facts in a knowledge graph, yet current language‑model training typically uses isolated head‑relation‑tail triples, depriving the model of the surrounding context that supports multi‑step inference. We propose to enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. The model will be fine‑tuned under two regimes: one using only the target triple/path and another that also incorporates the supporting context. To improve the reliability of the base facts, we will introduce an adaptive repair loop that detects one‑hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, we will apply reinforcement‑learning‑based optimization on lower‑hop QA instances and evaluate transfer to deeper multi‑hop queries.

## 3. Formalized Research Question

**Research question:** Does fine-tuning language models on context-enriched triple subgraphs (with adaptive repair) yield significantly higher multi-hop QA EM/F1 scores on benchmarks like HotpotQA compared to training on isolated triples, and does it improve transfer to deeper multi-hop queries?

**Hypothesis:** **[Hypothesis]** Providing local context subgraph during training improves multi-hop QA accuracy and factual consistency; the adaptive repair loop further improves base fact reliability, leading to better transfer to deeper hops.

**Refined direction (D002, MODIFY_METHOD):** **[Hypothesis]** Modify the method to incorporate cross-passage context enrichment and external knowledge-base verification for the adaptive repair loop, and evaluate on open-domain multi-hop QA benchmarks.. Hypothesis: Fine-tuning language models on context-enriched triple subgraphs that incorporate cross-passage evidence and using external KG-verified adaptive repair, followed by staged RL transfer, yields higher multi-hop QA EM/F1 on open-domain benchmarks than training on isolated triples or on same-passage context alone.. Why it deserves investigation: The core idea overlaps substantially with existing work (arXiv:2609.12230, UniKGQA, Co-E, SG-RAG MOT). To recover novelty and address unresolved validity and feasibility uncertainties (U003, U004), we refine the mechanism by broadening context beyond the same passage and adding objective verification, which are not present in the closest prior work. This direction targets the gap of missing open-domain evaluation (G001) and leverages the proposed modifications M001 and M002.

Direction history: D001 (MODIFY_METHOD, from the original idea): Modify the method to incorporate cross‑passage context enrichment and external knowledge‑base verification for the adaptive repair loop, and evaluate on open‑domain multi‑hop QA benchmarks.; D002 (MODIFY_METHOD, from D001): Modify the method to incorporate cross-passage context enrichment and external knowledge-base verification for the adaptive repair loop, and evaluate on open-domain multi-hop QA benchmarks.

| Aspect | Formalization |
|---|---|
| Problem | Multi-hop question answering relies on reasoning over chains of facts in a knowledge graph, but current language-model training typically uses isolated head-relation-tail triples, depriving the model of the surrounding context that supports multi-step inference. |
| Target domain | Knowledge graph-based multi-hop question answering using language models. |
| Proposed method | Enrich each target triple (or path) with additional triples drawn from the same source passage to form a local context subgraph, presented together with the primary supervision signal. Fine-tune under two regimes: (A) target triple/path only, (B) target triple/path plus local context subgraph. Introduce an adaptive repair loop that detects one-hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, apply reinforcement-learning-based optimization on lower-hop QA instances and evaluate transfer to deeper multi-hop queries. |
| Target system | Language models (e.g., T5, LLaMA) fine-tuned on knowledge graph triples derived from text. |
| Expected contribution | A training framework that integrates contextual subgraphs and an adaptive repair loop, demonstrating improved multi-hop QA performance and stronger generalization to higher-hop reasoning. |
| Independent variables | Training condition: isolated triples, Training condition: context-enriched triples only, Training condition: context-enriched triples + adaptive repair loop |
| Dependent variables | Multi-hop QA Exact Match (EM) score, Multi-hop QA F1 score, Transfer performance measured as improvement on 3-hop vs 2-hop queries |
| Controls | same base model architecture, same training data size across conditions, same optimizer (AdamW), same learning rate schedule, same random seed |

**Assumptions**

- Triples can be reliably extracted from source passages using existing extraction tools.
- Local context subgraph can be defined as all triples sharing at least one entity with the target triple within the same passage.
- The adaptive repair loop can detect failures via low confidence on one-hop predictions.
- Reinforcement learning optimization on lower-hop QA transfers to higher-hop QA.
- A mid-size language model (e.g., T5-base) is capable of learning from triple-text representations.

**Expected benefits / potential risks**

- Benefit: Improved multi-hop reasoning accuracy
- Benefit: Better factual consistency and reduced hallucination
- Benefit: Stronger generalization to longer reasoning chains
- Risk: Context may introduce noise leading to overfitting
- Risk: Adaptive repair loop may increase computational cost
- Risk: Reinforcement learning may be unstable or fail to transfer
- Risk: Performance depends on quality of triple extraction

**Ambiguities**

| Question | Resolution | Resolved by |
|---|---|---|
| Which multi-hop QA benchmark should be used for evaluation? | HotpotQA is a widely used benchmark for multi-hop question answering. | literature |
| Which evaluation metrics are standard for multi-hop QA? | Exact Match (EM) and F1 score are the standard metrics used in HotpotQA and similar datasets. | literature |
| How can triples be extracted from raw text passages? | Parser-based triple extraction methods exist for converting unstructured text into subject-predicate-object triples. | literature |
| What constitutes a local context subgraph around a target triple? | Prior work defines local context as the subgraph of triples sharing entities with the target triple within the same passage or document. | literature |
| Which knowledge graph provides the source triples for training? | Large-scale multilingual knowledge bases such as DBpedia (extracted from Wikipedia) are commonly used for KG-enhanced QA. | literature |

## 4. Existing Research

Overlap values are heuristic signals assigned during analysis, not measurements of novelty.

| Paper | Relevance | Method | Problem / method / evaluation overlap | Read from |
|---|---|---|---|---|
| UniKGQA: Unified Retrieval and Reasoning for Solving Multi-hop Question Answering Over Knowledge Graph (2022) [1] | high | We propose UniKGQA, a novel approach for multi-hop KGQA task, by unifying retrieval and reasoning in both model architecture and parameter learning. UniKGQA consists of a semantic matching module based on a pre-trained language model (PLM) for question-relation semantic matching, and a matching info | 0.9 / 0.4 / 0.8 | full_text |
| HOLMES: Hyper-Relational Knowledge Graphs for Multi-hop Question Answering using LLMs (2024) [4] | high | We propose to use a knowledge graph (KG) that is context-aware and distilled to contain query-relevant information. The compressed distilled KG is used as input to the LLM, resulting in up to 67% fewer tokens to represent query-relevant information compared to the state-of-the-art method. The method | 0.9 / 0.2 / 0.9 | full_text |
| Co-Evolving Graph and Text Memory for Training-Free Multi-Hop Question Answering (2026) [2] | high | We propose Co-E, a training-free system built around synchronized bidirectional graph-text working memory. A synchronization cycle consolidates textual memory, extracts relational triples into graph memory, and injects graph facts back into the generation context. Because both memories are maintaine | 0.8 / 0.2 / 0.7 | full_text |
| SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets for Knowledge Graph Multi-hop Question Answering (2025) [5] | high | SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets. Uses Cypher queries to search the KG and retrieve necessary subgraph, then applies hierarchical merging to reduce redundancy in retrieved triplets, and orders them using BFS traversal. | 0.8 / 0.2 / 0.5 | abstract |
| Training-Free Hybrid Evidence Retrieval for Question Answering: Dynamic Fusion of Knowledge-Graph Triples and Dense Text Embeddings (2025) [6] | high | A sub-50ms, training-free retrieval pipeline leveraging a Neo4j knowledge graph and a ChromaDB vector index. Questions and passages are embedded with Sentence-BERT; retrieved entities seed a one-hop Cypher expansion in the KG. A transparent fusion based on Dice-Sørensen overlap ranks passages and tr | 0.6 / 0.2 / 0.5 | abstract |
| Extracting triples from Vietnamese text to create knowledge graph (2020) [7] | medium | ["Extracting triples from Vietnamese text to create a knowledge graph."] | 0.1 / 0.1 / 0.0 | abstract |

<details><summary>Full paper analyses</summary>

#### UniKGQA: Unified Retrieval and Reasoning for Solving Multi-hop Question Answering Over Knowledge Graph (2022) [1]

- **Problem:** Multi-hop Question Answering over Knowledge Graph (KGQA) aims to find the answer entities that are multiple hops away from the topic entities mentioned in a natural language question on a large-scale Knowledge Graph (KG). To cope with the vast search space, existing work usually adopts a two-stage approach: it first retrieves a relatively small subgraph related to the question and then performs the reasoning on the subgraph to find the answer entities accurately.
- **Method:** We propose UniKGQA, a novel approach for multi-hop KGQA task, by unifying retrieval and reasoning in both model architecture and parameter learning. UniKGQA consists of a semantic matching module based on a pre-trained language model (PLM) for question-relation semantic matching, and a matching information propagation module to propagate the matching information along the directed edges on KGs. For parameter learning, we design a shared pre-training task based on question-relation matching for both retrieval and reasoning models, and then propose retrieval- and reasoning-oriented fine-tuning strategies.
- **Main contribution:** UniKGQA unifies retrieval and reasoning in both architecture and learning, demonstrating effectiveness on three benchmark datasets (MetaQA, WebQSP, CWQ) and outperforming state-of-the-art baselines by a large margin (e.g., 8.1% Hits@1 improvement on WebQSP, 2.0% on CWQ).
- **Key assumptions:** Retrieval and reasoning can be unified via a shared pre-training task on question-relation matching.; A semantic matching module and a matching information propagation module are sufficient for unified retrieval-reasoning.
- **Datasets / benchmarks:** MetaQA-1hop, MetaQA-2hop, MetaQA-3hop, WebQSP, CWQ, MetaQA-1hop, MetaQA-2hop, MetaQA-3hop, WebQSP, CWQ
- **Baselines:** KV-Mem, GraftNet, EmbedKGQA, NSM, TransferNet, PullNet, KGPT, BERTGRAG
- **Metrics:** Hits@1, F1
- **Results:** "On WebQSP and CWQ, UniKGQA outperforms existing state-of-the-art baselines by a large margin (e.g., 8.1% improvement of Hits@1 on WebQSP and 2.0% improvement of Hits@1 on CWQ)."
- **Limitations:** Not explicitly stated in the abstract or text.
- **Future work:** Not explicitly stated in the abstract or text.
- **Code availability:** Codes and data are publicly available at https://github.com/RUCAIBox/UniKGQA
- **Relation to idea:** UniKGQA unifies retrieval and reasoning via shared architecture and pre-training, whereas the proposed idea enriches training triples with local context subgraphs, adds an adaptive repair loop, and applies RL transfer to improve multi-hop QA. _(basis: not stated)_

#### HOLMES: Hyper-Relational Knowledge Graphs for Multi-hop Question Answering using LLMs (2024) [4]

- **Problem:** Given unstructured text, Large Language Models (LLMs) are adept at answering simple (single-hop) questions but performance degrades as question complexity increases due to overhead of understanding complex questions and filtering/aggregating unstructured information.
- **Method:** We propose to use a knowledge graph (KG) that is context-aware and distilled to contain query-relevant information. The compressed distilled KG is used as input to the LLM, resulting in up to 67% fewer tokens to represent query-relevant information compared to the state-of-the-art method. The method leverages hyper-relational KG to capture nuanced relations.
- **Main contribution:** HOLMES introduces a hyper-relational, context-aware distilled KG that reduces token usage by up to 67% and improves performance on EM, F1, BERTScore, and Human Evaluation on HotpotQA and MuSiQue benchmarks.
- **Key assumptions:** A context-aware, query-relevant distilled KG can reduce token overhead and improve LLM reasoning on multi-hop questions.; Hyper-relational KG representation preserves important relational nuances.
- **Datasets / benchmarks:** HotpotQA, MuSiQue, HotpotQA, MuSiQue
- **Baselines:** Unspecified baselines (referenced works: hwa et al., 2023; Robinson et al., 2022; Xu et al., 2023)
- **Metrics:** Exact Match (EM), F1, BERTScore, Human Evaluation
- **Results:** "Our experiments show consistent improvements over the state-of-the-art across several metrics (EM, F1, BERTScore, Human Eval) on HotpotQA and MuSiQue; the method utilizes up to 67% fewer tokens to represent query-relevant information."
- **Limitations:** Not explicitly stated in the abstract or text; potential limitations include dependence on KG quality and generalizability beyond the two datasets.
- **Future work:** Not explicitly stated in the abstract or text.
- **Code availability:** ["Not explicitly stated in the abstract or text."]
- **Relation to idea:** HOLMES focuses on inference-time use of a context-aware distilled KG to reduce token load, whereas the proposed idea enriches training triples with local context subgraphs, adds an adaptive repair loop, and applies RL transfer to improve multi-hop QA. _(basis: not stated)_

#### Co-Evolving Graph and Text Memory for Training-Free Multi-Hop Question Answering (2026) [2]

- **Problem:** Multi-hop question answering requires coordinating relational and textual evidence across reasoning steps, a combination neither a text corpus nor a knowledge graph can supply alone. Prior work often emphasizes only part of this loop: graph-augmented RAG retrieves from a pre-built or query-updated graph, KGQA systems search within topic-centered subgraphs, and memory-augmented agents maintain evolving memories without continuously reconciling graph memory with textual context.
- **Method:** We propose Co-E, a training-free system built around synchronized bidirectional graph-text working memory. A synchronization cycle consolidates textual memory, extracts relational triples into graph memory, and injects graph facts back into the generation context. Because both memories are maintained, they shape subsequent retrieval and generation.
- **Main contribution:** Proposing Co-E, a training-free multi-hop QA system that synchronizes graph and text memory, achieving strong results on six benchmarks and improving over comparable training-free baselines while competing with larger or trained systems.
- **Key assumptions:** Bidirectional coupling of textual and graph memories improves multi-hop reasoning.; Extracted relational triples from text are reliable enough to update graph memory.; Maintaining both memories allows them to shape retrieval and generation.
- **Datasets / benchmarks:** WebQSP, CWQ, HotpotQA, 2WikiMultiHopQA, MuSiQue, Bamboogle, WebQSP, CWQ, HotpotQA, 2WikiMultiHopQA, MuSiQue, Bamboogle
- **Baselines:** IRCoT, HopRAG, ComposeRAG, RT-RAG, Search-o1, Search-R1, MR-Search, RoG, GNN-RAG, PoG, SubgraphRAG, iQUEST, ToG 2.0, Live-KG KGQA
- **Metrics:** Hits@1 for KGQA, Exact Match (EM) for text-QA, LLM-judged accuracy (Acc)
- **Results:** "With a Qwen3-8B backbone and no training, Co-E reaches 72.6 EM on 2WikiMultiHopQA, 70.0 EM on Bamboogle and 74.9 Hits@1 on CWQ. For KGQA, Co-E (MCTS) achieves 85.5 Hits@1 on WebQSP and 85.3 Hits@1 (CoT), tying the strongest open 7B trained baselines (RoG, GNN-RAG at 85.7)."
- **Limitations:** Co-E is limited by the quality of the evidence it retrieves; bidirectional synchronization cannot reliably correct a wrong fact repeatedly supported by the retrieved corpus.; Co-E trades additional inference cost for stronger reasoning.
- **Future work:** Evaluate larger or more specialized models.; Extend the smaller-backbone study across all benchmarks.; Compare shared-memory MCTS with branch-local or reward-gated memory commits.; Investigate stronger early stopping, cached verification, or adaptive switching between CoT and MCTS to reduce inference cost.
- **Code availability:** Codebase available at https://github.com/hieum98/wemg
- **Relation to idea:** Co-E focuses on inference-time synchronization of graph and text memory without training, whereas the proposed idea enriches training triples with local context subgraphs and introduces an adaptive repair loop and RL transfer. _(basis: not stated)_

#### SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets for Knowledge Graph Multi-hop Question Answering (2025) [5]

- **Problem:** Large Language Models (LLMs) often hallucinate, especially on domain-specific tasks requiring reasoning; multi-hop question answering needs improved retrieval to reduce hallucination.
- **Method:** SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets. Uses Cypher queries to search the KG and retrieve necessary subgraph, then applies hierarchical merging to reduce redundancy in retrieved triplets, and orders them using BFS traversal.
- **Main contribution:** SG-RAG MOT enhances SG-RAG by adding a Merging and Ordering Triplets (MOT) step, providing more accurate answers than Chain-of-Thought and Graph Chain-of-Thought on the MetaQA benchmark.
- **Key assumptions:** Merging overlapping subgraphs reduces redundancy without losing relevant information.; Ordering triplets via BFS traversal helps the LLM generate more precise answers.
- **Datasets / benchmarks:** MetaQA (movies domain), MetaQA (movies domain)
- **Baselines:** Chain-of-Thought, Graph Chain-of-Thought
- **Metrics:** accuracy (exact match or similar)
- **Results:** "SG-RAG MOT provides more accurate answers than Chain-of-Thought and Graph Chain-of-Thought on MetaQA."
- **Limitations:** Not explicitly stated in abstract; potential limitations include dependence on MetaQA dataset and heuristic merging threshold.
- **Future work:** Not explicitly stated in abstract.
- **Code availability:** ["Not explicitly stated in abstract."]
- **Relation to idea:** SG-RAG MOT focuses on retrieval-augmented generation with subgraph merging and ordering, whereas the proposed idea enriches training triples with local context subgraphs, adds an adaptive repair loop, and applies RL transfer. _(basis: not stated)_

#### Training-Free Hybrid Evidence Retrieval for Question Answering: Dynamic Fusion of Knowledge-Graph Triples and Dense Text Embeddings (2025) [6]

- **Problem:** Efficient retrieval for question answering that combines knowledge graph triples and textual evidence to improve recall and ranking.
- **Method:** A sub-50ms, training-free retrieval pipeline leveraging a Neo4j knowledge graph and a ChromaDB vector index. Questions and passages are embedded with Sentence-BERT; retrieved entities seed a one-hop Cypher expansion in the KG. A transparent fusion based on Dice-Sørensen overlap ranks passages and triples.
- **Main contribution:** A training-free hybrid evidence retrieval pipeline that achieves superior Recall@10, MRR, and nDCG@10 on WebQSP and CQA-12k without learned parameters, offering a lightweight alternative to neural re-rankers.
- **Key assumptions:** Hybrid retrieval of KG triples and text embeddings improves QA performance.; One-hop KG expansion captures sufficient relevant triples.; Dice-Sørensen overlap provides effective fusion of passage and triple rankings.
- **Datasets / benchmarks:** WebQSP, CQA-12k, WebQSP, CQA-12k
- **Baselines:** BM25, graph-only, vector-only
- **Metrics:** Recall@10, MRR, nDCG@10
- **Results:** "On WebQSP and CQA-12k, the hybrid method achieves superior Recall@10, MRR, and nDCG@10 compared to BM25, graph-only, and vector-only baselines."
- **Limitations:** Not stated in abstract; potential limitations include reliance on one-hop KG expansion and applicability to broader QA settings.
- **Future work:** Not stated in abstract.
- **Code availability:** ["Not stated in abstract."]
- **Relation to idea:** This work focuses on a training-free hybrid retrieval pipeline for QA, whereas the proposed idea enriches training triples with local context subgraphs, adds an adaptive repair loop, and applies RL transfer. _(basis: not stated)_

#### Extracting triples from Vietnamese text to create knowledge graph (2020) [7]

- **Problem:** ["not stated in abstract"]
- **Method:** ["Extracting triples from Vietnamese text to create a knowledge graph."]
- **Main contribution:** ["A method for extracting triples from Vietnamese text to construct a knowledge graph."]
- **Key assumptions:** Triples can be extracted from Vietnamese text with sufficient accuracy.
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** ["not stated in abstract"]
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** ["not stated in abstract"]
- **Relation to idea:** This work focuses on triple extraction from Vietnamese text for KG construction, not on multi-hop QA training or reasoning. _(basis: not stated)_

</details>

## 5. Research Landscape

```text
Multi-hop Question Answering Approaches
├── Training-free methods  [2] [6] [5]
├── Unified retrieval-reasoning  [1]
├── Context-aware KG integration  [4]
├── Triple extraction  [7]
└── Context-enriched triple training with adaptive repair and RL transfer
```

**Where the idea fits:** **[Inference]** Context-enriched triple training with adaptive repair and RL transfer

**Dominant approaches**

- Training-free methods
- Unified retrieval-reasoning

**Common assumptions**

- Triples can be reliably extracted from source passages.
- Contextual information (e.g., local subgraphs, distilled KGs) improves multi-hop reasoning.
- Unified modeling of retrieval and reasoning enhances performance.
- Hybrid retrieval of KG triples and textual evidence improves QA recall and ranking.

**Common datasets**

- WebQSP
- CWQ
- HotpotQA
- MuSiQue
- MetaQA

**Common benchmarks**

- WebQSP
- CWQ
- HotpotQA
- MuSiQue
- MetaQA

**Common metrics**

- Hits@1
- Exact Match (EM)
- F1
- MRR
- nDCG@10
- BERTScore
- Human Evaluation

**Underexplored combinations**

- **[Hypothesis]** Combining context-enriched triple training with adaptive repair loops for fact correction.
- **[Hypothesis]** Integrating unified retrieval-reasoning frameworks with local context subgraph enrichment.
- **[Hypothesis]** Applying reinforcement learning transfer from lower-hop to higher-hop QA in training-free methods.
- **[Hypothesis]** Using adaptive repair to improve the quality of extracted triples from text.

**Limitations repeated across papers**

- Limitations not explicitly stated or discussed in the paper. [7], [5], [1], [4], [6]
- Performance limited by the quality of retrieved evidence or knowledge graph; errors in retrieval propagate and cannot be easily corrected. [2], [6], [4]
- Method evaluated on limited datasets or domains, raising questions about generalizability. [5], [4]

**Contradictions between papers**

- No direct contradictions found; differences lie in whether approaches rely on training the model (fine-tuning) versus inference-time mechanisms (retrieval, memory synchronization). 

## 6. Closest Existing Work

**[Inference]** UniKGQA (arxiv:2212.00959) unifies retrieval and reasoning via shared architecture and pre‑training, showing that integrating retrieval and reasoning helps; Co‑E (arxiv:2607.23278) synchronizes graph and text memory at inference, highlighting the value of context but also its limits in correcting persistent errors; arXiv:2609.12230 directly matches the proposed idea by enriching training triples with local context subgraphs, adding an LLM‑judged adaptive repair pipeline, and applying RL from lower‑hop to higher‑hop QA, demonstrating that the core components have already been explored.

- UniKGQA: Unified Retrieval and Reasoning for Solving Multi-hop Question Answering Over Knowledge Graph (2022) [1]: UniKGQA unifies retrieval and reasoning via shared architecture and pre-training, whereas the proposed idea enriches training triples with local context subgraphs, adds an adaptive repair loop, and applies RL transfer to improve multi-hop QA.
- Co-Evolving Graph and Text Memory for Training-Free Multi-Hop Question Answering (2026) [2]: Co-E focuses on inference-time synchronization of graph and text memory without training, whereas the proposed idea enriches training triples with local context subgraphs and introduces an adaptive repair loop and RL transfer.
- Repair Before Reinforce: Context-Augmented Knowledge Graph Reasoning for Multi-Hop Question Answering (2026) [3] (not analyzed in detail)

## 7. Potential Overlap

**Overlap:** **[Inference]** Overlaps with UniKGQA in seeking better integration of retrieval and reasoning, with Co‑E in leveraging graph‑text interactions, and with arXiv:2609.12230 in the specific combination of context‑augmented training, adaptive repair, and RL transfer.

**Potential distinction:** **[Inference]** Unlike UniKGQA (which unifies via shared architecture/pre‑training) and Co‑E (which synchronizes memory at inference), and unlike arXiv:2609.12230 (which evaluates on disease‑specific KGs), the proposed idea aims to be general across open‑domain KGs and may differ in implementation details of the adaptive repair loop and RL scheme, but the core is substantially overlapping.

**Novelty questions**

_None recorded._

## 8. Potential Research Gap

### G001: Lack of evaluation of context‑enriched triple training with adaptive repair and RL transfer on standard open‑domain multi-hop QA benchmarks (e.g., HotpotQA, MuSiQue, WebQSP, CWQ).

- **Status:** **[Hypothesis]** a potential gap, derived from the evidence below
- **Evidence:**
  - [3], p. 7 (direct support, verified) "Although generally applicable, in Fig. 2, we show how the pipeline can be adapted to the biomedical arena, specifically for gastroparesis. From the corresponding articles, available from PubMed Central [66], we construct a disease-specific KG using GraphMERT."
- **Related papers:** [3], [1], [2], [5]
- **Why existing work does not address it:** **[Inference]** Existing work either focuses on disease-specific KGs (arXiv:2609.12230) or lacks the combined context enrichment, adaptive repair, and RL transfer components (UniKGQA, Co‑E, SG‑RAG MOT).
- **Research question:** Does fine‑tuning language models on context‑enriched triple subgraphs with an adaptive repair loop and RL transfer yield significant improvements in EM/F1 on open‑domain multi-hop QA benchmarks compared to training on isolated triples?
- **Potential experiment:** Train a model using the proposed framework on a standard KG (e.g., Freebase or Wikidata) with QA pairs derived from HotpotQA, evaluate KG‑grounded and CG‑grounded supervision, include adaptive repair and RL transfer stages, and measure EM/F1 against baselines.
- **Confidence:** high
- **Verification required:** not stated

## 9. Critique

| | |
|---|---|
| Strongest argument FOR | The idea addresses a key limitation: current LM training uses isolated triples, depriving models of contextual clues that support multi-hop inference. Enriching triples with local context subgraphs provides richer supervision, and UniKGQA shows that unifying retrieval and reasoning improves performance, suggesting contextual enrichment can help. |
| Strongest argument AGAINST | The main technical risk is that context enrichment may introduce noise from imperfect triple extraction, leading to overfitting or incorrect facts. Moreover, the closely related work arXiv:2609.12230 already proposes essentially the same idea (context‑augmented training, adaptive repair, RL transfer), indicating limited novelty. |
| Most important unresolved question | Does fine‑tuning on context‑enriched triple subgraphs yield a statistically significant improvement in multi‑hop QA EM/F1 over training on isolated triples when controlling for triple extraction noise and compared to the recently proposed context‑augmented framework? |
| Most dangerous experimental confounder | Performance heavily depends on the quality of triple extraction from source passages; if extraction introduces spurious triples, the enriched context subgraph may inject incorrect facts, confounding any observed gains. |
| Closest existing work | [1], [2], [3] |
| Potential contribution | **[Hypothesis]** A training framework that enriches each target triple with a local context subgraph from the same passage, incorporates an adaptive repair loop to detect and correct one‑hop failures, and applies reinforcement learning transfer from lower‑hop to higher‑hop QA, aiming to improve multi‑hop reasoning accuracy and generalization. |

**Technical validity**

_None recorded._

**Experimental validity**

_None recorded._

**Practicality**

_None recorded._

## 10. Proposed Modifications

Difficulty ratings are qualitative (low / moderate / high) with the stated basis; no numeric scoring is used.

### M001: Cross‑passage context subgraph enrichment (recommended)

**[Hypothesis]** Instead of restricting supporting triples to the same source text chunk, collect triples from multiple related passages (e.g., via TF‑IDF or dense retrieval) that share entities with the target triple, forming a broader context subgraph that captures multi‑document evidence.

| | |
|---|---|
| Why it differs | The proposed idea and arXiv:2609.12230 limit context to triples from the same source passage; UniKGQA and Co‑E do not enrich training triples with any contextual triples. Expanding to cross‑passage context leverages wider evidence while still staying grounded in the source corpus. |
| Technical mechanism | For each target triple, retrieve top‑k passages containing its entities using a dense retriever (e.g., DPR), extract triples from those passages, and add them to the context graph. The resulting subgraph is used alongside the target triple in both KG‑grounded and CG‑grounded supervision settings. |
| Expected benefit | Increased recall of relevant facts, reduced dependence on single‑passage completeness, and improved robustness to passage‑level noise. |
| Potential novelty | Combining cross‑passage context extraction with adaptive repair and RL transfer has not been explicitly explored in multi‑hop QA training frameworks. |
| Implementation difficulty | moderate, because Requires integrating a passage retriever and triple extraction pipeline, but builds on existing tools (DPR, OpenIE). |
| Experimental difficulty | moderate, because Experiments involve varying k and measuring impact on EM/F1; ablation studies are straightforward. |
| Main risk | Increased noise from irrelevant passages may degrade performance if not filtered properly. |
| Required baselines | isolated triples, same‑passage context enrichment (as in arXiv:2609.12230) |
| Related work | [3], [1], [2], [6] |
| Addresses gaps | G001 |

### M002: External knowledge‑base verification for adaptive repair

**[Hypothesis]** Replace or augment the LLM‑judged adaptive repair loop with a verification step that checks candidate triples against a trusted external KG (e.g., Wikidata) using string matching or embedding similarity, and only retains triples that are supported by the external source.

| | |
|---|---|
| Why it differs | The adaptive repair in arXiv:2609.12230 relies solely on LLM judgments and self‑correction, which may perpetuate biases. UniKGQA and Co‑E do not include an explicit repair mechanism. Using an external KB provides an objective source of truth to reduce error propagation. |
| Technical mechanism | After generating repair examples from unresolved one‑hop failures, candidate triples are queried against a snapshot of Wikidata via SPARQL or a local triple store; triples with a match above a confidence threshold are kept, others are discarded or sent back for revision. |
| Expected benefit | Higher precision of the repaired knowledge base, leading to more reliable lower‑hop foundations and better generalization to higher‑hop QA. |
| Potential novelty | Integrating external KG verification into the adaptive repair loop for multi‑hop QA training has not been described in the surveyed literature. |
| Implementation difficulty | high, because Requires setting up and synchronizing a external KG snapshot, implementing SPARQL lookups, and handling missing matches. |
| Experimental difficulty | high, because Experiments must compare repair effectiveness with and without external verification, measuring changes in one‑hop accuracy and downstream multi‑hop performance. |
| Main risk | If the external KG is incomplete or out‑of‑sync with the source corpus, valid triples may be incorrectly removed, hurting recall. |
| Required baselines | LLM‑judged adaptive repair (as in arXiv:2609.12230), no repair |
| Related work | [3], [8], [1] |
| Addresses gaps | G001 |

### M003: Curriculum learning with staged reinforcement learning

**[Hypothesis]** Introduce a curriculum that first trains on 1‑hop QA with context enrichment and adaptive repair, then progressively adds 2‑hop, 3‑hop, etc., applying reinforcement learning at each stage before moving to the next hop count, rather than a single RL phase after repair.

| | |
|---|---|
| Why it differs | The proposed idea and arXiv:2609.12230 apply RL after a single repair stage on lower‑hop QA items. UniKGQA and Co‑E do not use RL. A staged curriculum allows the model to solidify foundational reasoning before tackling longer chains, potentially improving stability and performance. |
| Technical mechanism | For hop level h = 1 to H_max: generate QA items of exactly h hops from the KG (or context‑augmented KG), perform supervised fine‑tuning with context enrichment, run the adaptive repair loop to clean the hop‑h model, then apply reinforcement learning using the hop‑h QA items as training episodes; the resulting policy is used to initialize the next hop level. |
| Expected benefit | Better transfer learning across hop counts, reduced catastrophic forgetting, and improved performance on the highest‑hop benchmarks. |
| Potential novelty | Curriculum‑staged RL in the context of context‑enriched triple training and adaptive repair has not been explicitly explored for multi‑hop QA. |
| Implementation difficulty | moderate, because Requires generating hop‑specific QA datasets and looping the training‑repair‑RL pipeline, but each stage reuses the same codebase. |
| Experimental difficulty | moderate, because Ablation studies can compare final performance with staged RL vs. single‑stage RL and baselines. |
| Main risk | If the curriculum advances too quickly, the model may not adequately learn lower‑hop patterns, causing instability. |
| Required baselines | single‑stage RL after repair (as in arXiv:2609.12230), no RL |
| Related work | [3], [9], [1] |
| Addresses gaps | G001 |

## 11. Recommended Experimental Design

### E001: Evaluating Cross-Passage Context Enrichment with External KG-Verified Adaptive Repair and Staged RL Transfer for Multi-Hop QA

- **Research question:** Does fine-tuning language models on context-enriched triple subgraphs that incorporate cross-passage evidence and using external KG-verified adaptive repair, followed by staged RL transfer, yield higher multi-hop QA EM/F1 on open-domain benchmarks than training on isolated triples or on same-passage context alone?
- **Hypothesis:** **[Hypothesis]** The proposed method will achieve higher EM/F1 scores on HotpotQA, MuSiQue, WebQSP, and CWQ compared to baselines that use isolated triples, same-passage context only, or lack external verification and staged RL.
- **Proposed method:** 1. Retrieve triples from a large KG (e.g., Wikidata) aligned with text corpus (e.g., Wikipedia).  2. For each target triple (or path) from QA dataset, extract the source passage(s) and gather triples from the same passage (local context) and from other passages containing the same entities (cross-passage context) using a dense retriever (DPR) and triple extraction (OpenIE).  3. Form a context subgraph combining local and cross-passage triples, limited to top-k by relevance.  4. Fine-tune a language model (T5-base) under two regimes: KG-grounded (target triple only) and CG-grounded (target triple + context subgraph).  5. Apply adaptive repair loop: after each epoch, detect one-hop failures (low confidence on single-hop QA), generate corrective examples by querying an external KG (Wikidata) for triples involving the same entities, and replace or augment the training data with verified triples.  6. After repair, apply reinforcement learning in a staged curriculum: start with 1-hop QA, then 2-hop, etc., using policy gradient rewards based on QA accuracy.  7. Evaluate on held-out multi-hop QA sets.
- **Baselines:** Isolated triple training (target triple only), Same-passage context enrichment (as in arXiv:2609.12230), Context enrichment without adaptive repair, Context enrichment with adaptive repair but no external verification, Context enrichment with adaptive repair and external verification but no staged RL (single-stage RL after repair), UniKGQA, Co-E, SG-RAG MOT
- **Datasets:** HotpotQA, MuSiQue, WebQSP, CWQ
- **Workloads:** Training on QA pairs derived from the datasets and KG
- **Hardware:** 4x NVIDIA V100 GPUs
- **Software environment:** PyTorch, HuggingFace Transformers, DPR, OpenIE, Wikidata API
- **Metrics:** Exact Match (EM), F1 score, Hits@1 (for KGQA), Transfer performance (improvement on 3-hop vs 2-hop)
- **Ablations:** No cross-passage context (only local); No external verification in repair (LLM-judged only); No staged RL (single-stage after repair); No adaptive repair (direct to RL)
- **Controls:** Same model size; Same total training steps; Same optimizer (AdamW); Same learning rate schedule; Same random seed
- **Confounders addressed:** Not recorded
- **Expected outcomes:** The full method should outperform baselines, demonstrating the value of cross-passage context, external verification, and staged RL.
- **Failure conditions:** If triple extraction noise is too high, performance may degrade; If external KG is misaligned, verification may filter useful triples
- **Reproducibility:** Provide code, data splits, and hyperparameters.
- **Related work:** [3], [1], [2], [5], [6]

## 12. Experimental Results

Experiment not performed. The designs in Section 11 are untested.

## 13. Remaining Uncertainty

- Literature coverage: searched 11 queries over arxiv, crossref, openalex, semantic_scholar. Work outside these queries and sources, very recent preprints, and non-English work may be missing; the absence of matching work here does not establish novelty.
- Some source requests failed and their results are missing: semantic_scholar (api.semanticscholar.org failed after 5 attempts (HTTP 429)).
- Metadata warning for PullNet: Open Domain Question Answering with Iterative Retrieval on Knowledge Bases and Text (2019) [10]: abstracts from arxiv and openalex disagree; kept the one from arxiv, which matches the title better. Its abstract was not accepted as direct evidence.
- Metadata warning for SQALER: Scaling Question Answering by Decoupling Multi-Hop and Logical Reasoning (2021) [11]: abstract (from arxiv) never mentions 'SQALER'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for HOLMES: Hyper-Relational Knowledge Graphs for Multi-hop Question Answering using LLMs (2024) [4]: abstract (from arxiv) never mentions 'HOLMES'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for AgentRouter: A Knowledge-Graph-Guided LLM Router for Collaborative Multi-Agent Question Answering (2026) [12]: abstract (from openalex) never mentions 'AgentRouter'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Repair Before Reinforce: Context-Augmented Knowledge Graph Reasoning for Multi-Hop Question Answering (2026) [3]: abstract (from semantic_scholar) never mentions 'Repair Before Reinforce'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for QA-GNN: Reasoning with Language Models and Knowledge Graphs for Question Answering (2021) [13]: abstract (from openalex) never mentions 'QA-GNN'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering (2018) [14]: abstract (from openalex) never mentions 'HotpotQA'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Optimizing AI Reasoning: A Hamiltonian Dynamics Approach to Multi-Hop Question Answering (2025) [15]: abstract (from crossref) never mentions 'Optimizing AI Reasoning'; it may belong to another work. Its abstract was not accepted as direct evidence.
- 3 of 6 analyses are based on abstracts only.
- Unresolved question: Does fine‑tuning on context‑enriched triple subgraphs yield a statistically significant improvement in multi‑hop QA EM/F1 over training on isolated triples when controlling for triple extraction noise and compared to the recently proposed context‑augmented framework?
- Claims without a verified source: C004, C005, C006, C009.
- No hypothesis in this report has been tested experimentally.

**Uncertainty ledger**

| Id | Question | Category | Importance | Status | Evidence for / against | Resolution |
|---|---|---|---|---|---|---|
| U007 | The conclusion behind U006 was weakened by contradicting work; how should the direction change? (raised by ResearchForge) | direction | high | open | none / none | Not recorded |
| U009 | Has gap G001 already been addressed: Lack of evaluation of context‑enriched triple training with adaptive repair and RL transfer on standard open‑domain multi-hop QA benchmarks (e.g., HotpotQA, MuSiQue, WebQSP, CWQ).? (raised by ResearchForge) | novelty | high | open | none / none | No retrieved work evaluates the combination of context‑enriched triple training, adaptive repair loop, and RL transfer on standard open‑domain multi‑hop QA benchmarks; the closest work (arXiv:2609.12230) evaluates only on disease‑specific KGs. |
| U011 | Is direction D002 already explored or contradicted: Modify the method to incorporate cross-passage context enrichment and external knowledge-base verification for the adaptive repair loop, and evaluate on open-domain multi-hop QA benchmarks.? (raised by ResearchForge) | contradiction | high | open | none / none | Not recorded |
| U003 | Does an adaptive repair loop that detects one-hop failures and generates corrective examples improve the reliability of base facts in language models trained on KG triples? | validity | medium | partially resolved | none / none | No direct evidence found that an adaptive repair loop improves base fact reliability; Co-E shows models cannot reliably correct wrong facts repeatedly supported by retrieved evidence, suggesting repair may be challenging without external validation. |
| U004 | Can triples be reliably extracted from source passages at the scale needed for training, and what is the typical noise level of such extractions? | feasibility | medium | partially resolved | none / none | No specific measurements of triple extraction noise at scale found in surveyed literature; extraction quality varies by tool and domain, and errors could introduce noise into context subgraphs. |
| U001 | Is there existing work that already trains language models on context-enriched triple subgraphs (i.e., not just isolated triples but also surrounding triples from the same passage) for multi-hop KGQA? | novelty | high | resolved | [3] / none | Yes, arXiv:2609.12230 proposes a context-augmented training framework that attaches supporting triples from the same source text chunk to each primary KG triple, forming a context graph, and trains under KG-grounded and CG-grounded supervision. |
| U002 | How much does the proposed method overlap with existing subgraph retrieval approaches like SG-RAG MOT or UniKGQA that already incorporate surrounding triple information? | overlap | high | resolved | [1], [5], [16], [2] / none | Substantial overlap exists with existing subgraph retrieval approaches: UniKGQA unifies retrieval and reasoning via shared architecture and pre‑training; SG‑RAG MOT retrieves and orders subgraphs; other works (e.g., subgraph retrieval and link scoring model) also utilize surrounding triple information. The proposed idea overlaps in leveraging local context but differs by enriching training triples with that context, adding an adaptive repair loop, and applying RL transfer. |
| U005 | Does published work contradict the current assessment: Unlike UniKGQA (which unifies via shared architecture/pre-training) and Co-E (which synchronizes memory at inference), the proposed idea enriches training triples with local context subgraphs, adds an adaptive repair loop for fact correction, and uses RL transfer to improve higher-hop performance from lower-hop training.? (raised by ResearchForge) | contradiction | high | resolved (weakened) | none / [3] | The retrieved paper arXiv:2609.12230 proposes a context-augmented training framework that enriches each target triple with supporting triples from the same source text chunk (context graph), uses an LLM-judged history-aware adaptive repair pipeline to fix one-hop failures, and applies reinforcement learning from lower-hop QA to improve higher-hop generalization—directly matching the proposed idea's core components. This indicates the idea is not novel as claimed. |
| U006 | Does published work contradict the assessment that, unlike UniKGQA (which unifies via shared architecture/pre-training) and Co-E (which synchronizes memory at inference), the proposed idea enriches training triples with local context subgraphs, adds an adaptive repair loop for fact correction, and uses RL transfer to improve higher-hop performance from lower-hop training? | overlap | high | resolved (weakened) | none / [3] | The retrieved paper arXiv:2609.12230 proposes a context-augmented training framework that attaches supporting triples from the same source text chunk to form a context graph, uses an LLM-judged history-aware adaptive repair pipeline, and applies reinforcement learning from lower-hop QA to improve higher-hop generalization—directly matching the proposed idea's core components. This indicates the idea is not novel as claimed. |
| U008 | The conclusion behind U005 was weakened by contradicting work; how should the direction change? (raised by ResearchForge) | direction | high | resolved | none / none | We decided to modify the method to incorporate cross-passage context enrichment and external knowledge-base verification for the adaptive repair loop, and evaluate on open-domain multi-hop QA benchmarks, as a response to the weakened conclusion about distinctness from existing work. |
| U010 | Is direction D001 already explored or contradicted: Modify the method to incorporate cross‑passage context enrichment and external knowledge‑base verification for the adaptive repair loop, and evaluate on open‑domain multi‑hop QA benchmarks.? (raised by ResearchForge) | contradiction | high | resolved (holds) | none / none | Searches for cross‑passage context enrichment and external knowledge‑base verification in adaptive repair for multi‑hop QA returned no directly matching work; the closest papers either focus on single‑passage context, internal LLM‑judged repair, or unrelated KB verification, indicating that direction D001 (modify method to incorporate cross‑passage context and external KB verification, evaluate on open‑domain benchmarks) is not yet explored. |

## 14. Suggested Next Steps

1. Run the recommended experiment E001 (Evaluating Cross-Passage Context Enrichment with External KG-Verified Adaptive Repair and Staged RL Transfer for Multi-Hop QA) with budget-matched baselines.
2. Resolve: Does fine‑tuning on context‑enriched triple subgraphs yield a statistically significant improvement in multi‑hop QA EM/F1 over training on isolated triples when controlling for triple extraction noise and compared to the recently proposed context‑augmented framework?
3. Design a control for the confounder: Performance heavily depends on the quality of triple extraction from source passages; if extraction introduces spurious triples, the enriched context subgraph may inject incorrect facts, confounding any observed gains.
4. Search for work newer than the most recent retrieved paper (2026) before claiming a distinction.
5. Prototype the recommended modification M001 (Cross‑passage context subgraph enrichment).

## 15. References

1. Jinhao Jiang, Kun Zhou, Wayne Xin Zhao et al.. **UniKGQA: Unified Retrieval and Reasoning for Solving Multi-hop Question Answering Over Knowledge Graph**. _arXiv (preprint)_, 2022. <https://arxiv.org/abs/2212.00959> (id `arxiv:2212.00959`; retrieved from arxiv)
2. Hieu Man, Thien Huu Nguyen. **Co-Evolving Graph and Text Memory for Training-Free Multi-Hop Question Answering**. _arXiv.org_, 2026. <https://arxiv.org/abs/2607.23278> doi:10.48550/arxiv.2607.23278 (id `arxiv:2607.23278`; retrieved from arxiv, semantic_scholar; 0 citations per semantic_scholar)
3. Tharaka Fonseka, N. Jha. **Repair Before Reinforce: Context-Augmented Knowledge Graph Reasoning for Multi-Hop Question Answering**. 2026. <https://www.semanticscholar.org/paper/ec5848d2380c1c9f9664887fb517008245d1548c> (id `arxiv:2609.12230`; retrieved from semantic_scholar; 0 citations per semantic_scholar)
4. Pranoy Panda, Ankush Agarwal, Chaitanya Devaguptapu et al.. **HOLMES: Hyper-Relational Knowledge Graphs for Multi-hop Question Answering using LLMs**. _arXiv (preprint)_, 2024. <https://arxiv.org/abs/2406.06027> (id `arxiv:2406.06027`; retrieved from arxiv)
5. Ahmmad O. M. Saleh, Gokhan Tur, Yucel Saygin. **SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets for Knowledge Graph Multi-hop Question Answering**. _Machine Learning and Knowledge Extraction_, 2025. <https://doi.org/10.20944/preprints202505.1992.v1> (id `doi:10.20944/preprints202505.1992.v1`; retrieved from crossref; 0 citations per crossref)
6. Otávio Calaça Xavier, Anderson da Silva Soares. **Training-Free Hybrid Evidence Retrieval for Question Answering: Dynamic Fusion of Knowledge-Graph Triples and Dense Text Embeddings**. _Anais do XL Simpósio Brasileiro de Banco de Dados (SBBD 2025)_, 2025. <https://doi.org/10.5753/sbbd.2025.247297> (id `doi:10.5753/sbbd.2025.247297`; retrieved from crossref; 2 citations per crossref)
7. Huong Duong To, Phuc Do. **Extracting triples from Vietnamese text to create knowledge graph**. _2020 12th International Conference on Knowledge and Systems Engineering (KSE)_, 2020. <https://doi.org/10.1109/kse50997.2020.9287471> (id `doi:10.1109/kse50997.2020.9287471`; retrieved from crossref; 3 citations per crossref)
8. Jens Lehmann, Robert Isele, Max Jakob et al.. **DBpedia – A large-scale, multilingual knowledge base extracted from Wikipedia**. _Semantic Web_, 2015. <https://doi.org/10.3233/sw-140134> (id `doi:10.3233/sw-140134`; retrieved from openalex; 3239 citations per openalex)
9. Wuzhenghong Wen, Chao Xue, Su Pan et al.. **Reinforcement Learning Enhanced Multi-hop Reasoning for Temporal Knowledge Question Answering**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2601.01195> (id `arxiv:2601.01195`; retrieved from arxiv)
10. Haitian Sun, Tania Bedrax-Weiss, William W. Cohen. **PullNet: Open Domain Question Answering with Iterative Retrieval on Knowledge Bases and Text**. _arXiv (preprint)_, 2019. <https://arxiv.org/abs/1904.09537> doi:10.18653/v1/d19-1242 (id `arxiv:1904.09537`; retrieved from arxiv, openalex; 333 citations per openalex)
11. Mattia Atzeni, Jasmina Bogojeska, Andreas Loukas. **SQALER: Scaling Question Answering by Decoupling Multi-Hop and Logical Reasoning**. _arXiv (preprint)_, 2021. <https://arxiv.org/abs/2110.14266> (id `arxiv:2110.14266`; retrieved from arxiv)
12. Zheyuan Zhang, Kaiwen Shi, Zhengqing Yuan et al.. **AgentRouter: A Knowledge-Graph-Guided LLM Router for Collaborative Multi-Agent Question Answering**. 2026. <https://doi.org/10.18653/v1/2026.acl-long.33> (id `arxiv:2510.05445`; retrieved from openalex; 1 citations per openalex)
13. Michihiro Yasunaga, Hongyu Ren, Antoine Bosselut et al.. **QA-GNN: Reasoning with Language Models and Knowledge Graphs for Question Answering**. 2021. <https://doi.org/10.18653/v1/2021.naacl-main.45> (id `doi:10.18653/v1/2021.naacl-main.45`; retrieved from openalex; 529 citations per openalex)
14. Zhilin Yang, Peng Qi, Saizheng Zhang et al.. **HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering**. 2018. <https://doi.org/10.18653/v1/d18-1259> (id `doi:10.18653/v1/d18-1259`; retrieved from openalex; 1770 citations per openalex)
15. Javier Marin Valenzuela, A Preprint, Javier Marín. **Optimizing AI Reasoning: A Hamiltonian Dynamics Approach to Multi-Hop Question Answering**. 2025. <https://doi.org/10.22541/au.173645367.74451514/v1> (id `doi:10.22541/au.173645367.74451514/v1`; retrieved from crossref; 0 citations per crossref)
16. Changshun Zhou, Wenhao Ying, Shan Zhong et al.. **Subgraph retrieval and link scoring model for multi-hop question answering in knowledge graphs**. _Applied Intelligence_, 2025. <https://doi.org/10.1007/s10489-024-05935-8> (id `doi:10.1007/s10489-024-05935-8`; retrieved from crossref; 2 citations per crossref)
17. Yuwei Fang, Siqi Sun, Zhe Gan et al.. **Hierarchical Graph Network for Multi-hop Question Answering**. 2020. <https://doi.org/10.18653/v1/2020.emnlp-main.710> (id `doi:10.18653/v1/2020.emnlp-main.710`; retrieved from openalex; 161 citations per openalex)

<details><summary>Other retrieved papers (not cited in this report)</summary>

- KG-o1: Enhancing Multi-hop Question Answering in Large Language Models via Knowledge Graph Integration (2025) <https://arxiv.org/abs/2508.15790> `arxiv:2508.15790`
- Enhancing relation classification based on GCN Multi-hop Knowledge Graph Question Answering model of knowledge reasoning (2024) <https://doi.org/10.1109/ialp63756.2024.10661134> `doi:10.1109/ialp63756.2024.10661134`
- Parser Extraction of Triples in Unstructured Text (2018) <https://arxiv.org/abs/1811.05768> `arxiv:1811.05768`
- FabKG: A Knowledge graph of Manufacturing Science domain utilizing structured and unconventional unstructured knowledge source (2022) <https://arxiv.org/abs/2206.10318> `arxiv:2206.10318`
- A Method for Multi-Hop Question Answering on Persian Knowledge Graph (2025) <https://arxiv.org/abs/2501.16350> `arxiv:2501.16350`
- Scalable Multi-Hop Relational Reasoning for Knowledge-Aware Question Answering (2020) <https://arxiv.org/abs/2005.00646> `arxiv:2005.00646`
- Improving Multi-hop Knowledge Base Question Answering by Learning Intermediate Supervision Signals (2021) <https://doi.org/10.1145/3437963.3441753> `arxiv:2101.03737`
- Zero-resource Hallucination Detection for Text Generation via Graph-based Contextual Knowledge Triples Modeling (2024) <https://arxiv.org/abs/2409.11283> `arxiv:2409.11283`
- Multi-hop Question Answering (2024) <https://doi.org/10.1561/9781638283751> `doi:10.1561/9781638283751`
- Variational Reasoning for Question Answering With Knowledge Graph (2018) <https://doi.org/10.1609/aaai.v32i1.12057> `doi:10.1609/aaai.v32i1.12057`
- HybridQA: A Dataset of Multi-Hop Question Answering over Tabular and Textual Data (2020) <https://doi.org/10.18653/v1/2020.findings-emnlp.91> `doi:10.18653/v1/2020.findings-emnlp.91`
- Fine-Tuning vs. RAG for Multi-Hop Question Answering with Novel Knowledge (2026) <https://doi.org/10.18653/v1/2026.gem-main.37> `doi:10.18653/v1/2026.gem-main.37`
- LLM-KGMQA: Large Language Model-Augmented Multi-Hop Question-Answering System based on Knowledge Graph in Medical Field (2024) <https://doi.org/10.21203/rs.3.rs-4721418/v1> `doi:10.21203/rs.3.rs-4721418/v1`
- Multi-path reasoning for Multi-hop Question Answering over Knowledge Graphs (2022) <https://doi.org/10.22541/au.165426315.58267165/v1> `doi:10.22541/au.165426315.58267165/v1`
- Dynamic Multi-Hop Retrieval-Augmented Generation Framework for Professional Domain Question Answering (2026) <https://doi.org/10.22541/au.177499050.00368942/v1> `doi:10.22541/au.177499050.00368942/v1`
- Subgraph Retrieval Enhanced Model for Multi-hop Knowledge Base Question Answering (2022) <https://arxiv.org/abs/2202.13296> `arxiv:2202.13296`
- Triggering Multi-Hop Reasoning for Question Answering in Language Models using Soft Prompts and Random Walks (2023) <https://arxiv.org/abs/2306.04009> `arxiv:2306.04009`
- Improving Multi-hop Question Answering over Knowledge Graphs using Knowledge Base Embeddings (2020) <https://doi.org/10.18653/v1/2020.acl-main.412> `doi:10.18653/v1/2020.acl-main.412`
- Question Answering over Text (2022) <https://doi.org/10.1007/978-3-031-16552-8_5> `doi:10.1007/978-3-031-16552-8_5`
- Question Answering over Knowledge Base (2022) <https://doi.org/10.1007/978-3-031-16552-8_6> `doi:10.1007/978-3-031-16552-8_6`
- Improving embedded knowledge graph multi-hop question answering by introducing relational chain reasoning (2022) <https://doi.org/10.1007/s10618-022-00891-8> `arxiv:2110.12679`
- Incorporating multi-perspective information into reinforcement learning to address multi-hop knowledge graph question answering (2024) <https://doi.org/10.1016/j.eswa.2024.124652> `doi:10.1016/j.eswa.2024.124652`
- Incorporating anticipation embedding into reinforcement learning framework for multi-hop knowledge graph question answering (2023) <https://doi.org/10.1016/j.ins.2022.11.042> `doi:10.1016/j.ins.2022.11.042`
- Method for Multi-Hop Question Answering Based on Knowledge Graph with Fusion Path (2024) <https://www.semanticscholar.org/paper/8b298d210d59f6ae02b08986eb14b6141e5f0aee> `doi:10.1109/icaice63571.2024.10863895`
- Improving multi-hop question answering with prompting explicit and implicit knowledge aligned human reading comprehension (2025) <https://www.semanticscholar.org/paper/a5eace0d4de029d16342e53d05f13d81b452d060> `doi:10.1007/s13042-025-02712-y`
- Efficient LLM-Based Subgraph Retrieval for Multi-Hop Knowledge Base Question Answering (2026) <https://doi.org/10.1109/tkde.2026.3679080> `doi:10.1109/tkde.2026.3679080`
- Reinforcement learning-guided archival question answering with adaptive curriculum learning (2026) <https://doi.org/10.1038/s41598-026-67621-8> `doi:10.1038/s41598-026-67621-8`
- SentGraph: Hierarchical Sentence Graph for Multi-hop Retrieval-Augmented Question Answering (2026) <https://arxiv.org/abs/2601.03014> `arxiv:2601.03014`
- Dynamically Fused Graph Network for Multi-hop Reasoning (2019) <https://doi.org/10.18653/v1/p19-1617> `doi:10.18653/v1/p19-1617`
- Multi-attentive question answering over knowledge base (n.d.) <https://doi.org/10.5204/thesis.eprints.244138> `doi:10.5204/thesis.eprints.244138`
- SG-RAG: Multi-Hop Question Answering With Large Language Models Through Knowledge Graphs (2024) <https://www.semanticscholar.org/paper/ddf9c2aab6fafeeeca3dce50e2f25a3ba8c30435> `s2:ddf9c2aab6fafeeeca3dce50e2f25a3ba8c30435`
- Question Answering Evaluation (2022) <https://doi.org/10.1007/978-3-031-16552-8_3> `doi:10.1007/978-3-031-16552-8_3`
- Retrieving Minimal and Sufficient Reasoning Subgraphs with Graph Foundation Models for Path-aware GraphRAG (2026) <https://arxiv.org/abs/2603.07179> `arxiv:2603.07179`
- Commonsense for Generative Multi-Hop Question Answering Tasks (2018) <https://doi.org/10.18653/v1/d18-1454> `doi:10.18653/v1/d18-1454`
- Question Answering with Subgraph Embeddings (2014) <https://doi.org/10.3115/v1/d14-1067> `doi:10.3115/v1/d14-1067`
- Enhancing Document-Level Question Answering via Multi-Hop Retrieval-Augmented Generation with LLaMA 3 (2025) <https://doi.org/10.36227/techrxiv.175086164.45839186/v1> `doi:10.36227/techrxiv.175086164.45839186/v1`
- LAMRF: Logic-adaptive multi-source reasoning fusion for multi-hop knowledge graph question answering (2026) <https://doi.org/10.1016/j.knosys.2026.115902> `doi:10.1016/j.knosys.2026.115902`
- Language Generation with Multi-Hop Reasoning on Commonsense Knowledge Graph (2020) <https://doi.org/10.18653/v1/2020.emnlp-main.54> `doi:10.18653/v1/2020.emnlp-main.54`
- Semantic Reinforcement Learning Model for Education Question Answering (2023) <https://doi.org/10.21275/sr23213125341> `doi:10.21275/sr23213125341`
- When Iterative RAG Beats Ideal Evidence: A Diagnostic Study in Scientific Multi-hop Question Answering (2026) <https://www.semanticscholar.org/paper/37bbcda29cee967af1ed81c6259ac64e14e70cfe> `arxiv:2601.19827`
- MDER-DR: Multi-Hop Question Answering with Entity-Centric Summaries (2026) <https://www.semanticscholar.org/paper/622487eafd5422f02489df71a9e4e0679273dc60> `arxiv:2603.11223`
- CrossModalQA: A Cross-modal and Multi-hop Benchmark for Multimodal Retrieval-augmented Generation (2026) <https://arxiv.org/abs/2609.05518> `arxiv:2609.05518`
- In Situ Graph Reasoning and Knowledge Expansion Using Graph‐PRefLexOR (2025) <https://doi.org/10.1002/aidi.202500006> `doi:10.1002/aidi.202500006`
- Query Graph Generation for Answering Multi-hop Complex Questions from Knowledge Bases (2020) <https://doi.org/10.18653/v1/2020.acl-main.91> `doi:10.18653/v1/2020.acl-main.91`
- Multi-step Entity-centric Information Retrieval for Multi-Hop Question Answering (2019) <https://doi.org/10.18653/v1/d19-5816> `doi:10.18653/v1/d19-5816`
- Unsupervised Question Answering by Cloze Translation (2019) <https://doi.org/10.18653/v1/p19-1484> `arxiv:1906.04980`
- Evaluating Knowledge Graph-Enhanced Context for Multiple-Choice Question Answering (2025) <https://doi.org/10.1109/ickg66886.2025.00020> `doi:10.1109/ickg66886.2025.00020`
- A Survey on Knowledge Graphs: Representation, Acquisition, and Applications (2021) <https://doi.org/10.1109/tnnls.2021.3070843> `arxiv:2002.00388`
- Semantic Parsing on Freebase from Question-Answer Pairs (2013) <https://doi.org/10.18653/v1/d13-1160> `doi:10.18653/v1/d13-1160`
- ToolForge: A Data Synthesis Pipeline for Multi-Hop Search without Real-World APIs (2025) <https://arxiv.org/abs/2512.16149> `arxiv:2512.16149`
- GPB and BAC: two novel models towards building an intelligent motor fault maintenance question answering system (2024) <https://doi.org/10.1080/09544828.2024.2335135> `doi:10.1080/09544828.2024.2335135`
- ISEEQ: Information Seeking Question Generation Using Dynamic Meta-Information Retrieval and Knowledge Graphs (2022) <https://doi.org/10.1609/aaai.v36i10.21312> `doi:10.1609/aaai.v36i10.21312`
- Subgraph-Based Attention Network for Multi-Hop Question Answering (2024) <https://doi.org/10.1109/ijcnn60899.2024.10650851> `doi:10.1109/ijcnn60899.2024.10650851`
- Unifying Large Language Models and Knowledge Graphs: A Roadmap (2023) <http://arxiv.org/abs/2306.08302> `arxiv:2306.08302`
- Single and Multi-Hop Question-Answering Datasets for Reticular Chemistry with GPT-4-Turbo (n.d.) <https://doi.org/10.1021/acs.jctc.4c00805.s001> `doi:10.1021/acs.jctc.4c00805.s001`
- Self-Adaptive Reasoning on Sub-Questions for Multi-Hop Question Answering (2023) <https://doi.org/10.1109/icassp49357.2023.10097206> `doi:10.1109/icassp49357.2023.10097206`
- An overview of the BIOASQ large-scale biomedical semantic indexing and question answering competition (2015) <https://doi.org/10.1186/s12859-015-0564-6> `doi:10.1186/s12859-015-0564-6`
- Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions (2023) <https://doi.org/10.18653/v1/2023.acl-long.557> `doi:10.18653/v1/2023.acl-long.557`
- What Disease Does This Patient Have? A Large-Scale Open Domain Question Answering Dataset from Medical Exams (2021) <https://doi.org/10.3390/app11146421> `doi:10.3390/app11146421`
- Modeling Relational Data with Graph Convolutional Networks (2018) <https://doi.org/10.1007/978-3-319-93417-4_38> `arxiv:1703.06103`
- Knowledge Graphs (2021) <https://doi.org/10.1145/3447772> `arxiv:2003.02320`
- Table Pre-training: A Survey on Model Architectures, Pre-training Objectives, and Downstream Tasks (2022) <http://arxiv.org/abs/2201.09745> `arxiv:2201.09745`
- Question Answering on Freebase via Relation Extraction and Textual Evidence (2016) <https://doi.org/10.18653/v1/p16-1220> `doi:10.18653/v1/p16-1220`
- Question-Answering enhanced by Knowledge Graphs (2024) <https://doi.org/10.59350/3ar10-pfb19> `doi:10.59350/3ar10-pfb19`
- A comprehensive survey on integrating large language models with knowledge-based methods (2025) <https://doi.org/10.1016/j.knosys.2025.113503> `arxiv:2501.13947`
- Future Directions of Question Answering (2022) <https://doi.org/10.1007/978-3-031-16552-8_9> `doi:10.1007/978-3-031-16552-8_9`
- A survey on question answering technology from an information retrieval perspective (2011) <https://doi.org/10.1016/j.ins.2011.07.047> `doi:10.1016/j.ins.2011.07.047`
- A Comprehensive Survey on Automatic Knowledge Graph Construction (2023) <https://doi.org/10.1145/3618295> `doi:10.1145/3618295`
- QAngaroo (MedHop + WikiHop) - Constructing Datasets for Multi-hop Reading Comprehension Across Documents (2018) <https://zenodo.org/record/6407402> `doi:10.1162/tacl_a_00021`
- Retrieval-Augmented Generation for AI-Generated Content: A Survey (2024) <http://arxiv.org/abs/2402.19473> `arxiv:2402.19473`
- DeepProtein: deep learning library and benchmark for protein sequence learning (2025) <https://doi.org/10.1093/bioinformatics/btaf165> `arxiv:2410.02023`
- Organised Genome Dynamics in the Escherichia coli Species Results in Highly Diverse Adaptive Paths (2009) <https://doi.org/10.1371/journal.pgen.1000344> `doi:10.1371/journal.pgen.1000344`
- Reporting standards for endovascular aortic repair of aneurysms involving the renal-mesenteric arteries (2020) <https://doi.org/10.1016/j.jvs.2020.06.011> `doi:10.1016/j.jvs.2020.06.011`
- The science, policy and practice of nature-based solutions: An interdisciplinary perspective (2016) <https://doi.org/10.1016/j.scitotenv.2016.11.106> `doi:10.1016/j.scitotenv.2016.11.106`
- Frequently asked questions about in vivo chlorophyll fluorescence: practical issues (2014) <https://doi.org/10.1007/s11120-014-0024-6> `doi:10.1007/s11120-014-0024-6`
- Software Engineering for Self-Adaptive Systems: A Research Roadmap (2009) <https://doi.org/10.1007/978-3-642-02161-9_1> `doi:10.1007/978-3-642-02161-9_1`

</details>

## Appendix A. Evidence Ledger

### [Evidence] claims (3)

- **[Evidence]** UniKGQA proposes a novel approach for multi-hop KGQA task by unifying retrieval and reasoning in both model architecture and parameter learning. _(claim C001, confidence: high)_
  - [1], p. 1 (direct support, verified) "unifying retrieval and reasoning"
- **[Evidence]** Co-E is limited by the quality of the evidence it retrieves; bidirectional synchronization cannot reliably correct a wrong fact that is repeatedly supported by the retrieved corpus. _(claim C002, confidence: high)_
  - [2], p. 9 (direct support, verified) "cannot reliably correct a wrong fact"
- **[Evidence]** The main technical risk is that context enrichment may introduce noise from imperfect triple extraction, leading to overfitting or incorrect facts. _(claim C007, confidence: high)_
  - [2], p. 9 (direct support, verified) "cannot reliably correct a wrong fact"

### [Inference] claims (7)

- **[Inference]** If triple extraction from source passages is noisy, the enriched context subgraph may introduce incorrect facts, degrading multi-hop QA performance. _(claim C003, confidence: medium)_
  - [2], p. 9 (indirect support, verified) "cannot reliably correct a wrong fact"
- **[Inference]** The paper arXiv:2609.12230 proposes a context-augmented training framework that enriches each target KG triple with supporting triples from the same source text chunk to form a context graph, uses an LLM-judged history-aware adaptive repair pipeline to fix one-hop failures, and applies reinforcement learning from lower-hop QA to improve higher-hop generalization. _(claim C004, confidence: high)_
  - [3], p. 1 (indirect support, unverified) "For each primary KG triple, we attach supporting triples extracted from the same source text chunk to form a context graph (CG)."
- **[Inference]** The paper arXiv:2609.12230 proposes a context-augmented training framework that enriches each target KG triple with supporting triples from the same source text chunk (forming a context graph), uses an LLM-judged history-aware adaptive repair pipeline to fix one-hop failures, and applies reinforcement learning from lower-hop QA to improve higher-hop generalization. _(claim C005, confidence: high)_
  - [3], p. 2 (indirect support, unverified) "For each primary KG triple, we attach supporting triples extracted from the same source text chunk to form a context graph (CG)."
  - [3], p. 1 (indirect support, unverified) "We introduce an LLM-judged, history-aware adaptive repair pipeline that identifies unresolved one-hop failures, continually fine-tunes on targeted repair examples, and removes or quarantines problematic noisy triples."
  - [3], p. 1 (indirect support, unverified) "Finally, we employ reinforcement learning (RL) using lower-hop question-answer items and evaluate generalization on harder 3-hop, 4-hop, and 5-hop tasks."
- **[Inference]** The paper arXiv:2609.12230 proposes a context-augmented training framework that enriches each target triple with supporting triples from the same source text chunk (forming a context graph), uses an LLM-judged history-aware adaptive repair pipeline to fix one-hop failures, and applies reinforcement learning from lower-hop QA to improve higher-hop generalization. _(claim C006, confidence: medium)_
  - [3], p. 1 (indirect support, unverified) "supporting triples extracted from the same source text chunk"
  - [3], p. 1 (indirect support, unverified) "LLM-judged, history-aware adaptive repair pipeline"
  - [3], p. 1 (indirect support, unverified) "reinforcement learning (RL)"
- **[Inference]** If triple extraction from source passages is noisy, the enriched context subgraph may introduce incorrect facts, degrading multi-hop QA performance. _(claim C008, confidence: medium)_
  - [2], p. 9 (indirect support, verified) "cannot reliably correct a wrong fact"
- **[Inference]** No retrieved work combines cross‑passage context enrichment (using multiple related passages to build a context subgraph) with external knowledge‑base verification in an adaptive repair loop for multi‑hop question answering training. _(claim C009, confidence: medium)_
  - [17], abstract (weak support, unverified)
- **[Inference]** No retrieved work evaluates context‑enriched triple training with adaptive repair and RL transfer on standard open‑domain multi‑hop QA benchmarks (HotpotQA, MuSiQue, WebQSP, CWQ). _(claim C010, confidence: medium)_
  - [1], abstract (indirect support, verified) "unifying retrieval and reasoning in both model architecture and parameter learning"
  - [2], abstract (indirect support, verified) "training-free system built around synchronized bidirectional graph-text working memory"
  - [5], abstract (indirect support, unverified) "SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets"
  - [4], abstract (indirect support, unverified) "we propose to use a knowledge graph (KG) that is context-aware and distilled to contain query-relevant information"
  - [6], abstract (indirect support, verified) "training-free retrieval pipeline"
  - [7], abstract (indirect support, unverified) "Extracting triples from Vietnamese text to create knowledge graph"

## Appendix B. Search Log

| Query | Sources (status: results) | Papers |
|---|---|---|
| multi-hop question answering knowledge graph language model training context subgraph | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 13 |
| multi-hop question answering evaluation metrics EM F1 Hits@1 | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 10 |
| extracting triples from text for knowledge graph question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 15 |
| context enriched triple training multi-hop question answering | arxiv (ok: 1), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 16 |
| local context subgraph training multi-hop question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 15 |
| references of arxiv:2609.12230 | openalex (ok: 0) | 0 |
| citations of arxiv:2609.12230 | openalex (ok: 0) | 0 |
| subgraph retrieval multi-hop question answering | arxiv (ok: 10), openalex (ok: 10), semantic_scholar (error: 0), crossref (ok: 10) | 25 |
| cross passage context enrichment knowledge graph question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 7 |
| external knowledge base verification adaptive repair question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 10 |
| context enriched triple training adaptive repair reinforcement learning multi-hop question answering | arxiv (ok: 0), openalex (ok: 10), semantic_scholar (error: 0), crossref (ok: 10) | 20 |

## Appendix C. Investigation Log

Each step was chosen by the ResearchForge controller from the recorded research state.

| Step | Phase | Action | Why | Alternatives considered | Outcome | Information gain |
|---|---|---|---|---|---|---|
| 0 | INTAKE | INTAKE | Research idea received. | none | idea stored in the workspace | n/a |
| 1 | FORMALIZE | FORMALIZE | The idea has not been formalized into a testable research question. | none | +37 papers; +3 searches; idea formalized | 3 |
| 2 | PLAN | PLAN | No investigation plan exists yet, so it is unclear what must be determined. | none | +4 uncertainties; investigation plan recorded | 1 |
| 3 | INVESTIGATE | READ | Retrieved papers have not been analyzed enough to judge overlap. | none | +6 analyses | 3 |
| 4 | SYNTHESIZE | SYNTHESIZE | Analyses exist but the field has not been mapped. | none | landscape recorded | 1 |
| 5 | CRITIQUE | CRITIQUE | The idea has not been challenged yet. | none | +3 claims; +3 verified claims; critique recorded; uncertainties updated: U001, U002, U003, U004 | 4 |
| 6 | CHALLENGE | CHALLENGE (U005: Does published work contradict the current assessment: Unlike UniKGQA (whi) | The critique's assessment has not been challenged yet (U005); look for published work that contradicts it before investing in anything that builds on it. | none | +11 papers; +1 searches; +1 claims; +1 contradicted conclusions; +1 uncertainties; +1 resolved uncertainties | 6 |
| 7 | CRITIQUE | CRITIQUE (Does published work contradict the assessment that, unlike UniKGQA (which unifie) | The current critique predates contradicting evidence (U006 weakened); the assessment must be revised before continuing. | none | +1 claims; critique recorded | 1 |
| 8 | UNCERTAINTY | SEARCH (U001: Is there existing work that already trains language models on context-enri) | Most valuable next step for high-importance novelty question U001: score 1.26 = importance 3 x expected gain 0.6 x relevance 1 x evidence deficiency 0.7 / cost 1. Next best: CHALLENGE on U005 (0.85). | CHALLENGE U005 (0.85); COMPARE U001 (0.84) | +2 papers; +3 searches; +1 resolved uncertainties; uncertainties updated: U001 | 2.5 |
| 9 | UNCERTAINTY | SEARCH (U002: How much does the proposed method overlap with existing subgraph retrieval) | Most valuable next step for high-importance overlap question U002: score 0.903 = importance 3 x expected gain 0.717 x relevance 1 x evidence deficiency 0.42 / cost 1. Next best: CHALLENGE on U005 (0.85). | CHALLENGE U005 (0.85); REFINE U007 (0.81) | +14 papers; +1 searches; +1 resolved uncertainties; uncertainties updated: U002 | 4 |
| 10 | CHALLENGE | CHALLENGE (U005: Does published work contradict the current assessment: Unlike UniKGQA (whi) | Most valuable next step for high-importance contradiction question U005: score 0.85 = importance 3 x expected gain 0.425 x relevance 1 x evidence deficiency 1 / cost 1.5. Next best: REFINE on U007 (0.81). | REFINE U007 (0.81); SEARCH U004 (0.795) | +1 contradicted conclusions; +1 resolved uncertainties; uncertainties updated: U005 | 4 |
| 11 | CRITIQUE | CRITIQUE (Does published work contradict the current assessment: Unlike UniKGQA (which uni) | The current critique predates contradicting evidence (U005 weakened); the assessment must be revised before continuing. | none | +3 claims; +2 verified claims; critique recorded | 3 |
| 12 | UNCERTAINTY | REFINE (U007: The conclusion behind U006 was weakened by contradicting work; how should ) | Most valuable next step for high-importance direction question U007: score 0.81 = importance 3 x expected gain 0.5 x relevance 0.9 x evidence deficiency 0.6 / cost 1. Next best: REFINE on U008 (0.81). | REFINE U008 (0.81); SEARCH U004 (0.795) | +1 gaps; +3 modifications; +1 directions | 1 |
| 13 | CHALLENGE | CHALLENGE (U010: Is direction D001 already explored or contradicted: Modify the method to i) | Most valuable next step for high-importance contradiction question U010: score 1.8 = importance 3 x expected gain 0.9 x relevance 1 x evidence deficiency 1 / cost 1.5. Next best: INVESTIGATE_GAP on U009 (1.4). | INVESTIGATE_GAP U009 (1.4); SEARCH U004 (0.795) | +14 papers; +2 searches; +1 claims; +1 resolved uncertainties; uncertainties updated: U010 | 3.5 |
| 14 | CHALLENGE | INVESTIGATE_GAP (U009: Has gap G001 already been addressed: Lack of evaluation of context‑enriche) | Most valuable next step for high-importance novelty question U009: score 1.4 = importance 3 x expected gain 0.7 x relevance 1 x evidence deficiency 1 / cost 1.5. Next best: SEARCH on U004 (0.795). | SEARCH U004 (0.795); REFINE U008 (0.676) | +15 papers; +1 searches; +1 claims; +1 verified claims | 3 |
| 15 | UNCERTAINTY | REFINE (U008: The conclusion behind U005 was weakened by contradicting work; how should ) | Most valuable next step for high-importance direction question U008: score 0.676 = importance 3 x expected gain 0.417 x relevance 0.9 x evidence deficiency 0.6 / cost 1. Next best: VERIFY on U004 (0.392). | VERIFY U004 (0.392); READ U004 (0.367) | +1 directions; +1 experiment plans; +1 resolved uncertainties; uncertainties updated: U008 | 4 |
| 16 | FINALIZE | FINALIZE | Stopping: time budget reached (3600 s). | none | finalizing | n/a |
