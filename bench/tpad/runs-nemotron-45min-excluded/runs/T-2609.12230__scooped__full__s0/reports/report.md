# ResearchForge Investigation Report

Project `T-2609.12230__scooped__full__s0` · model `ollama-cloud/nemotron-3-super` · status **incomplete**

> Labels: **[Evidence]** directly supported by a verified quote from a retrieved source; **[Inference]** reasoning derived from cited evidence; **[Hypothesis]** proposed, not validated; **[Assumption]** taken as given without evidence; **[Experimental result]** observed in an executed experiment.

## 1. Executive Summary

**Investigated:** Multi‑hop question answering often relies on reasoning over a chain of facts in a knowledge graph, yet current language‑model training typically uses isolated head‑relation‑tail triples, depriving the model of the surrounding context that supports multi‑step inference. We propose to enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. The model will be fine‑tuned under two regimes: one using only the target triple/path and another that also incorporates the supporting context. To improve the reliability of the base facts, we will introduce an adaptive repair loop that detects one‑hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, we will apply reinforcement‑learning‑based optimization on lower‑hop QA instances and evaluate transfer to deeper multi‑hop queries.

**Research question:** Does enriching target triples with local context subgraphs from the same passage, combined with an adaptive repair loop for one-hop failures and RL optimization on lower-hop QA, improve multi-hop QA performance and transfer to deeper hops compared to training on isolated triples alone?

**Literature investigated:** 103 papers retrieved from 10 searches (openalex: 40, crossref: 31, arxiv: 25, semantic_scholar: 15); 8 analyzed; 8 rated highly relevant.

**Assessment:** Promising but requires experimental validation. **[Inference]** The idea introduces a novel training data enrichment strategy with adaptive repair and RL optimization, but technical risks (context noise) and experimental confounders (data size effects) must be investigated through controlled ablation studies to validate the claimed benefits.

**Closest existing work:** Subgraph Retrieval Enhanced Model for Multi-hop Knowledge Base Question Answering (2022) [1]

**Potential overlap:** Both our idea and subgraph retrieval methods utilize subgraphs to enhance reasoning in multi-hop KGQA, and both aim to improve performance over baseline methods that use isolated triples.

**Potential distinction:** Our idea applies subgraph enrichment at the training level to enrich supervision signals, includes an adaptive repair loop for iterative error correction, and evaluates transfer from lower-hop to higher-hop QA via RL optimization, whereas subgraph retrieval methods focus on inference-time retrieval without modifying training data or incorporating adaptive repair loops.

**Major risk:** The technical risk of noise and context overload from irrelevant triples in the local context subgraph (as seen in iterative RAG challenges like arxiv:2407.13101) and the experimental confounder that improvements might stem from increased training data size rather than contextual enrichment (as shown by data augmentation efficacy in arxiv:2506.09414) could undermine the claimed benefits, and the added complexity may not yield significant gains over simpler methods.

**Potential gap:** **[Hypothesis]** Determining the optimal size of the local context subgraph to balance contextual benefits against noise and computational overhead. (confidence: medium; 4 gap(s) recorded)

**Recommended modification:** **[Hypothesis]** Dynamic Context Sizing Mechanism: Replace the fixed-size local context subgraph with a dynamic sizing mechanism that determines the optimal number of additional triples per target triple based on passage complexity, entity density, or uncertainty estimates from a lightweight predictor.

**Recommended experiment:** Experimental Evaluation of Dynamic Context Enrichment with Adaptive Repair and RL Optimization for Multi-hop KGQA (E001)

**Research decision:** Insufficient evidence. **[Inference]** Basis: high-importance questions remain unresolved (U006, U007, U008, U009, U010, U011). This describes the state of the evidence, not the absolute value of the idea.

**Current research direction (refine scope, medium confidence):** **[Hypothesis]** MODIFY_METHOD (the original idea is kept in Section 2)

**Investigation:** 9 steps chosen from the research state; 11 uncertainties raised, 1 resolved, 10 still open or unresolved (Section 13, Appendix C).

**Stopped by a safety limit:** Stopping: time budget reached (2700 s). Conclusions below cover only what was recorded before the limit.

**Claim grounding:** 6/7 evidence and inference claims have at least one verified source.

This report does not declare the idea novel. Absence of a matching paper in these searches does not establish novelty; see Section 13.

## 2. Original Research Idea

> Multi‑hop question answering often relies on reasoning over a chain of facts in a knowledge graph, yet current language‑model training typically uses isolated head‑relation‑tail triples, depriving the model of the surrounding context that supports multi‑step inference. We propose to enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph that is presented together with the primary supervision signal. The model will be fine‑tuned under two regimes: one using only the target triple/path and another that also incorporates the supporting context. To improve the reliability of the base facts, we will introduce an adaptive repair loop that detects one‑hop failures, generates corrective examples, and iteratively refines the model. After this cleaning stage, we will apply reinforcement‑learning‑based optimization on lower‑hop QA instances and evaluate transfer to deeper multi‑hop queries.

## 3. Formalized Research Question

**Research question:** Does enriching target triples with local context subgraphs from the same passage, combined with an adaptive repair loop for one-hop failures and RL optimization on lower-hop QA, improve multi-hop QA performance and transfer to deeper hops compared to training on isolated triples alone?

**Hypothesis:** **[Hypothesis]** Training with local context subgraph improves multi-hop reasoning ability, the adaptive repair loop enhances base fact reliability, and RL optimization on lower-hop QA transfers to deeper multi-hop, resulting in higher QA accuracy and better transfer compared to training on isolated triples alone.

**Refined direction (D001, REFINE_SCOPE):** **[Hypothesis]** MODIFY_METHOD. Hypothesis: Training with dynamically sized and relevance-filtered local context subgraphs, combined with an adaptive repair loop that incorporates verification mechanisms and RL optimization on lower-hop QA instances, improves multi-hop QA performance and transfer to deeper hops compared to training on isolated triples or fixed-context enrichment.. Why it deserves investigation: The original idea faces key gaps: optimal context size determination (G001), context noise sensitivity (G004), and need for reliable repair mechanisms (related to G002/G003). The proposed modifications address these by: (1) dynamically sizing context per triple based on passage properties (M001), (2) filtering context triples by relevance to reduce noise (M002), and (3) integrating verification into the repair loop to ensure correction quality (M003). These changes are supported by evidence on context overload (arxiv:2407.13101), data augmentation challenges (arxiv:2506.09414), and verification techniques in closed-loop QA (doi:10.1117/12.3120384) and knowledge rewriting (doi:10.1109/iccc68654.2025.11437995). The modifications preserve the core innovation of training-level context enrichment while making it more robust and effective.

| Aspect | Formalization |
|---|---|
| Problem | Multi-hop question answering relies on reasoning over chains of facts in a knowledge graph, but current language model training uses isolated head-relation-tail triples, depriving the model of surrounding context that supports multi-step inference. |
| Target domain | Multi-hop question answering over knowledge graphs using language models. |
| Proposed method | Enrich each target triple (or path) with additional triples drawn from the same source passage, forming a local context subgraph presented together with the primary supervision signal. Introduce an adaptive repair loop that detects one-hop failures, generates corrective examples, and iteratively refines the model. After cleaning, apply reinforcement-learning-based optimization on lower-hop QA instances and evaluate transfer to deeper multi-hop queries. |
| Target system | Not recorded |
| Expected contribution | A training framework that leverages local context and adaptive repair to improve multi-hop QA performance and transfer, providing insights into the importance of contextual supervision for reasoning over knowledge graphs. |
| Independent variables | Training condition (baseline: target triple only; with local context; with local context + adaptive repair; with local context + adaptive repair + RL), Size of local context subgraph (number of extra triples) - to be experimentally determined |
| Dependent variables | Multi-hop QA accuracy (Exact Match, F1), Transfer gain from lower-hop to higher-hop QA performance |
| Controls | Base language model architecture (e.g., BERT, RoBERTa), Training data size, Evaluation datasets (HotpotQA, 2WikiMultiHopQA), Metrics (Exact Match, F1), Random seeds |

**Assumptions**

- The local context from the same passage is relevant and beneficial for multi-hop reasoning (resolved by literature on subgraph retrieval for KBQA).
- The adaptive repair loop can effectively detect and correct one-hop failures without introducing excessive noise (to be investigated).
- Reinforcement learning on lower-hop QA instances can learn transferable policies for deeper multi-hop queries (to be investigated).
- Evaluation datasets: HotpotQA and 2WikiMultiHopQA are standard for multi-hop QA (resolved by literature).
- Evaluation metrics: Exact Match and F1 are standard (resolved by literature).
- Base language model: BERT-base or RoBERTa are common baselines (resolved by literature).

**Expected benefits / potential risks**

_None recorded._

## 4. Existing Research

Overlap values are heuristic signals assigned during analysis, not measurements of novelty.

