"""Visual and quantitative analytics for ResearchForge investigations.

Calculates multi-dimensional novelty scores, similarity breakdowns across papers
(problem, method, and evaluation overlap), landscape concept network topologies,
publication timelines, and epistemic evidence grounding metrics.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from researchforge.schemas import Claim, Critique, Landscape, Paper, PaperAnalysis
from researchforge.workspace import Workspace


def compute_novelty_profile(ws: Workspace) -> dict[str, Any]:
    """Computes multidimensional novelty, rigor, and feasibility metrics."""
    idea = ws.idea_analysis()
    critique = ws.critique()
    analyses = ws.analyses()
    claims = ws.claims()
    gaps = ws.gaps()

    # 1. Problem & Method overlap signals
    max_problem_overlap = 0.0
    max_method_overlap = 0.0
    max_eval_overlap = 0.0
    avg_problem_overlap = 0.0
    avg_method_overlap = 0.0
    avg_eval_overlap = 0.0

    if analyses:
        probs = [a.relation_to_idea.problem_overlap for a in analyses]
        methods = [a.relation_to_idea.method_overlap for a in analyses]
        evals = [a.relation_to_idea.evaluation_overlap for a in analyses]
        max_problem_overlap = max(probs)
        max_method_overlap = max(methods)
        max_eval_overlap = max(evals)
        avg_problem_overlap = sum(probs) / len(probs)
        avg_method_overlap = sum(methods) / len(methods)
        avg_eval_overlap = sum(evals) / len(evals)

    # Problem Novelty: uniqueness of problem setting (0-100)
    # If problem overlap is 0.9, novelty in problem is 10%; if overlap is 0.3, novelty is 70%
    problem_novelty = max(5, int(round((1.0 - max_problem_overlap) * 100)))

    # Method Distinction: distance from closest existing approaches (0-100)
    method_distinction = max(5, int(round((1.0 - max_method_overlap) * 100)))

    # Evaluation Rigor: coverage of variables, baselines, and metrics
    rigor_points = 0
    if idea:
        if idea.variables.independent:
            rigor_points += 20
        if idea.variables.dependent:
            rigor_points += 20
        if idea.variables.controls:
            rigor_points += 20
        if len(idea.search_queries) >= 3:
            rigor_points += 20
        if idea.expected_benefits and idea.potential_risks:
            rigor_points += 20
    evaluation_rigor = max(20, min(100, rigor_points or 50))

    # Evidence Grounding: ratio of claims backed by verified verbatim quotes
    grounding_score = 50
    if claims:
        evidence_items = [e for c in claims for e in c.evidence]
        if evidence_items:
            verified_count = sum(1 for e in evidence_items if e.verified)
            grounding_score = int(round((verified_count / len(evidence_items)) * 100))

    # Practical Feasibility: inverse of critique objections and confounders
    feasibility_score = 75
    critique_severity_counts = {"high": 0, "moderate": 0, "low": 0}
    if critique:
        all_points = (
            critique.novelty
            + critique.technical_validity
            + critique.experimental_validity
            + critique.practicality
        )
        for pt in all_points:
            sev = pt.severity.lower()
            if sev in critique_severity_counts:
                critique_severity_counts[sev] += 1

        # Penalize high severity issues in practicality / validity
        penalty = (
            critique_severity_counts["high"] * 18
            + critique_severity_counts["moderate"] * 8
            + critique_severity_counts["low"] * 2
        )
        feasibility_score = max(10, min(95, 95 - penalty))

    # Gap Alignment: how well the idea targets identified unaddressed gaps
    gap_alignment = 60
    if gaps:
        verified_gaps = sum(1 for g in gaps if any(e.verified for e in g.evidence))
        gap_alignment = min(100, int(round((verified_gaps / len(gaps)) * 100)))

    dimensions = [
        {
            "axis": "Problem Novelty",
            "score": problem_novelty,
            "description": f"Uniqueness of the research question (max literature problem overlap: {int(max_problem_overlap * 100)}%)",
        },
        {
            "axis": "Method Distinction",
            "score": method_distinction,
            "description": f"Technical differentiation from prior work (max literature method overlap: {int(max_method_overlap * 100)}%)",
        },
        {
            "axis": "Evaluation Rigor",
            "score": evaluation_rigor,
            "description": "Specification of variables, baselines, controls, and testable outcomes",
        },
        {
            "axis": "Evidence Grounding",
            "score": grounding_score,
            "description": f"Percentage of claim citations verified word-for-word in retrieved text ({grounding_score}%)",
        },
        {
            "axis": "Practical Feasibility",
            "score": feasibility_score,
            "description": "Implementation viability accounting for confounders and resource constraints",
        },
        {
            "axis": "Gap Alignment",
            "score": gap_alignment,
            "description": f"Targeting substantiated literature gaps ({len(gaps)} gaps identified)",
        },
    ]

    # Overall Composite Novelty Score (0 - 100)
    composite_novelty = int(
        round(
            0.35 * method_distinction
            + 0.25 * problem_novelty
            + 0.15 * gap_alignment
            + 0.15 * grounding_score
            + 0.10 * feasibility_score
        )
    )

    overall_status = critique.overall_status if critique else "insufficient_evidence"

    return {
        "dimensions": dimensions,
        "composite_novelty_score": composite_novelty,
        "max_problem_overlap": round(max_problem_overlap, 3),
        "max_method_overlap": round(max_method_overlap, 3),
        "max_eval_overlap": round(max_eval_overlap, 3),
        "avg_problem_overlap": round(avg_problem_overlap, 3),
        "avg_method_overlap": round(avg_method_overlap, 3),
        "avg_eval_overlap": round(avg_eval_overlap, 3),
        "overall_status": overall_status,
        "status_rationale": critique.status_rationale if critique else "",
        "critique_severities": critique_severity_counts,
        "closest_paper_ids": critique.closest_paper_ids if critique else [],
    }


def compute_similarity_matrix(ws: Workspace) -> dict[str, Any]:
    """Computes multi-dimensional similarity metrics across all analyzed papers.
    
    Breaks down similarity across problem overlap, method overlap, evaluation overlap,
    and composite distance.
    """
    papers_by_id = {p.id: p for p in ws.papers()}
    analyses = ws.analyses()
    critique = ws.critique()
    closest_ids = set(critique.closest_paper_ids if critique else [])

    paper_points: list[dict[str, Any]] = []
    quadrant_counts = {
        "direct_overlap": 0,       # High Method, High Problem
        "alternative_solutions": 0, # Low Method, High Problem
        "transferable_methods": 0,  # High Method, Low Problem
        "peripheral": 0,           # Low Method, Low Problem
    }

    for a in analyses:
        p = papers_by_id.get(a.paper_id)
        rel = a.relation_to_idea
        p_over = float(rel.problem_overlap)
        m_over = float(rel.method_overlap)
        e_over = float(rel.evaluation_overlap)

        # Composite similarity: weighted average
        composite = round(0.45 * p_over + 0.40 * m_over + 0.15 * e_over, 3)

        # Categorize quadrant (threshold at 0.5)
        if p_over >= 0.5 and m_over >= 0.5:
            quad = "direct_overlap"
        elif p_over >= 0.5 and m_over < 0.5:
            quad = "alternative_solutions"
        elif p_over < 0.5 and m_over >= 0.5:
            quad = "transferable_methods"
        else:
            quad = "peripheral"
        quadrant_counts[quad] += 1

        authors_str = ""
        year = None
        venue = None
        citations = 0
        relevance = 0.0
        title = a.paper_id
        url = None

        if p:
            title = p.title
            year = p.year
            venue = p.venue
            citations = p.citation_count or 0
            relevance = round(p.relevance, 3)
            url = p.url
            if p.authors:
                authors_str = ", ".join(p.authors[:2]) + (" et al." if len(p.authors) > 2 else "")

        paper_points.append({
            "id": a.paper_id,
            "title": title,
            "authors": authors_str,
            "year": year,
            "venue": venue,
            "url": url,
            "citations": citations,
            "relevance": relevance,
            "relevance_tier": a.relevance_tier,
            "problem_overlap": round(p_over, 3),
            "method_overlap": round(m_over, 3),
            "evaluation_overlap": round(e_over, 3),
            "composite_similarity": composite,
            "conceptual_difference": rel.conceptual_difference,
            "basis": rel.basis,
            "quadrant": quad,
            "is_closest": a.paper_id in closest_ids,
        })

    # Sort papers by composite similarity descending
    paper_points.sort(key=lambda x: -x["composite_similarity"])

    # Statistical summary
    total_analyzed = len(paper_points)
    avg_problem = round(sum(p["problem_overlap"] for p in paper_points) / total_analyzed, 3) if total_analyzed else 0.0
    avg_method = round(sum(p["method_overlap"] for p in paper_points) / total_analyzed, 3) if total_analyzed else 0.0
    avg_eval = round(sum(p["evaluation_overlap"] for p in paper_points) / total_analyzed, 3) if total_analyzed else 0.0

    return {
        "papers": paper_points,
        "total_analyzed": total_analyzed,
        "quadrant_counts": quadrant_counts,
        "averages": {
            "problem_overlap": avg_problem,
            "method_overlap": avg_method,
            "evaluation_overlap": avg_eval,
        },
        "top_similar": paper_points[:10],
    }


# Unanalyzed papers shown in the concept network, highest lexical relevance first.
MAX_RETRIEVED_NODES = 40


def compute_landscape_network(ws: Workspace) -> dict[str, Any]:
    """Generates node-link topology for concept and citation relations.
    
    Includes Idea at center, Field categories as clusters, and analyzed papers
    connected by similarity and category membership.
    """
    landscape = ws.landscape()
    analyses = ws.analyses()
    papers_by_id = {p.id: p for p in ws.papers()}
    critique = ws.critique()
    closest_ids = set(critique.closest_paper_ids if critique else [])

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    node_ids: set[str] = set()

    # Center Idea Node
    idea_label = "Your Idea"
    idea_title = ws.raw_idea[:90] + ("..." if len(ws.raw_idea) > 90 else "")
    nodes.append({
        "id": "idea",
        "label": idea_label,
        "full_title": ws.raw_idea,
        "type": "idea",
        "group": "idea",
        "size": 34,
        "color": "#1f7a4d",
    })
    node_ids.add("idea")

    # Categories
    categories = landscape.categories if landscape else []
    cat_to_node_id: dict[str, str] = {}
    for i, cat in enumerate(categories):
        cid = f"cat_{i}"
        cat_to_node_id[cat.name] = cid
        nodes.append({
            "id": cid,
            "label": cat.name,
            "full_title": cat.description or cat.name,
            "type": "category",
            "group": "category",
            "size": 22,
            "color": "#3a5a7e",
        })
        node_ids.add(cid)

        # Connect category to Idea
        edges.append({
            "source": "idea",
            "target": cid,
            "weight": 1.5,
            "type": "idea_category",
            "color": "rgba(58, 90, 126, 0.4)",
        })

    # Map categories to papers (explicit landscape mapping or heuristic match)
    cat_papers_count = sum(len(cat.paper_ids) for cat in categories) if categories else 0
    paper_to_cat: dict[str, tuple[str, str]] = {}
    if categories:
        if cat_papers_count > 0:
            for cat in categories:
                cid = cat_to_node_id.get(cat.name)
                if cid:
                    for pid in cat.paper_ids:
                        paper_to_cat[pid] = (cid, cat.name)
        else:
            # Fallback heuristic: match paper title/abstract tokens against category names
            for a in analyses:
                pid = a.paper_id
                p = papers_by_id.get(pid)
                text = f"{p.title if p else ''} {(p.abstract or '') if p else ''} {a.relation_to_idea.conceptual_difference} {a.relation_to_idea.basis}".lower()
                best_cat = None
                best_score = -1
                for cat in categories:
                    words = [w for w in cat.name.lower().replace("/", " ").replace("-", " ").split() if len(w) > 3]
                    score = sum(1 for w in words if w in text)
                    if score > best_score:
                        best_score = score
                        best_cat = cat
                if best_cat and best_score >= 0:
                    cid = cat_to_node_id.get(best_cat.name)
                    if cid:
                        paper_to_cat[pid] = (cid, best_cat.name)

    # Analyzed Papers
    for a in analyses:
        pid = a.paper_id
        p = papers_by_id.get(pid)
        is_close = pid in closest_ids
        title = p.title if p else pid
        short_title = (title[:36] + "...") if len(title) > 36 else title
        p_over = float(a.relation_to_idea.problem_overlap)
        m_over = float(a.relation_to_idea.method_overlap)
        e_over = float(a.relation_to_idea.evaluation_overlap)
        similarity = round(0.45 * p_over + 0.40 * m_over + 0.15 * e_over, 3)

        color = "#1f7a4d" if is_close else ("#3a5a7e" if a.relevance_tier == "high" else "#8c96a4")
        size = 20 if is_close else (16 if a.relevance_tier == "high" else 12)

        assigned_cat = paper_to_cat.get(pid)

        nodes.append({
            "id": pid,
            "label": short_title,
            "full_title": title,
            "authors": ", ".join(p.authors[:2]) if p and p.authors else "",
            "year": p.year if p else None,
            "venue": p.venue if p else None,
            "citations": p.citation_count if p else 0,
            "type": "paper",
            "group": a.relevance_tier,
            "similarity": similarity,
            "problem_overlap": round(p_over, 3),
            "method_overlap": round(m_over, 3),
            "evaluation_overlap": round(e_over, 3),
            "conceptual_difference": a.relation_to_idea.conceptual_difference,
            "basis": a.relation_to_idea.basis,
            "url": p.url if p else None,
            "category_id": assigned_cat[0] if assigned_cat else None,
            "category_name": assigned_cat[1] if assigned_cat else None,
            "is_closest": is_close,
            "analyzed": True,
            "size": size,
            "color": color,
        })
        node_ids.add(pid)

        # Edge from Idea to Paper based on similarity
        if similarity >= 0.25 or is_close:
            edges.append({
                "source": "idea",
                "target": pid,
                "weight": max(1.0, similarity * 4),
                "similarity": similarity,
                "type": "similarity",
                "color": "rgba(31, 122, 77, 0.6)" if is_close else "rgba(90, 98, 108, 0.35)",
            })

        # Edge from Category to Paper
        if assigned_cat and assigned_cat[0] in node_ids:
            edges.append({
                "source": assigned_cat[0],
                "target": pid,
                "weight": 1.0,
                "type": "category_paper",
                "color": "rgba(58, 90, 126, 0.3)",
            })

    # Retrieved papers not analyzed yet: faint nodes, so the network grows while the search is still running.
    retrieved = sorted((p for p in papers_by_id.values() if p.id not in node_ids), key=lambda p: -p.relevance)
    for p in retrieved[:MAX_RETRIEVED_NODES]:
        nodes.append({
            "id": p.id,
            "label": (p.title[:36] + "...") if len(p.title) > 36 else p.title,
            "full_title": p.title,
            "authors": ", ".join(p.authors[:2]) if p.authors else "",
            "year": p.year,
            "venue": p.venue,
            "citations": p.citation_count or 0,
            "type": "paper",
            "group": "retrieved",
            "similarity": None,
            "url": p.url,
            "category_id": paper_to_cat.get(p.id, (None, None))[0],
            "category_name": paper_to_cat.get(p.id, (None, None))[1],
            "is_closest": False,
            "analyzed": False,
            "size": 8,
            "color": "#8c96a4",
        })
        node_ids.add(p.id)
        edges.append({"source": "idea", "target": p.id, "weight": 0.5, "type": "retrieved"})

    return {
        "nodes": nodes,
        "edges": edges,
        "retrieved_total": len(papers_by_id),
        "field_name": landscape.field_name if landscape else "",
        "idea_position": landscape.idea_position if landscape else "",
    }


def compute_timeline_trends(ws: Workspace) -> dict[str, Any]:
    """Computes publication year progression and citation volume over time."""
    papers = ws.papers()
    analyzed_ids = {a.paper_id for a in ws.analyses()}

    year_data: dict[int, dict[str, Any]] = defaultdict(lambda: {
        "year": 0,
        "count": 0,
        "analyzed_count": 0,
        "total_citations": 0,
        "avg_relevance": 0.0,
        "papers": [],
    })

    current_year = 2026
    for p in papers:
        y = p.year
        if not y or y < 2000 or y > current_year + 1:
            continue
        entry = year_data[y]
        entry["year"] = y
        entry["count"] += 1
        if p.id in analyzed_ids:
            entry["analyzed_count"] += 1
        entry["total_citations"] += p.citation_count or 0
        entry["avg_relevance"] += p.relevance
        if len(entry["papers"]) < 5:
            entry["papers"].append({"id": p.id, "title": p.title, "citations": p.citation_count or 0})

    # Sort years chronologically
    sorted_years = sorted(year_data.keys())
    timeline: list[dict[str, Any]] = []
    cumulative = 0

    for y in sorted_years:
        d = year_data[y]
        if d["count"]:
            d["avg_relevance"] = round(d["avg_relevance"] / d["count"], 3)
        cumulative += d["count"]
        d["cumulative_count"] = cumulative
        timeline.append(d)

    return {
        "timeline": timeline,
        "earliest_year": sorted_years[0] if sorted_years else None,
        "latest_year": sorted_years[-1] if sorted_years else None,
        "total_papers": len(papers),
    }


def compute_epistemic_grounding(ws: Workspace) -> dict[str, Any]:
    """Calculates breakdown of claims by kind and evidence verification status."""
    claims = ws.claims()
    kind_counts = Counter(c.kind for c in claims)
    conf_counts = Counter(c.confidence for c in claims)

    verified_quotes = 0
    unverified_quotes = 0
    no_quotes = 0
    total_items = 0

    for c in claims:
        for item in c.evidence:
            total_items += 1
            if item.verified:
                verified_quotes += 1
            elif item.quote:
                unverified_quotes += 1
            else:
                no_quotes += 1

    return {
        "total_claims": len(claims),
        "kinds": {
            "evidence": kind_counts.get("evidence", 0),
            "inference": kind_counts.get("inference", 0),
            "hypothesis": kind_counts.get("hypothesis", 0),
            "assumption": kind_counts.get("assumption", 0),
            "experimental": kind_counts.get("experimental", 0),
        },
        "confidence": {
            "high": conf_counts.get("high", 0),
            "medium": conf_counts.get("medium", 0),
            "low": conf_counts.get("low", 0),
        },
        "evidence_verification": {
            "total_items": total_items,
            "verified_quotes": verified_quotes,
            "unverified_quotes": unverified_quotes,
            "no_quotes": no_quotes,
            "verification_rate": round(verified_quotes / total_items, 3) if total_items else 0.0,
        },
    }


def compute_all_graph_data(ws: Workspace) -> dict[str, Any]:
    """Bundles novelty profile, similarity matrix, concept network, timeline, and epistemic metrics."""
    return {
        "project": ws.name,
        "raw_idea": ws.raw_idea,
        "novelty": compute_novelty_profile(ws),
        "similarity": compute_similarity_matrix(ws),
        "network": compute_landscape_network(ws),
        "timeline": compute_timeline_trends(ws),
        "epistemic": compute_epistemic_grounding(ws),
    }
