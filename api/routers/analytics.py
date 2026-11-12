"""
Analytics endpoints — expose existing Priority 1-4 analysis results.

All calculations delegate to src/ functions; no analysis logic lives here.
Respondent-level IDs are stripped from public responses to preserve anonymity.
"""

from __future__ import annotations

import math
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query

from api.data_loader import DataUnavailableError, build_communities, build_network, overview_counts, peer_discussion_summary, academic_summary

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

VALID_THRESHOLDS = {0.30, 0.50, 0.60}


def _503(message: str) -> HTTPException:
    return HTTPException(status_code=503, detail={"error": "data_unavailable", "message": message})


def _safe_float(value: object) -> Optional[float]:
    """Convert to float; return None for nan/inf to keep JSON valid."""
    try:
        f = float(value)  # type: ignore[arg-type]
        return None if not math.isfinite(f) else round(f, 6)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# GET /api/health
# ---------------------------------------------------------------------------

@router.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# GET /api/analytics/overview
# ---------------------------------------------------------------------------

@router.get("/overview")
async def get_overview():
    """
    High-level counts for the 24-respondent engineering cohort.

    Returns verified aggregate figures only — no respondent-level data.
    """
    try:
        counts = overview_counts()
    except DataUnavailableError as exc:
        raise _503(str(exc)) from exc

    return {
        "cohort": counts["cohort"],
        "total_respondents": counts["total_respondents"],
        "note": (
            "Survey of 24 engineering students. "
            "All figures are descriptive. "
            "The survey records self-reported preferences; "
            "similarity edges are inferred from shared attributes, "
            "not observed social ties."
        ),
        "branches": counts["branches"],
        "years": counts["years"],
        "preferred_subject_categories": counts["preferred_subject_categories"],
        "primary_reasons": counts["primary_reasons"],
    }


# ---------------------------------------------------------------------------
# GET /api/analytics/network
# ---------------------------------------------------------------------------

@router.get("/network")
async def get_network(
    threshold: float = Query(default=0.50, description="Similarity threshold (0.30, 0.50, or 0.60)"),
):
    """
    Nodes, edges, and graph metrics for the profile-similarity network.

    Supported thresholds: 0.30, 0.50, 0.60.
    Node IDs are anonymised respondent codes from the survey — not names.
    Edge weight is the weighted profile-similarity score (0–1).
    """
    if round(threshold, 2) not in VALID_THRESHOLDS:
        raise HTTPException(
            status_code=422,
            detail={"error": "invalid_threshold", "valid_values": [0.30, 0.50, 0.60]},
        )

    try:
        respondents, graph, tables = build_network(round(threshold, 2))
    except DataUnavailableError as exc:
        raise _503(str(exc)) from exc

    summary = tables["summary"].iloc[0]
    nodes_df = tables["nodes"]
    edges_df = tables["edges"]

    nodes = [
        {
            "id": row["respondent_id"],
            "branch": row["branch"],
            "year": row["year"],
            "preferred_subject_category": row["preferred_subject_category"],
            "component_id": row["component_id"],
            "is_isolated": bool(row["is_isolated"]),
            "metrics": {
                "degree": int(row["degree"]),
                "degree_centrality": _safe_float(row["degree_centrality"]),
                "betweenness_centrality": _safe_float(row["betweenness_centrality"]),
                "closeness_centrality": _safe_float(row["closeness_centrality"]),
                "weighted_degree_strength": _safe_float(row["weighted_degree_strength"]),
            },
        }
        for _, row in nodes_df.iterrows()
    ]

    edges = [
        {
            "source": row["student_1"],
            "target": row["student_2"],
            "weight": _safe_float(row["similarity_score"]),
            "shared_attributes": row["shared_attributes"],
        }
        for _, row in edges_df.iterrows()
    ]

    return {
        "threshold": threshold,
        "graph_summary": {
            "node_count": int(summary["node_count"]),
            "edge_count": int(summary["edge_count"]),
            "density": _safe_float(summary["density"]),
            "connected_component_count": int(summary["connected_component_count"]),
            "largest_component_size": int(summary["largest_component_size"]),
            "isolated_node_count": int(summary["isolated_node_count"]),
        },
        "interpretation_note": (
            "Edges connect respondents who share profile attributes above the threshold. "
            "These are similarity edges, not observed friendships or peer-influence ties."
        ),
        "nodes": nodes,
        "edges": edges,
    }