| Paper | Relevance | Method | Problem / method / evaluation overlap | Read from |
|---|---|---|---|---|
| Locate Then Ask: Interpretable Stepwise Reasoning for Multi-hop Question Answering (2022) [2] | high | Proposes an interpretable stepwise reasoning framework (StepReasoner) that incorporates both single-hop supporting sentence identification and single-hop question generation at each intermediate step, and utilizes the inference of the current hop for the next until reasoning out the final result. Em | 0.9 / 0.4 / 0.8 | full_text |
| Dr3: Ask Large Language Models Not to Give Off-Topic Answers in Open Domain Multi-Hop Question Answering (2024) [3] | high | Proposes the Discriminate→Re-Compose→Re-Solve→Re-Decompose (Dr3) mechanism consisting of two key modules: the Discriminator and the Corrector. The Discriminator leverages intrinsic LLM capabilities to judge whether generated answers are on-topic by prompting the LLM to conceptualize candidate answer | 0.6 / 0.3 / 0.8 | full_text |
| Retrieve, Summarize, Plan: Advancing Multi-hop Question Answering with an Iterative Approach (2024) [4] | high | Proposes ReSP (Retrieve, Summarize, Plan) with a dual-function summarizer that compresses information from retrieved documents, targeting both the overarching question and current sub-question concurrently. | 0.8 / 0.5 / 0.8 | abstract |
| S-Path-RAG: Semantic-Aware Shortest-Path Retrieval Augmented Generation for Multi-Hop Knowledge Graph Question Answering (2026) [5] | high | Introduces S-Path-RAG: a semantic-aware shortest-path RAG framework that enumerates bounded-length, semantically weighted candidate paths using hybrid weighted k-shortest, beam, and constrained random-walk strategy. Learns a differentiable path scorer with contrastive path encoder and lightweight ve | 0.8 / 0.6 / 0.7 | abstract |
| GRASP: Graph Agentic Search over Propositions for Multi-hop Question Answering (2026) [6] | high | Introduces Graph Agentic Search over Propositions (GRASP) that optimizes for high accuracy and minimal token usage. GRASP decomposes multi-hop queries into dependency-aware plans, dynamically scales sub-agents according to problem complexity, and uses a three-layer hierarchical graph (entities, prop | 0.7 / 0.4 / 0.8 | abstract |
| RAKR: A Reflection-Based Agent for Adaptive Knowledge Rewriting Technology Applied to Knowledge Graph Question Answering (2025) [7] | high | RAKR framework integrates chain-of-thought reasoning, reflection mechanism, and structured knowledge operations. Uses dual-layer reflection loop (open-ended before generation, closed-loop after generation) and Differentiated Preference Alignment (DAPA) training combining supervised fine-tuning with  | 0.7 / 0.5 / 0.6 | abstract |
| Closed-loop medical knowledge graph question answering with adaptive planning and consistency verification (2026) [8] | high | Proposes a closed-loop framework for medical KGQA combining subgoal decomposition, adaptive graph planning, unified memory, and backward consistency verification. Questions are decomposed into disease, symptom, examination, treatment, and contraindication subgoals. During search, candidate expansion | 0.7 / 0.6 / 0.5 | abstract |
| Pt-HotpotQA: Evaluating Multi-Hop Question Answering on Original and Portuguese-translated Datasets Using LLMs (2025) [9] | high | Introduces a publicly available Portuguese translation of the HotpotQA dataset. Evaluates several variants of Llama multilingual LLM across original and translated datasets, analyzing performance variations by language and impact of fine-tuning. | 0.3 / 0.2 / 0.9 | abstract |

<details><summary>Full paper analyses</summary>

#### Locate Then Ask: Interpretable Stepwise Reasoning for Multi-hop Question Answering (2022) [2]

- **Problem:** Multi-hop reasoning requires aggregating multiple documents to answer a complex question. Existing methods usually decompose the multi-hop question into simpler single-hop questions to solve the problem for illustrating the explainable reasoning process. However, they ignore grounding on the supporting facts of each reasoning step, which tends to generate inaccurate decompositions.
- **Method:** Proposes an interpretable stepwise reasoning framework (StepReasoner) that incorporates both single-hop supporting sentence identification and single-hop question generation at each intermediate step, and utilizes the inference of the current hop for the next until reasoning out the final result. Employs a unified reader model for both intermediate hop reasoning and final hop inference and adopts joint optimization for more accurate and robust multi-hop reasoning. The framework locates single-hop supporting sentences at each step to generate more fact-grounded and informative single-hop sub-questions without genuine or pseudo supervision, and integrates the sequential reasoning process into a unified multi-hop reader. It uses a pre-trained simple question generator and takes identified supporting sentences as base to generate single-hop questions, obviating the need for constructed supervision. To address exposure bias between training and inference (where predicted supporting sentences may deviate from oracle ones), two measures are proposed to reduce the discrepancy between train-test single-hop supporting sentences.
- **Main contribution:** Interpretable stepwise reasoning framework (StepReasoner) that improves performance and interpretability without decomposition supervision, using unified reader model, joint optimization, and exposure bias mitigation techniques.
- **Key assumptions:** Grounding on supporting facts improves reasoning step accuracy; Unified reader model for intermediate and final hop reasoning enables joint optimization; Inference from current hop can guide next hop reasoning; Addressing exposure bias between train-test supporting sentences improves robustness
- **Datasets / benchmarks:** HotpotQA, 2WikiMultiHopQA
- **Baselines:** Not recorded
- **Metrics:** Answer prediction, Supporting fact prediction (EM, F1), Joint EM/F1
- **Results:** StepReasoner outperforms all models in terms of both answer prediction and joint evaluation on HotpotQA and 2WikiMultiHopQA, achieving comparable performance in supporting fact prediction. Specifically, it performs better than both question decomposition based and one-step reading based methods.
- **Limitations:** Potential exposure bias between training and inference when predicted supporting sentences deviate from oracle ones (addressed by proposed two measures); Framework may still be limited by the quality of the initial context retrieval step
- **Future work:** Not recorded
- **Code availability:** Codes are publicly available at https://github.com/WangsyGit/StepwiseQA.
- **Relation to idea:** Locate Then Ask focuses on stepwise reasoning with supporting sentence identification and question generation for text-based multi-hop QA, while our idea focuses on enriching triples with local context subgraphs from source passages and adaptive repair loops for KGQA training. Both aim to improve multi-hop reasoning but Locate Then Ask works on text documents while our idea targets knowledge graph triples. _(basis: not stated)_

#### Dr3: Ask Large Language Models Not to Give Off-Topic Answers in Open Domain Multi-Hop Question Answering (2024) [3]

- **Problem:** Large Language Models (LLMs) may generate off-topic answers when attempting to solve Open Domain Multi-Hop Question Answering (ODMHQA), where generated answers are irrelevant to the original questions. This issue of off-topic answers accounts for approximately one-third of incorrect answers, yet remains underexplored despite its significance.
- **Method:** Proposes the Discriminate→Re-Compose→Re-Solve→Re-Decompose (Dr3) mechanism consisting of two key modules: the Discriminator and the Corrector. The Discriminator leverages intrinsic LLM capabilities to judge whether generated answers are on-topic by prompting the LLM to conceptualize candidate answers and assess whether the generated answer falls within available options (binary YES/NO judgment). When an off-topic answer is detected, the Corrector performs step-wise revisions along the reversed reasoning chain in three stages: Re-Compose→Re-Solve→Re-Decompose, which mirrors the original ReAct+ order of reasoning, composition, sub-question generation, and decomposition. This process continues until the Discriminator confirms the answer is on-topic.
- **Main contribution:** Dr3 mechanism that reduces off-topic answers in ODMHQA by nearly 13% and improves Exact Match (EM) by nearly 3% compared to baseline methods like ReAct, without relying on voting-based mechanisms or additional fact-checking tools.
- **Key assumptions:** LLMs can be used to discriminate on-topic vs off-topic answers through self-assessment; Step-wise revisions along reversed reasoning chain can correct off-topic answers; Off-topic answers significantly impact ODMHQA performance (approx. 1/3 of incorrect answers); Re-Compose→Re-Solve→Re-Decompose order effectively reverses the reasoning process to correct errors
- **Datasets / benchmarks:** HotpotQA, 2WikiMultiHopQA
- **Baselines:** Zero-Shot, Few-Shot, Chain-of-Thought (CoT), ReAct, ReAct+
- **Metrics:** Exact Match (EM), Token F1 score, Cover Exact Match (Cover EM)
- **Results:** Experimental results demonstrate that Dr3 mechanism considerably reduces the occurrence of off-topic answers by nearly 13%, improving EM by nearly 3% compared to baseline method without Dr3. The approach effectively harnesses intrinsic LLM capabilities for detection and correction.
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** Code and data will be available at https://github.com/Gy915/Dr3.
- **Relation to idea:** Dr3 focuses on detecting and correcting off-topic answers in LLM-based ODMHQA through a discrimination-correction loop, while our idea focuses on enriching triples with local context and adaptive repair loops for KGQA training. Both involve iterative improvement but Dr3 works on LLM answer post-processing while our idea works on training data enrichment. _(basis: not stated)_

#### Retrieve, Summarize, Plan: Advancing Multi-hop Question Answering with an Iterative Approach (2024) [4]

- **Problem:** Multi-hop question answering is challenging. Existing iterative RAG methods face context overload from multiple retrieval rounds and over-planning/repetitive planning due to lack of recorded retrieval trajectory.
- **Method:** Proposes ReSP (Retrieve, Summarize, Plan) with a dual-function summarizer that compresses information from retrieved documents, targeting both the overarching question and current sub-question concurrently.
- **Main contribution:** Novel iterative RAG method ReSP with dual-function summarizer that significantly outperforms state-of-the-art and shows excellent robustness concerning context length on HotpotQA and 2WikiMultihopQA.
- **Key assumptions:** Compressing retrieved information targeting both overarching and sub-questions reduces context overload; Recording retrieval trajectory prevents over-planning; Iterative RAG approaches can improve multi-hop QA performance
- **Datasets / benchmarks:** HotpotQA, 2WikiMultihopQA
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** Experimental results on HotpotQA and 2WikiMultihopQA demonstrate that ReSP significantly outperforms state-of-the-art and exhibits excellent robustness concerning context length.
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** not stated in abstract
- **Relation to idea:** ReSP focuses on iterative RAG with dual-function summarization to address context overload and over-planning, while our idea focuses on enriching triples with local context subgraphs and adaptive repair loops. Both aim to improve multi-hop QA but ReSP works on retrieval-augmented generation for text QA while our idea targets knowledge graph triple training. _(basis: not stated)_

#### S-Path-RAG: Semantic-Aware Shortest-Path Retrieval Augmented Generation for Multi-Hop Knowledge Graph Question Answering (2026) [5]

- **Problem:** Existing retrieval-augmented generation for multi-hop KGQA relies on one-shot, text-heavy retrieval that may not be optimal for knowledge graph traversal.
- **Method:** Introduces S-Path-RAG: a semantic-aware shortest-path RAG framework that enumerates bounded-length, semantically weighted candidate paths using hybrid weighted k-shortest, beam, and constrained random-walk strategy. Learns a differentiable path scorer with contrastive path encoder and lightweight verifier, injecting compact soft mixture of selected path latents into LM via cross-attention. Runs inside iterative Neural-Socratic Graph Dialogue loop where LM-produced diagnostic messages map to targeted graph edits or seed expansions for adaptive retrieval when model expresses uncertainty.
- **Main contribution:** S-Path-RAG framework that improves multi-hop KGQA through semantic-aware shortest-path retrieval, differentiable path scoring, and adaptive Neural-Socratic Graph Dialogue loop, demonstrating consistent improvements in answer accuracy, evidence coverage, and end-to-end efficiency.
- **Key assumptions:** Enumerating bounded-length semantically weighted candidate paths improves retrieval quality; Differentiable path scorer with contrastive encoder and verifier enhances path selection; Injecting path latents into LM via cross-attention improves KGQA performance; Neural-Socratic Graph Dialogue loop enables adaptive retrieval based on model uncertainty
- **Datasets / benchmarks:** standard multi-hop KGQA benchmarks
- **Baselines:** strong graph- and LLM-based baselines
- **Metrics:** answer accuracy, evidence coverage, end-to-end efficiency
- **Results:** Results demonstrate consistent improvements in answer accuracy, evidence coverage, and end-to-end efficiency compared to strong graph- and LLM-based baselines.
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** not stated in abstract
- **Relation to idea:** S-Path-RAG focuses on semantic-aware shortest-path retrieval augmented generation with adaptive retrieval via Neural-Socratic Graph Dialogue loop, while our idea focuses on enriching triples with local context subgraphs from source passages and adaptive repair loops for training. Both involve path-based reasoning and adaptive mechanisms but S-Path-RAG works on retrieval-augmented generation during inference while our idea works on training data enrichment for KGQA. _(basis: not stated)_

#### GRASP: Graph Agentic Search over Propositions for Multi-hop Question Answering (2026) [6]

- **Problem:** Agentic retrieval for multi-hop QA combined with knowledge graphs introduces significant cost: expensive graph construction at index time and compounding token usage at inference time.
- **Method:** Introduces Graph Agentic Search over Propositions (GRASP) that optimizes for high accuracy and minimal token usage. GRASP decomposes multi-hop queries into dependency-aware plans, dynamically scales sub-agents according to problem complexity, and uses a three-layer hierarchical graph (entities, propositions, passages) with entity layer for targeted traversal and proposition layer for high-recall passage retrieval via reciprocal-rank voting.
- **Main contribution:** GRASP achieves highest QA accuracy on MuSiQue and 2WikiMultiHopQA in open retrieval setting while using 40-50% fewer tokens than IRCoT+HippoRAG2, and leads on EM/F1 across datasets in LongBench setting while using 30% fewer tokens than next most accurate method. Introduces success economy metric for efficiency-aware evaluation.
- **Key assumptions:** Decomposing queries into dependency-aware plans enables dynamic sub-agent scaling; Three-layer hierarchical graph (entities, propositions, passages) improves retrieval efficiency; Reciprocal-rank voting at proposition layer enhances passage recall
- **Datasets / benchmarks:** MuSiQue, 2WikiMultihopQA, HotpotQA
- **Baselines:** Not recorded
- **Metrics:** QA accuracy, EM, F1, token usage
- **Results:** GRASP achieves highest QA accuracy in open retrieval setting on MuSiQue and 2Wiki while using 40-50% fewer tokens than IRCoT+HippoRAG2. Leads on EM and F1 across all three datasets in LongBench setting while using 30% fewer tokens than next most accurate method.
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** not stated in abstract
- **Relation to idea:** GRASP focuses on agentic retrieval with hierarchical graph search to optimize accuracy and token efficiency, while our idea focuses on enriching triples with local context subgraphs and adaptive repair loops for training. Both aim to improve multi-hop QA efficiency and accuracy but GRASP works on inference-time retrieval while our idea works on training data enrichment. _(basis: not stated)_

#### RAKR: A Reflection-Based Agent for Adaptive Knowledge Rewriting Technology Applied to Knowledge Graph Question Answering (2025) [7]

- **Problem:** Knowledge Graph Question Answering (KGQA) systems face challenges in bridging the gap between knowledge representation and language model understanding for complex queries.
- **Method:** RAKR framework integrates chain-of-thought reasoning, reflection mechanism, and structured knowledge operations. Uses dual-layer reflection loop (open-ended before generation, closed-loop after generation) and Differentiated Preference Alignment (DAPA) training combining supervised fine-tuning with RL based on human feedback.
- **Main contribution:** Introduces RAKR framework with dual-layer reflection loop and DAPA training method for KGQA, achieving up to 10.2% accuracy increase on complex multi-hop questions.
- **Key assumptions:** Reflection mechanisms can improve knowledge rewriting quality; Combining supervised fine-tuning with RL from human feedback improves knowledge rewriting; Structured knowledge operations can bridge the gap between KG representation and LM understanding
- **Datasets / benchmarks:** Not recorded
- **Baselines:** Not recorded
- **Metrics:** accuracy
- **Results:** RAKR substantially outperforms existing methods on KGQA benchmark tests, achieving up to a 10.2% increase in accuracy when handling complex questions requiring multi-hop reasoning.
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** not stated in abstract
- **Relation to idea:** RAKR focuses on knowledge rewriting via reflection loops and DAPA training for KGQA, while our idea focuses on enriching triples with local context subgraphs and adaptive repair loops for multi-hop QA. Both aim to improve KGQA but through different mechanisms. _(basis: not stated)_

#### Closed-loop medical knowledge graph question answering with adaptive planning and consistency verification (2026) [8]

- **Problem:** Medical knowledge graph question answering (KGQA) becomes unreliable when questions contain several coupled conditions requiring multi-hop evidence. Failures come from early commitment to locally plausible paths, omission of key constraints, and weak alignment between final answer and cited evidence.
- **Method:** Proposes a closed-loop framework for medical KGQA combining subgoal decomposition, adaptive graph planning, unified memory, and backward consistency verification. Questions are decomposed into disease, symptom, examination, treatment, and contraindication subgoals. During search, candidate expansions ranked by relation relevance, newly covered subgoals, historical usefulness, conflict risk, and path length. System records explored branches, unresolved conditions, conflicts, and explanation evidence in unified memory, using backward checking to decide branch acceptance, local revision, or rollback.
- **Main contribution:** Closed-loop framework for medical KGQA that combines subgoal decomposition, adaptive graph planning, unified memory, and backward consistency verification, showing consistent improvements in Accuracy, F1, and Faithfulness on GenMedGPT-5k, CMCQA, and ExplainCPE, especially under noisy or conflicting evidence.
- **Key assumptions:** Decomposing questions into disease/symptom/examination/treatment/contraindication subgoals improves medical KGQA; Ranking candidate expansions by multiple criteria enhances search quality; Unified memory with backward checking prevents unreliable commitment to locally plausible paths
- **Datasets / benchmarks:** GenMedGPT-5k, CMCQA, ExplainCPE
- **Baselines:** Not recorded
- **Metrics:** Accuracy, F1, Faithfulness
- **Results:** Experiments show consistent improvements in Accuracy, F1, and Faithfulness, with clearest gains under noisy or conflicting evidence.
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** not stated in abstract
- **Relation to idea:** This work focuses on a closed-loop framework for medical KGQA with subgoal decomposition and backward consistency verification, while our idea focuses on enriching triples with local context subgraphs and adaptive repair loops for general KGQA training. Both involve closed-loop/adaptive mechanisms but this is medical-specific and works on inference-time planning while our idea works on training data enrichment. _(basis: not stated)_

#### Pt-HotpotQA: Evaluating Multi-Hop Question Answering on Original and Portuguese-translated Datasets Using LLMs (2025) [9]

- **Problem:** Despite advancements in Multi-hop Question Answering (MHQA) for English, resources for evaluating Large Language Models (LLMs) in Portuguese remain scarce.
- **Method:** Introduces a publicly available Portuguese translation of the HotpotQA dataset. Evaluates several variants of Llama multilingual LLM across original and translated datasets, analyzing performance variations by language and impact of fine-tuning.
- **Main contribution:** Provides Portuguese translation of HotpotQA dataset and demonstrates that multilingual models perform better in English than Portuguese (gap narrows with model size), showing fine-tuning improves Portuguese MHQA performance.
- **Key assumptions:** Translating HotpotQA to Portuguese provides valuable benchmark for multilingual MHQA research; Multilingual LLMs show language-dependent performance variations; Fine-tuning can improve MHQA performance in low-resource languages like Portuguese
- **Datasets / benchmarks:** HotpotQA (English), Pt-HotpotQA (Portuguese translation)
- **Baselines:** Not recorded
- **Metrics:** Not recorded
- **Results:** Findings show multilingual models consistently perform better in English than Portuguese (gap narrows with increased model size), and fine-tuning improves MHQA performance in Portuguese.
- **Limitations:** Not recorded
- **Future work:** Not recorded
- **Code availability:** not stated in abstract
- **Relation to idea:** Pt-HotpotQA focuses on creating and evaluating a Portuguese translation of HotpotQA for multilingual LLM assessment, while our idea focuses on enriching triples with local context subgraphs and adaptive repair loops for KGQA training. Both involve multi-hop QA evaluation but Pt-HotpotQA addresses language resource gap while our idea targets training methodology improvement. _(basis: not stated)_

</details>

## 5. Research Landscape

```text
Multi-hop Question Answering over Knowledge Graphs
├── Stepwise Reasoning and Decomposition  [2]
├── Iterative Retrieval-Augmented Generation  [4] [5]
├── Agentic Search and Planning  [6]
├── Knowledge Rewriting and Reflection  [7]
├── Closed-loop Verification Systems  [8]
├── Answer Post-processing and Correction  [3]
├── Training Data Enrichment
└── Subgraph Retrieval Methods  [1]
```

**Where the idea fits:** **[Inference]** Training Data Enrichment

**Dominant approaches**

- Iterative Retrieval-Augmented Generation
- Agentic Search and Planning
- Stepwise Reasoning and Decomposition

**Common assumptions**

- Grounding on supporting facts or context improves reasoning accuracy
- Iterative or stepwise processes allow for error correction and refinement
- Unified models or joint optimization improve performance across reasoning steps
- Efficiency metrics (token usage, computational cost) are important for practical deployment

**Common datasets**

- HotpotQA
- 2WikiMultiHopQA
- MuSiQue

**Common benchmarks**

- HotpotQA distractor setting
- 2WikiMultiHopQA
- LongBench

**Common metrics**

- Exact Match (EM)
- F1 score
- Accuracy
- Token usage
- Supporting fact prediction (EM, F1)

**Underexplored combinations**

- **[Hypothesis]** Combining local context subgraph enrichment with adaptive repair loops for training data improvement
- **[Hypothesis]** Integrating reinforcement learning optimization with context-aware training for transfer to deeper hops
- **[Hypothesis]** Using closed-loop verification mechanisms in training data generation processes

**Limitations repeated across papers**

- Exposure bias between training and inference when predicted intermediate states deviate from ground truth [2]
- Context overload from multiple retrieval rounds or long contexts [4]
- Need for annotated evidence or decomposition supervision for training [2], [3]
- High computational costs from knowledge graph construction or iterative processing [6], [8]
- Limited generalization across different question types or domains [9]

**Contradictions between papers**

- Whether iterative retrieval improves or hinders interpretability - some argue it reduces interpretability while others claim stepwise reasoning enhances it [4], [2]

## 6. Closest Existing Work

**[Inference]** The Subgraph Retrieval Enhanced Model (SR) retrieves subgraphs at inference time to aid reasoning, while our idea enriches training triples with local context subgraphs from the same source passage and adds an adaptive repair loop for iterative refinement.

- Subgraph Retrieval Enhanced Model for Multi-hop Knowledge Base Question Answering (2022) [1] (not analyzed in detail)

## 7. Potential Overlap

**Overlap:** **[Inference]** Both our idea and subgraph retrieval methods utilize subgraphs to enhance reasoning in multi-hop KGQA, and both aim to improve performance over baseline methods that use isolated triples.

**Potential distinction:** **[Inference]** Our idea applies subgraph enrichment at the training level to enrich supervision signals, includes an adaptive repair loop for iterative error correction, and evaluates transfer from lower-hop to higher-hop QA via RL optimization, whereas subgraph retrieval methods focus on inference-time retrieval without modifying training data or incorporating adaptive repair loops.

**Novelty questions**

- **Has essentially the same idea been proposed?** (low severity): No directly matching work was found in the searched literature for enriching training triples with local context subgraphs combined with an adaptive repair loop and RL optimization. _([1]; [Inference] claim C007)_

## 8. Potential Research Gap

### G001: Determining the optimal size of the local context subgraph to balance contextual benefits against noise and computational overhead.

- **Status:** **[Hypothesis]** a potential gap, derived from the evidence below
- **Evidence:**
  - [4], abstract (indirect support, unverified)
  - [1], abstract (indirect support, unverified)
- **Related papers:** [4], [1]
- **Why existing work does not address it:** **[Inference]** Existing subgraph retrieval methods focus on retrieving relevant subgraphs at inference time but do not systematically study the impact of varying context sizes on training effectiveness for multi-hop QA, particularly in the context of enriching supervision signals with local context.
- **Research question:** What is the optimal number of additional triples to include in the local context subgraph for each target triple/path that maximizes multi-hop QA performance while minimizing noise and computational overhead?
- **Potential experiment:** Ablation study varying the number of additional triples (e.g., 0, 1, 2, 3, 5, 10) in the local context subgraph while keeping other factors constant, measuring Exact Match and F1 on HotpotQA and 2WikiMultiHopQA datasets.
- **Confidence:** medium
- **Verification required:** Controlled experiments to isolate context size effects from other variables such as training data size and model architecture.

### G002: Identifying the most suitable reinforcement learning algorithm for optimizing lower-hop QA instances to transfer to deeper multi-hop queries in the context of knowledge graph question answering.

- **Status:** **[Hypothesis]** a potential gap, derived from the evidence below
- **Evidence:**
  - [10], abstract (indirect support, unverified)
- **Related papers:** [10], [6]
- **Why existing work does not address it:** **[Inference]** While transfer learning in deep reinforcement learning has been surveyed, specific applications to knowledge graph question answering for transferring policies from lower-hop to higher-hop reasoning tasks remain unexplored, particularly in combination with context-enriched training and adaptive repair loops.
- **Research question:** Which reinforcement learning algorithm (e.g., PPO, REINFORCE, Q-learning) is most effective for optimizing lower-hop QA instances to learn transferable policies for deeper multi-hop queries when combined with local context subgraph enrichment and adaptive repair mechanisms?
- **Potential experiment:** Comparative study of different RL algorithms (PPO, A2C, DQN) applied to lower-hop QA optimization, measuring transfer gain to higher-hop QA performance on HotpotQA and 2WikiMultiHopQA.
- **Confidence:** medium
- **Verification required:** Empirical comparison of RL algorithms in the KGQA transfer optimization setting.

### G003: Quantifying the computational cost of training with local context subgraphs compared to isolated triples to assess feasibility for large-scale knowledge graphs.

- **Status:** **[Hypothesis]** a potential gap, derived from the evidence below
- **Evidence:**
  - [6], abstract (indirect support, unverified)
- **Related papers:** [6], [1]
- **Why existing work does not address it:** **[Inference]** Existing work on agentic retrieval and context-aware methods discusses computational costs but does not provide a direct comparison between training with enriched local context subgraphs versus isolated triples in the context of multi-hop QA model training.
- **Research question:** What is the computational overhead (training time, memory usage) of incorporating local context subgraphs into multi-hop QA training compared to training on isolated triples, and how does this scale with knowledge graph size?
- **Potential experiment:** Measure training time and memory consumption for varying sizes of local context subgraphs (0, 2, 5, 10 additional triples) on a subset of a large knowledge graph (e.g., Wikidata) using a standard multi-hop QA model architecture.
- **Confidence:** medium
- **Verification required:** Benchmarking experiments on realistic knowledge graph sizes to establish practical feasibility.

### G004: Assessing how the quality of extracted local context (e.g., noise from irrelevant triples) affects the final multi-hop QA performance and determining robust methods for context extraction.

- **Status:** **[Hypothesis]** a potential gap, derived from the evidence below
- **Evidence:**
  - [4], abstract (indirect support, unverified)
  - [11], abstract (indirect support, unverified)
- **Related papers:** [4], [11]
- **Why existing work does not address it:** **[Inference]** While data augmentation techniques exist for KGQA, few studies examine the impact of noisy or irrelevant contextual information in training data enrichment for multi-hop reasoning, particularly when leveraging local context from source passages.
- **Research question:** How does the precision and recall of local context extraction (proportion of relevant vs. irrelevant triples) influence multi-hop QA performance, and what extraction strategies maximize benefit while minimizing noise?
- **Potential experiment:** Systematically inject controlled levels of noise (irrelevant triples) into the local context subgraph and measure impact on Exact Match and F1 scores, comparing different context extraction strategies (e.g., proximity-based, attention-based, random).
- **Confidence:** medium
- **Verification required:** Experiments with controlled noise injection to establish sensitivity thresholds and robust extraction methods.

## 9. Critique

| | |
|---|---|
| Strongest argument FOR | The idea addresses a key limitation of current LM training (lack of context) by enriching triples with local context subgraphs, which has been shown to improve retrieval in subgraph retrieval methods (e.g., arxiv:2202.13296), and the adaptive repair loop can iteratively improve base fact reliability, similar to reflection loops in knowledge rewriting approaches (e.g., doi:10.1109/iccc68654.2025.11437995) and backward consistency verification (e.g., doi:10.1117/12.3120384). |
| Strongest argument AGAINST | The technical risk of noise and context overload from irrelevant triples in the local context subgraph (as seen in iterative RAG challenges like arxiv:2407.13101) and the experimental confounder that improvements might stem from increased training data size rather than contextual enrichment (as shown by data augmentation efficacy in arxiv:2506.09414) could undermine the claimed benefits, and the added complexity may not yield significant gains over simpler methods. |
| Most important unresolved question | What is the optimal size and composition of the local context subgraph to maximize benefit while minimizing noise? |
| Most dangerous experimental confounder | The observed improvements might be due to increased training data size rather than the contextual enrichment itself. |
| Closest existing work | [1] |
| Potential contribution | **[Hypothesis]** A training framework that leverages local context and adaptive repair to improve multi-hop QA performance and transfer, providing insights into the importance of contextual supervision for reasoning over knowledge graphs. |

**Technical validity**

- **Is the difference only implementation-level?** (moderate severity): The idea combines context enrichment with adaptive repair loop and RL optimization, representing a novel combination of mechanisms beyond existing approaches. _([1], [5], [7], [8]; [Inference] claim C007; [Evidence] claim C004; [Evidence] claim C005; [Evidence] claim C006)_

**Experimental validity**

- **What confounders could produce the claimed result?** (high severity): Observed improvements might be due to increased training data size from added context triples rather than contextual enrichment, and context noise could degrade performance. _([11], [4]; [Inference] claim C003; [Inference] claim C002)_

**Practicality**

- **Is it feasible?** (moderate severity): Feasibility depends on determining optimal context size, failure detection mechanism, and RL algorithm, which are unresolved but actively researched. _([12], [4], [11]; [Inference] claim C001; [Inference] claim C002; [Inference] claim C003)_

## 10. Proposed Modifications

Difficulty ratings are qualitative (low / moderate / high) with the stated basis; no numeric scoring is used.

### M001: Dynamic Context Sizing Mechanism (recommended)

**[Hypothesis]** Replace the fixed-size local context subgraph with a dynamic sizing mechanism that determines the optimal number of additional triples per target triple based on passage complexity, entity density, or uncertainty estimates from a lightweight predictor.

| | |
|---|---|
| Why it differs | Unlike fixed-context approaches in existing work (e.g., arxiv:2407.13101 uses fixed summarization, arxiv:2202.13296 retrieves variable-sized subgraphs but at inference time only), this modification adapts context size at the training level to optimize the trade-off between contextual benefit and noise for each specific triple. |
| Technical mechanism | Train a lightweight context size predictor (e.g., based on passage length, entity count, or relation diversity) that outputs the number of additional triples to include for each target triple, or use uncertainty estimation from the model's initial predictions to gate context inclusion. |
| Expected benefit | Reduces noise from irrelevant triples while preserving contextual benefits, leading to more efficient training and better generalization, particularly addressing the optimal context size gap (G001). |
| Potential novelty | Combines adaptive computation with context-enriched training for KGQA, which has not been explicitly explored in existing literature. |
| Implementation difficulty | moderate, because Requires designing and training a context size predictor or uncertainty estimator, adding moderate complexity to the training pipeline but using established techniques. |
| Experimental difficulty | moderate, because Requires ablation studies comparing fixed vs. dynamic sizing and implementation of the predictor mechanism. |
| Main risk | The predictor may add overhead or fail to accurately estimate optimal context size, potentially underperforming than a well-tuned fixed size. |
| Required baselines | Fixed context size (0, 2, 5, 10 additional triples), Base model without context enrichment |
| Related work | [4], [1], [5] |
| Addresses gaps | G001 |

### M002: Context Relevance Filtering Mechanism (recommended)

**[Hypothesis]** Implement a relevance scoring function to filter triples in the local context subgraph, retaining only those with high semantic or structural relevance to the target triple or query intent, thereby reducing noise from irrelevant contextual information.

| | |
|---|---|
| Why it differs | Existing context enrichment methods (e.g., arxiv:2506.09414's data augmentation, arxiv:2407.13101's summarization) either use all retrieved context or apply coarse filtering; this modification introduces fine-grained, triple-level relevance scoring to selectively enrich training signals with maximally informative context. |
| Technical mechanism | Use a lightweight relevance scorer (e.g., based on entity-relation embedding similarity, path ranking, or cross-attention weights) to assign relevance scores to candidate context triples and retain only those above a threshold, or select top-k most relevant triples. |
| Expected benefit | Mitigates the context noise problem (G004) by ensuring that enriched local context contains predominantly relevant information, improving signal-to-noise ratio in training data and reducing the risk of performance degradation from irrelevant triples. |
| Potential novelty | Applies relevance scoring mechanisms from information retrieval to the context enrichment step in KGQA training, combining techniques not previously integrated in this manner. |
| Implementation difficulty | moderate, because Requires implementing a relevance scoring function and integrating it into the context extraction pipeline, using established similarity or scoring methods. |
| Experimental difficulty | moderate, because Requires experiments with different relevance scoring strategies and threshold/selection mechanisms to optimize performance. |
| Main risk | Overly aggressive filtering may remove useful contextual information, while insufficient filtering may not adequately reduce noise; threshold tuning is critical. |
| Required baselines | No context filtering (all retrieved triples), Random triple selection, Base model without context enrichment |
| Related work | [11], [4], [1] |
| Addresses gaps | G004 |

### M003: Integrated Verification in Adaptive Repair Loop (recommended)

**[Hypothesis]** Enhance the adaptive repair loop by incorporating backward consistency verification or reflection mechanisms to validate generated corrective examples before using them for model refinement, ensuring that repairs are grounded and reliable.

| | |
|---|---|
| Why it differs | While adaptive repair loops exist in concept, existing work does not combine them with explicit verification mechanisms; this modification integrates ideas from closed-loop verification (doi:10.1117/12.3120384) and reflection loops (doi:10.1109/iccc68654.2025.11437995) to make the repair process more grounded and less prone to reinforcing errors. |
| Technical mechanism | After generating corrective examples from detected one-hop failures, apply a verification step (e.g., checking consistency between proposed corrections and source passage, or using a reflection mechanism to assess repair quality) before adding them to the training set for iterative refinement. |
| Expected benefit | Increases the reliability of the adaptive repair loop by preventing the propagation of incorrect corrections, leading to more stable and effective iterative refinement of the model's knowledge base. |
| Potential novelty | Combines adaptive repair with verification mechanisms from closed-loop QA and knowledge rewriting frameworks, creating a more trustworthy self-correction system for KGQA training. |
| Implementation difficulty | moderate, because Requires integrating verification techniques (e.g., consistency checks, reflection) into the repair loop, building on existing approaches but adding coordination complexity. |
| Experimental difficulty | moderate, because Requires comparing the integrated verification approach against a basic adaptive repair loop to measure impact on refinement stability and final performance. |
| Main risk | Verification may be too strict, filtering out useful corrective examples, or add computational overhead that slows down the repair process. |
| Required baselines | Basic adaptive repair loop without verification, Model without adaptive repair |
| Related work | [8], [7], [5] |
| Addresses gaps | G002, G003 |

## 11. Recommended Experimental Design

### E001: Experimental Evaluation of Dynamic Context Enrichment with Adaptive Repair and RL Optimization for Multi-hop KGQA

- **Research question:** Does training with dynamically sized and relevance-filtered local context subgraphs, combined with an adaptive repair loop that incorporates verification mechanisms and RL optimization on lower-hop QA instances, improve multi-hop QA performance and transfer to deeper hops compared to training on isolated triples or fixed-context enrichment?
- **Hypothesis:** **[Hypothesis]** The proposed method will achieve higher Exact Match and F1 scores on multi-hop QA benchmarks (HotpotQA, 2WikiMultiHopQA) and demonstrate positive transfer from lower-hop to higher-hop performance compared to baselines, due to better contextual supervision, reliable error correction, and learned transferable policies.
- **Proposed method:** For each target triple (or path) extracted from a source passage in the knowledge graph, we first retrieve additional triples from the same passage. A dynamic context sizing mechanism determines the optimal number of additional triples based on passage-level features (e.g., length, entity density). A relevance filtering mechanism then selects the most relevant triples using embedding-based similarity to the target triple. The resulting local context subgraph (target triple + selected context triples) is used as the training supervision signal. The model is fine-tuned on these enriched triples. An adaptive repair loop detects one-hop failures via model uncertainty signals (e.g., diagnostic messages from the language model) or backward consistency verification, generates corrective examples, and refines the model, with a verification step (e.g., consistency check with source passage or reflection mechanism) to ensure corrections are grounded before adding them to the training set. After this cleaning stage, reinforcement learning (specifically PPO) is applied on lower-hop QA instances to optimize a policy for transferring to deeper multi-hop queries, using a reward based on QA correctness. The final model is evaluated on held-out multi-hop QA test sets.
- **Baselines:** Isolated triples: training on target triples only without any context enrichment, Fixed-size context: training with a fixed number of additional triples (e.g., 2) per target triple, no dynamic sizing or filtering, Context without repair: training with dynamic sizing and relevance filtering but without the adaptive repair loop, Repair without verification: adaptive repair loop without the verification step for corrective examples, Repair without RL: full method but without the RL optimization stage on lower-hop QA, Subgraph Retrieval Enhanced Model (SR): inference-time subgraph retrieval method from arxiv:2202.13296 combined with a standard KGQA reasoner, GRASP: agentic retrieval method from arxiv:2605.16598 for comparison, S-Path-RAG: semantic-aware shortest-path RAG from arxiv:2603.23512 for comparison
- **Datasets:** HotpotQA, 2WikiMultiHopQA, MuSiQue (optional for broader evaluation)
- **Workloads:** Standard multi-hop question answering evaluation
- **Hardware:** "Single GPU with at least 24GB memory (e.g., RTX 3090 or A6000)"
- **Software environment:** "Python 3.8+, PyTorch 1.9+, HuggingFace Transformers 4.20+, DGL or PyG for graph operations, CUDA 11.0+"
- **Metrics:** Exact Match (EM), F1 score, Transfer gain
- **Ablations:** Ablate dynamic sizing (use fixed context size); Ablate relevance filtering (use all retrieved context triples); Ablate verification in repair loop (no verification of corrective examples); Ablate RL optimization stage (remove RL optimization on lower-hop QA)
- **Controls:** Base language model architecture (BERT-base or RoBERTa-base); Training data size (controlled by sub-sampling to match baseline when enrichment increases count); Random seeds (fixed across runs); Evaluation procedure and metrics; Negative sampling strategy for KGQA training
- **Confounders addressed:** Training data size effects: by controlling the number of training triples through sub-sampling when context enrichment increases the count; Model architecture variability: using the same base model across all conditions; Random seed variability: fixing seeds for reproducibility; Evaluation procedure consistency: using identical evaluation scripts and metrics
- **Expected outcomes:** ["The proposed method will achieve statistically significant improvements in EM and F1 over the isolated triples baseline and at least one of the fixed-context baselines.", "Ablation studies will show that each component (dynamic sizing, relevance filtering, verification, RL) contributes positively to performance.", "Transfer from lower-hop to higher-hop QA will be positive and significant compared to baselines lacking the RL optimization stage."]
- **Failure conditions:** The proposed method does not significantly outperform the isolated triples baseline (p>0.05) on both HotpotQA and 2WikiMultiHopQA.; Ablation studies reveal that removing any core component does not lead to a statistically significant decrease in performance.; Transfer gain is not significant or negative when comparing the full method to the method without RL optimization.
- **Reproducibility:** "All code, data splits, and hyperparameters will be made publicly available. Experiments will be run with fixed random seeds (e.g., 42) and repeated at least three times to report mean and standard deviation. Detailed training logs and checkpoint saving will be enabled."
- **Related work:** [4], [11], [8], [7], [1], [6], [5]
- **Executable spec:** Baseline_Isolated (baseline), Method_Full (method), Ablation_NoDynamic (ablation), Ablation_NoFilter (ablation), Ablation_NoVerify (ablation), Ablation_NoRL (ablation); status `awaiting_approval`; runs only after explicit approval

## 12. Experimental Results

Experiment not performed. The designs in Section 11 are untested.

## 13. Remaining Uncertainty

- Literature coverage: searched 10 queries over arxiv, crossref, openalex, semantic_scholar. Work outside these queries and sources, very recent preprints, and non-English work may be missing; the absence of matching work here does not establish novelty.
- Some source requests failed and their results are missing: semantic_scholar (api.semanticscholar.org failed after 5 attempts (HTTP 429)).
- Metadata warning for Locate Then Ask: Interpretable Stepwise Reasoning for Multi-hop Question Answering (2022) [2]: abstract (from arxiv) never mentions 'Locate Then Ask'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for HOLMES: Hyper-Relational Knowledge Graphs for Multi-hop Question Answering using LLMs (2024) [13]: abstract (from semantic_scholar) never mentions 'HOLMES'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Retrieve, Summarize, Plan: Advancing Multi-hop Question Answering with an Iterative Approach (2024) [4]: abstract (from arxiv) never mentions 'Retrieve, Summarize, Plan'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Regime-Conditional Retrieval: Theory and a Transferable Router for Two-Hop QA (2026) [14]: abstract (from arxiv) never mentions 'Regime-Conditional Retrieval'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering (2018) [12]: abstracts from openalex and semantic_scholar disagree; kept the one from semantic_scholar, which matches the title better. Its abstract was not accepted as direct evidence.
- Metadata warning for Answering while Summarizing: Multi-task Learning for Multi-hop QA with Evidence Extraction (2019) [15]: abstract (from openalex) never mentions 'Answering while Summarizing'; it may belong to another work. Its abstract was not accepted as direct evidence.
- Metadata warning for Pt-HotpotQA: Evaluating Multi-Hop Question Answering on Original and Portuguese-translated Datasets Using LLMs (2025) [9]: abstract (from crossref) never mentions 'Pt-HotpotQA'; it may belong to another work. Its abstract was not accepted as direct evidence.
- 6 of 8 analyses are based on abstracts only.
- Unresolved question: What is the optimal size and composition of the local context subgraph to maximize benefit while minimizing noise?
- Gap G001 requires verification: Controlled experiments to isolate context size effects from other variables such as training data size and model architecture.
- Gap G002 requires verification: Empirical comparison of RL algorithms in the KGQA transfer optimization setting.
- Gap G003 requires verification: Benchmarking experiments on realistic knowledge graph sizes to establish practical feasibility.
- Gap G004 requires verification: Experiments with controlled noise injection to establish sensitivity thresholds and robust extraction methods.
- Claims without a verified source: C002.
- No hypothesis in this report has been tested experimentally.

**Uncertainty ledger**

| Id | Question | Category | Importance | Status | Evidence for / against | Resolution |
|---|---|---|---|---|---|---|
| U006 | Does published work contradict the current assessment: Our idea applies subgraph enrichment at the training level to enrich supervision signals, includes an adaptive repair loop for iterative error correction, and evaluates transfer from lower-hop to higher-hop QA via RL optimization, whereas subgraph retrieval methods focus on inference-time retrieval without modifying training data or incorporating adaptive repair loops.? (raised by ResearchForge) | contradiction | high | open | none / none | Not recorded |
| U007 | Has gap G001 already been addressed: Determining the optimal size of the local context subgraph to balance contextual benefits against noise and computational overhead.? (raised by ResearchForge) | novelty | high | open | none / none | Not recorded |
| U008 | Has gap G002 already been addressed: Identifying the most suitable reinforcement learning algorithm for optimizing lower-hop QA instances to transfer to deeper multi-hop queries in the context of knowledge graph question answering.? (raised by ResearchForge) | novelty | high | open | none / none | Not recorded |
| U009 | Has gap G003 already been addressed: Quantifying the computational cost of training with local context subgraphs compared to isolated triples to assess feasibility for large-scale knowledge graphs.? (raised by ResearchForge) | novelty | high | open | none / none | Not recorded |
| U010 | Has gap G004 already been addressed: Assessing how the quality of extracted local context (e.g., noise from irrelevant triples) affects the final multi-hop QA performance and determining robust methods for context extraction.? (raised by ResearchForge) | novelty | high | open | none / none | Not recorded |
| U011 | Is direction D001 already explored or contradicted: MODIFY_METHOD? (raised by ResearchForge) | contradiction | high | open | none / none | Not recorded |
| U001 | What is the optimal number of additional triples to include in the local context subgraph for each target triple/path? | feasibility | medium | open | none / none | Not recorded |
| U003 | Which reinforcement learning algorithm is most suitable for optimizing lower-hop QA instances to transfer to deeper multi-hop queries? | feasibility | medium | open | none / none | Not recorded |
| U004 | What is the computational cost of training with local context subgraphs compared to isolated triples? | feasibility | medium | open | none / none | Not recorded |
| U005 | How does the quality of the extracted local context (e.g., noise from irrelevant triples) affect the final performance? | validity | medium | open | none / none | Not recorded |
| U002 | How should one-hop failures be detected to trigger the adaptive repair loop? | validity | high | resolved | [5], [8], [7], [3] / none | One-hop failures can be detected using several mechanisms: (1) model uncertainty signals such as diagnostic messages from the language model (as in S-Path-RAG's Neural-Socratic Graph Dialogue loop), (2) backward consistency verification that checks alignment between final answer and cited evidence (as in closed-loop medical KGQA), (3) reflection loops that iteratively optimize based on generation feedback (as in RAKR), and (4) discriminator-based judgments of answer correctness (as in Dr3's off-topic detection). These approaches enable triggering an adaptive repair loop to generate corrective examples and iteratively refine the model. |

## 14. Suggested Next Steps

1. Run the recommended experiment E001 (Experimental Evaluation of Dynamic Context Enrichment with Adaptive Repair and RL Optimization for Multi-hop KGQA) with budget-matched baselines.
2. Resolve: What is the optimal size and composition of the local context subgraph to maximize benefit while minimizing noise?
3. Design a control for the confounder: The observed improvements might be due to increased training data size rather than the contextual enrichment itself.
4. Verify gap G001: Controlled experiments to isolate context size effects from other variables such as training data size and model architecture.
5. Verify gap G002: Empirical comparison of RL algorithms in the KGQA transfer optimization setting.
6. Verify gap G003: Benchmarking experiments on realistic knowledge graph sizes to establish practical feasibility.
7. Verify gap G004: Experiments with controlled noise injection to establish sensitivity thresholds and robust extraction methods.
8. Search for work newer than the most recent retrieved paper (2026) before claiming a distinction.
9. Prototype the recommended modification M001 (Dynamic Context Sizing Mechanism).

## 15. References

1. Jing Zhang, Xiaokang Zhang, Jifan Yu et al.. **Subgraph Retrieval Enhanced Model for Multi-hop Knowledge Base Question Answering**. _Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)_, 2022. <https://doi.org/10.18653/v1/2022.acl-long.396> (id `arxiv:2202.13296`; retrieved from openalex; 109 citations per openalex)
2. Siyuan Wang, Zhongyu Wei, Zhihao Fan et al.. **Locate Then Ask: Interpretable Stepwise Reasoning for Multi-hop Question Answering**. _arXiv (preprint)_, 2022. <https://arxiv.org/abs/2208.10297> (id `arxiv:2208.10297`; retrieved from arxiv)
3. Yuan Gao, Yiheng Zhu, Yuanbin Cao et al.. **Dr3: Ask Large Language Models Not to Give Off-Topic Answers in Open Domain Multi-Hop Question Answering**. _arXiv (preprint)_, 2024. <https://arxiv.org/abs/2403.12393> (id `arxiv:2403.12393`; retrieved from arxiv)
4. Zhouyu Jiang, Mengshu Sun, Lei Liang et al.. **Retrieve, Summarize, Plan: Advancing Multi-hop Question Answering with an Iterative Approach**. _The Web Conference_, 2024. <https://arxiv.org/abs/2407.13101> doi:10.1145/3701716.3716889 (id `arxiv:2407.13101`; retrieved from arxiv, openalex, semantic_scholar; 12 citations per openalex)
5. Rong Fu, Yemin Wang, Tianxiang Xu et al.. **S-Path-RAG: Semantic-Aware Shortest-Path Retrieval Augmented Generation for Multi-Hop Knowledge Graph Question Answering**. _The Web Conference_, 2026. <https://www.semanticscholar.org/paper/a5849638f34e2346e89fe6b82683a22f74ab6fb0> doi:10.1145/3774904.3792459 (id `arxiv:2603.23512`; retrieved from semantic_scholar; 6 citations per semantic_scholar)
6. Stockton Jenkins, Ramya Korlakai Vinayak, Junjie Hu. **GRASP: Graph Agentic Search over Propositions for Multi-hop Question Answering**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2605.16598> (id `arxiv:2605.16598`; retrieved from arxiv)
7. Xiaolei Zhou, Xinyang Shao, Rui-Feng Guo et al.. **RAKR: A Reflection-Based Agent for Adaptive Knowledge Rewriting Technology Applied to Knowledge Graph Question Answering**. _2025 11th International Conference on Computer and Communications (ICCC)_, 2025. <https://www.semanticscholar.org/paper/be5dbbc970e6d0d722410bf4a5a8a6ee244756e3> doi:10.1109/iccc68654.2025.11437995 (id `doi:10.1109/iccc68654.2025.11437995`; retrieved from semantic_scholar; 0 citations per semantic_scholar)
8. Yibo Liang, Kaixin Wu, Shiying He et al.. **Closed-loop medical knowledge graph question answering with adaptive planning and consistency verification**. _International Conference on Generative Artificial Intelligence and Image Processing_, 2026. <https://www.semanticscholar.org/paper/65621acebd70acfff5b55019775f68234da41e4a> doi:10.1117/12.3120384 (id `doi:10.1117/12.3120384`; retrieved from semantic_scholar; 0 citations per semantic_scholar)
9. Sérgio S. Mucciaccia, Thiago M. Paixão, Filipe Mutz et al.. **Pt-HotpotQA: Evaluating Multi-Hop Question Answering on Original and Portuguese-translated Datasets Using LLMs**. _Journal of the Brazilian Computer Society_, 2025. <https://doi.org/10.5753/jbcs.2025.5801> (id `doi:10.5753/jbcs.2025.5801`; retrieved from crossref, semantic_scholar; 8 citations per crossref)
10. Zhuangdi Zhu, Kaixiang Lin, Anil Kumar Jain et al.. **Transfer Learning in Deep Reinforcement Learning: A Survey**. _IEEE Transactions on Pattern Analysis and Machine Intelligence_, 2023. <https://doi.org/10.1109/tpami.2023.3292075> (id `doi:10.1109/tpami.2023.3292075`; retrieved from openalex; 735 citations per openalex)
11. Xiujun Zhou, Pingjian Zhang, Deyou Tang. **PGDA-KGQA: A Prompt-Guided Generative Framework with Multiple Data Augmentation Strategies for Knowledge Graph Question Answering**. _arXiv (preprint)_, 2025. <https://arxiv.org/abs/2506.09414> (id `arxiv:2506.09414`; retrieved from arxiv)
12. Zhilin Yang, Peng Qi, Saizheng Zhang et al.. **HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering**. _Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing_, 2018. <https://doi.org/10.18653/v1/d18-1259> (id `doi:10.18653/v1/d18-1259`; retrieved from crossref, openalex, semantic_scholar; 1018 citations per crossref)
13. Pranoy Panda, Ankush Agarwal, Chaitanya Devaguptapu et al.. **HOLMES: Hyper-Relational Knowledge Graphs for Multi-hop Question Answering using LLMs**. _Annual Meeting of the Association for Computational Linguistics_, 2024. <https://www.semanticscholar.org/paper/aae6991b9ebdc53523931a0115c8b51bd5e4cc94> doi:10.48550/arxiv.2406.06027 (id `arxiv:2406.06027`; retrieved from semantic_scholar; 42 citations per semantic_scholar)
14. Andre Bacellar. **Regime-Conditional Retrieval: Theory and a Transferable Router for Two-Hop QA**. _arXiv (preprint)_, 2026. <https://arxiv.org/abs/2604.09019> (id `arxiv:2604.09019`; retrieved from arxiv)
15. Kosuke Nishida, Kyosuke Nishida, Masaaki Nagata et al.. **Answering while Summarizing: Multi-task Learning for Multi-hop QA with Evidence Extraction**. 2019. <https://doi.org/10.18653/v1/p19-1225> (id `doi:10.18653/v1/p19-1225`; retrieved from openalex; 97 citations per openalex)

