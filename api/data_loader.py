"""
Lazy-load the survey data and analysis results.

The survey CSV is gitignored and may not be present in every environment.
All public functions return a clear DataUnavailableError when that happens,
so API endpoints can return an honest 503 rather than a crash.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DATA_PATH = ROOT / "data" / "raw" / "survey_responses_anonymized.csv"


class DataUnavailableError(RuntimeError):
    """Raised when the survey CSV has not been placed in data/raw/."""


# ---------------------------------------------------------------------------
# Population
# ---------------------------------------------------------------------------

def _load_population():
    """Return the 24-respondent engineering DataFrame, or raise."""
    if not DATA_PATH.exists():
        raise DataUnavailableError(
            "Survey data file not found. "
            "Place survey_responses_anonymized.csv in data/raw/ to enable "
            "analytics endpoints."
        )
    from src.build_engineering_similarity_network import load_engineering_population
    return load_engineering_population(DATA_PATH)


# ---------------------------------------------------------------------------
# Network
# ---------------------------------------------------------------------------

def build_network(threshold: float = 0.50):
    """Build and return an nx.Graph at the requested threshold."""
    respondents = _load_population()
    from src.build_engineering_similarity_network import build_similarity_graph, analyze_similarity_graph
    graph = build_similarity_graph(respondents, threshold)
    tables = analyze_similarity_graph(graph, threshold)
    return respondents, graph, tables


# ---------------------------------------------------------------------------
# Communities
# ---------------------------------------------------------------------------

def build_communities(threshold: float = 0.50):
    """Return community analysis results at the requested threshold."""
    respondents = _load_population()
    from src.analyze_engineering_similarity_communities import analyze_communities
    results = analyze_communities(respondents, thresholds=(threshold,))
    return results


# ---------------------------------------------------------------------------
# Peer discussion
# ---------------------------------------------------------------------------

def peer_discussion_summary():
    """Return peer-discussion analysis DataFrames."""
    if not DATA_PATH.exists():
        raise DataUnavailableError(
            "Survey data file not found. "
            "Place survey_responses_anonymized.csv in data/raw/ to enable "
            "analytics endpoints."
        )
    from src.analyze_peer_discussion import analyze_peer_discussion, REQUIRED_COLUMNS
    from src.survey_analysis_utils import load_engineering_survey
    respondents = load_engineering_survey(REQUIRED_COLUMNS, DATA_PATH)
    return analyze_peer_discussion(respondents)


# ---------------------------------------------------------------------------
# Academic outcomes
# ---------------------------------------------------------------------------

def academic_summary():
    """Return academic-outcome analysis DataFrames."""
    if not DATA_PATH.exists():
        raise DataUnavailableError(
            "Survey data file not found. "
            "Place survey_responses_anonymized.csv in data/raw/ to enable "
            "analytics endpoints."
        )
    from src.analyze_elective_grades import (
        analyze_academic_outcomes,
        REQUIRED_COLUMNS as ACADEMIC_COLS,
    )
    from src.survey_analysis_utils import load_engineering_survey
    respondents = load_engineering_survey(ACADEMIC_COLS, DATA_PATH)
    return analyze_academic_outcomes(respondents)


# ---------------------------------------------------------------------------
# Overview counts (derived from population only)
# ---------------------------------------------------------------------------

def overview_counts() -> dict:
    """Return high-level aggregate counts for the overview endpoint."""
    respondents = _load_population()
    total = len(respondents)
    branches = respondents["branch"].value_counts().to_dict()
    years = respondents["year"].value_counts().to_dict()
    subjects = respondents["preferred_subject_category"].value_counts().to_dict()
    primary_reasons = respondents["primary_reason"].value_counts().to_dict()
    return {
        "total_respondents": total,
        "cohort": "engineering_only",
        "branches": branches,
        "years": years,
        "preferred_subject_categories": subjects,
        "primary_reasons": primary_reasons,
    }