# ---------------------------------------------------------------------------
# GET /api/analytics/communities
# ---------------------------------------------------------------------------

@router.get("/communities")
async def get_communities(
    threshold: float = Query(default=0.50),
):
    """
    Community detection results (Louvain + greedy modularity) at the given threshold.
    """
    if round(threshold, 2) not in VALID_THRESHOLDS:
        raise HTTPException(
            status_code=422,
            detail={"error": "invalid_threshold", "valid_values": [0.30, 0.50, 0.60]},
        )

    try:
        results = build_communities(round(threshold, 2))
    except DataUnavailableError as exc:
        raise _503(str(exc)) from exc

    sensitivity = results["threshold_sensitivity"]
    community_summary = results["community_summary"]
    attribute_mixing = results["attribute_mixing"]

    threshold_rows = sensitivity[sensitivity["threshold"] == round(threshold, 2)]

    algorithms = []
    for _, row in threshold_rows.iterrows():
        algo = row["algorithm"]
        communities_at_algo = community_summary[
            (community_summary["threshold"] == round(threshold, 2))
            & (community_summary["algorithm"] == algo)
        ]
        community_list = [
            {
                "community_id": r["community_id"],
                "size": int(r["community_size"]),
                "dominant_subject": r["dominant_preferred_subject_category"],
                "dominant_subject_share": _safe_float(r["dominant_subject_share"]),
                "dominant_branch": r["dominant_branch"],
                "dominant_branch_share": _safe_float(r["dominant_branch_share"]),
                "weighted_modularity": _safe_float(r["weighted_modularity"]),
            }
            for _, r in communities_at_algo.iterrows()
        ]
        algorithms.append({
            "algorithm": algo,
            "community_count": int(row["community_count"]),
            "weighted_modularity": _safe_float(row["weighted_modularity"]),
            "communities": community_list,
        })

    mixing_rows = [
        {
            "attribute": r["attribute"],
            "matching_edge_fraction": _safe_float(r["matching_edge_fraction"]),
            "weighted_categorical_assortativity": _safe_float(r["weighted_categorical_assortativity"]),
            "assortativity_defined": bool(r["assortativity_defined"]),
        }
        for _, r in attribute_mixing[
            attribute_mixing["threshold"] == round(threshold, 2)
        ].iterrows()
    ]

    return {
        "threshold": threshold,
        "interpretation_note": (
            "Communities are groups in an inferred profile-similarity graph. "
            "They are not observed social groups and must not be described as "
            "friendship clusters or peer-influence networks."
        ),
        "algorithms": algorithms,
        "attribute_mixing": mixing_rows,
    }


# ---------------------------------------------------------------------------
# GET /api/analytics/threshold-sensitivity
# ---------------------------------------------------------------------------

@router.get("/threshold-sensitivity")
async def get_threshold_sensitivity():
    """
    Graph and community statistics across thresholds 0.30, 0.50, and 0.60.
    """
    try:
        from src.build_engineering_similarity_network import (
            load_engineering_population,
            build_similarity_graph,
            analyze_similarity_graph,
        )
        from api.data_loader import DATA_PATH

        if not DATA_PATH.exists():
            raise DataUnavailableError(
                "Survey data file not found. "
                "Place survey_responses_anonymized.csv in data/raw/."
            )

        respondents = load_engineering_population(DATA_PATH)
        rows = []
        for threshold in sorted(VALID_THRESHOLDS):
            graph = build_similarity_graph(respondents, threshold)
            tables = analyze_similarity_graph(graph, threshold)
            summary = tables["summary"].iloc[0]
            rows.append({
                "threshold": threshold,
                "is_primary": threshold == 0.50,
                "node_count": int(summary["node_count"]),
                "edge_count": int(summary["edge_count"]),
                "density": _safe_float(summary["density"]),
                "connected_component_count": int(summary["connected_component_count"]),
                "largest_component_size": int(summary["largest_component_size"]),
                "isolated_node_count": int(summary["isolated_node_count"]),
            })
        return {"thresholds": rows}

    except DataUnavailableError as exc:
        raise _503(str(exc)) from exc


