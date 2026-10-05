# Literature review: autonomous research-idea investigation

Status: working draft, 2026-09-29. This is the review behind the paper plan in [research_plan.md](research_plan.md). Papers are cited by arXiv id. Full details are in [References](#references) and [references.bib](references.bib).

## 1. Scope and method

**Question.** What is known about LLM agents that take a research idea and investigate it against the literature? Such an agent retrieves prior work, judges novelty and gaps, critiques the idea and proposes changes. Where does evidence about these agents stop?

**Search.** Web search (2026-09-28/29) in three rounds:
1. **Clusters.** End-to-end AI-scientist systems; evaluations of those systems; ideation and idea evaluation; novelty-judgement benchmarks; literature synthesis and citation grounding; falsification and confirmation bias; search control and stopping in deep-research agents.
2. **Snowballing.** Follow-ups to Kosmos, evaluations of it, and the AI-scientist audits.
3. **Gap validation.** Searches aimed at each candidate gap. Examples: "benchmark agent detect idea already published", "novelty assessment retrieval recall of closest prior work", "self-falsification of novelty claims", "temporal holdout", "abstract metadata errors in OpenAlex/Semantic Scholar", "uncertainty-driven vs fixed pipeline", "open-weight deep research".

**Verification.** Every paper was resolved through the Semantic Scholar batch API by arXiv id. Its title was compared with the id, and its abstract was read. One search hit, 2609.32616, did not resolve and was dropped. Nothing here is cited from memory.

**Corpus.** 81 papers: 3 from 2023, 7 from 2024, 20 from 2025 and 51 from 2026.

**Limitations of this review.**
- **Abstracts only.** Statements about a paper come from its abstract. When a matrix cell says "not reported", the capability does not appear in the abstract. The system may still have it, and the full text must be checked before the paper is written (§7).
- **Mostly preprints.** Most 2026 entries are unrefereed arXiv preprints.
- **Coverage.** The search is arXiv-centred and CS-centred. Biomedical hypothesis generation is covered only through BioDisco and Kosmos.

## 2. Taxonomy of prior work

### 2.1 End-to-end AI-scientist systems

These systems go from an idea to experiments to a paper:
- AI Scientist [2408.06292] and AI Scientist-v2 [2504.08066];
- Agent Laboratory [2501.04227] and AgentRxiv [2503.18102];
- Co-Scientist [2502.18864];
- Kosmos [2511.02824];
- Jr. AI Scientist [2511.04583];
- AutoSOTA [2604.05550];
- Sibyl [2605.22343];
- NAIS [2607.11084];
- SCION [2607.03863];
- the interactive "Deep Research" system [2601.12542];
- pAI/MSc [2604.20622].

The literature step in these systems is a means to an end: the systems are judged by the papers or discoveries they produce.

Two design ideas recur, and ResearchForge shares both:
- **A persistent structured state.** Kosmos has a "structured world model"; [2601.12542] has a "persistent world state"; SCION uses "Research Execution Plan[s]" with "verification checkpoints".
- **Traceable claims.** Kosmos "cites all statements in its reports with code or primary literature".

Independent evaluation of these systems is sobering:
- Beel et al. [2502.14297] found the AI Scientist's literature review "relying on simplistic keyword searches … which leads to poor novelty assessments". In their words, "several generated research ideas were incorrectly classified as novel, including well-established concepts such as micro-batching for stochastic gradient descent".
- In radiation biology, Kosmos produced "one well-supported discovery, one plausible but uncertain result, and one false hypothesis" [2511.13825].
- A survey of 24 runnable systems found that only "38 percent report any novelty-verification method" [2608.05179].

### 2.2 Process-level evaluations of research agents

**AutoResearchEval / ARFT [2608.14905].**
- Scale: 100 tasks, 800 trajectories and 45 failure patterns.
- Main finding: current agents "lack a metacognitive loop, which entails the ability to check what they produced against what they found, revise when it does not hold up, and question whether the path they took was sound."
- The authors place the deficit "at the model level rather than in any particular scaffold". They leave open "whether orchestration-level interventions can close it".

**Other process-level evaluations.**
- ARAC-Bench [2608.12788] scores alignment of the research process with human practice.
- "Beyond Final Scores" [2608.13417] characterises within-run "Feedback Control".
- "Correct Answer, Wrong Mechanism" [2606.23175] argues that "outcome-only evaluation is insufficient".
- PaperRecon [2604.01128] measures hallucination in AI-written papers.
- SDE [2512.15567] evaluates project-level discovery.

### 2.3 Idea generation

These are generators that use literature:
- SciMON [2305.14259];
- ResearchAgent [2404.07738];
- Scideator [2409.14634];
- Chain of Ideas [2410.13185];
- ResearchStudio-Idea [2607.04439];
- BioDisco [2508.01285].

They improve ideas with review feedback or novelty loops. For example, SciMON iterates "until sufficient novelty is achieved".

Human studies bound what such generators achieve:
- **Ideation.** LLM ideas were judged "more novel (p<0.05) than human expert ideas" [2409.04109].
- **Execution.** After execution, however, their scores "decrease significantly more than expert-written ideas" [2506.20803].

AgentIdeaBench [2609.07611] compares static observation with active exploration. Active exploration improves "feasibility, clarity, and specificity while leaving measured originality unchanged". ResearchStudio-Idea includes "Scoop-Check, a standalone prior-art collision checker for novelty claims" and "retrieves potentially conflicting prior work".

### 2.4 Idea and novelty *assessment*

This is the closest area to ResearchForge.

**Benchmarks of novelty judgement.**
- **RINoBench** [2603.10303]: 1,381 ideas. LLM "reasoning closely mirrors human rationales" but judgements "diverge significantly" from gold labels.
- **NovBench** [2604.11543]: 1,684 paper–review pairs.
- **NovGauge** [2609.11234]: per-dimension labels. Over 70% of correct positive judgements cite evidence that "fails to logically support the stated reason".
- **RQ-Bench** [2606.12071]: a "novelty mirage", in which LLM judges rate generated research questions as novel and experts disagree.
- **Think-Probe-Respond** [2608.25660]: a "medium novel" bias.
- **Style Wins, Substance Loses** [2608.01666]: judges are swayed by writing style.
- **Ideation Arena** [2608.29696]: the best LLM judge reaches 72.56% soft accuracy against expert preferences.
- **LigBench** [2608.13136].
- **Lit2Test** [2608.22948]: proposals must "precommit the observation that would prove it wrong".
- **Outcome prediction** [2506.00794]: predicts which of two ideas performs better.

**Systems that assess novelty.**
- Idea Novelty Checker [2506.22026]: "retrieve-then-rerank".
- ScholarEval [2510.16234]: soundness and contribution grounded in the literature.
- InnoEval [2602.14367]: a multi-perspective review board.
- MemoNoveltyAgent [2603.20884]: memory-aware, with "a self-validation mechanism".
- OpenNovelty [2601.01576]: a four-phase pipeline "with explicit citations and evidence snippets".
- NoveltyRank [2512.14738]: a trained classifier.
- Ideation Space [2601.08901]: decomposed retrieval, with Recall@30 of 0.329.
- Novelty-Aware Agentic Retrieval [2606.22151]: a problem × method gap matrix, with "gap precision of 0.600".

**Temporal and forward-looking evaluation.**
- **ForeSci** [2606.00644]: hides post-cutoff papers and finds "evidence-decision decoupling": agents "cite relevant evidence while forecasting the wrong research object".
- **Reconstruction** [2608.16645]: recovers a paper's idea from its pre-publication bibliography under "a strict anti-leakage protocol".
- **BioDisco** [2508.01285]: uses "temporal evaluation".

### 2.5 Literature synthesis, citation and claim integrity

**Synthesis.** PaperQA2 [2409.13740] and OpenScholar [2411.14199] give strong cited synthesis and contradiction detection. ALCE [2305.14627] set up citation evaluation.

**Citation integrity.**
- 3–13% of citation URLs are hallucinated [2604.03173].
- BibTeX entries are "fully correct" only 50.9% of the time [2604.03159].
- HALLMARK [2607.18360] benchmarks citation verifiers.
- [2608.24306] localises citation errors to individual agents. 84.7% of final-report errors in one system originate at the orchestrator.

**Claim-level auditability.** [2602.13855] proposes "provenance coverage, provenance soundness, contradiction transparency, and audit effort" as measurable targets, as a perspective paper. EviBound [2511.05524] gates claims about *experiments* on machine-checkable artefacts.

**Source integrity.**
- An audit of 10,000 OpenAlex abstracts found "12% of abstracts have integrity issues, with insufficient content and misplaced metadata being the most prevalent" [2605.20168].
- MisKnow-Agent [2607.20891] shows that injecting one misleading document raises the false-conclusion adoption rate of deep-research agents from 0% to 54.7%. The authors call for "continuous verification when evidence enters intermediate research states".

### 2.6 Falsification, confirmation bias and belief revision

- **POPPER** [2502.09858] validates hypotheses through sequential falsification *experiments* with Type-I error control.
- **Adversarial experiments** [2604.22080] argues, as a position, that agentic claims be held to "a falsification-first standard".
- **Confirmation bias** [2604.02485]: LLMs show it, and prompting interventions raise rule discovery "from 42% to 56%".
- **DERELAB** [2608.30413]: models identify "a weakening update yet fail[] to revise their conclusion".

### 2.7 Search control and stopping in deep-research agents

- **Surveys and benchmarks:** [2506.18096]; DeepResearch Bench [2506.11763]; DRACO [2602.11685]; DR³-Eval [2604.14683]; AutoResearchBench [2604.25256] (9.39% accuracy on finding a target paper).
- **Stopping and control:**
  - RAAC [2608.15191] finds "the majority of iterations contribute little or no improvement" and controls actions with "search novelty and information coverage".
  - EDR [2604.24978] "enforces evidence-based completion criteria".
  - DAS [2602.03304] aligns the stop-searching boundary.
  - [2608.01913] finds "search effort and answer quality are only weakly aligned".
- **Uncertainty quantification.** Agent UQ is surveyed in [2602.05073]. Active retrieval dates to FLARE [2305.06983].
- **Contamination.** Search-time contamination can inflate measured performance "by up to 4%" [2606.05241].
- **Open pipelines.** OpenResearcher [2603.20278] offers a fully open offline pipeline.

## 3. Capability matrix

**Legend.**
- ✓ = the capability is stated in the abstract.
- ~ = partially stated.
- · = not reported in the abstract (the capability may still exist).

**Columns.**
- *Assess* = judges a given idea, rather than generating one.
- *Own-conclusion challenge* = searches for literature that contradicts the system's *own* novelty or gap conclusions.
- *Quote-verified evidence* = cited evidence is checked against source text.
- *Source-metadata checks* = detects wrong or mismatched records returned by bibliographic APIs.
- *Adaptive control* = the next step is chosen from the current state, not a fixed sequence.

| System | Assess | Active retrieval | Own-conclusion challenge | Quote-verified evidence | Source-metadata checks | Adaptive control / stopping | Evaluated on |
|---|---|---|---|---|---|---|---|
| AI Scientist v1/v2 [2408.06292, 2504.08066] | ~ (novelty check, judged poor by [2502.14297]) | ✓ | · | · | · | ~ (tree search over experiments) | automated and human review of papers |
| Kosmos [2511.02824] | · | ✓ | · | ~ (statements cite sources) | · | ✓ (world model, cycles) | expert accuracy of statements (79.4%) |
| Idea Novelty Checker [2506.22026] | ✓ | ✓ | · | · | · | · (fixed two-stage) | agreement with experts |
| ScholarEval [2510.16234] | ✓ | ✓ | · | · | · | · | rubric coverage, user study |
| InnoEval [2602.14367] | ✓ | ✓ | · | · | · | · | human alignment |
| OpenNovelty [2601.01576] | ✓ | ✓ | · | ~ (evidence snippets) | · | · (four fixed phases) | deployment on ICLR 2026 submissions |
| MemoNoveltyAgent [2603.20884] | ✓ | ✓ | ~ (self-validation of the report) | · | · | · | checklist evaluation vs Deep Research |
| ResearchStudio-Idea [2607.04439] | ~ | ✓ | ~ (collision retrieval for its own idea) | · | · | · | automated judges |
| AgentIdeaBench agents [2609.07611] | · | ✓ | · | · | · | ✓ (active exploration) | literature-verified critics |
| ForeSci agents [2606.00644] | ✓ (forward judgement) | ✓ | · | · | · | · | post-cutoff validation |
| RAAC [2608.15191] | · | ✓ | · | · | · | ✓ | QA accuracy (BrowseComp-Plus) |
| EviBound [2511.05524] | · | · | · | ✓ (experiment artefacts) | · | ~ (bounded retries) | 8 tasks, hallucinated completion |
| POPPER [2502.09858] | ✓ (hypotheses) | · | ✓ (falsification *experiments*) | · | · | ✓ (sequential testing) | Type-I error and power |
| **ResearchForge (this project)** | ✓ | ✓ | ✓ (CHALLENGE / INVESTIGATE_GAP; verdicts require retrieved contradicting papers) | ✓ (verbatim quote in abstract or full text) | ✓ (cross-source Jaccard, title-name check) | ✓ (uncertainty-scored actions, information-gain stopping, re-critique after contradiction) | nothing yet beyond unit and e2e tests |

The last row is the honest position: ResearchForge combines the capabilities, but it has **no empirical evaluation yet**. Each capability exists somewhere in prior work in some form. The contribution cannot be the capabilities themselves; it has to be what they are shown to do.

## 4. Gaps

Each gap lists the evidence for it and what would show it is not a gap.

### G1. No one has tested whether orchestration-level self-challenge fixes the metacognitive failure in idea assessment

**Evidence.**
- [2608.14905] identifies the missing loop ("check what they produced against what they found, revise when it does not hold up") and explicitly does not test "whether orchestration-level interventions can close it".
- DERELAB [2608.30413] and [2604.02485] show that models fail to revise, or seek confirming evidence. Prompting helps with the latter, but only for a toy rule-discovery task.
- The novelty assessors in the matrix are fixed retrieve→compare→report pipelines. At most they self-validate the report (MemoNoveltyAgent); none reports searching for evidence *against its own verdict*.
- POPPER falsifies through experiments, not through the literature.

**The gap.** A controlled ablation is missing. It would compare a harness that (a) challenges its own novelty/gap conclusions with contradiction-seeking searches and (b) revises its critique after contradicting evidence, against the same model without those steps, on idea assessment with ground truth.

**Would be refuted by** a paper that runs such an ablation. None was found in three search rounds. The full texts of MemoNoveltyAgent, OpenNovelty and ResearchStudio-Idea must still be checked (§7).

### G2. There is no objective ground truth for "this idea is already done"

**Evidence.**
- **Labels are subjective.** Novelty benchmarks rely on human labels [2603.10303, 2604.11543, 2609.11234]. Experts and LLM judges contradict each other [2606.12071], and the authors of [2409.04109] note that "human judgements of novelty can be difficult, even by experts".
- **The failure is documented.** The motivating failure is exactly "well-established concepts … classified as novel" [2502.14297].
- **Existing temporal protocols measure something else.** They exist for forward judgement [2606.00644] and idea recovery [2608.16645], not for prior-art detection.
- **Retrieval benchmarks are not idea-framed.** AutoResearchBench [2604.25256] tests finding a target paper, not whether an agent *concludes* an idea is taken.

**The gap.** Prior-art detection has an objective answer, and nothing measures it. Consider an idea whose realisation was published at a known date. With the literature visible up to today, the right verdict is "already explored", and the realising paper is the evidence. With the literature cut off before that date, the verdict should not be "already explored" because of that paper. This two-condition protocol, with the realising paper and its cited closest prior work as a retrieval target, measures both kinds of error: false "novel" and false "scooped".

**Would be refuted by** an existing benchmark of that design. None was found.

### G3. Nobody knows how corrupted bibliographic metadata spreads into research-agent conclusions

**Evidence.**
- **Corruption is common.** 12% of OpenAlex abstracts have integrity issues, including "misplaced metadata" [2605.20168]. We observed one case ourselves: OpenAlex served the abstract of an unrelated system for H2O (arXiv 2306.14048). See [AGENT_LOOP.md](../AGENT_LOOP.md#source-integrity).
- **Misleading evidence propagates.** Misleading documents drive false conclusions in deep-research agents [2607.20891]. That study injects *adversarial documents*, not metadata corruption from trusted APIs.
- **Checks elsewhere target other artefacts.** Citation verifiers [2607.18360, 2604.03159] check references that an LLM *generated*, not source records an agent *retrieved*.

**The gap.** Two things are unmeasured:
- how often a mismatched abstract ends up as evidence in a novelty or gap conclusion;
- whether cheap ingest-time consistency checks prevent that.

### G4. Budget-aware stopping has not been studied for open-ended assessment

**Evidence.**
- **Stopping work assumes a reference answer.** It targets QA with gold answers [2608.15191, 2602.03304, 2608.01913] or report coverage [2604.24978].
- **Idea assessment has no single answer string.** Its target is a verdict plus the evidence for it.
- **The problem is documented.** [2608.01913] observes "a long tail of low-yield retrieval steps".

**The gap.** Does information-gain-based closure keep verdict quality at lower cost, compared with fixed budgets?

**Caveat.** This is a secondary gap. It is plausible, but a reviewer may see it as an application of known ideas.

### G5. Nobody has measured whether verdicts follow the evidence

**Evidence.**
- ForeSci [2606.00644] reports "evidence-decision decoupling".
- NovGauge [2609.11234] finds that most correct judgements cite evidence that does not support them.

**The gap.** ResearchForge derives its final decision rule-based from the recorded evidence state (`controller.research_decision`), not from free text. Whether this reduces decoupling is untested.

**Caveat.** This is a secondary gap that is testable within the G1/G2 study.

## 5. What is *not* a gap (do not claim)

- **Quote-level grounding of claims** as a concept: Kosmos [2511.02824]; OpenNovelty [2601.01576]; ALCE [2305.14627]; the claim-auditability agenda [2602.13855]; EviBound [2511.05524] for experiment claims.
- **Persistent structured research state or world model:** Kosmos, [2601.12542], SCION, Sibyl.
- **Human approval before experiments:** NAIS [2607.11084], EviBound's approval gate, and Agent Laboratory's human feedback.
- **Literature-grounded novelty assessment in general:** §2.4 lists at least eight systems.
- **Detecting contradictions within the literature:** PaperQA2 [2409.13740].
- **Adaptive control and stopping in deep research:** RAAC, EDR, DAS.
- **An open-weight or open pipeline** is not a contribution by itself: OpenResearcher [2603.20278], OpenScholar [2411.14199].

## 6. Implications for the paper

The defensible paper is an **empirical study with a new evaluation protocol**, not a systems paper.
- **G2 supplies the protocol:** temporal prior-art detection.
- **G1 is the central question:** do orchestration-level self-challenge and revision close the metacognitive gap that [2608.14905] left open?
- **G3 is a robustness axis:** metadata corruption.
- **G4 and G5 are secondary analyses.**

ResearchForge is the instrument. Its switches for each component make the ablations cheap. The design is in [research_plan.md](research_plan.md).

## 7. Before submission: checks this review still owes

1. **Full texts.** Read the full texts of MemoNoveltyAgent, OpenNovelty, ResearchStudio-Idea, ScholarEval, InnoEval and AgentIdeaBench. Confirm that none runs a contradiction search against its own verdict, or an ablation of one (G1).
2. **Prior-art benchmarks.** Re-search just before submission for "prior-art detection" or "scooped idea" benchmarks. This area moved monthly in 2026.
3. **Follow-ups to [2608.14905].** Check whether a follow-up tests orchestration-level interventions.
4. **Venues.** Replace arXiv entries with their published versions where they exist.

## References

81 verified papers. Keys are arXiv ids, and [references.bib](references.bib) has BibTeX for all of them.

- **[2604.20622]** M. Abdelmoneum, Pierfrancesco Beneventano, Tomaso A. Poggio (2026). *pAI/MSc: ML Theory Research with Humans on the Loop*. arXiv:2604.20622. <https://arxiv.org/abs/2604.20622>
- **[2411.14199]** Akari Asai, Jacqueline He, Rulin Shao et al. (2024). *OpenScholar: Synthesizing Scientific Literature with Retrieval-augmented LMs*. arXiv:2411.14199. <https://arxiv.org/abs/2411.14199>
- **[2404.07738]** Jinheon Baek, S. Jauhar, Silviu Cucerzan et al. (2024). *ResearchAgent: Iterative Research Idea Generation over Scientific Literature with Large Language Models*. arXiv:2404.07738. <https://arxiv.org/abs/2404.07738>
- **[2502.14297]** Joeran Beel, Min-Yen Kan, Moritz Baumgart (2025). *Evaluating Sakana's AI Scientist: Bold Claims, Mixed Results, and a Promising Future?*. arXiv:2502.14297. <https://arxiv.org/abs/2502.14297>
- **[2511.05524]** Ruiying Chen (2025). *Evidence-Bound Autonomous Research (EviBound): A Governance Framework for Eliminating False Claims*. arXiv:2511.05524. <https://arxiv.org/abs/2511.05524>
- **[2608.16645]** Shao-Long Chen, Yanlin Fei, Nazhou Liu et al. (2026). *Reconstruction: A Blind Benchmark for Recovering Research Ideas from Pre-Publication Bibliographies*. arXiv:2608.16645. <https://arxiv.org/abs/2608.16645>
- **[2608.29696]** Zhi-Yu Chen, Keyu Zhao, Ji-Gao Fu et al. (2026). *Ideation Arena: Evaluating LLM Generated Research Ideas with Battle-style Human Expert Assessment*. arXiv:2608.29696. <https://arxiv.org/abs/2608.29696>
- **[2604.24978]** Prafulla Kumar Choubey, Kung-Hsiang Huang, P. Venkit et al. (2026). *Dont Stop Early: Scalable Enterprise Deep Research with Controlled Information Flow and Evidence-Aware Termination*. arXiv:2604.24978. <https://arxiv.org/abs/2604.24978>
- **[2608.12788]** Jiale Cui, Yue-Yao Yuan, Kai-Xi Zhong et al. (2026). *ARAC: Benchmarking Auto-Research's Alignment and Completeness on End-to-End Researchs*. arXiv:2608.12788. <https://arxiv.org/abs/2608.12788>
- **[2608.05179]** Tianyu Ding, Aditya Nannapaneni, Bingfan Liu et al. (2026). *Autonomous Research Agents: A Survey of AI Scientists and the Verification Gap*. arXiv:2608.05179. <https://arxiv.org/abs/2608.05179>
- **[2506.11763]** Ming-Xuan Du, Benfeng Xu, Chiwei Zhu et al. (2025). *DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents*. arXiv:2506.11763. <https://arxiv.org/abs/2506.11763>
- **[2606.23175]** S. Eulig (2026). *Position: Correct Answer, Wrong Mechanism - When AI Scientists Defend General Claims Their Own Data Contradicts*. arXiv:2606.23175. <https://arxiv.org/abs/2606.23175>
- **[2604.22080]** Dionizije Fa, Marko Čuljak (2026). *Sound Agentic Science Requires Adversarial Experiments*. arXiv:2604.22080. <https://arxiv.org/abs/2604.22080>
- **[2608.14905]** Yanlin Fei, Nazhou Liu, Xinmiao Yu et al. (2026). *How Do Agents Fail on AutoResearch: End-to-End Diagnostic Evaluation on 100 Real-World Frontier Research Tasks*. arXiv:2608.14905. <https://arxiv.org/abs/2608.14905>
- **[2305.14627]** Tianyu Gao, Howard Yen, Jia-Tong Yu et al. (2023). *Enabling Large Language Models to Generate Text with Citations*. arXiv:2305.14627. <https://arxiv.org/abs/2305.14627>
- **[2609.23735]** ScholarSeed AI Team Caoqinwei Gong, Xue Jiang, Wei Luo et al. (2026). *ScholarStack: Layered Research Asset Orchestration and Cross-Task Reuse for Scientific Agents*. arXiv:2609.23735. <https://arxiv.org/abs/2609.23735>
- **[2502.18864]** Juraj Gottweis, Wei-Hung Weng, A. Daryin et al. (2025). *Accelerating scientific discovery with Co-Scientist*. arXiv:2502.18864. <https://arxiv.org/abs/2502.18864>
- **[2606.22151]** Shoulin Han (2026). *Novelty-Aware Agentic Retrieval: Comparing Research Contributions Through Structured Multi-Step Reasoning*. arXiv:2606.22151. <https://arxiv.org/abs/2606.22151>
- **[2608.24306]** Eran Hirsch, David Wan, Han Wang et al. (2026). *Who is the Agent to Blame? Localizing Faithfulness and Citation Mistakes in Agentic Deep Research*. arXiv:2608.24306. <https://arxiv.org/abs/2608.24306>
- **[2603.20884]** Jiajun Hou, Hexuan Deng, Wenxiang Jiao et al. (2026). *MemoNoveltyAgent: A Historical Research Memory-Aware Agent Workflow for Paper Novelty Assessment*. arXiv:2603.20884. <https://arxiv.org/abs/2603.20884>
- **[2502.09858]** Kexin Huang, Ying Jin, Ryan Li et al. (2025). *Automated Hypothesis Validation with Agentic Sequential Falsifications*. arXiv:2502.09858. <https://arxiv.org/abs/2502.09858>
- **[2506.18096]** Yuxuan Huang, Yi-Hang Chen, Haozhen Zhang et al. (2025). *Deep Research Agents: A Systematic Examination And Roadmap*. arXiv:2506.18096. <https://arxiv.org/abs/2506.18096>
- **[2607.11084]** Eddie Huang, K.-F. Liao, Iven Fu et al. (2026). *NVAITC AI Scientist: A Governed End-to-End Research System - A Hypertension GWAS Case Study*. arXiv:2607.11084. <https://arxiv.org/abs/2607.11084>
- **[2604.02485]** Ayush Jhaveri, Anthony GX-Chen, Ilia Sucholutsky et al. (2026). *Failing to Falsify: Evaluating and Mitigating Confirmation Bias in Language Models*. arXiv:2604.02485. <https://arxiv.org/abs/2604.02485>
- **[2608.01666]** Feng-Xian Ji, Yuke Li, Jing-Pu Yang et al. (2026). *Style Wins, Substance Loses: A Diagnosis of LLM-as-Judge in Idea Generation*. arXiv:2608.01666. <https://arxiv.org/abs/2608.01666>
- **[2305.06983]** Zhengbao Jiang, Frank F. Xu, Luyu Gao et al. (2023). *Active Retrieval Augmented Generation*. arXiv:2305.06983. <https://arxiv.org/abs/2305.06983>
- **[2508.01285]** Yujing Ke, K. George, Kathan Pandya et al. (2025). *BioDisco: Multi-agent hypothesis generation with dual-mode evidence, iterative feedback and temporal evaluation*. arXiv:2508.01285. <https://arxiv.org/abs/2508.01285>
- **[2605.20168]** Seorin Kim, Vincent Holst, Vincent Ginis (2026). *One in Eight OpenAlex Abstracts Has Integrity Issues*. arXiv:2605.20168. <https://arxiv.org/abs/2605.20168>
- **[2410.13185]** Long Li, Wei-Wen Xu, Jiayan Guo et al. (2024). *Chain of Ideas: Revolutionizing Research Via Novel Idea Development with LLM Agents*. arXiv:2410.13185. <https://arxiv.org/abs/2410.13185>
- **[2603.20278]** Zhuofeng Li, Dongfu Jiang, Xueguang Ma et al. (2026). *OpenResearcher: A Fully Open Pipeline for Long-Horizon Deep Research Trajectory Synthesis*. arXiv:2603.20278. <https://arxiv.org/abs/2603.20278>
- **[2604.05550]** Yu Li, Chenyang Shao, Xinyang Liu et al. (2026). *AutoSOTA: An End-to-End Automated Research System for State-of-the-Art AI Model Discovery*. arXiv:2604.05550. <https://arxiv.org/abs/2604.05550>
- **[2608.13417]** Yi-Wei Li, Wanli Yang, He-Xiang Tan et al. (2026). *Beyond Final Scores: A Systematic Evaluation of Agents for Long-Horizon AI Research and Development*. arXiv:2608.13417. <https://arxiv.org/abs/2608.13417>
- **[2608.01913]** Qi Liu, Jia-Xin Mao, Fengbin Zhu et al. (2026). *Diagnosing Search Behavior and Failure Modes in Long-Horizon Search Agents*. arXiv:2608.01913. <https://arxiv.org/abs/2608.01913>
- **[2408.06292]** Chris Lu, Cong Lu, R. Lange et al. (2024). *The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery*. arXiv:2408.06292. <https://arxiv.org/abs/2408.06292>
- **[2511.02824]** L. Mitchener, Angela Yiu, Benjamin Chang et al. (2025). *Kosmos: An AI Scientist for Autonomous Discovery*. arXiv:2511.02824. <https://arxiv.org/abs/2511.02824>
- **[2511.04583]** Atsuyuki Miyai, M. Toyooka, Takashi Otonari et al. (2025). *Jr. AI Scientist and Its Risk Report: Autonomous Scientific Exploration from a Baseline Paper*. arXiv:2511.04583. <https://arxiv.org/abs/2511.04583>
- **[2604.01128]** Atsuyuki Miyai, M. Toyooka, Zaiying Zhao et al. (2026). *Paper Reconstruction Evaluation: Evaluating Presentation and Hallucination in AI-written Papers*. arXiv:2604.01128. <https://arxiv.org/abs/2604.01128>
- **[2609.07611]** Yunxiang Mo, Tianshi ZHENG, Yi-Sen Gao et al. (2026). *AgentIdeaBench: Benchmarking Scientific Ideation in the Agent Era*. arXiv:2609.07611. <https://arxiv.org/abs/2609.07611>
- **[2510.16234]** Hanane Nour Moussa, Patrick Queiroz Da Silva, Daniel Adu-Ampratwum et al. (2025). *ScholarEval: Research Idea Evaluation Grounded in Literature*. arXiv:2510.16234. <https://arxiv.org/abs/2510.16234>
- **[2511.13825]** H. Nusrat, Omar Nusrat (2025). *When AI Does Science: Evaluating the Autonomous AI Scientist KOSMOS in Radiation Biology*. arXiv:2511.13825. <https://arxiv.org/abs/2511.13825>
- **[2602.05073]** Changdae Oh, Seongheon Park, To Eun Kim et al. (2026). *Uncertainty Quantification in LLM Agents: Foundations, Emerging Challenges, and Opportunities*. arXiv:2602.05073. <https://arxiv.org/abs/2602.05073>
- **[2602.14367]** Shuo-Fei Qiao, Yun-Xiang Wei, Xue-Hai Wang et al. (2026). *InnoEval: On Research Idea Evaluation as a Knowledge-Grounded, Multi-Perspective Reasoning Problem*. arXiv:2602.14367. <https://arxiv.org/abs/2602.14367>
- **[2409.14634]** Marissa Radensky, Simra Shahid, Raymond Fok et al. (2024). *Human-LLM Compound System for Scientific Ideation through Facet Recombination and Novelty Evaluation*. arXiv:2409.14634. <https://arxiv.org/abs/2409.14634>
- **[2604.03159]** D. Rao, Christopher Callison-Burch (2026). *BibTeX Citation Errors in Scientific Publishing Agents: Evaluation and Mitigation*. arXiv:2604.03159. <https://arxiv.org/abs/2604.03159>
- **[2604.03173]** D. Rao, Eric Wong, Christopher Callison-Burch (2026). *Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents*. arXiv:2604.03173. <https://arxiv.org/abs/2604.03173>
- **[2602.13855]** Razeen A Rasheed, Somnath Banerjee, Animesh Mukherjee et al. (2026). *From Fluent to Verifiable: Claim-Level Auditability for Deep Research Agents*. arXiv:2602.13855. <https://arxiv.org/abs/2602.13855>
- **[2607.18360]** Patrik Reizinger, Wieland Brendel (2026). *HALLMARK: Diagnosing Three Failure Modes in LLM Citation Verifiers*. arXiv:2607.18360. <https://arxiv.org/abs/2607.18360>
- **[2503.24047]** Shuo Ren, Pu Jian, Zhen-Jiang Ren et al. (2025). *Towards Scientific Intelligence: A Survey of LLM-based Scientific Agents*. arXiv:2503.24047. <https://arxiv.org/abs/2503.24047>
- **[2608.30413]** Jayanta Sadhu, S. Shahad, Kenneth Marino (2026). *DERELAB: Probing Defeasible Reasoning and Confirmation Bias in LLMs with a Generative Benchmark*. arXiv:2608.30413. <https://arxiv.org/abs/2608.30413>
- **[2501.04227]** Samuel Schmidgall, Yu-Sheng Su, Ze Wang et al. (2025). *Agent Laboratory: Using LLM Agents as Research Assistants*. arXiv:2501.04227. <https://arxiv.org/abs/2501.04227>
- **[2503.18102]** S. Schmidgall, Michael Moor (2025). *AgentRxiv: Towards Collaborative Autonomous Research*. arXiv:2503.18102. <https://arxiv.org/abs/2503.18102>
- **[2603.10303]** Tim Schopf, Michael Farber (2026). *Is this Idea Novel? An Automated Benchmark for Judgment of Research Ideas*. arXiv:2603.10303. <https://arxiv.org/abs/2603.10303>
- **[2608.25660]** Tim Schopf, Tobias Schreieder, Akiko Aizawa (2026). *Think-Probe-Respond: Improving Large Language Models as Judges of Research Idea Novelty*. arXiv:2608.25660. <https://arxiv.org/abs/2608.25660>
- **[2506.22026]** Simra Shahid, Marissa Radensky, Raymond Fok et al. (2025). *Literature-Grounded Novelty Assessment of Scientific Ideas*. arXiv:2506.22026. <https://arxiv.org/abs/2506.22026>
- **[2601.08901]** Yue Shen, Minqian Liu, Da-Wei Zhou et al. (2026). *Navigating Ideation Space: Decomposed Conceptual Representations for Positioning Scientific Ideas*. arXiv:2601.08901. <https://arxiv.org/abs/2601.08901>
- **[2409.04109]** Chenglei Si, Diyi Yang, Tatsunori Hashimoto (2024). *Can LLMs Generate Novel Research Ideas? A Large-Scale Human Study with 100+ NLP Researchers*. arXiv:2409.04109. <https://arxiv.org/abs/2409.04109>
- **[2506.20803]** Chenglei Si, Tatsunori Hashimoto, Diyi Yang (2025). *The Ideation-Execution Gap: Execution Outcomes of LLM-Generated versus Human Research Ideas*. arXiv:2506.20803. <https://arxiv.org/abs/2506.20803>
- **[2606.12071]** Soumitra Sinhahajari, Navonil Majumder, Soujanya Poria (2026). *On the Limits of LLM-as-Judge for Scientific Novelty Assessment*. arXiv:2606.12071. <https://arxiv.org/abs/2606.12071>
- **[2409.13740]** Michael Skarlinski, Sam Cox, Jon M. Laurent et al. (2024). *Language agents achieve superhuman synthesis of scientific knowledge*. arXiv:2409.13740. <https://arxiv.org/abs/2409.13740>
- **[2512.15567]** Zhangde Song, Jieyu Lu, Yuanqi Du et al. (2025). *Evaluating Large Language Models in Scientific Discovery*. arXiv:2512.15567. <https://arxiv.org/abs/2512.15567>
- **[2608.15191]** Heydar Soudani, Elisabeth Lingg, Faegheh Hasibi et al. (2026). *When Deep Research Agents Stagnate: Enhancing Reasoning with Retrieval-Aware Agent Control*. arXiv:2608.15191. <https://arxiv.org/abs/2608.15191>
- **[2606.00644]** Qiuyu Tian, Hao Yin, Yingce Xia et al. (2026). *ForeSci: Evaluating LLM Agents for Forward-Looking AI Research Judgment*. arXiv:2606.00644. <https://arxiv.org/abs/2606.00644>
- **[2305.14259]** Qingyun Wang, Doug Downey, Heng Ji et al. (2023). *SciMON: Scientific Inspiration Machines Optimized for Novelty*. arXiv:2305.14259. <https://arxiv.org/abs/2305.14259>
- **[2605.22343]** Cheng-Cheng Wang, Qinhua Xie, Wei He et al. (2026). *Sibyl-AutoResearch: Autonomous Research Needs Self-Evolving Trial-and-Error Harnesses, Not Paper Generators*. arXiv:2605.22343. <https://arxiv.org/abs/2605.22343>
- **[2606.05241]** Yong-Jie Wang, Xinyu Crystina Zhang, Kunhong Yao et al. (2026). *Search-Time Contamination in Deep Research Agents: Measuring Performance Inflation in Public Benchmark Evaluation*. arXiv:2606.05241. <https://arxiv.org/abs/2606.05241>
- **[2608.13136]** Chen-Run Wang, Mingxuan Zhu, Tiancheng Huang et al. (2026). *LigBench: A Unified and Human-Aligned Benchmark for LLM-based Research Idea Generation*. arXiv:2608.13136. <https://arxiv.org/abs/2608.13136>
- **[2608.22948]** Zi-Yue Wang, Aomufei Yuan, Yi-Ran Yao et al. (2026). *What Proves You Wrong: Benchmarking Language Models on Falsifiable Research Ideation*. arXiv:2608.22948. <https://arxiv.org/abs/2608.22948>
- **[2601.12542]** L. Weidener, Marko Brki'c, Mihailo R. Jovanović et al. (2026). *Rethinking the AI Scientist: Interactive Multi-Agent Workflows for Scientific Discovery*. arXiv:2601.12542. <https://arxiv.org/abs/2601.12542>
- **[2506.00794]** Jia-Xin Wen, Chenglei Si, Chen Yueh-Han et al. (2025). *Predicting Empirical AI Research Outcomes with Language Models*. arXiv:2506.00794. <https://arxiv.org/abs/2506.00794>
- **[2604.11543]** Wen-Qing Wu, Yi Zhao, Yuzhuo Wang et al. (2026). *NovBench: Evaluating Large Language Models on Academic Paper Novelty Assessment*. arXiv:2604.11543. <https://arxiv.org/abs/2604.11543>
- **[2604.14683]** Qianqian Xie, Qing Xiong, He Zhu et al. (2026). *DR3-Eval: Towards Realistic and Reproducible Deep Research Evaluation*. arXiv:2604.14683. <https://arxiv.org/abs/2604.14683>
- **[2604.25256]** Lei Xiong, Kun Luo, Ziyi Xia et al. (2026). *AutoResearchBench: Benchmarking AI Agents on Complex Scientific Literature Discovery*. arXiv:2604.25256. <https://arxiv.org/abs/2604.25256>
- **[2504.08066]** Yutaro Yamada, R. Lange, Cong Lu et al. (2025). *The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search*. arXiv:2504.08066. <https://arxiv.org/abs/2504.08066>
- **[2512.14738]** Zheng-Xu Yan, Han Li, Yuming Feng (2025). *NoveltyRank: A Retrieval-Augmented Framework for Conceptual Novelty Estimation in AI Research*. arXiv:2512.14738. <https://arxiv.org/abs/2512.14738>
- **[2601.01576]** Ming Zhang, Ke-Xin Tan, Yue-Yuan Huang et al. (2026). *OpenNovelty: An LLM-powered Agentic System for Verifiable Scholarly Novelty Assessment*. arXiv:2601.01576. <https://arxiv.org/abs/2601.01576>
- **[2602.03304]** Wenlin Zhang, Kui-Cai Dong, J. Li et al. (2026). *To Search or Not to Search: Aligning the Decision Boundary of Deep Search Agents via Causal Intervention*. arXiv:2602.03304. <https://arxiv.org/abs/2602.03304>
- **[2609.11234]** Guo-Qiang Zhang, Ke-Xin Tan, Ming Zhang et al. (2026). *NovGauge: A Fine-Grained Benchmark for Diagnosing LLMs'Capability in Paper Novelty Assessment*. arXiv:2609.11234. <https://arxiv.org/abs/2609.11234>
- **[2607.04439]** Qihao Zhao, Yangyu Huang, Yalun Dai et al. (2026). *ResearchStudio-Idea: An Evidence-Grounded Research-Ideation Skill Suite from ML Conference Outcomes*. arXiv:2607.04439. <https://arxiv.org/abs/2607.04439>
- **[2607.03863]** Y. Zheng, Yu-Xin Wang, Jiahao Lu et al. (2026). *Rethinking Scientific Discovery in the Agentic Era*. arXiv:2607.03863. <https://arxiv.org/abs/2607.03863>
- **[2602.11685]** J. Zhong, Hao Zhang, Clare Southern et al. (2026). *DRACO: a Cross-Domain Benchmark for Deep Research Accuracy, Completeness, and Objectivity*. arXiv:2602.11685. <https://arxiv.org/abs/2602.11685>
- **[2607.20891]** Peng-Yu Zhu, Lijun Li, Long-Ping Yang et al. (2026). *Is Deep Research Reliable? Misleading Knowledge Induces False Conclusions*. arXiv:2607.20891. <https://arxiv.org/abs/2607.20891>