<details><summary>Other retrieved papers (not cited in this report)</summary>

- Harnessing Large Language Models for Knowledge Graph Question Answering via Adaptive Multi-Aspect Retrieval-Augmentation (2025) <https://www.semanticscholar.org/paper/2bbcf9638bb779d4ca2bff3b4fbf52ffc9225c83> `doi:10.1609/aaai.v39i24.34747`
- Exploiting Verification Asymmetry for Failure-Aware Graph Reasoning in Knowledge Graph Question Answering with LLMs (2026) <https://www.semanticscholar.org/paper/f11e3be5357db98636628b5210c2dd49b9c9ff42> `doi:10.3390/sym18081340`
- Analyzing the Effectiveness of the Underlying Reasoning Tasks in Multi-hop Question Answering (2023) <https://arxiv.org/abs/2302.05963> `arxiv:2302.05963`
- The Answer Path and the Grounding Instruction in LLM Question Answering over Knowledge Graphs (2026) <https://arxiv.org/abs/2609.10237> `arxiv:2609.10237`
- Subgraph retrieval and link scoring model for multi-hop question answering in knowledge graphs (2025) <https://doi.org/10.1007/s10489-024-05935-8> `doi:10.1007/s10489-024-05935-8`
- SG-RAG MOT: SubGraph Retrieval Augmented Generation with Merging and Ordering Triplets for Knowledge Graph Multi-hop Question Answering (2025) <https://doi.org/10.20944/preprints202505.1992.v1> `doi:10.20944/preprints202505.1992.v1`
- PRISM: Agentic Retrieval with LLMs for Multi-Hop Question Answering (2025) <https://www.semanticscholar.org/paper/cb882a8440581ee70d1d5006bd6e64dbd19919ec> `arxiv:2510.14278`
- Co-Evolving Graph and Text Memory for Training-Free Multi-Hop Question Answering (2026) <https://arxiv.org/abs/2607.23278> `arxiv:2607.23278`
- Commonsense for Generative Multi-Hop Question Answering Tasks (2018) <https://doi.org/10.18653/v1/d18-1454> `doi:10.18653/v1/d18-1454`
- Open-domain Factoid Question Answering via Knowledge Graph Search (2016) <https://doi.org/10.18653/v1/w16-0104> `doi:10.18653/v1/w16-0104`
- Retrieval-enhanced Knowledge Editing in Language Models for Multi-Hop Question Answering (2024) <https://www.semanticscholar.org/paper/d24013cc145edc491504c9a39bf9cc3af275a99e> `arxiv:2403.19631`
- KG-CQR: Leveraging Structured Relation Representations in Knowledge Graphs for Contextual Query Retrieval (2025) <https://arxiv.org/abs/2508.20417> `arxiv:2508.20417`
- Subgraph-Based Attention Network for Multi-Hop Question Answering (2024) <https://doi.org/10.1109/ijcnn60899.2024.10650851> `doi:10.1109/ijcnn60899.2024.10650851`
- Multi-hop Question Answering (2024) <https://doi.org/10.1561/9781638283751> `doi:10.1561/9781638283751`
- Improving Multi-hop Question Answering over Knowledge Graphs using Knowledge Base Embeddings (2020) <https://doi.org/10.18653/v1/2020.acl-main.412> `doi:10.18653/v1/2020.acl-main.412`
- Constructing A Multi-hop QA Dataset for Comprehensive Evaluation of Reasoning Steps (2020) <https://doi.org/10.18653/v1/2020.coling-main.580> `doi:10.18653/v1/2020.coling-main.580`
- Scalable Multi-Hop Relational Reasoning for Knowledge-Aware Question Answering (2020) <https://doi.org/10.18653/v1/2020.emnlp-main.99> `doi:10.18653/v1/2020.emnlp-main.99`
- HybridQA: A Dataset of Multi-Hop Question Answering over Tabular and Textual Data (2020) <https://doi.org/10.18653/v1/2020.findings-emnlp.91> `doi:10.18653/v1/2020.findings-emnlp.91`
- Generate-then-Ground in Retrieval-Augmented Generation for Multi-hop Question Answering (2024) <https://doi.org/10.18653/v1/2024.acl-long.397> `doi:10.18653/v1/2024.acl-long.397`
- End-to-End Beam Retrieval for Multi-Hop Question Answering (2024) <https://doi.org/10.18653/v1/2024.naacl-long.96> `doi:10.18653/v1/2024.naacl-long.96`
- Tackling Distractor Documents in Multi-Hop QA with Reinforcement and Curriculum Learning (2026) <https://doi.org/10.18653/v1/2026.findings-eacl.294> `doi:10.18653/v1/2026.findings-eacl.294`
- Uav Path Selection in Multi-Hop Cooperative Non-Terresrtial-Netwotk:A Deep Reinforcement Learning Approach (2024) <https://doi.org/10.2139/ssrn.4896376> `doi:10.2139/ssrn.4896376`
- Multi-path reasoning for Multi-hop Question Answering over Knowledge Graphs (2022) <https://doi.org/10.22541/au.165426315.58267165/v1> `doi:10.22541/au.165426315.58267165/v1`
- SG-RAG: Multi-Hop Question Answering With Large Language Models Through Knowledge Graphs (2024) <https://www.semanticscholar.org/paper/ddf9c2aab6fafeeeca3dce50e2f25a3ba8c30435> `s2:ddf9c2aab6fafeeeca3dce50e2f25a3ba8c30435`
- Knowledge-Graph Paths as Intermediate Supervision for Self-Evolving Search Agents (2026) <https://arxiv.org/abs/2605.05702> `arxiv:2605.05702`
- Interleaving Retrieval with Chain-of-Thought Reasoning for Knowledge-Intensive Multi-Step Questions (2023) <https://doi.org/10.18653/v1/2023.acl-long.557> `doi:10.18653/v1/2023.acl-long.557`
- StepChain GraphRAG: Reasoning Over Knowledge Graphs for Multi-Hop Question Answering (2025) <https://arxiv.org/abs/2510.02827> `arxiv:2510.02827`
- Retrieving Minimal and Sufficient Reasoning Subgraphs with Graph Foundation Models for Path-aware GraphRAG (2026) <https://arxiv.org/abs/2603.07179> `arxiv:2603.07179`
- Single and Multi-Hop Question-Answering Datasets for Reticular Chemistry with GPT-4-Turbo (n.d.) <https://doi.org/10.1021/acs.jctc.4c00805.s001> `doi:10.1021/acs.jctc.4c00805.s001`
- Knowledge Graph Multi-Hop Question Answering Based on Dependent Syntactic Semantic Augmented Graph Networks (2024) <https://doi.org/10.3390/electronics13081436> `doi:10.3390/electronics13081436`
- Improving Multi-hop Knowledge Base Question Answering by Learning Intermediate Supervision Signals (2021) <https://doi.org/10.1145/3437963.3441753> `arxiv:2101.03737`
- Counterfactual-Augmented Data for Multi-Hop Knowledge Base Question Answering (2021) <https://doi.org/10.1145/3442442.3453706> `doi:10.1145/3442442.3453706`
- Logic-Guided Data Augmentation and Regularization for Consistent Question Answering (2020) <https://doi.org/10.18653/v1/2020.acl-main.499> `doi:10.18653/v1/2020.acl-main.499`
- Vision-language models for medical report generation and visual question answering: a review (2024) <https://doi.org/10.3389/frai.2024.1430984> `arxiv:2403.02469`
- Question-Answering enhanced by Knowledge Graphs (2024) <https://doi.org/10.59350/3ar10-pfb19> `doi:10.59350/3ar10-pfb19`
- Unrestricted multi-hop reasoning network for interpretable question answering over knowledge graph (2022) <https://doi.org/10.1016/j.knosys.2022.108515> `doi:10.1016/j.knosys.2022.108515`
- LAMRF: Logic-adaptive multi-source reasoning fusion for multi-hop knowledge graph question answering (2026) <https://doi.org/10.1016/j.knosys.2026.115902> `doi:10.1016/j.knosys.2026.115902`
- Multi-hop Question Answering with Knowledge Graph Embedding in a Similar Semantic Space (2022) <https://doi.org/10.1109/ijcnn55064.2022.9892550> `doi:10.1109/ijcnn55064.2022.9892550`
- Knowledge Graph Based Retrieval-Augmented Generation for Multi-Hop Question Answering Enhancement (2024) <https://doi.org/10.1109/ikt65497.2024.10892619> `doi:10.1109/ikt65497.2024.10892619`
- Training Question Answering Models From Synthetic Data (2020) <https://doi.org/10.18653/v1/2020.emnlp-main.468> `arxiv:2002.09599`
- MFORT-QA: Multi-hop Few-shot Open Rich Table Question Answering (2024) <https://arxiv.org/abs/2403.19116> `arxiv:2403.19116`
- TTQA-RS- A break-down prompting approach for Multi-hop Table-Text Question Answering with Reasoning and Summarization (2024) <https://arxiv.org/abs/2406.14732> `arxiv:2406.14732`
- VLMT: Vision-Language Multimodal Transformer for Multimodal Multi-hop Question Answering (2025) <https://arxiv.org/abs/2504.08269> `arxiv:2504.08269`
- FrugalRAG: Less is More in RL Finetuning for Multi-Hop Question Answering (2025) <https://arxiv.org/abs/2507.07634> `arxiv:2507.07634`
- StepGap: A Hybrid NLI-LLM Checker for Step-Level Evidence-Gap Detectionin Multi-Hop Question Answering (2026) <https://arxiv.org/abs/2605.24733> `arxiv:2605.24733`
- Discernment and Social Learning as a Companion Training Layer (2022) <http://arxiv.org/abs/2203.02155> `arxiv:2203.02155`
- Memory Augmented Sequential Paragraph Retrieval for Multi-hop Question Answering (2021) <https://arxiv.org/abs/2102.03741> `arxiv:2102.03741`
- DualRAG: A Dual-Process Approach to Integrate Reasoning and Retrieval for Multi-Hop Question Answering (2025) <https://www.semanticscholar.org/paper/a1c2e27b15388be62e36ec8fcfa960ad99c1c324> `arxiv:2504.18243`
- Overview of the MedHopQA track at BioCreative IX: track description, participation and evaluation of systems for multi-hop medical question answering (2026) <https://arxiv.org/abs/2605.12313> `arxiv:2605.12313`
- Comparative Study of Bert Models and Roberta in Transformer based Question Answering (2023) <https://doi.org/10.1109/conit59222.2023.10205622> `doi:10.1109/conit59222.2023.10205622`
- Single- and Multi-Hop BERT Question Classifier for Open-Domain Question Answering (SiMQC) (2023) <https://doi.org/10.1109/icee59167.2023.10334827> `doi:10.1109/icee59167.2023.10334827`
- Hierarchical Graph Network for Multi-hop Question Answering (2020) <https://doi.org/10.18653/v1/2020.emnlp-main.710> `doi:10.18653/v1/2020.emnlp-main.710`
- Structured Knowledge for Multi-hop QA: A Comparative Study of GraphRAG and RAG (2025) <https://doi.org/10.21203/rs.3.rs-8283065/v1> `doi:10.21203/rs.3.rs-8283065/v1`
- Construction of Knowledge Graphs: Current State and Challenges (2024) <https://doi.org/10.3390/info15080509> `doi:10.3390/info15080509`
- Construction of engineering ontologies for knowledge sharing and reuse (1997) <https://doi.org/10.3990/1.9789036509886> `doi:10.3990/1.9789036509886`
- Single Sequence Prediction over Reasoning Graphs for Multi-hop QA (2023) <https://arxiv.org/abs/2307.00335> `arxiv:2307.00335`
- Mitigating Lost-in-Retrieval Problems in Retrieval Augmented Multi-Hop Question Answering (2025) <https://www.semanticscholar.org/paper/481c5e007c42b3194701aa81d81ba0f06aa3bfcf> `arxiv:2502.14245`
- How Well Do Multi-hop Reading Comprehension Models Understand Date Information? (2022) <https://arxiv.org/abs/2210.05208> `arxiv:2210.05208`
- Unsupervised Question Decomposition for Question Answering (2020) <https://doi.org/10.18653/v1/2020.emnlp-main.713> `arxiv:2002.09758`
- Unsupervised Commonsense Question Answering with Self-Talk (2020) <https://doi.org/10.18653/v1/2020.emnlp-main.373> `arxiv:2004.05483`
- A Simple Yet Strong Pipeline for HotpotQA (2020) <https://arxiv.org/abs/2004.06753> `arxiv:2004.06753`
- Multi-hop clustering for reasoning chain extraction in multi-hop question answering (2026) <https://doi.org/10.1007/s10618-026-01203-0> `doi:10.1007/s10618-026-01203-0`
- Retrieval Augmentation Reduces Hallucination in Conversation (2021) <https://doi.org/10.18653/v1/2021.findings-emnlp.320> `doi:10.18653/v1/2021.findings-emnlp.320`
- MAFQA: A Dataset for Benchmarking Multi-Hop Arabic Fatwa Question Answering (2026) <https://doi.org/10.3390/data11030064> `doi:10.3390/data11030064`
- Cognitive Graph for Multi-Hop Reading Comprehension at Scale (2019) <http://arxiv.org/abs/1905.05460> `arxiv:1905.05460`
- MedResearcher-R1: Expert-Level Medical Deep Researcher via A Knowledge-Informed Trajectory Synthesis Framework (2025) <https://arxiv.org/abs/2508.14880> `arxiv:2508.14880`
- Multi-Hop Financial Knowledge Question-Answering Model Based on Knowledge Graph (2024) <https://doi.org/10.1109/icaice63571.2024.10864319> `doi:10.1109/icaice63571.2024.10864319`
- Multi-hop Attention GNN with Answer-Evidence Contrastive Loss for Multi-hop QA (2023) <https://doi.org/10.1109/ijcnn54540.2023.10191117> `doi:10.1109/ijcnn54540.2023.10191117`
- Complex Knowledge Base Question Answering: A Survey (2022) <https://doi.org/10.1109/tkde.2022.3223858> `doi:10.1109/tkde.2022.3223858`
- Deep Learning applications for COVID-19 (2021) <https://doi.org/10.1186/s40537-020-00392-9> `doi:10.1186/s40537-020-00392-9`
- CoralX.AI: Multi-Hop, Redundancy-Aware Scientific QA via Hybrid Semantic-Graph Retrieval and RAG (2025) <https://doi.org/10.31274/cc-20251215-154> `doi:10.31274/cc-20251215-154`
- An Effective Method to Answer Multi-hop Questions by Single-hop QA System (2022) <https://doi.org/10.5220/0010824200003116> `doi:10.5220/0010824200003116`
- Prioritized repairing and consistent query answering in relational databases (2012) <https://doi.org/10.1007/s10472-012-9288-8> `doi:10.1007/s10472-012-9288-8`
- Vendi-RAG: Adaptively Trading-Off Diversity And Quality Significantly Improves Retrieval Augmented Generation With LLMs (2025) <https://arxiv.org/abs/2502.11228> `arxiv:2502.11228`
- A State-transition Framework to Answer Complex Questions over Knowledge Base (2018) <https://doi.org/10.18653/v1/d18-1234> `doi:10.18653/v1/d18-1234`
- Information Extraction over Structured Data: Question Answering with Freebase (2014) <https://doi.org/10.3115/v1/p14-1090> `doi:10.3115/v1/p14-1090`
- UNIFIEDQA: Crossing Format Boundaries with a Single QA System (2020) <https://doi.org/10.18653/v1/2020.findings-emnlp.171> `arxiv:2005.00700`
- TinyBERT: Distilling BERT for Natural Language Understanding (2020) <https://doi.org/10.18653/v1/2020.findings-emnlp.372> `doi:10.18653/v1/2020.findings-emnlp.372`
- Figure 12: Comparison of exact match of MRC using proposed ExtGPT-QA over SQuAD 1.0 dataset. (n.d.) <https://doi.org/10.7717/peerjcs.1422/fig-12> `doi:10.7717/peerjcs.1422/fig-12`
- Figure 14: Comparison of exact match of MRC using proposed ExtGPT-QA over SQuAD 2.0 dataset. (n.d.) <https://doi.org/10.7717/peerjcs.1422/fig-14> `doi:10.7717/peerjcs.1422/fig-14`
- Figure 16: Comparison of exact match of MRC using proposed ExtGPT-QA over Wiki-QA dataset. (n.d.) <https://doi.org/10.7717/peerjcs.1422/fig-16> `doi:10.7717/peerjcs.1422/fig-16`
- Figure 18: Comparison of exact match of MRC using proposed ExtGPT-QA over News-QA dataset. (n.d.) <https://doi.org/10.7717/peerjcs.1422/fig-18> `doi:10.7717/peerjcs.1422/fig-18`
- Evaluating question answering over linked data (2013) <https://doi.org/10.1016/j.websem.2013.05.006> `doi:10.1016/j.websem.2013.05.006`
- Decomposing Complex Questions Makes Multi-Hop QA Easier and More Interpretable (2021) <https://doi.org/10.18653/v1/2021.findings-emnlp.17> `doi:10.18653/v1/2021.findings-emnlp.17`
- Graph Neural Networks: A Review of Methods and Applications (2018) <http://arxiv.org/abs/1812.08434> `arxiv:1812.08434`
- Adversarial Attacks and Defenses in Images, Graphs and Text: A Review (2020) <https://doi.org/10.1007/s11633-019-1211-x> `arxiv:1909.08072`
- Systematic methodological review: developing a framework for a qualitative semi‐structured interview guide (2016) <https://doi.org/10.1111/jan.13031> `doi:10.1111/jan.13031`
- A graph-based system for network-vulnerability analysis (1998) <https://doi.org/10.1145/310889.310919> `doi:10.1145/310889.310919`