# ---------------------------------------------------------------------------
# GET /api/analytics/peer-discussion
# ---------------------------------------------------------------------------

@router.get("/peer-discussion")
async def get_peer_discussion():
    """
    Self-reported peer-discussion distributions and cross-tabulations.

    Does not infer discussion partners or social ties.
    """
    try:
        results = peer_discussion_summary()
    except DataUnavailableError as exc:
        raise _503(str(exc)) from exc

    summary_df = results["summary"]

    def _variable_summary(variable: str) -> list[dict]:
        rows = summary_df[summary_df["variable"] == variable]
        return [
            {
                "category": r["category"],
                "response_class": r["response_class"],
                "count": int(r["respondent_count"]),
                "percent": _safe_float(r["percent_of_denominator"]),
                "denominator": int(r["denominator"]),
            }
            for _, r in rows.iterrows()
        ]

    stats_df = results["statistics"]
    discussion_stat = stats_df[
        stats_df["analysis"] == "discussion_status_by_best_friend_same_elective"
    ].iloc[0]

    return {
        "discussion_status": _variable_summary("discussed_elective_with_friends"),
        "best_friend_same_elective": _variable_summary("best_friend_same_elective"),
        "best_friend_choice_reason": _variable_summary("best_friend_choice_reason"),
        "best_friend_marks_range": _variable_summary("best_friend_marks_range"),
        "discussion_vs_friend_same_elective": {
            "test_used": discussion_stat["test_used"],
            "test_statistic": _safe_float(discussion_stat["test_statistic"]),
            "p_value": _safe_float(discussion_stat["p_value"]),
            "sample_size": int(discussion_stat["sample_size"]),
            "denominator": int(discussion_stat["denominator"]),
            "note": (
                "Fisher exact (two-sided). Small sample; treat as descriptive. "
                "p < 0.05 would indicate a statistical association, not causation."
            ),
        },
        "interpretation_note": (
            "The survey records whether respondents discussed the elective with friends. "
            "It does not identify discussion partners; "
            "no observed peer-influence network can be constructed from these data."
        ),
    }


# ---------------------------------------------------------------------------
# GET /api/analytics/academic
# ---------------------------------------------------------------------------

@router.get("/academic")
async def get_academic():
    """
    Descriptive academic outcome distributions and exploratory statistics.
    """
    try:
        results = academic_summary()
    except DataUnavailableError as exc:
        raise _503(str(exc)) from exc

    summary_df = results["summary"]

    def _variable_summary(variable: str) -> list[dict]:
        rows = summary_df[summary_df["variable"] == variable]
        return [
            {
                "category": r["category"],
                "response_class": r["response_class"],
                "count": int(r["respondent_count"]),
                "percent": _safe_float(r["percent_of_denominator"]),
                "denominator": int(r["denominator"]),
            }
            for _, r in rows.iterrows()
        ]

    stats_df = results["statistics"]

    ordinal_stats = []
    for _, row in stats_df[stats_df["test_used"] == "Spearman rank correlation"].iterrows():
        ordinal_stats.append({
            "analysis": row["analysis"],
            "sample_size": int(row["sample_size"]),
            "denominator": int(row["denominator"]),
            "excluded_count": int(row.get("excluded_count", 0)),
            "spearman_rho": _safe_float(row["effect_size"]),
            "p_value": _safe_float(row["p_value"]),
            "p_value_method": row["p_value_method"],
        })

    return {
        "academic_outcome": _variable_summary("academic_outcome"),
        "course_difficulty": _variable_summary("course_difficulty"),
        "final_score_range": _variable_summary("final_score_range"),
        "study_hours_per_week": _variable_summary("study_hours_per_week"),
        "score_met_expectations": _variable_summary("score_met_expectations"),
        "ordinal_associations": ordinal_stats,
        "interpretation_note": (
            "All figures are descriptive. "
            "Sparse expected counts prevent formal chi-square tests for most cross-tabulations. "
            "Spearman estimates are exploratory with permutation p-values; "
            "cross-sectional associations are not causal."
        ),
    }
