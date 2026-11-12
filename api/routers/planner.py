"""
Student planner endpoints — pseudonymous elective assistant.

Storage design
--------------
Profiles are stored in a single JSON file at data/planner/profiles.json.
This is NOT a secure authentication system: it is a lightweight session store
suitable for a local development / research assistant context.

A profile is identified by a client-generated token (UUID).  The API never
issues tokens; it stores and retrieves whatever token the client sends.

Do NOT store:
  - Real student IDs or registration numbers.
  - Contact details, full names, or any other identifying information.

If you need real authentication or persistent multi-user storage, replace the
_load/_save functions below with a proper database and auth layer.  The API
contract (request/response shapes) is designed to be stable across that
migration.

Persistence note
----------------
The JSON file approach is appropriate for a single-server research tool with
a small number of users.  It is not appropriate for production multi-server
deployment or high-concurrency access.  For production: replace with SQLite
(via SQLAlchemy) or a lightweight hosted database.
"""

from __future__ import annotations

import json
import re
import uuid
from pathlib import Path
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

ROOT = Path(__file__).resolve().parents[2]
PROFILES_PATH = ROOT / "data" / "planner" / "profiles.json"
PROFILES_PATH.parent.mkdir(parents=True, exist_ok=True)

router = APIRouter(prefix="/api/planner", tags=["planner"])

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"^[a-zA-Z0-9_\-]{8,64}$")


class ProfileCreate(BaseModel):
    """Fields required when creating a new profile."""
    token: str = Field(
        description=(
            "Client-generated pseudonymous token (UUID or similar). "
            "Do not use a real student ID or name."
        )
    )
    alias: Optional[str] = Field(default=None, max_length=40)
    branch: Optional[str] = Field(default=None, max_length=80)
    year: Optional[str] = Field(default=None, max_length=20)
    interests: List[str] = Field(default_factory=list)
    preferred_subject_areas: List[str] = Field(default_factory=list)
    completed_electives: List[str] = Field(default_factory=list)

    @field_validator("token")
    @classmethod
    def validate_token(cls, v: str) -> str:
        if not _TOKEN_RE.match(v):
            raise ValueError(
                "token must be 8–64 characters, alphanumeric with hyphens/underscores only"
            )
        return v


class ShortlistUpdate(BaseModel):
    elective_ids: List[str]


class ComparisonUpdate(BaseModel):
    elective_ids: List[str] = Field(description="2–4 elective IDs to compare")

    @field_validator("elective_ids")
    @classmethod
    def at_least_two(cls, v: list) -> list:
        if len(v) < 2:
            raise ValueError("Provide at least two elective IDs to compare")
        return v


# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

def _load_profiles() -> dict[str, Any]:
    if not PROFILES_PATH.exists():
        return {}
    with PROFILES_PATH.open(encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError:
            return {}


def _save_profiles(profiles: dict[str, Any]) -> None:
    with PROFILES_PATH.open("w", encoding="utf-8") as fh:
        json.dump(profiles, fh, ensure_ascii=False, indent=2)


def _get_or_404(token: str) -> dict[str, Any]:
    profiles = _load_profiles()
    if token not in profiles:
        raise HTTPException(
            status_code=404,
            detail={"error": "profile_not_found", "token": token},
        )
    return profiles[token]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/profile", status_code=201)
async def create_profile(body: ProfileCreate):
    """
    Create a pseudonymous student profile.

    The token is supplied by the client — use a UUID generated in the browser.
    No real student ID, name, or contact detail should be sent.

    Returns 409 if the token already exists.
    """
    profiles = _load_profiles()
    if body.token in profiles:
        raise HTTPException(
            status_code=409,
            detail={"error": "token_already_exists", "token": body.token},
        )
    profile = {
        "token": body.token,
        "alias": body.alias,
        "branch": body.branch,
        "year": body.year,
        "interests": body.interests,
        "preferred_subject_areas": body.preferred_subject_areas,
        "completed_electives": body.completed_electives,
        "shortlisted_electives": [],
        "saved_comparisons": [],
    }
    profiles[body.token] = profile
    _save_profiles(profiles)
    return {"created": True, "token": body.token}


@router.get("/profile/{token}")
async def get_profile(token: str):
    """Retrieve a saved profile by its token."""
    return _get_or_404(token)


@router.patch("/profile/{token}")
async def update_profile(token: str, body: ProfileCreate):
    """
    Update profile fields.  Token in path must match body token.
    """
    if token != body.token:
        raise HTTPException(
            status_code=422,
            detail={"error": "token_mismatch"},
        )
    profiles = _load_profiles()
    if token not in profiles:
        raise HTTPException(
            status_code=404,
            detail={"error": "profile_not_found", "token": token},
        )
    existing = profiles[token]
    existing.update({
        "alias": body.alias,
        "branch": body.branch,
        "year": body.year,
        "interests": body.interests,
        "preferred_subject_areas": body.preferred_subject_areas,
        "completed_electives": body.completed_electives,
    })
    profiles[token] = existing
    _save_profiles(profiles)
    return {"updated": True, "token": token}


@router.delete("/profile/{token}", status_code=200)
async def delete_profile(token: str):
    """Delete a profile and all associated saved data."""
    profiles = _load_profiles()
    if token not in profiles:
        raise HTTPException(
            status_code=404,
            detail={"error": "profile_not_found", "token": token},
        )
    del profiles[token]
    _save_profiles(profiles)
    return {"deleted": True, "token": token}


# ---------------------------------------------------------------------------
# Shortlist
# ---------------------------------------------------------------------------

@router.put("/profile/{token}/shortlist")
async def update_shortlist(token: str, body: ShortlistUpdate):
    """Replace the shortlisted electives list for this profile."""
    profiles = _load_profiles()
    _get_or_404(token)
    profiles[token]["shortlisted_electives"] = list(dict.fromkeys(body.elective_ids))
    _save_profiles(profiles)
    return {"token": token, "shortlisted_electives": profiles[token]["shortlisted_electives"]}


@router.get("/profile/{token}/shortlist")
async def get_shortlist(token: str):
    """Return the shortlisted electives for this profile."""
    profile = _get_or_404(token)
    return {"token": token, "shortlisted_electives": profile.get("shortlisted_electives", [])}


# ---------------------------------------------------------------------------
# Comparisons
# ---------------------------------------------------------------------------

@router.post("/profile/{token}/comparisons")
async def save_comparison(token: str, body: ComparisonUpdate):
    """
    Save a set of elective IDs as a named comparison for this profile.
    Returns the index of the saved comparison.
    """
    profiles = _load_profiles()
    _get_or_404(token)
    comparisons: list = profiles[token].setdefault("saved_comparisons", [])
    comparisons.append(body.elective_ids)
    _save_profiles(profiles)
    return {"token": token, "comparison_index": len(comparisons) - 1, "elective_ids": body.elective_ids}


@router.get("/profile/{token}/comparisons")
async def get_comparisons(token: str):
    """Return all saved comparisons for this profile."""
    profile = _get_or_404(token)
    return {"token": token, "saved_comparisons": profile.get("saved_comparisons", [])}
