"""
Recommendation endpoints — rule-based elective matching.

Design principles
-----------------
- Transparent: every recommendation carries a plain-English reason list.
- Honest: confidence depends on data_verified status of catalogue entries.
- Conservative: does NOT use the 24-response survey as a predictive model.
- Fallback-aware: when the catalogue is empty or unverified, the endpoint says
  so rather than fabricating recommendations.

No machine-learning model is used here.  Matching is based on set intersection
of a student's self-reported interests and the elective's suitable_interests
list in data/catalogue/electives.json.  When official catalogue fields
(difficulty, prerequisites) have been verified, those are factored in too.

Recommendation inputs
---------------------
- branch          (str, optional) — engineering branch
- year            (str, optional) — academic year
- interests       (list of str)   — freeform interest tags
- preferred_subject_areas (list)  — subject categories
- completed_electives  (list)     — IDs of electives already done
- max_results     (int)           — cap (default 5)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE_PATH = ROOT / "data" / "catalogue" / "electives.json"

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


# ---------------------------------------------------------------------------
# Request model
# ---------------------------------------------------------------------------

class RecommendationRequest(BaseModel):
    branch: Optional[str] = None
    year: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    preferred_subject_areas: List[str] = Field(default_factory=list)
    completed_electives: List[str] = Field(default_factory=list)
    max_results: int = Field(default=5, ge=1, le=20)

    @field_validator("interests", "preferred_subject_areas", mode="before")
    @classmethod
    def _normalise(cls, v):
        if isinstance(v, list):
            return [s.strip().lower() for s in v if s.strip()]
        return v


# ---------------------------------------------------------------------------
# Matching logic
# ---------------------------------------------------------------------------

def _score_elective(elective: dict, req: RecommendationRequest) -> dict | None:
    """
    Score one elective against the request.

    Returns a dict with score, reasons, and warnings, or None if the elective
    should be excluded entirely (already completed, no interest match at all).
    """
    eid = elective["id"]

    # Exclude already-completed electives
    if eid in req.completed_electives:
        return None

    student_tags = set(req.interests) | set(req.preferred_subject_areas)
    elective_tags = {t.strip().lower() for t in elective.get("suitable_interests", [])}

    # Compute interest overlap
    matched_tags = student_tags & elective_tags
    score = len(matched_tags)

    reasons: list[str] = []
    warnings: list[str] = []

    if matched_tags:
        reasons.append(
            f"Matches your interest(s): {', '.join(sorted(matched_tags))}."
        )

    # Preferred subject-area overlap
    pref_areas = set(req.preferred_subject_areas)
    pref_match = pref_areas & elective_tags
    if pref_match:
        score += len(pref_match)  # extra weight for preferred area match
        reasons.append(
            f"Aligns with your preferred subject area(s): {', '.join(sorted(pref_match))}."
        )

    # Branch signal — purely informational (no hard filter without verified data)
    if req.branch:
        reasons.append(f"You are studying {req.branch}; check prerequisites below.")

    # Prerequisite warning (only when verified)
    prereqs = elective.get("prerequisites", [])
    if prereqs and elective.get("data_verified"):
        completed = set(req.completed_electives)
        missing = [p for p in prereqs if p not in completed]
        if missing:
            warnings.append(
                f"You may not meet prerequisites: {', '.join(missing)}. Confirm with your department."
            )

    # Difficulty note (only when verified)
    if elective.get("difficulty_level") and elective.get("data_verified"):
        reasons.append(f"Difficulty: {elective['difficulty_level']}.")

    # Workload note (only when verified)
    wl = elective.get("expected_workload_hours_per_week")
    if wl and elective.get("data_verified"):
        reasons.append(f"Estimated workload: ~{wl} hours/week.")

    # No match at all — exclude from results
    if score == 0:
        return None

    return {
        "elective_id": eid,
        "elective_name": elective["name"],
        "code": elective.get("code"),
        "score": score,
        "data_verified": elective.get("data_verified", False),
        "match_reasons": reasons,
        "warnings": warnings,
        "topics": elective.get("topics", []),
        "skills_gained": elective.get("skills_gained", []),
        "career_areas": elective.get("career_areas", []),
        "difficulty_level": elective.get("difficulty_level"),
        "expected_workload_hours_per_week": elective.get("expected_workload_hours_per_week"),
        "prerequisites": prereqs,
        "materials_available": len(elective.get("materials", [])) > 0,
    }


def _load_catalogue() -> list[dict]:
    if not CATALOGUE_PATH.exists():
        return []
    with CATALOGUE_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("electives", [])


# ---------------------------------------------------------------------------
# POST /api/recommendations
# ---------------------------------------------------------------------------

@router.post("")
async def get_recommendations(body: RecommendationRequest):
    """
    Return rule-based elective recommendations for a student profile.

    Matching is based on interest-tag overlap with the elective catalogue.
    Recommendations are sorted by match score (descending).

    Confidence note
    ---------------
    - `data_verified: false` on a result means the elective entry has not been
      confirmed against official syllabus data.  Treat such entries as
      provisional.
    - This is NOT a predictive model.  The 24-response research survey is not
      used for matching.
    """
    catalogue = _load_catalogue()

    if not catalogue:
        return {
            "recommendations": [],
            "count": 0,
            "catalogue_available": False,
            "fallback_note": (
                "No elective catalogue data is available yet. "
                "Populate data/catalogue/electives.json with verified course "
                "information to enable recommendations."
            ),
            "methodology_note": None,
        }

    scored = []
    for elective in catalogue:
        result = _score_elective(elective, body)
        if result is not None:
            scored.append(result)

    # Sort by score descending, then alphabetically by name for stable ordering
    scored.sort(key=lambda r: (-r["score"], r["elective_name"]))
    top = scored[: body.max_results]

    unverified_count = sum(1 for r in top if not r["data_verified"])
    unverified_note = (
        f"{unverified_count} of {len(top)} result(s) are from unverified catalogue "
        "entries. Fields such as difficulty, prerequisites and workload are null "
        "until confirmed against official course documentation."
        if unverified_count
        else None
    )

    return {
        "recommendations": top,
        "count": len(top),
        "catalogue_available": True,
        "unverified_catalogue_note": unverified_note,
        "methodology_note": (
            "Matching is rule-based: electives are ranked by overlap between "
            "your stated interests and the elective's suitable_interests tags. "
            "No machine-learning model is used. "
            "These recommendations are not scientifically validated and should "
            "be one input among several when choosing an elective."
        ),
        "fallback_note": (
            None
            if top
            else (
                "No electives matched your stated interests. "
                "Try broadening your interest list, or browse the full catalogue "
                "at GET /api/electives."
            )
        ),
    }
