# ResearchForge Investigation Report

Project `T-2609.12230__prepub__nochal__s0` · model `ollama-cloud/nemotron-3-super` · status **incomplete**

> Labels: **[Evidence]** directly supported by a verified quote from a retrieved source; **[Inference]** reasoning derived from cited evidence; **[Hypothesis]** proposed, not validated; **[Assumption]** taken as given without evidence; **[Experimental result]** observed in an executed experiment.

## 1. Executive Summary

**Investigated:** Multi‑hop question answering often relies on reasoning over a chain of facts in a knowledge graph, yet current language‑model training typically uses isolated head‑relation‑tail triples, depriving the model of the surrounding context that supports multi‑step inference. We propose to enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. The model will be fine‑tuned under two regimes: one using only the target triple/path and another that also incorporates the supporting context. To improve the reliability of the base facts, we will introduce an adaptive repair loop that detects one‑hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, we will apply reinforcement‑learning‑based optimization on lower‑hop QA instances and evaluate transfer to deeper multi‑hop queries.

**Research question:** In the setting of multi-hop question answering over knowledge graphs, does augmenting each training triple with additional triples from the same source passage (forming a local context subgraph) and applying an adaptive repair loop that iteratively corrects one-hop failures result in significantly higher exact match and F1 scores on 2-hop and 3-hop benchmark datasets compared to training on the target triple alone, when both models are first pre-trained on 1-hop question-answer pairs?

**Literature investigated:** 101 papers retrieved from 8 searches (openalex: 33, arxiv: 32, crossref: 25, semantic_scholar: 19); 25 analyzed; 25 rated highly relevant.

**Assessment:** Promising but requires experimental validation. **[Inference]** While the idea addresses a clear gap and offers a novel combination of techniques, significant overlap with existing context-enrichment and iterative refinement methods raises novelty concerns. Empirical validation is needed to determine whether the proposed combination yields measurable gains over strong baselines.

**Closest existing work:** Ontology-Guided Evidence Path Inference for Multi-hop Knowledge Graph Question Answering (2026) [1]

**Potential overlap:** Overlaps with OPI in targeting noisy mixed-type paths and improving semantic alignment; both use iterative processes (refinement vs repair loop) and aim to utilize structural constraints. However, OPI relies on an ontology graph and bidirectional retrieval, while the idea enriches triples with passage-derived subgraphs and uses an adaptive repair loop.

**Potential distinction:** The idea differs by focusing on training-time enrichment of triples with local context from the same passage, employing an adaptive repair loop that detects and corrects one-hop failures via corrective examples, and applying reinforcement learning on lower-hop QA instances for transfer to deeper multi-hop queries—components not combined in existing work.

**Major risk:** The idea may overlap significantly with existing approaches such as OPI, which already uses ontology-guided retrieval and iterative refinement to filter spurious evidence (C001) and address noisy mixed-type paths (C002). The adaptive repair loop may be similar to iterative refinement strategies, raising novelty concerns (U006). Additionally, performance gains could be confounded by the inherent reasoning ability of LLMs (C003).

**Potential gap:** **[Hypothesis]** No existing work enriches training triples with local context subgraphs from the same passage for multi-hop knowledge graph question answering, which limits the model's ability to leverage passage-level contextual supervision during training. (confidence: medium; 1 gap(s) recorded)

**Recommended modification:** **[Hypothesis]** Training Data Enrichment Only: Simplify the proposed method by using only the training regime that enriches each target triple with local context subgraphs from the same passage, and omit the adaptive repair loop and reinforcement learning lower-hop transfer stages.

**Research decision:** Insufficient evidence. **[Inference]** Basis: high-importance questions remain unresolved (U001, U002). This describes the state of the evidence, not the absolute value of the idea.

**Investigation:** 13 steps chosen from the research state; 6 uncertainties raised, 1 resolved, 5 still open or unresolved (Section 13, Appendix C).

**Stopped by a safety limit:** Stopping: tool-call budget reached (250). Conclusions below cover only what was recorded before the limit.

**Claim grounding:** 11/13 evidence and inference claims have at least one verified source.

**Incomplete phases:** experiments. Sections that depend on them are marked as not recorded.

This report does not declare the idea novel. Absence of a matching paper in these searches does not establish novelty; see Section 13.

## 2. Original Research Idea

> Multi‑hop question answering often relies on reasoning over a chain of facts in a knowledge graph, yet current language‑model training typically uses isolated head‑relation‑tail triples, depriving the model of the surrounding context that supports multi‑step inference. We propose to enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. The model will be fine‑tuned under two regimes: one using only the target triple/path and another that also incorporates the supporting context. To improve the reliability of the base facts, we will introduce an adaptive repair loop that detects one‑hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, we will apply reinforcement‑learning‑based optimization on lower‑hop QA instances and evaluate transfer to deeper multi‑hop queries.

## 3. Formalized Research Question

**Research question:** In the setting of multi-hop question answering over knowledge graphs, does augmenting each training triple with additional triples from the same source passage (forming a local context subgraph) and applying an adaptive repair loop that iteratively corrects one-hop failures result in significantly higher exact match and F1 scores on 2-hop and 3-hop benchmark datasets compared to training on the target triple alone, when both models are first pre-trained on 1-hop question-answer pairs?

**Hypothesis:** **[Hypothesis]** Enriching training data with local context subgraphs and using an adaptive repair loop will improve the model's ability to perform multi-hop reasoning, especially when transferring from lower-hop to higher-hop QA, leading to higher exact match and F1 scores on benchmark datasets compared to training on isolated triples alone.

| Aspect | Formalization |
|---|---|
| Problem | Multi-hop question answering often relies on reasoning over a chain of facts in a knowledge graph, yet current language-model training typically uses isolated head-relation-tail triples, depriving the model of the surrounding context that supports multi-step inference. |
| Target domain | Multi-hop question answering over knowledge graphs |
| Proposed method | Enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. Fine-tune the model under two regimes: (1) using only the target triple/path, and (2) using the target triple/path plus the local context subgraph. Introduce an adaptive repair loop that detects one-hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, apply reinforcement-learning-based optimization on lower-hop QA instances and evaluate transfer to deeper multi-hop queries. |
| Target system | Language models fine-tuned for knowledge graph-based question answering |
| Expected contribution | A training method that improves multi-hop QA performance by providing contextual supervision and iterative error correction, bridging the gap between isolated triple training and structured reasoning. |
| Independent variables | Training regime (with context vs without), Presence of adaptive repair loop, RL optimization stage |
| Dependent variables | Exact Match score, F1 score on 2-hop and 3-hop questions |
| Controls | Base model architecture, Dataset size, Training duration, Random seed |

**Assumptions**

- The source passage contains relevant triples that can form a useful context subgraph.
- The adaptive repair loop can effectively detect and correct one-hop failures.
- RL-based optimization on lower-hop QA instances will transfer to deeper multi-hop queries.

**Expected benefits / potential risks**

- Benefit: Improved accuracy on multi-hop QA benchmarks
- Benefit: Better generalization from lower-hop to higher-hop reasoning
- Benefit: Reduced reliance on spurious correlations
- Risk: Context noise may degrade performance if irrelevant triples are included
- Risk: Adaptive repair loop may amplify errors if not properly constrained
- Risk: RL optimization may be unstable or require extensive hyperparameter tuning

**Ambiguities**

| Question | Resolution | Resolved by |
|---|---|---|
| Which multi-hop QA datasets are typically used for evaluation? | Commonly used datasets include HotpotQA, 2WikiMultiHopQA, MetaQA, and MuSiQue, as evidenced by papers such as KGEIR and SG-RAG MOT. | literature |
| What type of language model is being fine-tuned? | Recent work uses large language models (LLMs) such as LLaMA, T5, or BERT-based models, as seen in UniKGQA and SG-RAG MOT. | literature |
| What metrics are used to evaluate performance? | Exact Match (EM) and F1 score are standard for QA evaluation, as demonstrated in the HotpotQA dataset paper and widely adopted in the field. | literature |
| How is the 'local context subgraph' defined? | Assumed to be the set of triples extracted from the same sentence or paragraph as the target triple, based on typical information extraction pipelines for QA. | assumption |
| What constitutes a 'one-hop failure' in the adaptive repair loop? | Assumed to be a failure to correctly predict the relation or entity for a single-hop query derived from the knowledge graph. | assumption |
| What is the 'reinforcement-learning-based optimization' stage? | Assumed to involve policy gradient methods that maximize reward based on QA accuracy, similar to approaches like DeepPath or KG-Reasoner. | assumption |
| What are considered 'lower-hop QA instances'? | Lower-hop QA instances typically refer to 1-hop questions, which are used as supervision signals for intermediate reasoning, as shown in works like 'Improving Multi-hop Knowledge Base Question Answering by Learning Intermediate Supervision Signals'. | literature |

## 4. Existing Research

Overlap values are heuristic signals assigned during analysis, not measurements of novelty.