</details>

## Appendix A. Evidence Ledger

### [Evidence] claims (3)

- **[Evidence]** S-Path-RAG uses an iterative Neural-Socratic Graph Dialogue loop where the language model produces concise diagnostic messages that are mapped to targeted graph edits or seed expansions, enabling adaptive retrieval when the model expresses uncertainty. _(claim C004, confidence: high)_
  - [5], abstract (direct support, verified) "The system runs inside an iterative Neural-Socratic Graph Dialogue loop in which concise diagnostic messages produced by the language model are mapped to targeted graph edits or seed expansions, enabling adaptive retrieval when the model expresses uncertainty."
- **[Evidence]** RAKR framework integrates a dual-layer reflection loop mechanism: open-ended reflection before generation for immediate iterative optimization, and closed-loop reflection after generation for constructing long-term memory used for subsequent question retrieval, enabling continuous optimization of knowledge rewriting strategies through feedback from historical interactions. _(claim C005, confidence: high)_
  - [7], abstract (direct support, verified) "RAKR achieves dynamic semantic transformation of subgraphs in knowledge graphs by introducing an intelligent agent capable of performing precise reasoning planning, relationship exploration, and knowledge organization. The innovation of RAKR lies in its dual-layer reflection loop mechanism: the open-ended reflection before generation for immediate iterative optimization, and the closed-loop reflection after generation for constructing long-term memory used for subsequent question retrieval."
