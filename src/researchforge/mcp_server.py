"""MCP server exposing the ResearchToolkit to DeepSeek Harness.

dsh launches this module through ``@deepseek-ai/dsh-mcp-client`` (stdio).
The model sees each tool as ``mcp__researchforge__<name>``.

Environment:
    RESEARCHFORGE_PROJECT_DIR   the investigation workspace (required)
    RESEARCHFORGE_CONFIG        optional settings file
    RESEARCHFORGE_CREATE        "1" to initialise a missing workspace (interactive dsh use)
    RESEARCHFORGE_IDEA          idea text for a newly initialised workspace
"""

from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError as McpToolError
from mcp_types import ToolAnnotations

from researchforge import logging_setup
from researchforge.config import load_settings
from researchforge.schemas import (
    Critique,
    ExperimentPlan,
    Gap,
    IdeaAnalysis,
    Landscape,
    Modification,
    PaperAnalysis,
)
from researchforge.toolkit import EvidenceInput, ResearchToolkit, ToolError
from researchforge.workspace import Workspace

SYSTEM_FIELDS = {"id", "recorded_at", "raw_idea", "status", "verified", "verification_note"}

INSTRUCTIONS = (
    "ResearchForge research tools. Search and read literature with search_papers, list_papers, get_paper, "
    "fetch_paper_text, search_paper_text, expand_citations, search_github and inspect_repository. Persist every "
    "result with the record_* tools; only recorded results appear in the investigation report. Cite only paper ids "
    "returned by these tools."
)

READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=True)
RECORD = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)


def flat_signature(model: type[BaseModel], *, exclude: set[str] = frozenset(), overrides: dict[str, Any] | None = None, extra: list[inspect.Parameter] | None = None) -> inspect.Signature:
    """Build a keyword-only signature whose parameters are ``model``'s fields.

    MCP derives the tool's JSON schema from the signature, so the model gets a
    flat argument object instead of a wrapper object.
    """
    overrides = overrides or {}
    params: list[inspect.Parameter] = []
    for name, info in model.model_fields.items():
        if name in SYSTEM_FIELDS or name in exclude:
            continue
        annotation = overrides.get(name, info.annotation)
        field_kwargs = {"description": info.description} if info.description else {}
        annotated = Annotated[annotation, Field(**field_kwargs)] if field_kwargs else annotation
        if info.is_required():
            default = inspect.Parameter.empty
        elif info.default_factory is not None:
            default = info.default_factory()
        else:
            default = info.default
        params.append(inspect.Parameter(name, inspect.Parameter.KEYWORD_ONLY, default=default, annotation=annotated))
    params.sort(key=lambda p: p.default is not inspect.Parameter.empty)
    params += extra or []
    return inspect.Signature(params)


def _record_tool(server: MCPServer, name: str, description: str, handler, sig: inspect.Signature) -> None:
    def fn(**kwargs):
        try:
            return handler(**_dump(kwargs))
        except ToolError as exc:
            raise McpToolError(str(exc)) from exc

    fn.__name__ = name
    fn.__signature__ = sig  # type: ignore[attr-defined]
    fn.__doc__ = description
    server.add_tool(fn, name=name, description=description, annotations=RECORD)


def _dump(value):
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_dump(v) for v in value]
    if isinstance(value, dict):
        return {k: _dump(v) for k, v in value.items()}
    return value