| Paper | Relevance | Method | Problem / method / evaluation overlap | Read from |
|---|---|---|---|---|
| Improving Multi-hop Knowledge Base Question Answering by Learning Intermediate Supervision Signals (2021) [2] | high | Teacher-student framework: student network predicts final answer; teacher network learns intermediate supervision signals via forward and backward reasoning to provide more reliable entity distributions at intermediate steps, which are used as supervision signals for the student network. | 0.6 / 0.4 / 0.5 | full_text |
| Graphhopper: Multi-Hop Scene Graph Reasoning for Visual Question Answering (2021) [3] | high | Graphhopper: derive a scene graph describing objects, attributes, and relationships from an image; train a reinforcement learning agent to autonomously navigate in a multi-hop manner over the extracted scene graph to generate reasoning paths, which are used to derive answers. | 0.1 / 0.1 / 0.1 | full_text |
| Few-Shot Data Synthesis for Open Domain Multi-Hop Question Answering (2023) [4] | high | Data synthesis framework: start from Wikipedia document pairs, prompt LLMs to generate questions, answers, and queries (single or two), verify queries via retrievers, then fine-tune smaller language models on the synthetic data. | 0.5 / 0.4 / 0.6 | full_text |
| PokeMQA: Programmable knowledge editing for Multi-hop Question Answering (2023) [5] | high | PokeMQA: a programmable knowledge editing framework that decouples jobs by using a trainable scope detector to detect conflicts and a knowledge prompt generator to retrieve relevant contextual information, allowing LLMs to be prompted with augmented input to answer multi-hop questions based on edite | 0.4 / 0.2 / 0.3 | full_text |
| Dr3: Ask Large Language Models Not to Give Off-Topic Answers in Open Domain Multi-Hop Question Answering (2024) [6] | high | Dr3 mechanism: Discriminator judges whether the generated answer is on-topic using LLM intrinsic capabilities; if off-topic, Corrector performs stepwise revisions along the reversed reasoning chain (Re-Compose → Re-Solve → Re-Decompose) until the answer becomes on-topic. | 0.3 / 0.2 / 0.2 | full_text |
| A Method for Multi-Hop Question Answering on Persian Knowledge Graph (2025) [7] | high | Developed a dataset of 5,600 Persian multi-hop complex questions with decomposed forms based on semantic representation (MRDCPQ); trained Persian language models using this dataset; proposed an architecture comprising question decomposition component, MRDCPQ to SPARQL query generator component, and  | 0.4 / 0.2 / 0.3 | full_text |
| Mitigating Lost-in-Retrieval Problems in Retrieval Augmented Multi-Hop Question Answering (2025) [8] | high | ChainRAG: a progressive retrieval and rewriting framework that constructs a sentence graph with entity indexing, performs question decomposition, retrieves relevant sentences from the graph, and rewrites sub-questions to complete missing key entities, iteratively building a seamless chain for accura | 0.5 / 0.3 / 0.7 | full_text |
| VLMT: Vision-Language Multimodal Transformer for Multimodal Multi-hop Question Answering (2025) [9] | high | Vision-Language Multimodal Transformer (VLMT) integrates a transformer-based vision encoder with a sequence-to-sequence language model, uses direct token-level injection to fuse visual and textual inputs in a shared embedding space, employs a three-stage pretraining strategy to progressively align v | 0.2 / 0.1 / 0.1 | full_text |
| Autofocus Retrieval: An Effective Pipeline for Multi-Hop Question Answering With Semi-Structured Knowledge (2025) [10] | high | FocusedRetriever: a modular SKB-based framework integrating (1) VSS-based entity search, (2) LLM-based generation of Cypher queries from natural language, (3) node set joins to filter answer candidates using extracted triplets and constraints, (4) vector similarity search to retrieve and rank releva | 0.4 / 0.2 / 0.3 | full_text |
| Optimizing Question Semantic Space for Dynamic Retrieval-Augmented Multi-hop Question Answering (2025) [11] | high | Q-DREAM: a three-module pipeline comprising (1) Question Decomposition Module (QDM) that splits multi-hop questions into fine-grained subquestions; (2) Subquestion Dependency Optimizer Module (SDOM) that models interdependent relations among subquestions; (3) Dynamic Passage Retrieval Module (DPRM)  | 0.5 / 0.2 / 0.6 | full_text |
| DynaSearcher: Dynamic Knowledge Graph Augmented Search Agent via Multi-Reward Reinforcement Learning (2025) [12] | high | DynaSearcher: leverages knowledge graphs as external structured knowledge to guide the search process by explicitly modeling entity relationships, ensuring factual consistency in intermediate queries and mitigating biases from irrelevant information; employs a multi-reward RL framework for fine-grai | 0.6 / 0.4 / 0.5 | full_text |
| StepChain GraphRAG: Reasoning Over Knowledge Graphs for Multi-Hop Question Answering (2025) [13] | high | StepChain GraphRAG builds a global index over the corpus; at inference, retrieves passages are parsed on-the-fly into a knowledge graph; the complex query is split into sub-questions; for each sub-question, a BFS-based traversal dynamically expands along relevant edges, assembling explicit evidence  | 0.6 / 0.4 / 0.5 | full_text |
| Reinforcement Learning Enhanced Multi-hop Reasoning for Temporal Knowledge Question Answering (2026) [14] | high | Multi-hop Reasoning Enhanced (MRE) framework: (1) prompt engineering to guide LLM in generating diverse reasoning trajectories; (2) selecting valid trajectories for supervised fine-tuning (cold-start); (3) Tree-Group Relative Policy Optimization (T-GRPO)—a recursive, tree-structured learning-by-expl | 0.6 / 0.4 / 0.5 | full_text |
| CacheRAG: A Semantic Caching System for Retrieval-Augmented Generation in Knowledge Graph Question Answering (2026) [15] | high | CacheRAG: a systematic cache-augmented architecture for LLM-based KGQA that transforms stateless planners into continual learners via (1) Schema-agnostic user interface (two-stage semantic parsing via Intermediate Semantic Representation), (2) Diversity-optimized cache retrieval (two-layer hierarchi | 0.5 / 0.2 / 0.3 | full_text |
| Ontology-Guided Evidence Path Inference for Multi-hop Knowledge Graph Question Answering (2026) [1] | high | OPI (Ontology-Guided Evidence Path Inference) framework: (1) construct a relation-centric ontology graph capturing head-tail type constraints of relations for answer-side constraints; (2) bidirectional retrieval: map predicted answer type to compatible final-hop relations, combine topic-side prefix  | 0.8 / 0.5 / 0.6 | full_text |
| IterCOMP: Reasoning-aware Adaptive Prompt Compression for Multi-hop Question Answering (2026) [16] | high | IterCOMP: a unified, training-free prompt compression framework that incorporates multi-hop reasoning within an iterative compression loop. It decomposes documents into evidence segments, evaluates question answerability, and generates targeted follow-up questions to iteratively integrate essential  | 0.4 / 0.2 / 0.3 | full_text |
| Multi-hop clustering for reasoning chain extraction in multi-hop question answering (2026) [17] | high | not stated in abstract | 0.0 / 0.0 / 0.0 | abstract |
| Incorporating multi-perspective information into reinforcement learning to address multi-hop knowledge graph question answering (2024) [18] | high | not stated in abstract | 0.0 / 0.0 / 0.0 | abstract |
| Incorporating anticipation embedding into reinforcement learning framework for multi-hop knowledge graph question answering (2022) [19] | high | not stated in abstract | 0.0 / 0.0 / 0.0 | abstract |
| Reinforcement learning with dynamic completion for answering multi-hop questions over incomplete knowledge graph (2023) [20] | high | not stated in abstract | 0.0 / 0.0 / 0.0 | abstract |
| Path-based multi-hop reasoning over knowledge graph for answering questions via adversarial reinforcement learning (2023) [21] | high | not stated in abstract | 0.0 / 0.0 / 0.0 | abstract |
| Multi-hop Question Answering (2024) [22] | high | This paper is a survey; it does not propose a new method but organizes and summarizes existing MHQA frameworks, datasets, evaluation techniques, and generation methods. | 0.6 / 0.1 / 0.5 | abstract |
| Hierarchical Graph Network for Multi-hop Question Answering (2020) [23] | high | Hierarchical Graph Network (HGN) constructs a hierarchical graph with nodes at different granularities (question, paragraph, sentence, entity), encodes them with pretrained contextual encoders (e.g., RoBERTa), performs graph reasoning via GNN, and jointly predicts paragraph selection, supporting fac | 0.6 / 0.3 / 0.7 | full_text |
| Scalable Multi-Hop Relational Reasoning for Knowledge-Aware Question Answering (2020) [24] | high | MHGRN (Multi-hop Graph Relation Network) equips pretrained language models with a multi-hop relational reasoning module that performs multi-hop, multi-relational reasoning over subgraphs extracted from external KGs, unifying path-based reasoning and GNNs via structured relational attention, and supp | 0.6 / 0.3 / 0.6 | full_text |
| KGEIR: Knowledge Graph-Enhanced Iterative Reasoning for Multi-Hop Question Answering (2025) [25] | high | KGEIR: dynamically constructs and refines knowledge graphs during question answering. It identifies key entities from questions, builds an initial graph from retrieved paragraphs, reasons over this structure, identifies information gaps, and iteratively retrieves additional context to refine the gra | 0.5 / 0.3 / 0.8 | full_text |

<details><summary>Full paper analyses</summary>

#### Improving Multi-hop Knowledge Base Question Answering by Learning Intermediate Supervision Signals (2021) [2]

- **Problem:** Multi-hop Knowledge Base Question Answering (KBQA) lacks supervision signals at intermediate reasoning steps, making learning unstable or ineffective because only final answer feedback is available.
- **Method:** Teacher-student framework: student network predicts final answer; teacher network learns intermediate supervision signals via forward and backward reasoning to provide more reliable entity distributions at intermediate steps, which are used as supervision signals for the student network.
- **Main contribution:** Proposes a novel teacher-student approach that learns intermediate supervision signals via forward and backward reasoning, demonstrating effectiveness on three benchmark datasets (MetaQA, WebQuestionsSP, Complex WebQuestions) and showing improvement over baseline NSM model, especially on harder datasets where Hits@1 increases by up to ~5.6 absolute points.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** MetaQA-1hop, MetaQA-2hop, MetaQA-3hop, WebQuestionsSP (webqsp), Complex WebQuestions 1.1 (CWQ), MetaQA-1hop, MetaQA-2hop, MetaQA-3hop, WebQuestionsSP, Complex WebQuestions 1.1 (CWQ)
- **Baselines:** KV-Mem, GraftNet, PullNet, SRN, EmbedKGQA, NSM (Neural State Machine)
- **Metrics:** Hits@1, F1
- **Results:** MetaQA-1hop: NSM 97.1%, NSM+𝑝 97.3%, NSM+ℎ 97.2%; MetaQA-2hop: NSM 99.9%, NSM+𝑝 99.9%, NSM+ℎ 99.9%; MetaQA-3hop: NSM 98.9%, NSM+𝑝 98.9%, NSM+ℎ 98.9%; WebQuestionsSP: NSM 68.7%, NSM+𝑝 73.9%, NSM+ℎ 74.3%; Complex WebQuestions: NSM 47.6%, NSM+𝑝 48.3%, NSM+ℎ 48.8%. F1 scores follow similar trends.
- **Limitations:** Not explicitly stated in the paper.
- **Future work:** Enhancing entity embeddings using KB embedding methods to obtain better intermediate supervision signals.
- **Code availability:** not stated in abstract
- **Relation to idea:** Both aim to improve multi-hop reasoning via supervisory signals: the idea enriches training triples with local context subgraphs and uses an adaptive repair loop to generate corrective examples from one-hop failures followed by RL lower-hop transfer, while this paper learns intermediate supervision signals via a teacher network performing forward/backward reasoning to guide a student network. Overlap in using supervision signals; differences in mechanism (training data enrichment + failure-driven examples vs teacher-student intermediate signal learning) and stage (training data modification vs inference-time guidance). _(basis: not stated)_

#### Graphhopper: Multi-Hop Scene Graph Reasoning for Visual Question Answering (2021) [3]

- **Problem:** Visual Question Answering (VQA) requires understanding and reasoning over image and language, but existing methods lack explicit reasoning capabilities for complex questions requiring long reasoning chains.
- **Method:** Graphhopper: derive a scene graph describing objects, attributes, and relationships from an image; train a reinforcement learning agent to autonomously navigate in a multi-hop manner over the extracted scene graph to generate reasoning paths, which are used to derive answers.
- **Main contribution:** Graphhopper keeps up with human performance on manually curated scene graphs and outperforms another state-of-the-art scene graph reasoning model (NSM) by a significant margin on both manually curated and automatically generated scene graphs.
- **Key assumptions:** The scene graph accurately captures the objects and their relationships in the image.; The RL agent can learn an effective navigation policy to reach correct answers.; Reasoning paths over the scene graph correspond to valid reasoning chains for answering the question.
- **Datasets / benchmarks:** GQA (manually curated scene graphs), GQA (automatically generated scene graphs), GQA
- **Baselines:** Human performance, Neural State Machine (NSM)
- **Metrics:** Accuracy (Hits@1), Binary accuracy, Open accuracy, Consistency, Validity, Plausibility
- **Results:** On manually curated scene graphs: Graphhopper Accuracy 92.30, Human 89.3, NSM 34.5; Binary 92.18 vs Human 91.2 vs NSM 51.03; Open 92.40 vs Human 87.4 vs NSM 18.79; Consistency 91.92 vs Human 98.4 vs NSM 81.36; Validity 93.68 vs Human 98.9 vs NSM 83.69; Plausibility 93.13 vs Human 97.2 vs NSM 79.12. On automatically generated scene graphs: Graphhopper outperforms NSM by a significant margin (exact numbers not given in abstract).
- **Limitations:** Not explicitly stated in the paper.
- **Future work:** Not explicitly stated in the paper.
- **Code availability:** not stated in abstract
- **Relation to idea:** Graphhopper addresses visual question answering using scene graphs and reinforcement learning, while the idea focuses on training data enrichment for textual knowledge graph question answering. Overlap is minimal as they target different modalities and reasoning settings. _(basis: not stated)_

#### Few-Shot Data Synthesis for Open Domain Multi-Hop Question Answering (2023) [4]

- **Problem:** Few-shot learning for open domain multi-hop question answering relies on large language models (LLMs) which are inefficient at inference time; need to improve smaller language models with limited human-annotated question-answer pairs.
- **Method:** Data synthesis framework: start from Wikipedia document pairs, prompt LLMs to generate questions, answers, and queries (single or two), verify queries via retrievers, then fine-tune smaller language models on the synthetic data.
- **Main contribution:** Proposes a data synthesis framework that enables improving smaller LMs (e.g., LLaMA 7B/65B) with fewer than 10 human-annotated QA pairs, achieving competitive performance with prior methods while using much smaller model sizes; demonstrates significant improvements on HotpotQA, MuSiQue, 2WikiQA, and FEVER benchmarks.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** HotpotQA, MuSiQue, 2WikiMultiHopQA (2WikiQA), FEVER, HotpotQA, MuSiQue, 2WikiMultiHopQA, FEVER
- **Baselines:** Prior few-shot prompting approaches (SelfAsk, DSP), re-implemented with LLaMA, plus self-consistency
- **Metrics:** Exact Match (EM), F1 score, accuracy (for FEVER)
- **Results:** Fine-tuned LLaMA 65B on synthetic data: HotpotQA EM 46.4%, F1 58.6%; MuSiQue EM 29.6%, F1 38.6%; 2WikiQA EM 49.3%, F1 56.6%; FEVER accuracy 64.1%. With self-consistency improves further (e.g., HotpotQA EM 49.7%, F1 62.1%).
- **Limitations:** Approach depends on synthesizing large amounts of data, which is expensive even with smaller LLMs; fine-tuning language models is not applicable to closed-source language models (e.g., GPT-3); third limitation not fully captured in available text.
- **Future work:** Finding the exact optimal amount of finetuning data for future work.
- **Code availability:** not stated in abstract
- **Relation to idea:** Both aim to improve multi-hop QA performance via training data augmentation: the idea enriches each target triple with local context subgraphs from the same passage and uses an adaptive repair loop to generate corrective examples from one-hop failures followed by RL lower-hop transfer, while this paper synthesizes new question-answer-claim tuples via LLMs from document pairs, filters them, and fine-tunes smaller LMs on the synthetic data. Overlap in generating additional training data; differences in mechanism (local context enrichment + failure-driven correction vs LLM-based question generation + verification) and additional components (adaptive repair loop, RL lower-hop transfer) in the idea. _(basis: not stated)_

#### PokeMQA: Programmable knowledge editing for Multi-hop Question Answering (2023) [5]

- **Problem:** Knowledge editing for multi-hop question answering requires updating models with up-to-date facts while avoiding expensive retraining; existing methods that mix prompts for editing and reasoning suffer from unreliable reasoning due to coupling of disparate tasks.
- **Method:** PokeMQA: a programmable knowledge editing framework that decouples jobs by using a trainable scope detector to detect conflicts and a knowledge prompt generator to retrieve relevant contextual information, allowing LLMs to be prompted with augmented input to answer multi-hop questions based on edited facts without modifying model parameters.
- **Main contribution:** PokeMQA demonstrates superior performance in knowledge editing of multi-hop QA across three LLM backbones and two benchmark datasets (MQUAKE-CF-3K and MQUAKE-T), outperforming baselines by a large margin and consistently producing reliable reasoning processes.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** MQUAKE-CF-3K, MQUAKE-T, MQUAKE-CF-3K, MQUAKE-T
- **Baselines:** FT (fine-tuning), ROME, MEMIT, MeLLo (memory-based)
- **Metrics:** Multi-hop accuracy (Hop-Acc)
- **Results:** PokeMQA achieves the highest Hop-Acc across all settings, e.g., for LLaMa-2-7B with 1 edited batch ~45.8% and for GPT-3.5-turbo-instruct with 1 edited batch ~67.3%, significantly outperforming baselines such as MeLLo (~57.4% and ~88.1%? Actually MeLLo higher for GPT-3.5? We note PokeMQA outperforms baselines by large margin in almost all settings.
- **Limitations:** The scope detector architecture is not task‑specific optimized for higher fact retrieval accuracy; context length pressure on LLM reasoning capabilities for complex multi‑hop questions is not fully mitigated.
- **Future work:** Improving the scope detector for higher fact retrieval accuracy and mitigating context length pressure; addressing challenges of combining more facts for complex reasoning processes.
- **Code availability:** https://github.com/Hengrui-Gu/PokeMQA
- **Relation to idea:** Both aim to improve multi-hop QA correctness under knowledge changes: the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop to generate corrective examples from one‑hop failures followed by RL lower‑hop transfer, while PokeMQA uses a trainable scope detector and knowledge prompt generator to detect conflicts and generate appropriate prompts for knowledge editing at inference time without modifying model weights. Overlap in using additional components to guide LLMs; differences in mechanism (training data enrichment + failure‑driven correction vs inference‑time detection + prompting) and stage (training vs inference). _(basis: not stated)_

#### Dr3: Ask Large Language Models Not to Give Off-Topic Answers in Open Domain Multi-Hop Question Answering (2024) [6]

- **Problem:** Large Language Models (LLMs) may generate off-topic answers in open-domain multi-hop question answering, which account for approximately one-third of incorrect answers.
- **Method:** Dr3 mechanism: Discriminator judges whether the generated answer is on-topic using LLM intrinsic capabilities; if off-topic, Corrector performs stepwise revisions along the reversed reasoning chain (Re-Compose → Re-Solve → Re-Decompose) until the answer becomes on-topic.
- **Main contribution:** Dr3 mechanism considerably reduces off-topic answers in ODMHQA by nearly 13% and improves Exact Match (EM) by nearly 3% compared to baseline without Dr3 on HotpotQA and 2WikiMultiHopQA datasets.
- **Key assumptions:** The Discriminator can reliably detect off-topic answers.; The Corrector can successfully revise the reasoning chain to correct off-topic answers.
- **Datasets / benchmarks:** HotpotQA, 2WikiMultiHopQA, HotpotQA, 2WikiMultiHopQA
- **Baselines:** Baseline method without Dr3 (likely ReAct+)
- **Metrics:** Exact Match (EM)
- **Results:** Dr3 reduces off-topic answers by nearly 13% and improves EM by nearly 3% compared to baseline.
- **Limitations:** Not explicitly stated in the paper.
- **Future work:** Not explicitly stated in the paper.
- **Code availability:** https://github.com/Gy915/Dr3
- **Relation to idea:** Dr3 addresses off-topic answers via post-hoc correction (Discriminator-Corrector loop), while the idea enriches training triples with local context subgraphs and uses an adaptive repair loop for one-hop failures. Both aim to improve correctness but differ in focus (inference-time correction vs training data enrichment and failure-driven example generation). _(basis: not stated)_

#### A Method for Multi-Hop Question Answering on Persian Knowledge Graph (2025) [7]

- **Problem:** Accurate understanding and transformation of Persian multi-hop complex questions into semantically equivalent SPARQL queries is a major challenge for Persian knowledge graph question answering (KGQA).
- **Method:** Developed a dataset of 5,600 Persian multi-hop complex questions with decomposed forms based on semantic representation (MRDCPQ); trained Persian language models using this dataset; proposed an architecture comprising question decomposition component, MRDCPQ to SPARQL query generator component, and SPARQL query execution and response composition for answering complex questions using a Persian knowledge graph.
- **Main contribution:** The proposed method achieves an improvement of 12.57% in F1-score and 12.06% in accuracy over the best comparable method (Etezadi’s Method) on the PeCoQ dataset, demonstrating superiority in answering complex Persian questions via knowledge graph-based semantic decomposition and SPARQL generation.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** PeCoQ, Persian MRDCPQ dataset (5,600 questions), PeCoQ
- **Baselines:** Best comparable method (Etezadi’s Method)
- **Metrics:** F1-score, Accuracy
- **Results:** Our Method: Precision 84.36%, Recall 68.41%, F1 75.55%, Accuracy 74.81%; Etezadi’s Method: Precision 71.24%, Recall 56.45%, F1 62.98%, Accuracy 62.75%.
- **Limitations:** Not explicitly stated in the paper.
- **Future work:** Not explicitly stated in the paper.
- **Code availability:** not stated in abstract
- **Relation to idea:** Both aim to improve multi-hop QA performance: the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop to generate corrective examples from one‑hop failures followed by RL lower‑hop transfer, while this paper focuses on question decomposition, semantic representation conversion to SPARQL, and execution on a Persian knowledge graph for Persian KGQA. Overlap in addressing multi‑hop challenges; differences in mechanism (training data enrichment + failure‑driven RL vs decomposition + SPARQL generation) and language/domain specificity (general vs Persian). _(basis: not stated)_

#### Mitigating Lost-in-Retrieval Problems in Retrieval Augmented Multi-Hop Question Answering (2025) [8]

- **Problem:** In retrieval-augmented multi-hop question answering, the key entities are often missed in LLMs’ sub-question decomposition, known as the “lost-in-retrieval” problem, which degrades retrieval performance and disrupts the reasoning chain, leading to incorrect answers.
- **Method:** ChainRAG: a progressive retrieval and rewriting framework that constructs a sentence graph with entity indexing, performs question decomposition, retrieves relevant sentences from the graph, and rewrites sub-questions to complete missing key entities, iteratively building a seamless chain for accurate retrieval and answer generation.
- **Main contribution:** ChainRAG consistently outperforms baselines (NaiveRAG, Iter-RetGen, LongRAG, HippoRAG+IR-CoT) on MuSiQue, 2WikiMultiHopQA, and HotpotQA datasets in both effectiveness (F1/EM) and efficiency, demonstrating that mitigating lost-in-retrieval improves multi-hop QA performance.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** MuSiQue, 2WikiMultiHopQA (2Wiki), HotpotQA, MuSiQue, 2WikiMultiHopQA, HotpotQA
- **Baselines:** NaiveRAG, Iter-RetGen (Shao et al., 2023), LongRAG (Jiang et al., 2024), HippoRAG w/ IR-CoT (Gutiérrez et al., 2024)
- **Metrics:** Exact Match (EM), F1-score
- **Results:** ChainRAG (CxtInt variant) achieves EM 49.40% on MuSiQue, 70.58% on 2Wiki, 64.22% on HotpotQA; F1 38.00%, 61.50%, 50.00% respectively. Compared to NaiveRAG, ChainRAG improves average F1 by approximately 60% on MuSiQue and shows significant gains across all datasets vs advanced RAG methods.
- **Limitations:** The iterative process of retrieval and sub-question rewriting increases computational resources and time compared to NaiveRAG, posing challenges for resource-constrained environments; additional limitations not fully captured in the available text.
- **Future work:** Optimize efficiency by exploring lightweight graph traversal and adaptive termination strategies to reduce LLM calls and resource consumption; enhance dynamic adaptability by developing dataset-specific edge construction policies to better align with diverse text structures.
- **Code availability:** not stated in abstract
- **Relation to idea:** Both aim to improve retrieval-augmented multi-hop QA: the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop to generate corrective examples from one‑hop failures followed by RL lower‑hop transfer, while ChainRAG focuses on mitigating lost-in-retrieval via sentence graph construction, question decomposition, retrieval, and sub‑question rewriting at inference time. Overlap in using additional context to improve reasoning; differences in mechanism (training data enrichment + failure‑driven RL vs graph‑based retrieval + rewriting) and stage (training vs inference). _(basis: not stated)_

#### VLMT: Vision-Language Multimodal Transformer for Multimodal Multi-hop Question Answering (2025) [9]

- **Problem:** Existing methods for Multimodal Multi-hop Question Answering (MMQA) suffer from limited reasoning capabilities, reliance on modality conversion, and inadequate alignment between visual and textual representations.
- **Method:** Vision-Language Multimodal Transformer (VLMT) integrates a transformer-based vision encoder with a sequence-to-sequence language model, uses direct token-level injection to fuse visual and textual inputs in a shared embedding space, employs a three-stage pretraining strategy to progressively align vision-language representations, and instantiates two task-specific modules (multimodal reranker and multimodal QA model) to form a two-stage MMQA framework.
- **Main contribution:** VLMT-Large achieves 76.5% Exact Match and 80.1% F1 on MultimodalQA validation set, outperforming previous SOTA by +9.1% EM and +8.8% F1; on WebQA, it attains a QA score of 47.6, surpassing PERQA by +3.2.
- **Key assumptions:** Direct token-level injection effectively fuses modalities without intermediate projection layers.; Three-stage pretraining sufficiently aligns vision and language representations for multimodal reasoning.; The two-stage framework (reranker then QA) efficiently retrieves relevant contexts and generates grounded answers.
- **Datasets / benchmarks:** MultimodalQA, WebQA, MultimodalQA, WebQA
- **Baselines:** PERQA, VLP, VLP+VinVL, and other baselines mentioned in related work
- **Metrics:** Exact Match (EM), F1 score, QA score (for WebQA)
- **Results:** VLMT-Large: MultimodalQA EM 76.5%, F1 80.1%; WebQA QA score 47.6.
- **Limitations:** Reliance on modality conversion pipelines (e.g., image-to-text) can introduce information degradation and challenges for real-world deployment; persistent challenges in efficient alignment and reasoning across modalities.
- **Future work:** Not explicitly stated in the paper.
- **Code availability:** not stated in abstract
- **Relation to idea:** VLMT focuses on multimodal fusion and pretraining for vision-language reasoning, while the idea focuses on training data enrichment with local context subgraphs and adaptive repair loop for text-based KGQA. Overlap is low as they address different modalities and reasoning settings. _(basis: not stated)_

#### Autofocus Retrieval: An Effective Pipeline for Multi-Hop Question Answering With Semi-Structured Knowledge (2025) [10]

- **Problem:** Question answering over semi-structured knowledge bases (SKBs) requires integrating relational reasoning over structured elements and contextual interpretation of unstructured texts, yet existing methods often focus on isolated techniques and fail to leverage complementary strategies.
- **Method:** FocusedRetriever: a modular SKB-based framework integrating (1) VSS-based entity search, (2) LLM-based generation of Cypher queries from natural language, (3) node set joins to filter answer candidates using extracted triplets and constraints, (4) vector similarity search to retrieve and rank relevant unstructured content, and (5) LLM-based reranking (point-wise, pair-wise, list-wise) to rank top-k answers.
- **Main contribution:** FocusedRetriever outperforms state-of-the-art methods across all three STaRK benchmark datasets (AMAZON, MAG, PRIME) in hit@1, hit@5, hit@20, and MRR, with an average first-hit rate exceeding the second-best method by 25.7%, demonstrating that integrating complementary retrieval and ranking strategies improves multi-hop QA over SKBs.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** AMAZON, MAG, PRIME, AMAZON, MAG, PRIME
- **Baselines:** Vector Similarity Search (VSS), Dense Passage Retriever (DPR), QA-GNN, VSS+[pointwise]Reranker, DERIVE_CYPHER, Other baselines from STaRK benchmark
- **Metrics:** hit@1, hit@5, hit@20, MRR (Mean Reciprocal Rank)
- **Results:** FocusedRetriever achieves state-of-the-art performance across all three STaRK benchmarks, outperforming baselines in hit@1, hit@5, hit@20, and MRR; average first-hit rate exceeds second-best by 25.7% (exact per-dataset values: see Table 4 in paper).
- **Limitations:** List-wise reranking may exceed context window when including relational information, preventing evaluation in some cases; evaluation uses base LLMs without fine-tuning, leaving room for improvement.
- **Future work:** Explore fine-tuning components such as Cypher generation and reranking for further gains; extend framework to support more expressive logical reasoning.
- **Code availability:** https://github.com/kramerlab/FocusedRetriever
- **Relation to idea:** Both aim to improve multi-hop question answering: the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop to generate corrective examples from one‑hop failures followed by RL lower‑hop transfer, while FocusedRetriever focuses on inference‑time retrieval and re‑ranking over semi‑structured knowledge bases using LLMs for entity search, query generation, and ranking. Overlap in using LLMs to extract relational facts; differences in stage (training vs inference), mechanism (training data enrichment + failure‑driven RL vs retrieval + ranking), and output format (triple enrichment vs answer ranking). _(basis: not stated)_

#### Optimizing Question Semantic Space for Dynamic Retrieval-Augmented Multi-hop Question Answering (2025) [11]

- **Problem:** Conventional retrieve-and-read RAG methods suffer from semantic mismatching (retrieving semantically similar but unhelpful passages) and high computational cost when handling interdependent sub-questions in multi-hop question answering.
- **Method:** Q-DREAM: a three-module pipeline comprising (1) Question Decomposition Module (QDM) that splits multi-hop questions into fine-grained subquestions; (2) Subquestion Dependency Optimizer Module (SDOM) that models interdependent relations among subquestions; (3) Dynamic Passage Retrieval Module (DPRM) that aligns subquestions with relevant passages by optimizing semantic embeddings.
- **Main contribution:** Q-DREAM significantly outperforms existing RAG methods on HotpotQA, 2WikiMQA, and IIRC, achieving state-of-the-art exact match (EM) and F1 scores while improving retrieval efficiency; e.g., EM 48.6/F1 62.1 on 2WikiMQA (in-domain), EM 48.4/F1 60.9 on HotpotQA, EM 28.2/F1 31.9 on IIRC, with average EM 41.7/F1 51.6.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** HotpotQA, 2WikiMultiHopQA (2WikiMQA), IIRC, HotpotQA, 2WikiMultiHopQA, IIRC
- **Baselines:** InstructRAG, ChatQA2, Llama InstructRAG (Llama3-8B), SURE, IRCoT, ChatGPT (no retrieval)
- **Metrics:** Exact Match (EM), F1 score
- **Results:** Q-DREAM achieves EM 48.6/F1 62.1 on 2WikiMQA, EM 48.4/F1 60.9 on HotpotQA, EM 28.2/F1 31.9 on IIRC, average EM 41.7/F1 51.6; absolute improvements of 25.0 EM and 32.9 F1 over ChatGPT without retrieval on 2WikiMQA.
- **Limitations:** Performance remains to be studied with other complex reasoning tasks; long-tail knowledge retrieval for RAG remains to be studied.
- **Future work:** Extend to multilingual or multimodal settings; investigate effectiveness on more out-of-domain datasets.
- **Code availability:** not stated in abstract
- **Relation to idea:** Both target multi-hop QA improvement: Q-DREAM optimizes question semantic space via decomposition, dependency modeling, and dynamic passage retrieval at inference time, while the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop to generate corrective examples from one‑hop failures followed by RL lower‑hop transfer. Overlap in using semantic embeddings to bridge question‑passage gaps; differences in stage (inference vs training), mechanism (question‑level optimization vs training data enrichment + failure‑driven RL), and additional components (adaptive repair loop, RL transfer) in the idea. _(basis: not stated)_

#### DynaSearcher: Dynamic Knowledge Graph Augmented Search Agent via Multi-Reward Reinforcement Learning (2025) [12]

- **Problem:** Multi-step agentic retrieval systems based on LLMs are limited by factually inconsistent intermediate queries and inefficient search trajectories, causing reasoning deviations and redundant computations.
- **Method:** DynaSearcher: leverages knowledge graphs as external structured knowledge to guide the search process by explicitly modeling entity relationships, ensuring factual consistency in intermediate queries and mitigating biases from irrelevant information; employs a multi-reward RL framework for fine-grained control over training objectives such as retrieval accuracy, efficiency, and response quality.
- **Main contribution:** Achieves state-of-the-art answer accuracy on six multi-hop QA datasets, exhibits strong generalization and robustness across diverse retrieval environments and larger-scale models.
- **Key assumptions:** Knowledge graphs can effectively guide search and ensure factual consistency of intermediate queries.; Multi-reward RL can balance retrieval accuracy, efficiency, and response quality to produce high-quality intermediate queries and final answers.
- **Datasets / benchmarks:** HotpotQA, 2WikiMultiHopQA, Musique, Bamboogle, MoreHopQA, Frames, HotpotQA, 2WikiMultiHopQA, Musique, Bamboogle, MoreHopQA, Frames
- **Baselines:** State-of-the-art LLMs (DeepSeek-R1-0528, Qwen3-235B-A22B, GPT-4.1-0414, o4-mini-0416, Gemini-2.5-Pro-0325), advanced RAG methods, RL-based agentic search models
- **Metrics:** F1 score, Cover Exact Match (CEM), Exact Match (EM)
- **Results:** DynaSearcher achieves significant performance improvements across multiple benchmarks under all evaluation metrics; e.g., on in-domain datasets it achieves F1 ~66.1, CEM ~62.8, EM ~52.0 (approximate from table); on out-of-domain datasets F1 ~71.3, CEM ~63.1, EM ~57.4.
- **Limitations:** Not explicitly stated in the paper.
- **Future work:** Not explicitly stated in the paper.
- **Code availability:** not stated in abstract
- **Relation to idea:** Both use reinforcement learning and knowledge graphs to improve reasoning: DynaSearcher employs KG-guided search with multi-reward RL at inference time, while the idea enriches training triples with local context subgraphs and uses an adaptive repair loop for one-hop failures followed by RL lower-hop transfer. Overlap in using RL and KG; differences in focus (search agent training vs training data enrichment) and stage (inference vs training). _(basis: not stated)_

#### StepChain GraphRAG: Reasoning Over Knowledge Graphs for Multi-Hop Question Answering (2025) [13]

- **Problem:** Challenges persist in integrating iterative reasoning steps with external knowledge retrieval; existing GraphRAG methods rely on ad-hoc strategies that fail to exploit full potential of multi-hop reasoning.
- **Method:** StepChain GraphRAG builds a global index over the corpus; at inference, retrieves passages are parsed on-the-fly into a knowledge graph; the complex query is split into sub-questions; for each sub-question, a BFS-based traversal dynamically expands along relevant edges, assembling explicit evidence chains without overwhelming the language model with superfluous context; incremental graph augmentation merges results.
- **Main contribution:** StepChain GraphRAG achieves state-of-the-art Exact Match and F1 scores on MuSiQue, 2WikiMultiHopQA, and HotpotQA, lifting average EM by 2.57% and F1 by 2.13% over the SOTA method, with the largest gain on HotpotQA (+4.70% EM, +3.44% F1), and fosters enhanced explainability by preserving the chain-of-thought across intermediate retrieval steps.
- **Key assumptions:** BFS-based traversal can efficiently find relevant evidence along edges without excessive expansion.; Incremental graph augmentation preserves relevant information while avoiding overwhelm.; Question decomposition into sub-questions is effective for multi-hop reasoning.
- **Datasets / benchmarks:** MuSiQue, 2WikiMultiHopQA, HotpotQA, MuSiQue, 2WikiMultiHopQA, HotpotQA
- **Baselines:** SOTA method (unspecified in abstract)
- **Metrics:** Exact Match (EM), F1 score
- **Results:** StepChain GraphRAG lifts average EM by 2.57% and F1 by 2.13% over SOTA; largest gain on HotpotQA: +4.70% EM, +3.44% F1.
- **Limitations:** Reliance on explicit graph construction imposes extra computational overhead and memory demands; LLMs can hallucinate, allowing spurious facts to propagate; errors or uncertainty in early sub-questions can make retrieval for later sub-questions brittle.
- **Future work:** Mitigate computational overhead and address potential hallucinations from large language models to refine efficiency and reliability in multi-hop QA.
- **Code availability:** not stated in abstract
- **Relation to idea:** Both involve graph-based reasoning: StepChain builds a knowledge graph from retrieved passages and uses BFS traversal, while the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop for one-hop failures. Overlap in using graph structures to support reasoning; differences in context source (retrieved passages vs same-passage triples) and mechanism (BFS traversal vs failure-driven example generation). _(basis: not stated)_

#### Reinforcement Learning Enhanced Multi-hop Reasoning for Temporal Knowledge Question Answering (2026) [14]

- **Problem:** Temporal knowledge graph question answering (TKGQA) suffers from suboptimal decisions and error propagation because large language models retrieve subgraphs with numerous temporally similar and semantically complex relations at each hop.
- **Method:** Multi-hop Reasoning Enhanced (MRE) framework: (1) prompt engineering to guide LLM in generating diverse reasoning trajectories; (2) selecting valid trajectories for supervised fine-tuning (cold-start); (3) Tree-Group Relative Policy Optimization (T-GRPO)—a recursive, tree-structured learning-by-exploration approach where at each hop exploration establishes strong causal dependencies on the previous hop and evaluation is informed by multi-path exploration feedback from subsequent hops.
- **Main contribution:** A unified framework (MRE) integrating trajectory sampling, supervised fine-tuning, and a novel T-GRPO algorithm for TKGQA, improving LLM with structured subgraph retrieval and trajectory-aware temporal reasoning.
- **Key assumptions:** Prompt engineering can generate diverse and useful reasoning trajectories.; Selecting valid trajectories for supervised fine-tuning provides a good initialization for RL.; Tree-structured credit assignment in T-GRPO improves exploration and reduces reliance on sparse final-step rewards.
- **Datasets / benchmarks:** CRONQUESTIONS, TIMEQUESTIONS, CRONQUESTIONS, TIMEQUESTIONS
- **Baselines:** CRONQUESTIONS: EaE, EmbedKGQA, CronKGQA, EntityQR, TMA, TSQA, CTRN, TempoQR, BERT, RoBERTa, ChatGPT; TIMEQUESTIONS: CronKGQA, TempoQR, TwiRGCN
- **Metrics:** Hits@1, Hits@10
- **Results:** MRE sets new SOTA on CRONQUESTIONS with 98.2% Hits@1 and 99.6% Hits@10 (outperforming TempoQR by +6.4% and +1.8%); near-perfect on simple questions (99.9% Hits@1); strong performance on entity and time question types; reduces 3-hop error rate by over 75% vs TempoQR. On TIMEQUESTIONS achieves 59.4% Hits@1, matching TwiRGCN and outperforming CronKGQA and TempoQR; shows improved performance on implicit (+4.5%) and ordinal (+6.0%) question types.
- **Limitations:** GRPO (Flat) relies on sparse reward supervision assigned only at the final step, limiting exploration; T-GRPO addresses this by leveraging tree-structured reward propagation.; Dependence on quality of prompt-generated trajectories may affect performance.
- **Future work:** Not explicitly stated in the paper.
- **Code availability:** not stated in abstract
- **Relation to idea:** Both aim to improve multi-hop reasoning; the paper uses RL with trajectory-based optimization, while the idea proposes context subgraph enrichment and adaptive repair loop followed by RL lower-hop transfer. Overlap in using RL for reasoning, but differs in context enrichment and repair loop. _(basis: not stated)_

#### CacheRAG: A Semantic Caching System for Retrieval-Augmented Generation in Knowledge Graph Question Answering (2026) [15]

- **Problem:** Existing LLM-driven KGQA systems act as stateless planners, generating retrieval plans in isolation without exploiting historical query patterns, leading to schema hallucinations and limited retrieval coverage.
- **Method:** CacheRAG: a systematic cache-augmented architecture for LLM-based KGQA that transforms stateless planners into continual learners via (1) Schema-agnostic user interface (two-stage semantic parsing via Intermediate Semantic Representation), (2) Diversity-optimized cache retrieval (two-layer hierarchical index + Maximal Marginal Relevance), (3) Bounded heuristic expansion (deterministic depth and breadth subgraph operators with strict complexity guarantees).
- **Main contribution:** CacheRAG significantly outperforms state-of-the-art baselines (e.g., +13.2% accuracy and +17.5% truthfulness on the CRAG dataset) by transforming stateless LLM planners into continual learners that exploit historical query patterns.
- **Key assumptions:** Intermediate Semantic Representation can effectively bridge natural language queries and local schema context.; Diversity-optimized cache retrieval improves structural variety and mitigates reasoning homogeneity.; Bounded heuristic expansion enhances retrieval recall without risking unbounded API execution.
- **Datasets / benchmarks:** CRAG, QALD-10-en, WebQSP, CWQ, CRAG, QALD-10-en, WebQSP, CWQ
- **Baselines:** LLM base models (GPT-4o, Llama-3.1-70B-Instruct, Deepseek-chat-V3-0324), LLM tool-calling models (StructGPT variants), KDD Cup-winning solutions (db3, apex), SPARQL-based state-of-the-art solutions (ToG, ToG-2, sparql-qa, Decaf, CBR)
- **Metrics:** For CRAG: accuracy, miss rate, hallucination rate, truthfulness score (T = A - H). For SPARQL-based datasets: Hit@1 score.
- **Results:** On CRAG: accuracy 0.824, hallucination rate 0.112, miss rate 0.064, truthfulness 0.711. On QALD-10-en: Hit@1 0.587 (+4.6% over prior SOTA). On WebQSP: Hit@1 0.840 (+1.9% over prior SOTA). On CWQ: Hit@1 0.736 (+3.2% over prior SOTA).
- **Limitations:** Not explicitly stated in the paper.
- **Future work:** Not explicitly stated in the paper.
- **Code availability:** not stated in abstract
- **Relation to idea:** CacheRAG focuses on caching retrieval plans to improve efficiency and reduce hallucinations via semantic planning and reuse, while the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop for one-hop failures followed by RL lower-hop transfer. Both aim to improve KGQA correctness, but CacheRAG operates at inference time via plan reuse, whereas the idea operates at training time via data enrichment and failure-driven example generation. _(basis: not stated)_

#### Ontology-Guided Evidence Path Inference for Multi-hop Knowledge Graph Question Answering (2026) [1]

- **Problem:** Existing multi-hop KGQA methods rely on topic-centered expansion, causing rapid search space growth with noisy mixed-type paths and retrieved paths that may fail to satisfy semantic constraints of complex questions.
- **Method:** OPI (Ontology-Guided Evidence Path Inference) framework: (1) construct a relation-centric ontology graph capturing head-tail type constraints of relations for answer-side constraints; (2) bidirectional retrieval: map predicted answer type to compatible final-hop relations, combine topic-side prefix expansion with answer-side final-hop matching to suppress noisy mixed-type expansion; (3) iterative refinement: reassess retrieved paths and candidate answers under question context, filtering type-compatible but question-irrelevant evidence.
- **Main contribution:** OPI provides a compact, reusable relation-centric ontology graph for retrieval, substantially reduces search space, improves Hit@1/F1 over prior results on WebQSP, CWQ, and MetaQA, and achieves near-saturated Hit@1 on MetaQA with retrieval alone.
- **Key assumptions:** The ontology graph can be constructed accurately from the KG to reflect type constraints.; Bidirectional retrieval effectively reduces noisy mixed-type expansion while preserving relevant paths.; Iterative refinement improves answer precision by removing irrelevant evidence under question context.
- **Datasets / benchmarks:** WebQSP, CWQ, MetaQA (including 1-hop, 2-hop, 3-hop subsets), WebQSP, CWQ, MetaQA
- **Baselines:** Embedding-based: KV-Mem, NSM, TransferNet, KGT5; Retrieval-based: (not fully listed); Standalone LLMs: Llama-2, Llama-3.1, ChatGPT, GPT-4o, DeepSeek-v3; KG-enhanced LLM methods: ToG, RoG, SymAgent, GNN-RAG, R2, ORT, GCR
- **Metrics:** Hit@1, F1
- **Results:** OPI(Llama-2-7B + GPT-4o) achieves WebQSP Hit@1 91.3, F1 76.8; CWQ Hit@1 72.3, F1 62.7 (improvements of +4.6 Hit@1, +5.0 F1 on WebQSP; +8.9 Hit@1, +3.3 F1 on CWQ over strongest prior results). Near-saturated Hit@1 on MetaQA with retrieval module alone.
- **Limitations:** LLMs may hallucinate unsupported facts when lacking explicit graph-grounded evidence (mitigated by OPI's ontology-guided retrieval).; Performance depends on quality and completeness of the ontology graph; may degrade on KGs with weak or missing type information.
- **Future work:** Extend OPI to knowledge graphs with weaker or less reliable type information by constructing and updating relation signatures when entity types are missing, noisy, or partially available.
- **Code availability:** https://github.com/shanyongxue/OPI_KGQA
- **Relation to idea:** Both address multi-hop KGQA challenges; OPI uses ontology-guided retrieval and iterative refinement, while the idea proposes local context subgraph enrichment, adaptive repair loop, and RL lower-hop transfer. Overlap in aiming to improve reasoning quality, but differs in mechanism (context subgraph vs ontology graph, repair loop vs iterative refinement). _(basis: not stated)_

#### IterCOMP: Reasoning-aware Adaptive Prompt Compression for Multi-hop Question Answering (2026) [16]

- **Problem:** Multi-hop question answering requires complex reasoning across multiple evidence segments, which often overwhelms retrieval-augmented generation systems with lengthy and noisy contexts, thereby undermining both efficiency and accuracy.
- **Method:** IterCOMP: a unified, training-free prompt compression framework that incorporates multi-hop reasoning within an iterative compression loop. It decomposes documents into evidence segments, evaluates question answerability, and generates targeted follow-up questions to iteratively integrate essential evidence, producing a compact, reasoning-oriented prompt.
- **Main contribution:** IterCOMP achieves substantial improvements in Exact Match and F1 scores while reducing token budget, outperforming existing prompt compression baselines and demonstrating robustness as reasoning complexity increases.
- **Key assumptions:** The underlying LLM can accurately judge whether provided evidence is sufficient to answer a question and identify missing information.; Iterative compression loop can retain essential evidence while discarding irrelevant or noisy content.
- **Datasets / benchmarks:** MuSiQue, 2WikiMultiHopQA, HotpotQA, MuSiQue, 2WikiMultiHopQA, HotpotQA
- **Baselines:** Raw Documents (no compression), Oracle (gold supporting documents only), Selective-Context, RECOMP (extractive), MLingua, LLMLingua-2, LongLLMLingua, R2C
- **Metrics:** Exact Match (EM), F1 score, Compression ratio (Ratio)
- **Results:** On MuSiQue: EM increased from 9.69 to 16.67, F1 from 19.92 to 27.36, compression ratio 0.14. On 2WikiMultiHopQA: EM from 24.06 to 27.39, F1 from 36.75 to 39.69, ratio 0.37. On HotpotQA: EM from 31.60 to 37.65, F1 from 43.63 to 51.78, ratio 0.19.
- **Limitations:** Effectiveness depends on the reasoning capability of the underlying LLM for answerability judgment and missing information detection, introducing risk of error propagation.; Existing abstractive compression methods (e.g., RECOMP, CompAct) were excluded from main comparison due to inconsistent length-control mechanisms.
- **Future work:** Validating generalization to diverse reasoning types and non-Wikipedia domains.
- **Code availability:** not stated in abstract
- **Relation to idea:** IterCOMP focuses on prompt compression for retrieval-augmented generation by iteratively integrating essential evidence via follow-up questions, while the idea enriches training triples with local context subgraphs from the same source passage and uses an adaptive repair loop for one-hop failures. Both aim to improve reasoning efficiency and accuracy, but IterCOMP operates at inference time via prompt compression, whereas the idea operates at training time via data enrichment and failure-driven example generation. _(basis: not stated)_

#### Multi-hop clustering for reasoning chain extraction in multi-hop question answering (2026) [17]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** not stated in abstract
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** not stated in abstract _(basis: not stated)_

#### Incorporating multi-perspective information into reinforcement learning to address multi-hop knowledge graph question answering (2024) [18]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** not stated in abstract
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** No abstract available to assess overlap. _(basis: not stated)_

#### Incorporating anticipation embedding into reinforcement learning framework for multi-hop knowledge graph question answering (2022) [19]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** not stated in abstract
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** No abstract available to assess overlap. _(basis: not stated)_

#### Reinforcement learning with dynamic completion for answering multi-hop questions over incomplete knowledge graph (2023) [20]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** not stated in abstract
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** No abstract available to assess overlap. _(basis: not stated)_

#### Path-based multi-hop reasoning over knowledge graph for answering questions via adversarial reinforcement learning (2023) [21]

- **Problem:** not stated in abstract
- **Method:** not stated in abstract
- **Main contribution:** not stated in abstract
- **Key assumptions:** not stated in abstract
- **Datasets / benchmarks:** not stated in abstract, not stated in abstract
- **Baselines:** not stated in abstract
- **Metrics:** not stated in abstract
- **Results:** not stated in abstract
- **Limitations:** not stated in abstract
- **Future work:** not stated in abstract
- **Code availability:** not stated in abstract
- **Relation to idea:** No abstract available to assess overlap. _(basis: not stated)_

#### Multi-hop Question Answering (2024) [22]

- **Problem:** Defining and surveying the multi-hop question answering (MHQA) task, which involves extracting and combining multiple pieces of information and performing multi-step reasoning, is challenging due to the variety of tasks, datasets, and models that hinder generalization.
- **Method:** This paper is a survey; it does not propose a new method but organizes and summarizes existing MHQA frameworks, datasets, evaluation techniques, and generation methods.
- **Main contribution:** Provides a general and formal definition of MHQA, organizes and summarizes existing MHQA frameworks, outlines best practices for creating MHQA datasets, and discusses evaluation metrics and future research directions.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** HotpotQA, 2WikiMultiHopQA, MetaQA, HybridQA, Wikitables, NarrativeQA, and others surveyed in the paper, Same as datasets surveyed
- **Baselines:** Surveys a wide range of MHQA methods including retrieval-based, reasoning-based, graph-based, decomposition-based, and hybrid approaches
- **Metrics:** Exact Match (EM), F1 score, Partial Match (PM), BLEU, ROUGE, CIDer, and task-specific metrics discussed in Section 6
- **Results:** ["N/A (survey paper)"]
- **Limitations:** May not cover the very latest works due to the time of writing; the survey’s completeness depends on the literature covered up to its publication date.
- **Future work:** Explore flexible any-hop models, explainable multi-hop QA, better datasets, improved evaluation metrics, incorporation of commonsense knowledge, and handling of arithmetic questions (as outlined in Section 8).
- **Code availability:** not applicable (survey)
- **Relation to idea:** The survey provides a broad overview of MHQA, including definitions, datasets, methods, and metrics, which overlaps with the idea’s focus on multi-hop QA over knowledge graphs. However, the idea proposes a specific training‑data enrichment strategy with local context subgraphs, an adaptive repair loop, and RL lower‑hop transfer, which is not covered as a distinct method in the survey. Overlap in the general problem domain; differences in specificity (survey vs concrete proposal). _(basis: not stated)_

#### Hierarchical Graph Network for Multi-hop Question Answering (2020) [23]

- **Problem:** Existing multi-hop QA models struggle to effectively aggregate evidence from scattered texts across multiple documents; many approaches decompose the task into single-hop sub-problems, losing the ability to jointly model subtasks such as paragraph selection, supporting facts extraction, and answer prediction.
- **Method:** Hierarchical Graph Network (HGN) constructs a hierarchical graph with nodes at different granularities (question, paragraph, sentence, entity), encodes them with pretrained contextual encoders (e.g., RoBERTa), performs graph reasoning via GNN, and jointly predicts paragraph selection, supporting facts, entity, and answer span via multi-task prediction.
- **Main contribution:** HGN achieves state-of-the-art performance on HotpotQA Distractor and Fullwiki settings, outperforming prior work by significant margins (e.g., joint EM/F1 47.11/74.21 in Distractor, 37.17/60.74 in Fullwiki) by weaving heterogeneous nodes into a unified graph and enabling joint multi-task reasoning.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** HotpotQA (Distractor and Fullwiki settings), HotpotQA
- **Baselines:** TPReasoner, Baseline Model, QFE, MUPPET, Graph Recur. Retriever, DFGN, EPS, SAE, Longformer⋆, ETC-large⋆, RoBERTa-large, ALBERT-xxlarge-v2
- **Metrics:** Exact Match (EM) and F1 score for answer prediction and supporting facts; joint EM/F1
- **Results:** HGN (RoBERTa-large) achieves joint EM/F1 47.11/74.21 on HotpotQA Distractor (Δ+2.44/1.48 over prior SOTA) and 37.17/60.74 on Fullwiki.
- **Limitations:** Not explicitly stated; handling very long documents may require sliding-window chunking or larger transformer backbones.
- **Future work:** Investigate interaction and joint training between HGN and paragraph retriever for performance improvement.
- **Code availability:** https://github.com/yuwfan/HGN
- **Relation to idea:** Both aim to improve multi-hop QA: HGN uses hierarchical graph reasoning at inference time to jointly model subtasks, while the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop to generate corrective examples from one‑hop failures followed by RL lower‑hop transfer. Overlap in using graph structures and reasoning; differences in stage (inference vs training), mechanism (hierarchical GNN with multi‑task prediction vs training data enrichment + failure‑driven RL), and additional components (adaptive repair loop, RL transfer) in the idea. _(basis: not stated)_

#### Scalable Multi-Hop Relational Reasoning for Knowledge-Aware Question Answering (2020) [24]

- **Problem:** Existing knowledge-aware QA models either struggle to model multi-hop relations efficiently over external knowledge graphs or lack transparency into the model’s prediction rationale.
- **Method:** MHGRN (Multi-hop Graph Relation Network) equips pretrained language models with a multi-hop relational reasoning module that performs multi-hop, multi-relational reasoning over subgraphs extracted from external KGs, unifying path-based reasoning and GNNs via structured relational attention, and supports path decoding for interpretability.
- **Main contribution:** MHGRN brings significant improvements over knowledge-agnostic PTLMs and outperforms other graph encoding methods by a large margin on CommonsenseQA and OpenbookQA; e.g., achieves 75.4 accuracy on official CommonsenseQA test, 68.10 dev / 66.85 test on OpenbookQA with RoBERTa-large, and scales well with number of hops while providing interpretable reasoning paths.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** CommonsenseQA, OpenbookQA, CommonsenseQA, OpenbookQA
- **Baselines:** Knowledge-agnostic PTLMs (RoBERTa, XLNet, ALBERT), KG-augmented models (RoBERTa+KEDGN, RoBERTa+KE, RoBERTa+HyKAS 2.0, RoBERTa+FreeLB, XLNet+DREAM, XLNet+GR, ALBERT), leaderboard UniﬁedQA (T5-11B)
- **Metrics:** Accuracy (since multiple-choice)
- **Results:** MHGRN (K=2) achieves 75.4 accuracy on official CommonsenseQA test, 76.5 on in-house test; MHGRN (K=3) achieves 68.10 dev / 66.85 test on OpenbookQA with RoBERTa-large; with AristoRoBERTaV7 + MHGRN (K=3): 78.6 dev / 80.6 test on OpenbookQA.
- **Limitations:** Not explicitly stated; potential overhead of subgraph extraction per question.
- **Future work:** Not explicitly stated; possible directions include scaling to larger KHs, applying to other KGs, or integrating with newer PTLMs.
- **Code availability:** https://github.com/INK-USC/MHGRN
- **Relation to idea:** Both target knowledge-aware QA: MHGRN performs multi-hop relational reasoning over KG subgraphs at inference time via a specialized GNN with path decoding, while the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop to generate corrective examples from one‑hop failures followed by RL lower‑hop transfer. Overlap in using KG and reasoning; differences in stage (inference vs training), mechanism (relational attention + path decoding vs training data enrichment + failure‑driven RL), and additional components (adaptive repair loop, RL transfer) in the idea. _(basis: not stated)_

#### KGEIR: Knowledge Graph-Enhanced Iterative Reasoning for Multi-Hop Question Answering (2025) [25]

- **Problem:** Multi-hop question answering requires integrating information across multiple sources to derive answers that cannot be found in any individual source; existing approaches struggle with capturing bridging information and reasoning over multiple documents.
- **Method:** KGEIR: dynamically constructs and refines knowledge graphs during question answering. It identifies key entities from questions, builds an initial graph from retrieved paragraphs, reasons over this structure, identifies information gaps, and iteratively retrieves additional context to refine the graph until sufficient information is gathered.
- **Main contribution:** KGEIR demonstrates competitive or superior performance to state-of-the-art methods on HotpotQA, 2WikiMultiHopQA, and MuSiQue benchmarks, showing that dynamic knowledge graph construction and iterative reasoning improve multi-hop QA, with ablation studies confirming structured knowledge representations outperform traditional prompting approaches.
- **Key assumptions:** Not explicitly stated in the paper.
- **Datasets / benchmarks:** HotpotQA, 2WikiMultiHopQA, MuSiQue, HotpotQA, 2WikiMultiHopQA, MuSiQue
- **Baselines:** State-of-the-art methods (unspecified), Chain-of-Thought, Tree-of-Thought, HopRAG
- **Metrics:** Exact Match (EM), F1 score
- **Results:** HotpotQA: EM 63.15%, F1 76.77%; 2WikiMultiHopQA: EM 59.13%, F1 69.55%; MuSiQue: EM 44.50%, F1 53.12%.
- **Limitations:** Not explicitly stated in the paper.
- **Future work:** Not explicitly stated in the paper.
- **Code availability:** https://github.com/TiandaSun/KGEIR
- **Relation to idea:** KGEIR focuses on dynamic knowledge graph construction and iterative refinement at inference time to retrieve relevant information, while the idea enriches training triples with local context subgraphs from the same passage and uses an adaptive repair loop for one-hop failures followed by RL lower-hop transfer. Both address multi-hop QA and utilize knowledge graphs, but differ in stage (inference vs training) and mechanism (iterative KG refinement vs training data enrichment and failure-driven example generation). _(basis: not stated)_

</details>

## 5. Research Landscape

```text
Multi-hop Knowledge Graph Question Answering
├── Embedding-based Methods
├── Retrieval-based Methods
├── Reinforcement Learning Methods  [14] [18] [19] [20] [21]
│   ├── Trajectory-based RL Optimization  [14]
│   └── Ontology-guided Retrieval with Iterative Refinement  [1]
├── Context-enriched Triple Training
├── Adaptive Repair Loop for One-hop Failures
└── Lower-hop Transfer Learning
```

**Where the idea fits:** **[Inference]** Context-enriched Triple Training with Adaptive Repair Loop and Lower-hop Transfer

**Dominant approaches**

- Reinforcement Learning Methods
- Retrieval-based Methods

**Common assumptions**

- The knowledge graph contains sufficient relational information to support multi-hop reasoning.
- Question answering performance can be improved by better utilization of KG structure and semantics.
- Reasoning trajectories or evidence paths can be refined to reduce noise and improve accuracy.

**Common datasets**

- WebQSP
- CWQ
- MetaQA
- CRONQUESTIONS
- TIMEQUESTIONS

**Common benchmarks**

- WebQSP
- CWQ
- MetaQA
- CRONQUESTIONS
- TIMEQUESTIONS

**Common metrics**

- Hit@1
- F1 score
- Hits@10

**Underexplored combinations**

- **[Hypothesis]** Combining context subgraph enrichment with ontology-guided retrieval mechanisms
- **[Hypothesis]** Integrating adaptive repair loops with trajectory-based RL optimization approaches
- **[Hypothesis]** Using lower-hop transfer learning with context-enriched triple training for improved generalization

**Limitations repeated across papers**

- Dependence on quality of auxiliary components (e.g., prompt-generated trajectories, ontology graph) affects overall performance. [14], [1]
- LLMs may hallucinate or generate unsupported facts when lacking explicit graph-grounded evidence. [14], [1]

**Contradictions between papers**

_None recorded._

## 6. Closest Existing Work

**[Inference]** OPI (arxiv:2606.28076) addresses similar challenges: it reduces noisy mixed-type paths via ontology-guided retrieval and applies iterative refinement to filter spurious evidence. Both aim to improve reasoning quality, but OPI uses an ontology graph and answer-side constraints, whereas the idea proposes local context subgraph enrichment from source passages and an adaptive repair loop for error correction.

- Ontology-Guided Evidence Path Inference for Multi-hop Knowledge Graph Question Answering (2026) [1]: Both address multi-hop KGQA challenges; OPI uses ontology-guided retrieval and iterative refinement, while the idea proposes local context subgraph enrichment, adaptive repair loop, and RL lower-hop transfer. Overlap in aiming to improve reasoning quality, but differs in mechanism (context subgraph vs ontology graph, repair loop vs iterative refinement).

## 7. Potential Overlap

**Overlap:** **[Inference]** Overlaps with OPI in targeting noisy mixed-type paths and improving semantic alignment; both use iterative processes (refinement vs repair loop) and aim to utilize structural constraints. However, OPI relies on an ontology graph and bidirectional retrieval, while the idea enriches triples with passage-derived subgraphs and uses an adaptive repair loop.

**Potential distinction:** **[Inference]** The idea differs by focusing on training-time enrichment of triples with local context from the same passage, employing an adaptive repair loop that detects and corrects one-hop failures via corrective examples, and applying reinforcement learning on lower-hop QA instances for transfer to deeper multi-hop queries—components not combined in existing work.

**Novelty questions**

- **Is the local context subgraph enrichment and adaptive repair loop truly novel given existing iterative refinement and ontology-guided retrieval methods?** (moderate severity): Existing work like OPI already uses iterative refinement to filter spurious evidence and addresses noisy mixed-type paths, suggesting parts of the idea may not be novel. _([1]; [Evidence] claim C001; [Evidence] claim C002)_

## 8. Potential Research Gap

### G001: No existing work enriches training triples with local context subgraphs from the same passage for multi-hop knowledge graph question answering, which limits the model's ability to leverage passage-level contextual supervision during training.

- **Status:** **[Hypothesis]** a potential gap, derived from the evidence below
- **Evidence:**
  - [25], p. 1 (indirect support, verified) "KGEIR identifies key entities from questions, builds an initial graph from retrieved paragraphs, reasons over this structure, identifies information gaps, and iteratively re-trieves additional context to refine the graph until sufficient information is gathered."
  - [2], p. 3 (indirect support, verified) "In our approach, the student network aims to find the correct answer to the query, while the teacher network tries to learn intermediate supervision signals for improving the reasoning capacity of the student network."
  - [4], p. 1 (indirect support, verified) "We propose a data synthesis framework for multi-hop question answering that allows for improving smaller language models with less than 10 human-annotated question answer pairs."
  - [5], p. 3 (indirect support, verified) "PokeMQA is a lightweight model editor that can be seamlessly integrated into any backbone LLMs, without changing parameters in the deployed language models."
  - [7], p. 11 (indirect support, unverified) "Our method consists of four main components: question parsing, named entity recognition, conversion of complex questions into SPARQL queries, and SPARQL query execution and response composition."
  - [8], p. 1 (indirect support, unverified) "ChainRAG progressively handles each sub-question by completing missing key entities and retrieving relevant sentences from a sentence graph for answer generation."
- **Related papers:** [25], [2], [4], [5], [7], [8]
- **Why existing work does not address it:** **[Inference]** Prior work focuses on inference-time knowledge graph construction, teacher-student intermediate supervision, LLM-based data synthesis, knowledge editing, question decomposition, or retrieval augmentation with sentence graphs, but none modify the training triples themselves to include passage-level context subgraphs.
- **Research question:** Does enriching each training triple with additional triples from the same source passage (forming a local context subgraph) improve multi-hop KGQA performance compared to training on isolated triples alone?
- **Potential experiment:** Fine-tune a language model on a multi-hop KGQA dataset (e.g., HotpotQA) using two regimes: (A) training on isolated head-relation-tail triples extracted from the corpus; (B) training on triples enriched with additional triples from the same source passage (local context subgraph). Evaluate both models on held-out multi-hop QA Exact Match and F1 scores.
- **Confidence:** medium
- **Verification required:** not stated

## 9. Critique

| | |
|---|---|
| Strongest argument FOR | The idea addresses a key limitation: current language-model training uses isolated head-relation-tail triples, depriving models of surrounding context that supports multi-step inference. Enriching triples with local context subgraphs from the same passage provides richer supervision, which is supported by evidence that noisy mixed-type paths hinder reasoning (C002) and that LLMs show strength in multi-hop reasoning due to extensive pre-trained knowledge (C003), suggesting context helps. |
| Strongest argument AGAINST | The idea may overlap significantly with existing approaches such as OPI, which already uses ontology-guided retrieval and iterative refinement to filter spurious evidence (C001) and address noisy mixed-type paths (C002). The adaptive repair loop may be similar to iterative refinement strategies, raising novelty concerns (U006). Additionally, performance gains could be confounded by the inherent reasoning ability of LLMs (C003). |
| Most important unresolved question | Does enriching training triples with local context subgraphs from the same source passage provide significant improvements over existing methods that already incorporate context via retrieval or ontology guidance, considering the risk of context noise and potential overlap with iterative refinement? |
| Most dangerous experimental confounder | The inherent reasoning ability of large language models, which can achieve reasonable results without explicit graph retrieval, may drive observed improvements, making it difficult to isolate the effect of local context subgraph enrichment (C003). |
| Closest existing work | [1] |
| Potential contribution | **[Hypothesis]** A training method that combines local context subgraph enrichment, adaptive repair loop for one-hop failure correction, and reinforcement-learning-based lower-hop transfer to improve multi-hop question answering performance and generalization. |

**Technical validity**

- **Does adding local context subgraphs risk introducing irrelevant noise that could hurt performance?** (moderate severity): Noisy mixed-type paths are a known challenge that degrades reasoning, supporting the technical rationale for context enrichment. _([1]; [Evidence] claim C002)_

**Experimental validity**

- **Are the observed improvements due to the method or the inherent reasoning ability of LLMs?** (high severity): LLMs show strength in multi-hop reasoning due to pre-trained knowledge, which could confound experimental results if not properly controlled. _([14]; [Evidence] claim C003)_

**Practicality**

- **Is it practical to implement the adaptive repair loop and extract local context subgraphs at scale?** (low severity): Iterative refinement and ontology-guided retrieval are implementable, as demonstrated by OPI, suggesting the adaptive repair loop and context enrichment are feasible. _([1]; [Evidence] claim C001)_

## 10. Proposed Modifications

Difficulty ratings are qualitative (low / moderate / high) with the stated basis; no numeric scoring is used.

### M001: Training Data Enrichment Only (recommended)

**[Hypothesis]** Simplify the proposed method by using only the training regime that enriches each target triple with local context subgraphs from the same passage, and omit the adaptive repair loop and reinforcement learning lower-hop transfer stages.

| | |
|---|---|
| Why it differs | The original idea includes three stages: (1) training with/without context subgraphs, (2) adaptive repair loop to detect and correct one-hop failures, and (3) RL lower-hop transfer. This modification removes stages (2) and (3) to isolate the effect of context subgraph enrichment alone. |
| Technical mechanism | During fine-tuning, for each training instance (question, answer, knowledge graph), extract the source passage(s) that yielded the answer triple(s). From these passages, extract all head-relation-tail triples (using an off-the-shelf IE system) to form a local context subgraph. Concatenate the target triple(s) with the context subgraph triples as training input. No further iterative correction or RL optimization is applied. |
| Expected benefit | Reduces complexity and training time; allows clear ablation of the contribution of context subgraph enrichment; easier to implement and debug. |
| Potential novelty | While context enrichment at training is unexplored, this modification tests whether the core hypothesis (context subgraphs help) holds without additional complexity. |
| Implementation difficulty | low, because Requires only a passage-to-triple extraction step and concatenation of triples; no new model architectures or reinforcement learning components. |
| Experimental difficulty | low, because Experiments involve two training regimes and standard evaluation; no need for iterative failure detection or RL tuning. |
| Main risk | The adaptive repair loop and RL transfer might be necessary for significant gains; removing them could underestimate the full potential of the idea. |
| Required baselines | Baseline A: training on isolated triples, Baseline B: training on triples with random context subgraphs (noise control) |
| Related work | [25], [2], [4], [5], [7], [8], [16], [12], [15] |
| Addresses gaps | G001 |

### M002: Heuristic Noise Filtering + RL Lower-Hop Transfer (recommended)

**[Hypothesis]** Replace the adaptive repair loop that detects one-hop failures and generates corrective examples with a heuristic filtering step: triples extracted from the source passage are retained only if their extraction confidence exceeds a threshold; the filtered context subgraph is then used for training enrichment, followed by the RL lower-hop transfer stage.

| | |
|---|---|
| Why it differs | The original adaptive repair loop iteratively detects one-hop failures, generates corrective examples, and refines the model. This modification substitutes that iterative, model-based correction with a static confidence‑based filter, reducing complexity while still attempting to prune irrelevant context before training enrichment and RL transfer. |
| Technical mechanism | 1. For each training triple, retrieve the source passage and extract candidate triples with confidence scores from an IE pipeline. 2. Keep only triples with confidence ≥ τ (e.g., τ=0.8) to form the local context subgraph. 3. Form enriched training instances by concatenating target triple(s) with filtered context subgraph triples. 4. Train a model on these enriched instances. 5. Apply reinforcement learning lower-hop transfer: sample lower‑hop QA instances from the training set, compute rewards based on QA accuracy, and optimize the policy using a policy gradient method (e.g., REINFORCE). |
| Expected benefit | Cuts down the iterative loop expense, reduces risk of error propagation from the repair loop, and leverages established RL lower‑hop transfer for potential gains. |
| Potential novelty | Combines a simple confidence‑based context filter with RL lower‑hop transfer, a combination not explicitly explored in prior work. |
| Implementation difficulty | moderate, because Requires IE confidence scoring, thresholding, and implementation of an RL lower‑hop transfer stage (policy gradient), which is more involved than a plain enrichment baseline but less complex than a failure‑driven generative repair loop. |
| Experimental difficulty | moderate, because Experiments must compare: (i) enrichment with heuristic filter + RL transfer, (ii) enrichment without filter + RL transfer, (iii) enrichment only, (iv) baseline. This adds ablation steps but remains feasible with standard QA evaluation. |
| Main risk | Heuristic filtering may discard useful low‑confidence triples or retain noisy high‑confidence false positives; the RL stage may still be unstable or require careful hyperparameter tuning. |
| Required baselines | Baseline: isolated triples, Baseline: enriched triples with heuristic filter (no RL), Baseline: enriched triples + RL transfer (no filter), Baseline: enriched triples + RL transfer + heuristic filter (full) |
| Related work | [16], [12], [15], [18], [19], [25], [2], [4], [5], [7], [8] |
| Addresses gaps | G001 |

## 11. Recommended Experimental Design

_Not recorded: this phase did not produce the required records._

## 12. Experimental Results

Experiment not performed. The designs in Section 11 are untested.

## 13. Remaining Uncertainty

- Literature coverage: searched 8 queries over arxiv, crossref, openalex, semantic_scholar. Work outside these queries and sources, very recent preprints, and non-English work may be missing; the absence of matching work here does not establish novelty.
- Some source requests failed and their results are missing: semantic_scholar (api.semanticscholar.org failed after 5 attempts (HTTP 429)).
- Metadata warning for Autofocus Retrieval: An Effective Pipeline for Multi-Hop Question Answering With Semi-Structured Knowledge (2025) [10]: abstract (from semantic_scholar) never mentions 'Autofocus Retrieval'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Learning to Refine: An Agentic RL Approach for Iterative SPARQL Query Construction (2025) [26]: abstract (from arxiv) never mentions 'Learning to Refine'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for QA-GNN: Reasoning with Language Models and Knowledge Graphs for Question Answering (2021) [27]: abstract (from openalex) never mentions 'QA-GNN'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for DeepPath: A Reinforcement Learning Method for Knowledge Graph Reasoning (2017) [28]: abstract (from openalex) never mentions 'DeepPath'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering (2018) [29]: abstract (from openalex) never mentions 'HotpotQA'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for PullNet: Open Domain Question Answering with Iterative Retrieval on Knowledge Bases and Text (2019) [30]: abstract (from openalex) never mentions 'PullNet'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Optimizing AI Reasoning: A Hamiltonian Dynamics Approach to Multi-Hop Question Answering (2025) [31]: abstract (from crossref) never mentions 'Optimizing AI Reasoning'; it may belong to another work. Its abstract was not accepted as direct evidence.
- 6 of 25 analyses are based on abstracts only.
- Unresolved question: Does enriching training triples with local context subgraphs from the same source passage provide significant improvements over existing methods that already incorporate context via retrieval or ontology guidance, considering the risk of context noise and potential overlap with iterative refinement?
- Ambiguity (assumption): How is the 'local context subgraph' defined?; assumed: Assumed to be the set of triples extracted from the same sentence or paragraph as the target triple, based on typical information extraction pipelines for QA.
- Ambiguity (assumption): What constitutes a 'one-hop failure' in the adaptive repair loop?; assumed: Assumed to be a failure to correctly predict the relation or entity for a single-hop query derived from the knowledge graph.
- Ambiguity (assumption): What is the 'reinforcement-learning-based optimization' stage?; assumed: Assumed to involve policy gradient methods that maximize reward based on QA accuracy, similar to approaches like DeepPath or KG-Reasoner.
- Claims without a verified source: C006, C007.
- Phases that did not complete: experiments.
- No hypothesis in this report has been tested experimentally.

**Uncertainty ledger**

| Id | Question | Category | Importance | Status | Evidence for / against | Resolution |
|---|---|---|---|---|---|---|
| U001 | Has prior work already proposed enriching training triples with local context subgraphs from the same passage for multi-hop KGQA? | novelty | high | open | none / none | No directly matching work found that enriches training triples with local context subgraphs from the same passage for multi-hop KGQA; the analyzed papers focus on inference-time KG construction, teacher-student supervision, data synthesis, knowledge editing, question decomposition, or retrieval augmentation, but not on training data enrichment with passage-level context subgraphs. |
| U002 | How similar is the proposed local context subgraph method to existing context-enrichment approaches like SG-RAG MOT or retrieval-augmented generation? | overlap | high | unresolved | [32], [15] / none | The proposed local context subgraph enrichment method shows low overlap with existing context-enrichment approaches like SG-RAG MOT, RAG, IterCOMP, DynaSearcher, CacheRAG, etc. Analyzed papers demonstrate differences: they focus on inference-time KG construction (KGEIR), teacher-student intermediate signals (He et al. 2021), LLM-based data synthesis (Chen et al. 2023), knowledge editing (PokeMQA), question decomposition and SPARQL generation (Persian KGQA, ChainRAG), or retrieval augmentation with sentence graphs, none of which enrich training triples with passage-level context subgraphs or use an adaptive repair loop to generate corrective examples from one-hop failures followed by RL lower-hop transfer. |
| U003 | Will adding local context subgraphs improve multi-hop reasoning performance, or could the added noise degrade it? | validity | medium | partially resolved | [16], [12], [15] / none | Evidence from related work indicates that retaining relevant contextual information improves multi-hop QA performance, while irrelevant or noisy context degrades it. For example, IterCOMP shows that reasoning-aware prompt compression that preserves relevant context yields better results; DynaSearcher and CacheRAG demonstrate that dynamic knowledge graph augmentation and semantic caching improve retrieval-augmented generation when relevant context is retained. Teacher-student frameworks (He et al. 2021) show that intermediate supervision signals improve reasoning capacity. These findings support the validity of enriching training with local context subgraphs, though direct evidence of the specific enrichment strategy is lacking. |
| U004 | Is the adaptive repair loop that detects one-hop failures and generates corrective examples practical to implement and likely to converge? | feasibility | medium | partially resolved | none / none | Feasibility of the adaptive repair loop is supported by works showing iterative refinement improves performance (IterCOMP, DynaSearcher, CacheRAG). Reinforcement learning lower-hop transfer has been explored in multi-hop KGQA (e.g., the RL-based methods in the analyzed papers), indicating that optimizing on lower-hop QA instances can transfer to deeper multi-hop queries. However, direct evidence combining an adaptive repair loop that detects one-hop failures, generates corrective examples, and then applies RL lower-hop transfer is not present in the literature. |
| U005 | Are Exact Match and F1 sufficient to capture improvements in multi-hop reasoning, or should additional metrics (e.g., hop-wise accuracy) be considered? | evaluation | low | partially resolved | none / none | While Exact Match (EM) and F1 are widely used standard metrics for multi-hop QA (as seen in Q-DREAM, HGN, and surveyed works), the survey paper indicates that EM can be too strict and that alternative metrics like Partial Match (PM), BLEU, ROUGE, CIDer, and task-specific metrics are employed depending on the task formulation. Additionally, retrieval-focused works (e.g., FocusedRetriever) use hit@k and MRR. This suggests that EM and F1 alone may not fully capture improvements in multi-hop reasoning, and additional metrics such as hop-wise accuracy or reasoning chain evaluation may be needed to assess intermediate reasoning steps. |
| U006 | Is the proposed adaptive repair loop (detecting one-hop failures and generating corrective examples) distinct from iterative refinement strategies used in existing works like OPI, or does it constitute a similar approach? | overlap | high | resolved | [1], [14] / none | The proposed adaptive repair loop is distinct from existing iterative refinement strategies. OPI's iterative refinement filters question-irrelevant evidence to improve precision, while the adaptive repair loop detects one-hop failures and generates corrective examples to iteratively refine the model. The MRE framework samples trajectories and uses correct ones as positive examples, which is complementary but different from failure-driven example generation. |

## 14. Suggested Next Steps

1. Resolve: Does enriching training triples with local context subgraphs from the same source passage provide significant improvements over existing methods that already incorporate context via retrieval or ontology guidance, considering the risk of context noise and potential overlap with iterative refinement?
2. Design a control for the confounder: The inherent reasoning ability of large language models, which can achieve reasonable results without explicit graph retrieval, may drive observed improvements, making it difficult to isolate the effect of local context subgraph enrichment (C003).
3. Search for work newer than the most recent retrieved paper (2026) before claiming a distinction.
4. Prototype the recommended modification M001 (Training Data Enrichment Only).

## 15. References

1. Yongxue Shan, Meihan Wu, Cundi Fang et al.. **Ontology-Guided Evidence Path Inference for Multi-hop Knowledge Graph Question Answering**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2606.28076> (id `arxiv:2606.28076`; retrieved from arxiv)
2. Gaole He, Yunshi Lan, Jing Jiang et al.. **Improving Multi-hop Knowledge Base Question Answering by Learning Intermediate Supervision Signals**. 2021. <https://doi.org/10.1145/3437963.3441753> (id `arxiv:2101.03737`; retrieved from openalex; 205 citations per openalex)
3. Rajat Koner, Hang Li, Marcel Hildebrandt et al.. **Graphhopper: Multi-Hop Scene Graph Reasoning for Visual Question Answering**. _arXiv (preprint)_, 2021. <https://arxiv.org/abs/2107.06325> (id `arxiv:2107.06325`; retrieved from arxiv)
4. Mingda Chen, Xilun Chen, Wen-tau Yih. **Few-Shot Data Synthesis for Open Domain Multi-Hop Question Answering**. _arXiv (preprint)_, 2023. <https://arxiv.org/abs/2305.13691> (id `arxiv:2305.13691`; retrieved from arxiv)
5. Hengrui Gu, Kaixiong Zhou, Xiaotian Han et al.. **PokeMQA: Programmable knowledge editing for Multi-hop Question Answering**. _Annual Meeting of the Association for Computational Linguistics_, 2023. <https://www.semanticscholar.org/paper/74f20c57ac323f5fdd6acbab558eb704253ef4e6> doi:10.48550/arxiv.2312.15194 (id `arxiv:2312.15194`; retrieved from semantic_scholar; 49 citations per semantic_scholar)
6. Yuan Gao, Yiheng Zhu, Yuanbin Cao et al.. **Dr3: Ask Large Language Models Not to Give Off-Topic Answers in Open Domain Multi-Hop Question Answering**. _arXiv (preprint)_, 2024. <https://arxiv.org/abs/2403.12393> (id `arxiv:2403.12393`; retrieved from arxiv)
7. Arash Ghafouri, Mahdi Firouzmandi, Hasan Naderi. **A Method for Multi-Hop Question Answering on Persian Knowledge Graph**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2501.16350> (id `arxiv:2501.16350`; retrieved from arxiv)
8. Rongzhi Zhu, Xiang-Yu Liu, Ze-Qun Sun et al.. **Mitigating Lost-in-Retrieval Problems in Retrieval Augmented Multi-Hop Question Answering**. _Annual Meeting of the Association for Computational Linguistics_, 2025. <https://www.semanticscholar.org/paper/481c5e007c42b3194701aa81d81ba0f06aa3bfcf> doi:10.48550/arxiv.2502.14245 (id `arxiv:2502.14245`; retrieved from semantic_scholar; 28 citations per semantic_scholar)
9. Qi Zhi Lim, Chin Poo Lee, Kian Ming Lim et al.. **VLMT: Vision-Language Multimodal Transformer for Multimodal Multi-hop Question Answering**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2504.08269> (id `arxiv:2504.08269`; retrieved from arxiv)
10. Derian Boer, Stephen Roth, Stefan Kramer. **Autofocus Retrieval: An Effective Pipeline for Multi-Hop Question Answering With Semi-Structured Knowledge**. _Trans. Mach. Learn. Res._, 2025. <https://www.semanticscholar.org/paper/6bda496fbcdd3447227a25f61bebd978f0f7c3e7> (id `arxiv:2505.09246`; retrieved from semantic_scholar; 2 citations per semantic_scholar)
11. Linhao Ye, Lang Yu, Zhikai Lei et al.. **Optimizing Question Semantic Space for Dynamic Retrieval-Augmented Multi-hop Question Answering**. _Annual Meeting of the Association for Computational Linguistics_, 2025. <https://www.semanticscholar.org/paper/1319e939e03f38f02ed32ae7021fe8549b6cb610> doi:10.48550/arxiv.2506.00491 (id `arxiv:2506.00491`; retrieved from semantic_scholar; 10 citations per semantic_scholar)
12. Chuzhan Hao, Wenfeng Feng, Yuewei Zhang et al.. **DynaSearcher: Dynamic Knowledge Graph Augmented Search Agent via Multi-Reward Reinforcement Learning**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2507.17365> (id `arxiv:2507.17365`; retrieved from arxiv)
13. Tengjun Ni, Xin Yuan, Shenghong Li et al.. **StepChain GraphRAG: Reasoning Over Knowledge Graphs for Multi-Hop Question Answering**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2510.02827> (id `arxiv:2510.02827`; retrieved from arxiv)
14. Wuzhenghong Wen, Chao Xue, Su Pan et al.. **Reinforcement Learning Enhanced Multi-hop Reasoning for Temporal Knowledge Question Answering**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2601.01195> (id `arxiv:2601.01195`; retrieved from arxiv)
15. Yushi Sun, Lei Chen. **CacheRAG: A Semantic Caching System for Retrieval-Augmented Generation in Knowledge Graph Question Answering**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2604.26176> (id `arxiv:2604.26176`; retrieved from arxiv)
16. JungMin Yun, YoungBin Kim. **IterCOMP: Reasoning-aware Adaptive Prompt Compression for Multi-hop Question Answering**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2608.13588> doi:10.18653/v1/2026.acl-long.1559 (id `arxiv:2608.13588`; retrieved from arxiv)
17. Maryam Jamehshourani, Afsaneh Fatemi, Mohammad Ali Nematbakhsh. **Multi-hop clustering for reasoning chain extraction in multi-hop question answering**. _Data Mining and Knowledge Discovery_, 2026. <https://doi.org/10.1007/s10618-026-01203-0> (id `doi:10.1007/s10618-026-01203-0`; retrieved from crossref; 0 citations per crossref)
18. Chuanyang Gong, Zhihua Wei, Rui Wang et al.. **Incorporating multi-perspective information into reinforcement learning to address multi-hop knowledge graph question answering**. _Expert Systems with Applications_, 2024. <https://doi.org/10.1016/j.eswa.2024.124652> (id `doi:10.1016/j.eswa.2024.124652`; retrieved from crossref; 12 citations per crossref)
19. Hai Ning Cui, Tao Peng, Feng Xiao et al.. **Incorporating anticipation embedding into reinforcement learning framework for multi-hop knowledge graph question answering**. _Information Sciences_, 2022. <https://doi.org/10.1016/j.ins.2022.11.042> (id `doi:10.1016/j.ins.2022.11.042`; retrieved from crossref, openalex; 53 citations per openalex)
20. Hai Ning Cui, Tao Peng, Ridong Han et al.. **Reinforcement learning with dynamic completion for answering multi-hop questions over incomplete knowledge graph**. _Information Processing & Management_, 2023. <https://doi.org/10.1016/j.ipm.2023.103283> (id `doi:10.1016/j.ipm.2023.103283`; retrieved from openalex; 31 citations per openalex)
21. Hai Ning Cui, Tao Peng, Ridong Han et al.. **Path-based multi-hop reasoning over knowledge graph for answering questions via adversarial reinforcement learning**. _Knowledge-Based Systems_, 2023. <https://doi.org/10.1016/j.knosys.2023.110760> (id `doi:10.1016/j.knosys.2023.110760`; retrieved from crossref, openalex; 27 citations per openalex)
22. Vaibhav Mavi, Anubhav Jangra, Jatowt Adam. **Multi-hop Question Answering**. _Foundations and Trends in Information Retrieval_, 2024. <https://doi.org/10.1561/9781638283751> (id `doi:10.1561/9781638283751`; retrieved from arxiv, crossref, semantic_scholar; 10 citations per crossref)
23. Yuwei Fang, Siqi Sun, Zhe Gan et al.. **Hierarchical Graph Network for Multi-hop Question Answering**. 2020. <https://doi.org/10.18653/v1/2020.emnlp-main.710> (id `doi:10.18653/v1/2020.emnlp-main.710`; retrieved from openalex; 161 citations per openalex)
24. Yanlin Feng, Xinyue Chen, Bill Yuchen Lin et al.. **Scalable Multi-Hop Relational Reasoning for Knowledge-Aware Question Answering**. 2020. <https://doi.org/10.18653/v1/2020.emnlp-main.99> (id `doi:10.18653/v1/2020.emnlp-main.99`; retrieved from openalex; 214 citations per openalex)
25. Tianda Sun, D. Kazakov. **KGEIR: Knowledge Graph-Enhanced Iterative Reasoning for Multi-Hop Question Answering**. _Proceedings of the First Workshop on Comparative Performance Evaluation: From Rules to Language Models_, 2025. <https://www.semanticscholar.org/paper/a73345964e3a50e32a3dd04f77ac285eb3d32cb7> doi:10.26615/978-954-452-102-8-014 (id `doi:10.26615/978-954-452-102-8-014`; retrieved from crossref, semantic_scholar; 1 citations per semantic_scholar)
26. Floris Vossebeld, Shenghui Wang. **Learning to Refine: An Agentic RL Approach for Iterative SPARQL Query Construction**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2511.11770> (id `arxiv:2511.11770`; retrieved from arxiv)
27. Michihiro Yasunaga, Hongyu Ren, Antoine Bosselut et al.. **QA-GNN: Reasoning with Language Models and Knowledge Graphs for Question Answering**. 2021. <https://doi.org/10.18653/v1/2021.naacl-main.45> (id `doi:10.18653/v1/2021.naacl-main.45`; retrieved from openalex; 529 citations per openalex)
28. Wenhan Xiong, Thien Hoang, William Yang Wang. **DeepPath: A Reinforcement Learning Method for Knowledge Graph Reasoning**. 2017. <https://doi.org/10.18653/v1/d17-1060> (id `doi:10.18653/v1/d17-1060`; retrieved from openalex; 789 citations per openalex)
29. Zhilin Yang, Peng Qi, Saizheng Zhang et al.. **HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering**. 2018. <https://doi.org/10.18653/v1/d18-1259> (id `doi:10.18653/v1/d18-1259`; retrieved from openalex; 1770 citations per openalex)
30. Haitian Sun, Tania Bedrax-Weiss, William W. Cohen. **PullNet: Open Domain Question Answering with Iterative Retrieval on Knowledge Bases and Text**. 2019. <https://doi.org/10.18653/v1/d19-1242> (id `doi:10.18653/v1/d19-1242`; retrieved from openalex; 333 citations per openalex)
31. Javier Marin Valenzuela, A Preprint, Javier Marín. **Optimizing AI Reasoning: A Hamiltonian Dynamics Approach to Multi-Hop Question Answering**. 2025. <https://doi.org/10.22541/au.173645367.74451514/v1> (id `doi:10.22541/au.173645367.74451514/v1`; retrieved from crossref; 0 citations per crossref)
32. Ahmmad O. M. Saleh, Gokhan Tur, Y. Saygín. **SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets for Knowledge Graph Multi-Hop Question Answering**. _Machine Learning and Knowledge Extraction_, 2025. <https://www.semanticscholar.org/paper/092f905ad69b69867796f2336ac63200300583fd> doi:10.3390/make7030074 (id `doi:10.3390/make7030074`; retrieved from crossref, semantic_scholar; 5 citations per semantic_scholar)

<details><summary>Other retrieved papers (not cited in this report)</summary>

- Commonsense for Generative Multi-Hop Question Answering Tasks (2018) <https://doi.org/10.18653/v1/d18-1454> `doi:10.18653/v1/d18-1454`
- Multi-path reasoning for Multi-hop Question Answering over Knowledge Graphs (2022) <https://doi.org/10.22541/au.165426315.58267165/v1> `doi:10.22541/au.165426315.58267165/v1`
- Dynamic Multi-Hop Retrieval-Augmented Generation Framework for Professional Domain Question Answering (2026) <https://doi.org/10.22541/au.177499050.00368942/v1> `doi:10.22541/au.177499050.00368942/v1`
- Omne-R1: Learning to Reason with Memory for Multi-hop Question Answering (2025) <https://arxiv.org/abs/2508.17330> `arxiv:2508.17330`
- KG-Reasoner: A Reinforced Model for End-to-End Multi-Hop Knowledge Graph Reasoning (2026) <https://arxiv.org/abs/2604.12487> `arxiv:2604.12487`
- Temporal knowledge graph question answering via subgraph reasoning (2022) <https://doi.org/10.1016/j.knosys.2022.109134> `doi:10.1016/j.knosys.2022.109134`
- Multi-hop Knowledge Base Question Answering with an Iterative Sequence Matching Model (2019) <https://doi.org/10.1109/icdm.2019.00046> `doi:10.1109/icdm.2019.00046`
- Enriching Subgraph Retrieval with Attribute Values for Complex Question Answering Over Knowledge Graph (2025) <https://doi.org/10.2139/ssrn.5146217> `doi:10.2139/ssrn.5146217`
- Knowledge Graph Multi-Hop Question Answering Based on Dependent Syntactic Semantic Augmented Graph Networks (2024) <https://doi.org/10.3390/electronics13081436> `doi:10.3390/electronics13081436`
- UniKGQA: Unified Retrieval and Reasoning for Solving Multi-hop Question Answering Over Knowledge Graph (2022) <https://www.semanticscholar.org/paper/2d01da2c9ece0969d6ec56d22f78caf57050fc03> `arxiv:2212.00959`
- SABET-QA: Temporal Knowledge Graph Question Answering (2026) <https://arxiv.org/abs/2608.20083> `arxiv:2608.20083`
- CAM: Question Answering on Entity-Centric Videos with Continuous Extraction and Adaptive Querying (2026) <https://arxiv.org/abs/2609.06504> `arxiv:2609.06504`
- FARSIQA: Faithful and Advanced RAG System for Islamic Question Answering (2025) <https://arxiv.org/abs/2510.25621> `arxiv:2510.25621`
- Co-Evolving Graph and Text Memory for Training-Free Multi-Hop Question Answering (2026) <https://arxiv.org/abs/2607.23278> `arxiv:2607.23278`
- DEEPAMBIGQA: Ambiguous Multi-hop Questions for Benchmarking LLM Answer Completeness (2025) <https://arxiv.org/abs/2511.01323> `arxiv:2511.01323`
- An overview of the BIOASQ large-scale biomedical semantic indexing and question answering competition (2015) <https://doi.org/10.1186/s12859-015-0564-6> `doi:10.1186/s12859-015-0564-6`
- HybridQA: A Dataset of Multi-Hop Question Answering over Tabular and Textual Data (2020) <https://doi.org/10.18653/v1/2020.findings-emnlp.91> `doi:10.18653/v1/2020.findings-emnlp.91`
- TransferNet: An Effective and Transparent Framework for Multi-hop Question Answering over Relation Graph (2021) <https://doi.org/10.18653/v1/2021.emnlp-main.341> `doi:10.18653/v1/2021.emnlp-main.341`
- Multi-Hop Paragraph Retrieval for Open-Domain Question Answering (2019) <https://doi.org/10.18653/v1/p19-1222> `doi:10.18653/v1/p19-1222`
- Explainable Multi-Hop Question Answering: A Rationale-Based Approach (2025) <https://doi.org/10.20944/preprints202509.1957.v1> `doi:10.20944/preprints202509.1957.v1`
- Passage selection to improve Question Answering (2002) <https://doi.org/10.3115/1118845.1118851> `doi:10.3115/1118845.1118851`
- Dependency Relation Triples Matching for Question Answering (2009) <https://doi.org/10.3724/sp.j.1004.2008.01410> `doi:10.3724/sp.j.1004.2008.01410`
- A Language Modeling Approach to Passage Question Answering (2003) <https://doi.org/10.6028/nist.sp.500-255.qa-nus.sun> `doi:10.6028/nist.sp.500-255.qa-nus.sun`
- Evaluating Knowledge Graph-Enhanced Context for Multiple-Choice Question Answering (2025) <https://doi.org/10.1109/ickg66886.2025.00020> `doi:10.1109/ickg66886.2025.00020`
- Variational Reasoning for Question Answering With Knowledge Graph (2018) <https://doi.org/10.1609/aaai.v32i1.12057> `doi:10.1609/aaai.v32i1.12057`
- Semantic Parsing via Staged Query Graph Generation: Question Answering with Knowledge Base (2015) <https://doi.org/10.3115/v1/p15-1128> `doi:10.3115/v1/p15-1128`
- PIE-QG: Paraphrased Information Extraction for Unsupervised Question Generation from Small Corpora (2023) <https://arxiv.org/abs/2301.01064> `arxiv:2301.01064`
- KazQAD: Kazakh Open-Domain Question Answering Dataset (2024) <https://arxiv.org/abs/2404.04487> `arxiv:2404.04487`
- Talk to Right Specialists: Iterative Routing in Multi-agent Systems for Question Answering (2025) <https://arxiv.org/abs/2501.07813> `arxiv:2501.07813`
- KG-CQR: Leveraging Structured Relation Representations in Knowledge Graphs for Contextual Query Retrieval (2025) <https://arxiv.org/abs/2508.20417> `arxiv:2508.20417`
- Controlled Evaluation of Graph and Multimodal Augmentation in RAG for Document Question Answering (2026) <https://arxiv.org/abs/2607.16604> `arxiv:2607.16604`
- KGCaRe: Explainable Complex Conditional Question Answering using Automatic Knowledge Graph Construction and Context Retrieval with LLMs (2026) <https://arxiv.org/abs/2608.09779> `arxiv:2608.09779`
- HANIA: Planner-Guided Multimodal Graph Evidence Selection for Grounded Question Answering (2026) <https://arxiv.org/abs/2608.29088> `arxiv:2608.29088`
- Improving Multi-hop Question Answering over Knowledge Graphs using Knowledge Base Embeddings (2020) <https://doi.org/10.18653/v1/2020.acl-main.412> `doi:10.18653/v1/2020.acl-main.412`
- Open Domain Question Answering Using Early Fusion of Knowledge Bases and Text (2018) <https://doi.org/10.18653/v1/d18-1455> `doi:10.18653/v1/d18-1455`
- Multi-hop Reading Comprehension through Question Decomposition and Rescoring (2019) <https://doi.org/10.18653/v1/p19-1613> `doi:10.18653/v1/p19-1613`
- Dynamic Subgraph Reasoning of Knowledge Base Question Answering Based on Multi-Task Learning (2024) <https://doi.org/10.2139/ssrn.4757418> `doi:10.2139/ssrn.4757418`
- Retrieving Minimal and Sufficient Reasoning Subgraphs with Graph Foundation Models for Path-aware GraphRAG (2026) <https://arxiv.org/abs/2603.07179> `arxiv:2603.07179`
- A Storage-Retrieval Gap in Parametric Knowledge Graph Memory (2026) <https://arxiv.org/abs/2608.25489> `arxiv:2608.25489`
- Latent Retrieval for Weakly Supervised Open Domain Question Answering (2019) <https://doi.org/10.18653/v1/p19-1612> `arxiv:1906.00300`
- Entity-Relation Extraction as Multi-Turn Question Answering (2019) <https://doi.org/10.18653/v1/p19-1129> `doi:10.18653/v1/p19-1129`
- PaGLR: A path-aware GNN-LLM framework for evidence-grounded multi-hop knowledge graph question answering (2026) <https://www.semanticscholar.org/paper/58751dcdd5279b27b1b6438640398e9e706a4f72> `doi:10.1007/s44443-026-00763-x`
- SPIMP-RAG: structure-prior injected message passing for low-budget triple retrieval in LLM-based knowledge graph question answering (2026) <https://www.semanticscholar.org/paper/ff04b0d4d20f9a338f43630429e36631cc77ef5f> `doi:10.1007/s44443-026-00999-7`
- LLM-KGMQA: large language model-augmented multi-hop question-answering system based on knowledge graph in medical field (2025) <https://www.semanticscholar.org/paper/b66d0d456925627df53ec49576537662258c9b7c> `doi:10.1007/s10115-025-02399-1`
- Enhancing Question Answering through Effective Candidate Answer Selection and Mitigation of Incomplete Knowledge Graphs and over-smoothing in Graph Convolutional Networks (2024) <https://www.semanticscholar.org/paper/bdf5554653c9160e7876fbb385c6b7653815370a> `doi:10.1109/ijcnn60899.2024.10650447`
- Hybrid Graph Neural Network and Large Language Model Framework for Robust Knowledge Graph Question Answering via Retrieval-Augmented Generation (2026) <https://www.semanticscholar.org/paper/625a1cefe499a2cde59e0c643cf98650c92b0822> `doi:10.22214/ijraset.2026.82233`
- Question-aware memory network for multi-hop question answering in human–robot interaction (2021) <https://www.semanticscholar.org/paper/3a4d44ba181b954401ff2d167f66d5c7db6611a6> `arxiv:2104.13173`
- Knowledge-Graph Paths as Intermediate Supervision for Self-Evolving Search Agents (2026) <https://arxiv.org/abs/2605.05702> `arxiv:2605.05702`
- Improving embedded knowledge graph multi-hop question answering by introducing relational chain reasoning (2022) <https://doi.org/10.1007/s10618-022-00891-8> `arxiv:2110.12679`
- Subgraph retrieval and link scoring model for multi-hop question answering in knowledge graphs (2025) <https://doi.org/10.1007/s10489-024-05935-8> `doi:10.1007/s10489-024-05935-8`
- Subgraph Retrieval Enhanced Model for Multi-hop Knowledge Base Question Answering (2022) <https://doi.org/10.18653/v1/2022.acl-long.396> `doi:10.18653/v1/2022.acl-long.396`
- DualGraphRAG: A Dual-View Graph-Enhanced Retrieval-Augmented Generation Framework for Reliable and Efficient Question Answering (2026) <https://www.semanticscholar.org/paper/a9a53672aee294272e32a03fa0e23fe3c9abf55e> `doi:10.3390/app16052221`
- A Survey on Knowledge Graphs: Representation, Acquisition, and Applications (2021) <https://doi.org/10.1109/tnnls.2021.3070843> `arxiv:2002.00388`
- Language Generation with Multi-Hop Reasoning on Commonsense Knowledge Graph (2020) <https://doi.org/10.18653/v1/2020.emnlp-main.54> `doi:10.18653/v1/2020.emnlp-main.54`
- Embedding Entities and Relations for Learning and Inference in Knowledge Bases (2014) <http://arxiv.org/abs/1412.6575> `arxiv:1412.6575`
- GraphQAG: A Knowledge-Graph-Guided Visual Analytics Framework for Question-Answer Pairs Generation (2026) <https://arxiv.org/abs/2607.27182> `arxiv:2607.27182`
- Extracting Semantics from Question-Answering Services for Snippet Reuse (2021) <https://doi.org/10.26226/morressier.604907f41a80aac83ca25d36> `doi:10.26226/morressier.604907f41a80aac83ca25d36`
- Question-Answering Using Semantic Relation Triples (1999) <https://doi.org/10.6028/nist.sp.500-246.qa-clresearch2> `doi:10.6028/nist.sp.500-246.qa-clresearch2`
- MedResearcher-R1: Expert-Level Medical Deep Researcher via A Knowledge-Informed Trajectory Synthesis Framework (2025) <https://arxiv.org/abs/2508.14880> `arxiv:2508.14880`
- Subgraph-Based Attention Network for Multi-Hop Question Answering (2024) <https://doi.org/10.1109/ijcnn60899.2024.10650851> `doi:10.1109/ijcnn60899.2024.10650851`
- An End-to-End Model for Question Answering over Knowledge Base with Cross-Attention Combining Global Knowledge (2017) <https://doi.org/10.18653/v1/p17-1021> `doi:10.18653/v1/p17-1021`
- ToolForge: A Data Synthesis Pipeline for Multi-Hop Search without Real-World APIs (2025) <https://www.semanticscholar.org/paper/2fd6513fde30e2e38c73335037390685d98cc336> `arxiv:2512.16149`
- Question Answering on Freebase via Relation Extraction and Textual Evidence (2016) <https://doi.org/10.18653/v1/p16-1220> `doi:10.18653/v1/p16-1220`
- Graph Neural Networks: A Review of Methods and Applications (2018) <http://arxiv.org/abs/1812.08434> `arxiv:1812.08434`
- Knowledge Graphs (2021) <https://doi.org/10.1145/3447772> `arxiv:2003.02320`
- Graph convolutional networks: a comprehensive review (2019) <https://doi.org/10.1186/s40649-019-0069-y> `doi:10.1186/s40649-019-0069-y`
- Gradient-based learning applied to document recognition (1998) <https://doi.org/10.1109/5.726791> `doi:10.1109/5.726791`
- LSECG: LLM-based semantic enhancement and context-guided GNNs in multi-hop KGQA (2026) <https://www.semanticscholar.org/paper/4b2eacf316dcdc562143b85ce4d87224a382b745> `doi:10.1007/s13042-026-03216-z`
- From Frequency to Meaning: Vector Space Models of Semantics (2010) <https://doi.org/10.1613/jair.2934> `arxiv:1003.1141`

</details>

## Appendix A. Evidence Ledger

### [Evidence] claims (8)

- **[Evidence]** OPI applies an iterative refinement strategy to filter spurious evidence and improve semantic alignment with the question. _(claim C001, confidence: high)_
  - [1], p. 2 (direct support, verified) "It then applies an iterative refinement strategy to filter spurious evidence and improve semantic alignment with the question."
- **[Evidence]** Topic-centered expansion in multi-hop KGQA leads to rapidly growing search space with noisy mixed-type paths, and retrieved paths may fail to satisfy semantic constraints of complex questions. _(claim C002, confidence: high)_
  - [1], p. 1 (direct support, verified) "topic-centered expansion, which faces two key challenges: the search space rapidly grows with noisy mixed-type paths, and retrieved paths may fail to satisfy the semantic constraints of complex questions."
- **[Evidence]** LLMs show particular strength in multi-hop temporal reasoning, where answering a question requires traversing a sequence of temporally grounded facts. _(claim C003, confidence: high)_
  - [14], p. 1 (direct support, verified) "LLMs show particular strength in multi-hop temporal reasoning, where answering a question requires traversing a sequence of temporally grounded facts."
- **[Evidence]** SG-RAG MOT uses SubGraph Retrieval Augmented Generation (SG-RAG) to retrieve a subgraph from the knowledge graph via Cypher queries, then adds a Merging and Ordering Triplets (MOT) step that decreases redundancy via hierarchical merging and provides ordering among triplets using Breadth-First Search (BFS) traversal. _(claim C004, confidence: high)_
  - [32], abstract (direct support, verified) "SG-RAG leverages Cypher queries to search a given knowledge graph and retrieve the subgraph necessary to answer the question. The results from our previous work showed the higher performance of our method compared to the traditional Retrieval Augmented Generation (RAG). In this work, we further enhanced SG-RAG by proposing an additional step called Merging and Ordering Triplets (MOT). The new MOT step seeks to decrease the redundancy in the retrieved triplets by applying hierarchical merging to the retrieved subgraphs. Moreover, it provides an ordering among the triplets using the Breadth-First Search (BFS) traversal algorithm."
- **[Evidence]** The integration of Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) has significantly advanced Knowledge Graph Question Answering (KGQA). _(claim C005, confidence: high)_
  - [15], abstract (direct support, verified) "The integration of Large Language Models (LLMs) with Retrieval-Augmented Generation (RAG) has significantly advanced Knowledge Graph Question Answering (KGQA)."
- **[Evidence]** OPI adopts an iterative refinement strategy to reassess retrieved paths and candidate answers under the question context, filtering type-compatible but question-irrelevant evidence for more reliable answer prediction. _(claim C008, confidence: high)_
  - [1], abstract (direct support, verified) "OPI further adopts an iterative refinement strategy to reassess retrieved paths and candidate answers under the question context, filtering type-compatible but question-irrelevant evidence for more reliable answer prediction."
- **[Evidence]** we sample diverse multi-hop reasoning trajectories from a few-shot dataset under varying temperature settings _(claim C010, confidence: high)_
  - [14], p. 2 (direct support, verified) "we sample diverse multi-hop reasoning trajectories from a few-shot dataset under varying temperature settings"
- **[Evidence]** Trajectories that produce the correct final answers are identified as positive examples _(claim C011, confidence: high)_
  - [14], p. 2 (direct support, verified) "Trajectories that produce the correct final answers are identified as positive examples"

### [Inference] claims (5)

- **[Inference]** The proposed local context subgraph enrichment adds triples from the same source passage to each target triple, while SG-RAG MOT retrieves a subgraph from the knowledge graph and applies merging/ordering, and RAG retrieves passages to augment generation; all aim to enrich context but differ in source (passage-derived triples vs KG subgraph vs retrieved passages) and mechanism (direct addition vs merging/ordering vs passage concatenation). _(claim C006, confidence: medium)_
  - [32], abstract (indirect support, unverified)
  - [15], abstract (indirect support, unverified)
- **[Inference]** The proposed local context subgraph enrichment adds triples from the same source passage to each target triple, while SG-RAG MOT retrieves a subgraph from the knowledge graph and applies merging/ordering, and RAG retrieves passages to augment generation; all aim to enrich context but differ in source (passage-derived triples vs KG subgraph vs retrieved passages) and mechanism (direct addition vs merging/ordering vs passage concatenation). _(claim C007, confidence: medium)_
  - [32], abstract (indirect support, unverified)
  - [15], abstract (indirect support, unverified)
- **[Inference]** While OPI's iterative refinement reassesses retrieved paths and filters question-irrelevant evidence under question context, the proposed adaptive repair loop detects one-hop failures and generates corrective examples to iteratively refine the model, representing a different approach to error correction that focuses on failure detection and example generation rather than evidence filtering. _(claim C009, confidence: medium)_
  - [1], abstract (direct support, verified) "OPI further adopts an iterative refinement strategy to reassess retrieved paths and candidate answers under the question context, filtering type-compatible but question-irrelevant evidence for more reliable answer prediction."
- **[Inference]** While the MRE framework samples reasoning trajectories and uses those yielding correct answers as positive examples for training, the proposed adaptive repair loop detects one-hop failures and generates corrective examples to iteratively refine the model, representing a complementary approach that focuses on learning from failures rather than reinforcing correct trajectories. _(claim C012, confidence: medium)_
  - [14], p. 2 (direct support, verified) "we sample diverse multi-hop reasoning trajectories from a few-shot dataset under varying temperature settings"
  - [14], p. 2 (direct support, verified) "Trajectories that produce the correct final answers are identified as positive examples"
- **[Inference]** OPI's iterative refinement strategy filters type-compatible but question-irrelevant evidence to improve answer precision, while the proposed adaptive repair loop specifically detects one-hop failures and generates corrective examples, indicating a different focus on explicit failure detection and example generation rather than evidence filtering. _(claim C013, confidence: medium)_
  - [1], abstract (direct support, verified) "OPI further adopts an iterative refinement strategy to reassess retrieved paths and candidate answers under the question context, filtering type-compatible but question-irrelevant evidence for more reliable answer prediction."

## Appendix B. Search Log

| Query | Sources (status: results) | Papers |
|---|---|---|
| multi-hop question answering knowledge graph context subgraph training | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 16 |
| iterative refinement multi-hop question answering knowledge graph | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 13 |
| reinforcement learning multi-hop question answering knowledge graph | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 12 |
| local context subgraph knowledge graph question answering | arxiv (ok: 3), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 12 |
| "Exact Match" multi-hop question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 15 |
| extracting triples from passage for question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 15 |
| "one-hop" multi-hop question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 18 |
| local context subgraph training triples multi-hop question answering | arxiv (ok: 0), openalex (ok: 10), semantic_scholar (ok: 10), crossref (ok: 10) | 28 |

## Appendix C. Investigation Log

Each step was chosen by the ResearchForge controller from the recorded research state.

| Step | Phase | Action | Why | Alternatives considered | Outcome | Information gain |
|---|---|---|---|---|---|---|
| 0 | INTAKE | INTAKE | Research idea received. | none | idea stored in the workspace | n/a |
| 1 | FORMALIZE | FORMALIZE | The idea has not been formalized into a testable research question. | none | +85 papers; +7 searches; idea formalized | 3 |
| 2 | PLAN | PLAN | No investigation plan exists yet, so it is unclear what must be determined. | none | +5 uncertainties; investigation plan recorded | 1 |
| 3 | INVESTIGATE | READ | Retrieved papers have not been analyzed enough to judge overlap. | none | +6 analyses; +1 uncertainties | 3 |
| 4 | SYNTHESIZE | SYNTHESIZE | Analyses exist but the field has not been mapped. | none | landscape recorded | 1 |
| 5 | CRITIQUE | CRITIQUE | The idea has not been challenged yet. | none | +3 claims; +3 verified claims; critique recorded | 4 |
| 6 | UNCERTAINTY | SEARCH (U001: Has prior work already proposed enriching training triples with local cont) | Most valuable next step for high-importance novelty question U001: score 1.8 = importance 3 x expected gain 0.6 x relevance 1 x evidence deficiency 1 / cost 1. Next best: COMPARE on U002 (1.2). | COMPARE U002 (1.2); COMPARE U006 (1.2) | +16 papers; +1 searches | 2 |
| 7 | UNCERTAINTY | COMPARE (U002: How similar is the proposed local context subgraph method to existing cont) | Most valuable next step for high-importance overlap question U002: score 1.2 = importance 3 x expected gain 0.6 x relevance 1 x evidence deficiency 1 / cost 1.5. Next best: COMPARE on U006 (1.2). | COMPARE U006 (1.2); READ U001 (1.125) | +4 claims; +2 verified claims; uncertainties updated: U002 | 2 |
| 8 | UNCERTAINTY | COMPARE (U006: Is the proposed adaptive repair loop (detecting one-hop failures and gener) | Most valuable next step for high-importance overlap question U006: score 1.266 = importance 3 x expected gain 0.633 x relevance 1 x evidence deficiency 1 / cost 1.5. Next best: READ on U001 (1.125). | READ U001 (1.125); READ U006 (1.125) | +6 claims; +6 verified claims; +1 resolved uncertainties; uncertainties updated: U006 | 8 |
| 9 | UNCERTAINTY | READ (U001: Has prior work already proposed enriching training triples with local cont) | Most valuable next step for high-importance novelty question U001: score 1.125 = importance 3 x expected gain 0.75 x relevance 1 x evidence deficiency 1 / cost 2. Next best: READ on U003 (0.675). | READ U003 (0.675); READ U004 (0.525) | +3 analyses | 1.5 |
| 10 | UNCERTAINTY | READ (U003: Will adding local context subgraphs improve multi-hop reasoning performanc) | Most valuable next step for medium-importance validity question U003: score 0.6 = importance 2 x expected gain 0.667 x relevance 0.9 x evidence deficiency 1 / cost 2. Next best: READ on U004 (0.467). | READ U004 (0.467); READ U002 (0.42) | +4 analyses; uncertainties updated: U003 | 2 |
| 11 | UNCERTAINTY | READ (U004: Is the adaptive repair loop that detects one-hop failures and generates co) | Most valuable next step for medium-importance feasibility question U004: score 0.467 = importance 2 x expected gain 0.667 x relevance 0.7 x evidence deficiency 1 / cost 2. Next best: READ on U002 (0.42). | READ U002 (0.42); COMPARE U002 (0.318) | no recorded change | 0 |
| 12 | UNCERTAINTY | READ (U002: How similar is the proposed local context subgraph method to existing cont) | Most valuable next step for high-importance overlap question U002: score 0.336 = importance 3 x expected gain 0.533 x relevance 1 x evidence deficiency 0.42 / cost 2. Next best: COMPARE on U002 (0.318). | COMPARE U002 (0.318); READ U005 (0.213) | no recorded change | 0 |
| 13 | UNCERTAINTY | READ (U005: Are Exact Match and F1 sufficient to capture improvements in multi-hop rea) | Most valuable next step for low-importance evaluation question U005: score 0.178 = importance 1 x expected gain 0.444 x relevance 0.8 x evidence deficiency 1 / cost 2. Next best: READ on U003 (0.084). | READ U003 (0.084); READ U004 (0.065) | +6 analyses; uncertainties updated: U005 | 3 |
| 14 | FINALIZE | FINALIZE | Stopping: tool-call budget reached (250). | none | finalizing | n/a |