- **[Evidence]** The closed-loop medical KGQA framework uses backward consistency verification to decide whether a branch should be accepted, locally revised, or rolled back, by recording explored branches, unresolved conditions, conflicts, and explanation evidence in a unified memory and applying backward checking. _(claim C006, confidence: high)_
  - [8], abstract (direct support, verified) "We propose a closed-loop framework for medical KGQA that combines subgoal decomposition, adaptive graph planning, unified memory, and backward consistency verification. A question is decomposed into disease, symptom, examination, treatment, and contraindication subgoals. During search, candidate expansions are ranked by relation relevance, newly covered subgoals, historical usefulness, conflict risk, and path length. The system records explored branches, unresolved conditions, conflicts, and explanation evidence in a unified memory, and uses backward checking to decide whether a branch should be accepted, locally revised, or rolled back."

### [Inference] claims (4)

- **[Inference]** The closest existing work to our idea is subgraph retrieval methods for multi-hop KGQA (e.g., the Subgraph Retrieval Enhanced Model from arxiv:2202.13296) that retrieve subgraphs at inference time to aid reasoning, whereas our idea proposes enriching training triples with local context subgraphs from the same source passage and adding an adaptive repair loop for iterative refinement. _(claim C001, confidence: medium)_
  - [1], abstract (indirect support, verified) "Subgraph Retrieval Enhanced Model for Multi-hop Knowledge Base Question Answering"