def _async_tool(server: MCPServer, fn, description: str) -> None:
    async def wrapper(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except ToolError as exc:
            raise McpToolError(str(exc)) from exc

    wrapper.__name__ = fn.__name__
    wrapper.__signature__ = inspect.signature(fn, eval_str=True)  # type: ignore[attr-defined]
    server.add_tool(wrapper, name=fn.__name__, description=description, annotations=READ_ONLY)


def _sync_tool(server: MCPServer, fn, description: str, annotations: ToolAnnotations = READ_ONLY) -> None:
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ToolError as exc:
            raise McpToolError(str(exc)) from exc

    wrapper.__name__ = fn.__name__
    wrapper.__signature__ = inspect.signature(fn, eval_str=True)  # type: ignore[attr-defined]
    server.add_tool(wrapper, name=fn.__name__, description=description, annotations=annotations)


def build_server(toolkit: ResearchToolkit) -> MCPServer:
    server = MCPServer(name="researchforge", instructions=INSTRUCTIONS, version="0.1.0")
    tk = toolkit
    evidence_list = list[EvidenceInput]

    # ---- read-only research tools
    _sync_tool(server, tk.get_research_state, "Digest of the investigation: idea, papers, records, and each phase's outstanding requirements.")
    _async_tool(server, tk.search_papers, "Search open scholarly sources (arXiv, OpenAlex, Semantic Scholar, Crossref). Results are stored with provenance and get stable paper ids. Repeated queries return stored results.")
    _sync_tool(server, tk.get_paper, "Full stored record for one paper (abstract, venue, provenance) and its analysis if recorded.")
    _sync_tool(server, tk.list_papers, "List retrieved papers by heuristic relevance, optionally only those not yet analyzed.")
    _async_tool(server, tk.fetch_paper_text, "Download and extract the open-access full text (arXiv or OA PDF) of a retrieved paper. Returns an outline with page numbers.")
    _async_tool(server, tk.search_paper_text, "Regex/keyword search inside a paper's full text; returns passages with page locations to quote as evidence.")
    _async_tool(server, tk.expand_citations, "Follow the citation graph via OpenAlex: 'citations' (works citing the paper) or 'references' (works it cites). New papers are stored.")
    _async_tool(server, tk.search_github, "Search GitHub repositories (read-only).")
    _async_tool(server, tk.inspect_repository, "Inspect a GitHub repository (read-only): README excerpt, languages, benchmarks/models mentioned, reproducibility signals. Pass paper_id to link it as that paper's code.")
    _sync_tool(server, tk.get_records, "Return full recorded items of one kind for review.")

    # ---- record tools (write only inside the investigation workspace)
    _record_tool(server, "record_idea_analysis", "Record the formalized research idea (phase 1).", tk.record_idea_analysis, flat_signature(IdeaAnalysis))
    _record_tool(server, "record_paper_analysis", "Record a structured analysis of one retrieved paper and its relation to the idea. Overlap scores are heuristic; explain their basis.", tk.record_paper_analysis, flat_signature(PaperAnalysis))
    _record_tool(
        server,
        "record_claim",
        "Record a claim with its evidence. kind='evidence' needs a verbatim quote (support='direct') from a retrieved paper, which is verified automatically; kind='inference' is a conclusion derived from cited evidence; kind='hypothesis' is an untested proposal; kind='assumption' is something taken as given without evidence (it is never treated as established).",
        tk.record_claim,
        inspect.Signature(
            [
                inspect.Parameter("statement", inspect.Parameter.KEYWORD_ONLY, annotation=str),
                inspect.Parameter("kind", inspect.Parameter.KEYWORD_ONLY, annotation=Literal["evidence", "inference", "hypothesis", "assumption"]),
                inspect.Parameter("confidence", inspect.Parameter.KEYWORD_ONLY, annotation=Literal["low", "medium", "high"]),
                inspect.Parameter("evidence", inspect.Parameter.KEYWORD_ONLY, default=[], annotation=evidence_list),
                inspect.Parameter("tags", inspect.Parameter.KEYWORD_ONLY, default=[], annotation=list[str]),
            ]
        ),
    )
    _record_tool(server, "record_landscape", "Record the research landscape: taxonomy of approaches (with paper ids), where the idea fits, common datasets/metrics, repeated limitations and contradictions.", tk.record_landscape, flat_signature(Landscape))
    _record_tool(server, "record_critique", "Record the critique of the idea: strongest arguments for/against, unresolved question, dangerous confounder, closest work, overall status.", tk.record_critique, flat_signature(Critique))
    id_param = [inspect.Parameter("id", inspect.Parameter.KEYWORD_ONLY, default=None, annotation=Annotated[str | None, Field(description="Pass an existing id to revise that record.")])]
    _record_tool(server, "record_gap", "Record an evidence-linked research gap.", tk.record_gap, flat_signature(Gap, overrides={"evidence": evidence_list}, extra=id_param))
    _record_tool(
        server,
        "record_no_gap",
        "Record that the retrieved evidence supports no research gap, with the rationale and the papers that cover the space.",
        tk.record_no_gap,
        inspect.Signature(
            [
                inspect.Parameter("rationale", inspect.Parameter.KEYWORD_ONLY, annotation=str),
                inspect.Parameter("paper_ids", inspect.Parameter.KEYWORD_ONLY, annotation=list[str]),
            ]
        ),
    )
    _record_tool(server, "record_modification", "Record one proposed modification of the idea (2-5 in total). Use qualitative difficulty levels with their basis; no numeric scores.", tk.record_modification, flat_signature(Modification, extra=id_param))
    _record_tool(server, "record_experiment_plan", "Record an experiment plan. An optional execution spec is saved for human approval; it never runs automatically.", tk.record_experiment_plan, flat_signature(ExperimentPlan, extra=id_param))

    # ---- investigation loop records
    P = inspect.Parameter
    KW = P.KEYWORD_ONLY
    importance = Literal["high", "medium", "low"]
    u_action = Literal["SEARCH", "READ", "COMPARE", "VERIFY", "CHALLENGE", "INVESTIGATE_GAP", "REFINE", "PLAN_EXPERIMENT"]
    category = Literal["novelty", "overlap", "validity", "confounder", "evaluation", "feasibility", "contradiction", "direction", "other"]
    ids = list[str]
    conf = Annotated[float | None, Field(ge=0, le=1, description="Only with a confidence_basis; omit if you cannot justify a value.")]
    _record_tool(
        server, "record_investigation_plan",
        "Record the investigation plan: the questions the investigation must answer, the literature topics (including alternative terminology) to search, and known methods to compare against.",
        tk.record_investigation_plan,
        inspect.Signature([P("questions", KW, annotation=ids), P("search_topics", KW, annotation=ids), P("comparison_targets", KW, default=[], annotation=ids)]),
    )
    _record_tool(
        server, "record_uncertainty",
        "Record an open question that could change the assessment: its category, importance, the preferred next_action and other possible_actions that could reduce it, and any supporting or contradicting papers already known. ResearchForge scores open questions by importance, evidence deficiency, expected information gain and cost to choose what to investigate next.",
        tk.record_uncertainty,
        inspect.Signature([P("question", KW, annotation=str), P("importance", KW, annotation=importance), P("category", KW, default="other", annotation=category),
                           P("next_action", KW, default="SEARCH", annotation=u_action), P("possible_actions", KW, default=[], annotation=list[u_action]),
                           P("description", KW, default="", annotation=str), P("rationale", KW, default="", annotation=str),
                           P("paper_ids", KW, default=[], annotation=ids), P("supporting_paper_ids", KW, default=[], annotation=ids),
                           P("contradicting_paper_ids", KW, default=[], annotation=ids),
                           P("confidence", KW, default=None, annotation=conf), P("confidence_basis", KW, default="", annotation=str)]),
    )
    _record_tool(
        server, "update_uncertainty",
        "Update an uncertainty after investigating it: status resolved / partially_resolved (explain what the evidence shows) or open with a different next_action; cite supporting and contradicting papers and claims.",
        tk.update_uncertainty,
        inspect.Signature([P("id", KW, annotation=str), P("status", KW, annotation=Literal["open", "partially_resolved", "resolved", "unresolved"]),
                           P("resolution", KW, default="", annotation=str), P("paper_ids", KW, default=[], annotation=ids),
                           P("supporting_paper_ids", KW, default=[], annotation=ids), P("contradicting_paper_ids", KW, default=[], annotation=ids),
                           P("claim_ids", KW, default=[], annotation=ids), P("next_action", KW, default=None, annotation=u_action | None),
                           P("confidence", KW, default=None, annotation=conf), P("confidence_basis", KW, default="", annotation=str)]),
    )
    _record_tool(
        server, "record_challenge_result",
        "Close a contradictory-evidence search (CHALLENGE / INVESTIGATE_GAP): does the challenged conclusion hold, or is it weakened or refuted by retrieved work? weakened/refuted require contradicting_paper_ids.",
        tk.record_challenge_result,
        inspect.Signature([P("uncertainty_id", KW, annotation=str), P("verdict", KW, annotation=Literal["holds", "weakened", "refuted"]),
                           P("rationale", KW, annotation=str), P("supporting_paper_ids", KW, default=[], annotation=ids),
                           P("contradicting_paper_ids", KW, default=[], annotation=ids)]),
    )
    _record_tool(
        server, "record_direction",
        "Record a research direction decision: change_type (KEEP_ORIGINAL, REFINE_SCOPE, MODIFY_METHOD, CHANGE_RESEARCH_QUESTION, CHANGE_HYPOTHESIS, REJECT_DIRECTION), the direction and hypothesis, the reason with supporting papers and motivating uncertainties, and a confidence. The original idea is preserved; this records how understanding changed.",
        tk.record_direction,
        inspect.Signature([P("direction", KW, annotation=str), P("hypothesis", KW, annotation=str), P("rationale", KW, annotation=str),
                           P("change_type", KW, default="REFINE_SCOPE", annotation=Literal["KEEP_ORIGINAL", "REFINE_SCOPE", "MODIFY_METHOD", "CHANGE_RESEARCH_QUESTION", "CHANGE_HYPOTHESIS", "REJECT_DIRECTION"]),
                           P("research_question", KW, default=None, annotation=str | None),
                           P("confidence", KW, default="medium", annotation=importance),
                           P("modification_id", KW, default=None, annotation=str | None), P("paper_ids", KW, default=[], annotation=ids),
                           P("uncertainty_ids", KW, default=[], annotation=ids)]),
    )
    _record_tool(
        server, "record_hypothesis_evaluation",
        "Evaluate the hypothesis against an executed, verified experiment: SUPPORTED (only if the run passed verification), NOT_SUPPORTED or INCONCLUSIVE, with the rationale and the next step.",
        tk.record_hypothesis_evaluation,
        inspect.Signature([P("plan_id", KW, annotation=str), P("verdict", KW, annotation=Literal["SUPPORTED", "NOT_SUPPORTED", "INCONCLUSIVE"]),
                           P("rationale", KW, annotation=str), P("next_step", KW, default="", annotation=str)]),
    )
    return server


def main() -> None:
    project = os.environ.get("RESEARCHFORGE_PROJECT_DIR")
    if not project:
        print("RESEARCHFORGE_PROJECT_DIR is required", file=sys.stderr)
        raise SystemExit(2)
    settings = load_settings()
    logging_setup.configure(settings.log_level)
    ws = Workspace(Path(project))
    if not (ws.root / "idea.yaml").exists():
        if os.environ.get("RESEARCHFORGE_CREATE") != "1":
            print(f"{ws.root} is not a ResearchForge project", file=sys.stderr)
            raise SystemExit(2)
        # Interactive use from the dsh bundle: the idea is stated in the conversation.
        ws = Workspace.init_at(ws.root, os.environ.get("RESEARCHFORGE_IDEA") or "(interactive dsh session; see the conversation)")
    build_server(ResearchToolkit(ws, settings)).run("stdio")


if __name__ == "__main__":
    main()
