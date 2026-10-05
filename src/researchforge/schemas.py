"""Typed records for an investigation.

Every record the model produces passes through one of these models before it
is persisted. Fields that the *system* owns (ids, timestamps, verification
results) are assigned by ResearchForge, never accepted from the model.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Confidence = Literal["low", "medium", "high"]
Level = Literal["low", "moderate", "high"]
Support = Literal["direct", "indirect", "weak"]
ClaimKind = Literal["evidence", "inference", "hypothesis", "assumption", "experimental"]
RelevanceTier = Literal["high", "medium", "low", "not_relevant"]
OverallStatus = Literal[
    "promising_needs_validation",
    "substantial_overlap",
    "weak_or_flawed",
    "insufficient_evidence",
]
PhaseStatus = Literal["pending", "running", "complete", "incomplete", "failed", "skipped"]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _strip_list(values: list[str]) -> list[str]:
    return [v.strip() for v in values if v and v.strip()]


# ---------------------------------------------------------------- idea


class Variables(Record):
    independent: list[str] = Field(default_factory=list)
    dependent: list[str] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)


class Ambiguity(Record):
    question: str
    resolution: str | None = Field(default=None, description="How it was resolved, or null if still open.")
    resolved_by: Literal["literature", "assumption", "user", "unresolved"] = "unresolved"


class IdeaAnalysis(Record):
    raw_idea: str = ""
    problem: str
    target_domain: str
    proposed_method: str
    hypothesis: str
    research_question: str = Field(description="A single testable research question.")
    expected_contribution: str
    assumptions: list[str] = Field(default_factory=list)
    variables: Variables = Field(default_factory=Variables)
    target_system: str = ""
    expected_benefits: list[str] = Field(default_factory=list)
    potential_risks: list[str] = Field(default_factory=list)
    ambiguities: list[Ambiguity] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(min_length=2)
    recorded_at: datetime = Field(default_factory=utcnow)

    @field_validator("assumptions", "expected_benefits", "potential_risks", "keywords", "search_queries")
    @classmethod
    def _clean(cls, value: list[str]) -> list[str]:
        return _strip_list(value)


# ---------------------------------------------------------------- literature


class Paper(Record):
    id: str = Field(description="Stable local id, e.g. arxiv:2306.14048, doi:10.1234/x, openalex:W123.")
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    published: str | None = Field(default=None, description="Earliest known publication date (YYYY-MM-DD) across sources.")
    venue: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    abstract: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    openalex_id: str | None = None
    s2_id: str | None = None
    source: str = Field(description="First source that returned this paper.")
    sources: list[str] = Field(default_factory=list, description="Every source that returned this paper.")
    citation_count: int | None = None
    citation_count_source: str | None = None
    retrieved_at: datetime = Field(default_factory=utcnow)
    relevance: float = 0.0
    relevance_basis: str = "heuristic: lexical overlap between idea keywords and title/abstract"
    queries: list[str] = Field(default_factory=list)
    code_urls: list[str] = Field(default_factory=list)
    has_full_text: bool = False
    abstract_source: str | None = Field(default=None, description="Source whose abstract is stored.")
    metadata_warnings: list[str] = Field(default_factory=list, description="Detected inconsistencies, e.g. an abstract that may belong to another work.")


class SourceStatus(Record):
    source: str
    status: Literal["ok", "cached", "error", "skipped"]
    count: int = 0
    detail: str | None = None


class SearchRecord(Record):
    query: str
    sources: list[SourceStatus]
    paper_ids: list[str]
    at: datetime = Field(default_factory=utcnow)


class Overlap(Record):
    problem_overlap: float = Field(ge=0, le=1)
    method_overlap: float = Field(ge=0, le=1)
    evaluation_overlap: float = Field(ge=0, le=1)
    conceptual_difference: str
    basis: str = Field(
        default="",
        description="Why these values were chosen. Scores are heuristic signals, not proof of novelty or overlap.",
    )


class PaperAnalysis(Record):
    paper_id: str
    relevance_tier: RelevanceTier
    problem: str
    method: str
    key_assumptions: list[str] = Field(default_factory=list)
    main_contribution: str = ""
    datasets: list[str] = Field(default_factory=list)
    benchmarks: list[str] = Field(default_factory=list)
    baselines: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    results: str = ""
    limitations: list[str] = Field(default_factory=list)
    future_work: list[str] = Field(default_factory=list)
    code_availability: str = "unknown"
    relation_to_idea: Overlap
    analyzed_from: Literal["abstract", "full_text"] = "abstract"
    recorded_at: datetime = Field(default_factory=utcnow)


# ---------------------------------------------------------------- evidence


class EvidenceItem(Record):
    paper_id: str | None = None
    experiment_run_id: str | None = None
    location: str = Field(default="abstract", description="Where in the source, e.g. 'abstract', 'p. 5', 'Table 2'.")
    quote: str | None = Field(default=None, description="Verbatim text from the source. Required for direct support.")
    support: Support = "indirect"
    verified: bool = Field(default=False, description="Set by ResearchForge: quote found in the retrieved text.")
    verification_note: str | None = None


class Claim(Record):
    id: str = ""
    statement: str
    kind: ClaimKind
    evidence: list[EvidenceItem] = Field(default_factory=list)
    confidence: Confidence
    phase: str = ""
    tags: list[str] = Field(default_factory=list)
    recorded_at: datetime = Field(default_factory=utcnow)


# ---------------------------------------------------------------- landscape & critique


class LandscapeCategory(Record):
    name: str
    parent: str | None = None
    description: str = ""
    paper_ids: list[str] = Field(default_factory=list)


class LinkedFinding(Record):
    description: str
    paper_ids: list[str] = Field(default_factory=list)


class Landscape(Record):
    field_name: str
    categories: list[LandscapeCategory] = Field(min_length=1)
    idea_position: str = Field(description="Where the proposed idea fits, naming a category.")
    dominant_approaches: list[str] = Field(default_factory=list)
    common_assumptions: list[str] = Field(default_factory=list)
    common_datasets: list[str] = Field(default_factory=list)
    common_benchmarks: list[str] = Field(default_factory=list)
    common_metrics: list[str] = Field(default_factory=list)
    repeated_limitations: list[LinkedFinding] = Field(default_factory=list)
    underexplored_combinations: list[str] = Field(default_factory=list)
    contradictions: list[LinkedFinding] = Field(default_factory=list)
    recorded_at: datetime = Field(default_factory=utcnow)


class CritiquePoint(Record):
    question: str
    finding: str
    severity: Level
    claim_ids: list[str] = Field(default_factory=list)
    paper_ids: list[str] = Field(default_factory=list)


class Critique(Record):
    strongest_for: str
    strongest_against: str
    most_important_unresolved_question: str
    most_dangerous_confounder: str
    closest_paper_ids: list[str] = Field(min_length=1)
    closest_work_explanation: str
    potential_contribution: str
    overlap_summary: str
    distinction_summary: str
    novelty: list[CritiquePoint] = Field(default_factory=list)
    technical_validity: list[CritiquePoint] = Field(default_factory=list)
    experimental_validity: list[CritiquePoint] = Field(default_factory=list)
    practicality: list[CritiquePoint] = Field(default_factory=list)
    overall_status: OverallStatus
    status_rationale: str
    recorded_at: datetime = Field(default_factory=utcnow)


class Gap(Record):
    id: str = ""
    gap: str
    evidence: list[EvidenceItem] = Field(min_length=1)
    related_paper_ids: list[str] = Field(default_factory=list)
    why_unaddressed: str
    research_question: str
    potential_experiment: str
    confidence: Confidence
    verification_required: str = ""
    recorded_at: datetime = Field(default_factory=utcnow)


class NoGapFinding(Record):
    """Recorded when the agent concludes the evidence supports no gap."""

    rationale: str
    paper_ids: list[str] = Field(default_factory=list)
    recorded_at: datetime = Field(default_factory=utcnow)


class Modification(Record):
    id: str = ""
    title: str
    description: str
    why_differs: str
    technical_mechanism: str
    expected_benefit: str
    potential_novelty: str
    implementation_difficulty: Level
    implementation_difficulty_basis: str
    experimental_difficulty: Level
    experimental_difficulty_basis: str
    main_risk: str
    required_baselines: list[str] = Field(default_factory=list)
    related_paper_ids: list[str] = Field(default_factory=list)
    addresses_gap_ids: list[str] = Field(default_factory=list)
    recommended: bool = False
    recorded_at: datetime = Field(default_factory=utcnow)


# ---------------------------------------------------------------- experiments


class ExperimentArm(Record):
    name: str = Field(pattern=r"^[A-Za-z0-9_.-]{1,64}$")
    role: Literal["baseline", "method", "ablation"]
    command: str = Field(description="Run as argv (shlex-split, no shell). Must write JSON metrics to $RF_RESULTS_FILE.")
    config: dict[str, str | int | float | bool] = Field(default_factory=dict)


class ExecutionSpec(Record):
    repo_url: str | None = Field(default=None, description="Public git repository to clone into the experiment directory.")
    repo_ref: str | None = None
    setup: list[str] = Field(default_factory=list, description="Setup commands, each run as argv without a shell.")
    arms: list[ExperimentArm] = Field(min_length=1)
    expected_metrics: list[str] = Field(default_factory=list)
    higher_is_better: dict[str, bool] = Field(default_factory=dict)
    sample_count_key: str | None = Field(default=None, description="Metric key holding the number of evaluated samples.")
    timeout_s: float | None = None
    docker_image: str | None = None


class ExperimentPlan(Record):
    id: str = ""
    title: str
    research_question: str
    hypothesis: str
    proposed_method: str
    baselines: list[str] = Field(min_length=1)
    datasets: list[str] = Field(default_factory=list)
    workloads: list[str] = Field(default_factory=list)
    hardware: str = ""
    software_environment: str = ""
    metrics: list[str] = Field(min_length=1)
    ablations: list[str] = Field(default_factory=list)
    controls: list[str] = Field(default_factory=list)
    confounders_addressed: list[str] = Field(default_factory=list)
    expected_outcomes: str = ""
    failure_conditions: list[str] = Field(default_factory=list)
    reproducibility_notes: str = ""
    related_modification_id: str | None = None
    related_paper_ids: list[str] = Field(default_factory=list)
    execution: ExecutionSpec | None = None
    status: Literal["planned", "awaiting_approval", "completed", "failed"] = "planned"
    recorded_at: datetime = Field(default_factory=utcnow)


class ExperimentRun(Record):
    id: str
    plan_id: str
    arm: str
    role: str
    status: Literal["ok", "failed", "timeout"]
    argv: list[str]
    cwd: str
    backend: str
    env: dict[str, str] = Field(default_factory=dict)
    config: dict[str, str | int | float | bool] = Field(default_factory=dict)
    git_commit: str | None = None
    hardware: dict[str, str] = Field(default_factory=dict)
    started_at: datetime
    finished_at: datetime
    duration_s: float
    exit_code: int | None
    stdout_path: str
    stderr_path: str
    results: dict | None = None
    error: str | None = None


class VerificationIssue(Record):
    severity: Literal["error", "warning"]
    code: str
    message: str
    suggestion: str = ""


class MetricComparison(Record):
    metric: str
    baseline_arm: str
    method_arm: str
    baseline_value: float
    method_value: float
    relative_change: float | None


class ExperimentAnalysis(Record):
    plan_id: str
    status: Literal["PASSED", "FAILED", "SUSPICIOUS"]
    run_ids: list[str]
    issues: list[VerificationIssue] = Field(default_factory=list)
    comparisons: list[MetricComparison] = Field(default_factory=list)
    summary: str = ""
    analyzed_at: datetime = Field(default_factory=utcnow)


# ---------------------------------------------------------------- investigation loop

# Loop actions. Spec names map onto these (docs/AGENT_LOOP.md): READ = READ_PAPER, VERIFY = VERIFY_CLAIM,
# COMPARE = COMPARE_METHODS, CHALLENGE = LOOK_FOR_CONTRADICTORY_WORK, REFINE = REFINE_HYPOTHESIS /
# REFINE_RESEARCH_QUESTION, PLAN_EXPERIMENT = DESIGN_EXPERIMENT, EXPERIMENT = RUN_EXPERIMENT,
# ANALYZE_RESULTS = ANALYZE_EXPERIMENT.
LoopAction = Literal[
    "INTAKE", "FORMALIZE", "PLAN", "SEARCH", "READ", "SYNTHESIZE", "COMPARE", "VERIFY", "CHALLENGE", "INVESTIGATE_GAP",
    "CRITIQUE", "REFINE", "PLAN_EXPERIMENT", "EXPERIMENT", "ANALYZE_RESULTS", "FINALIZE",
]
LoopPhase = Literal[
    "INTAKE", "FORMALIZE", "PLAN", "INVESTIGATE", "SYNTHESIZE", "CRITIQUE", "UNCERTAINTY", "CHALLENGE",
    "REFINE", "EXPERIMENT_PLAN", "EXPERIMENT", "ANALYZE", "FINALIZE",
]
UncertaintyAction = Literal["SEARCH", "READ", "COMPARE", "VERIFY", "CHALLENGE", "INVESTIGATE_GAP", "REFINE", "PLAN_EXPERIMENT"]
UncertaintyCategory = Literal["novelty", "overlap", "validity", "confounder", "evaluation", "feasibility", "contradiction", "direction", "other"]
DirectionChange = Literal["KEEP_ORIGINAL", "REFINE_SCOPE", "MODIFY_METHOD", "CHANGE_RESEARCH_QUESTION", "CHANGE_HYPOTHESIS", "REJECT_DIRECTION"]
ResearchDecision = Literal[
    "PROMISING", "NEEDS_MODIFICATION", "ALREADY_WELL_EXPLORED", "INSUFFICIENT_EVIDENCE",
    "EXPERIMENTALLY_SUPPORTED", "EXPERIMENTALLY_UNSUPPORTED",
]


class InvestigationPlan(Record):
    questions: list[str] = Field(min_length=1, description="What the investigation must determine.")
    search_topics: list[str] = Field(min_length=1, description="Literature topics and alternative terminology to search.")
    comparison_targets: list[str] = Field(default_factory=list, description="Known methods the idea must be compared against.")
    recorded_at: datetime = Field(default_factory=utcnow)


class Uncertainty(Record):
    id: str = ""
    question: str
    description: str = ""
    category: UncertaintyCategory = "other"
    importance: Literal["high", "medium", "low"]
    status: Literal["open", "partially_resolved", "resolved", "unresolved"] = "open"
    next_action: UncertaintyAction = "SEARCH"
    possible_actions: list[UncertaintyAction] = Field(default_factory=list, description="Actions that could reduce it; next_action is the preferred one.")
    confidence: float | None = Field(default=None, ge=0, le=1, description="Model-reported confidence in the current answer, with a basis. Never set by the controller.")
    confidence_basis: str = ""
    rationale: str = ""
    resolution: str = ""
    paper_ids: list[str] = Field(default_factory=list)
    supporting_paper_ids: list[str] = Field(default_factory=list)
    contradicting_paper_ids: list[str] = Field(default_factory=list)
    claim_ids: list[str] = Field(default_factory=list)
    challenge_verdict: Literal["holds", "weakened", "refuted"] | None = Field(default=None, description="Outcome of a contradictory-evidence search.")
    target_ref: str | None = Field(default=None, description="Record challenged or investigated (critique, G001, D002, E001).")
    attempts: int = 0
    source: str = Field(default="", description="Loop phase that raised it; 'controller' for system-raised items.")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)

    def actions(self) -> list[str]:
        return list(dict.fromkeys([self.next_action, *self.possible_actions]))


class Direction(Record):
    """A research direction decision. The original idea is never overwritten."""

    id: str = ""
    direction: str
    hypothesis: str
    rationale: str
    change_type: DirectionChange = "REFINE_SCOPE"
    previous_direction_id: str | None = Field(default=None, description="Direction this one replaces; None means it departs from the original idea.")
    research_question: str | None = Field(default=None, description="Set when the change reformulates the research question.")
    confidence: Literal["low", "medium", "high"] = "medium"
    modification_id: str | None = None
    paper_ids: list[str] = Field(default_factory=list)
    uncertainty_ids: list[str] = Field(default_factory=list, description="Uncertainties whose evidence motivated the change.")
    recorded_at: datetime = Field(default_factory=utcnow)


class HypothesisEvaluation(Record):
    plan_id: str
    verdict: Literal["SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE"]
    rationale: str
    run_ids: list[str] = Field(default_factory=list)
    next_step: str = ""
    recorded_at: datetime = Field(default_factory=utcnow)


class Candidate(Record):
    """One action the controller considered, with the terms of its score."""

    action: LoopAction
    uncertainty_id: str | None = None
    target: str = ""
    importance: float = 0.0
    expected_gain: float = 0.0
    gain_basis: str = ""
    relevance: float = 0.0
    deficiency: float = 0.0
    cost: float = 1.0
    score: float = 0.0


class Decision(Record):
    """One autonomous step (the action history). Structured summary, not hidden reasoning."""

    iteration: int
    phase: LoopPhase
    action: LoopAction
    focus: str | None = None
    focus_id: str | None = Field(default=None, description="Triggering uncertainty (or plan) id.")
    reason: str
    evidence: str = ""
    expected_outcome: str = ""
    outcome: str = ""
    candidates: list[Candidate] = Field(default_factory=list, description="Alternatives considered, best first.")
    expected_gain: float | None = None
    estimated_cost: float | None = None
    tools_used: list[str] = Field(default_factory=list)
    state_changes: dict[str, int] = Field(default_factory=dict)
    info_gain: float | None = Field(default=None, description="Observed information gain of the step (definition in controller.information_gain).")
    closes_investigation: str | None = Field(default=None, description="Set when this decision ends uncertainty investigation, with the reason.")
    at: datetime = Field(default_factory=utcnow)


class LoopBudget(Record):
    iterations: int = 0
    tool_calls: int = 0
    failed_tool_calls: int = 0
    runtime_failures: int = 0
    seconds: float = 0.0
    tokens: int = 0


# ---------------------------------------------------------------- state & events


class PhaseState(Record):
    name: str
    status: PhaseStatus = "pending"
    attempts: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    missing: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    tool_calls: int = 0
    failed_tool_calls: int = 0


class ResearchState(Record):
    project: str
    idea: str
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    status: Literal["created", "running", "complete", "incomplete", "failed", "awaiting_approval"] = "created"
    dsh_session_id: str | None = None
    provider: str = ""
    model: str = ""
    phases: list[PhaseState] = Field(default_factory=list)
    error: str | None = None
    # investigation loop
    loop_phase: LoopPhase = "INTAKE"
    current_action: LoopAction | None = None
    current_focus: str | None = None
    budget: LoopBudget = Field(default_factory=LoopBudget)
    decisions: list[Decision] = Field(default_factory=list)
    no_progress: dict[str, int] = Field(default_factory=dict, description="Consecutive no-progress count per action key.")
    blocked_actions: list[str] = Field(default_factory=list)
    critiques: int = 0
    papers_at_last_critique: int = 0
    finalize_reason: str | None = None
    awaiting_approval: list[str] = Field(default_factory=list)
    investigation_closed: str | None = Field(default=None, description="Why uncertainty investigation stopped (diminishing returns, low value).")
    investigation_closed_at: datetime | None = Field(default=None, description="Uncertainties raised after this time reopen investigation.")
    challenged_refs: list[str] = Field(default_factory=list, description="Conclusions already put up for a contradictory-evidence search.")
    research_decision: ResearchDecision | None = None
    research_decision_basis: str = ""

    @property
    def iteration(self) -> int:
        return self.budget.iterations

    def phase(self, name: str) -> PhaseState:
        for p in self.phases:
            if p.name == name:
                return p
        raise KeyError(name)


class Event(Record):
    seq: int
    ts: datetime = Field(default_factory=utcnow)
    kind: Literal["phase_start", "phase_end", "tool_call", "tool_result", "agent_text", "info", "warning", "error", "decision"]
    phase: str | None = None
    data: dict = Field(default_factory=dict)