- **[Inference]** A main technical risk is that the local context subgraph may introduce noise or irrelevant triples, potentially degrading performance, and determining the optimal size of the context subgraph is non-trivial, as highlighted by challenges of context overload in iterative RAG methods (e.g., arxiv:2407.13101). _(claim C002, confidence: medium)_
  - [4], abstract (indirect support, unverified)
- **[Inference]** A main experimental confounder is that observed improvements might be due to increased training data size from the added context triples rather than the contextual enrichment itself, as shown by data augmentation techniques in KGQA (e.g., arxiv:2506.09414) that improve performance by addressing scarcity of annotated data. _(claim C003, confidence: medium)_
  - [11], abstract (indirect support, verified) "Recent methods utilizing large language models (LLMs) have shown remarkable semantic parsing capabilities but are limited by the scarcity of diverse annotated data and multi-hop reasoning samples."
- **[Inference]** The closest existing work to our idea is subgraph retrieval methods for multi-hop KGQA (e.g., arxiv:2202.13296) that retrieve subgraphs at inference time to aid reasoning, whereas our idea proposes enriching training triples with local context subgraphs from the same source passage and adding an adaptive repair loop for iterative refinement. _(claim C007, confidence: medium)_
  - [1], abstract (indirect support, verified) "Subgraph Retrieval Enhanced Model for Multi-hop Knowledge Base Question Answering"

