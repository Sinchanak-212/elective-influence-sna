"""
Elective catalogue endpoints.

Data comes from data/catalogue/electives.json.  Every field that has not been
verified against the institution's official handbook is explicitly null in that
file and is surfaced as null here — never invented.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE_PATH = ROOT / "data" / "catalogue" / "electives.json"

router = APIRouter(prefix="/api/electives", tags=["electives"])


def _load_catalogue() -> list[dict]:
    if not CATALOGUE_PATH.exists():
        return []
    with CATALOGUE_PATH.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data.get("electives", [])


# ---------------------------------------------------------------------------
# GET /api/electives
# ---------------------------------------------------------------------------

@router.get("")
async def list_electives():
    """
    List all electives in the catalogue.

    Fields that have not been verified against official course documentation
    are returned as null.  The `data_verified` flag on each record indicates
    whether the entry has been reviewed against the institution's syllabus.
    """
    electives = _load_catalogue()
    return {
        "count": len(electives),
        "catalogue_note": (
            "Elective details are placeholders until verified against the "
            "institution's official syllabus or academic handbook. "
            "Fields marked null have not yet been confirmed."
        ),
        "electives": electives,
    }


# ---------------------------------------------------------------------------
# GET /api/electives/{elective_id}
# ---------------------------------------------------------------------------

@router.get("/{elective_id}")
async def get_elective(elective_id: str):
    """Return a single elective record by its ID."""
    electives = _load_catalogue()
    match = next((e for e in electives if e["id"] == elective_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail={"error": "not_found", "elective_id": elective_id})
    return match


# ---------------------------------------------------------------------------
# GET /api/electives/{elective_id}/materials
# ---------------------------------------------------------------------------

@router.get("/{elective_id}/materials")
async def get_elective_materials(elective_id: str):
    """
    Return learning materials for a specific elective.

    Materials are only listed when verified entries exist in the catalogue.
    """
    electives = _load_catalogue()
    match = next((e for e in electives if e["id"] == elective_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail={"error": "not_found", "elective_id": elective_id})

    materials = match.get("materials", [])
    return {
        "elective_id": elective_id,
        "elective_name": match.get("name"),
        "materials_available": len(materials) > 0,
        "materials_note": (
            None if materials
            else "No verified materials have been added for this elective yet. "
                 "Add entries to data/catalogue/electives.json once confirmed."
        ),
        "materials": materials,
    }