## Appendix B. Search Log

| Query | Sources (status: results) | Papers |
|---|---|---|
| multi-hop question answering context subgraph training | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 15 |
| multi-hop question answering datasets HotpotQA 2WikiMultiHopQA | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 14 |
| adaptive repair loop knowledge graph question answering | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 12 |
| reinforcement learning multi-hop QA transfer lower hop | arxiv (ok: 0), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 10 |
| subgraph size multi-hop question answering context | arxiv (ok: 2), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 17 |
| HotpotQA 2WikiMultiHopQA multi-hop QA datasets | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 14 |
| Exact Match F1 multi-hop QA | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 15 |
| BERT RoBERTa multi-hop question answering | arxiv (ok: 1), openalex (ok: 5), semantic_scholar (ok: 5), crossref (ok: 5) | 15 |
| data augmentation multi-hop question answering | arxiv (ok: 5), openalex (ok: 5), semantic_scholar (error: 0), crossref (ok: 5) | 15 |
| detecting one-hop failures knowledge graph question answering | arxiv (ok: 0), openalex (ok: 10), semantic_scholar (error: 0), crossref (ok: 10) | 17 |

## Appendix C. Investigation Log

Each step was chosen by the ResearchForge controller from the recorded research state.

| Step | Phase | Action | Why | Alternatives considered | Outcome | Information gain |
|---|---|---|---|---|---|---|
| 0 | INTAKE | INTAKE | Research idea received. | none | idea stored in the workspace | n/a |
| 1 | FORMALIZE | FORMALIZE | The idea has not been formalized into a testable research question. | none | +76 papers; +8 searches; +3 uncertainties; idea formalized | 3 |
| 2 | PLAN | PLAN | No investigation plan exists yet, so it is unclear what must be determined. | none | +2 uncertainties; investigation plan recorded | 1 |
| 3 | INVESTIGATE | READ | Retrieved papers have not been analyzed enough to judge overlap. | none | +8 analyses; runtime note: phase exceeded 900.0s and was stopped | 4 |
| 4 | SYNTHESIZE | SYNTHESIZE | Analyses exist but the field has not been mapped. | none | landscape recorded | 1 |
| 5 | CRITIQUE | CRITIQUE | The idea has not been challenged yet. | none | +13 papers; +1 searches; +3 claims; +2 verified claims; critique recorded | 5 |
| 6 | UNCERTAINTY | SEARCH (U002: How should one-hop failures be detected to trigger the adaptive repair loo) | Most valuable next step for high-importance validity question U002: score 1.62 = importance 3 x expected gain 0.6 x relevance 0.9 x evidence deficiency 1 / cost 1. Next best: CHALLENGE on U006 (1.4). | CHALLENGE U006 (1.4); SEARCH U005 (0.648) | +14 papers; +1 searches; +3 claims; +3 verified claims; +1 resolved uncertainties; uncertainties updated: U002 | 7 |
| 7 | CRITIQUE | CRITIQUE | 14 papers arrived since the last critique. | none | +1 claims; +1 verified claims; critique recorded | 2 |
| 8 | REFINE | REFINE | The findings have not yet been turned into gaps, modifications and a direction decision. | none | +4 gaps; +3 modifications; +1 directions | 1 |
| 9 | EXPERIMENT_PLAN | PLAN_EXPERIMENT | A research direction exists but no experiment would test it. | none | +1 experiment plans | 1 |
| 10 | FINALIZE | FINALIZE | Stopping: time budget reached (2700 s). | none | finalizing | n/a |
