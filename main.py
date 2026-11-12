"""
Elective Influence Analytics — FastAPI application entry point.

Run:
    uvicorn main:app --reload --port 8000

The API serves:
  /api/health                        — liveness check
  /api/analytics/*                   — Priority 1-4 research analysis
  /api/electives/*                   — configurable elective catalogue
  /api/planner/*                     — pseudonymous student planner
  /api/recommendations               — rule-based elective matching
  /docs                              — Swagger UI
  /redoc                             — ReDoc
"""

from __future__ import annotations

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import analytics, electives, planner, recommendations

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Elective Influence Analytics API",
    description=(
        "Research analytics and elective assistant for an engineering cohort. "
        "Analytics endpoints expose the existing Priority 1-4 SNA study. "
        "Elective and planner endpoints support a student-facing assistant. "
        "No respondent-level data is surfaced publicly."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

# Allow the frontend dev server origin(s).  Extend via CORS_ORIGINS env var,
# comma-separated.  Example: CORS_ORIGINS=http://localhost:3000,http://localhost:5173
_default_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]
_extra = os.getenv("CORS_ORIGINS", "")
_allowed_origins = _default_origins + [o.strip() for o in _extra.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(analytics.router)
app.include_router(electives.router)
app.include_router(planner.router)
app.include_router(recommendations.router)


# ---------------------------------------------------------------------------
# Root redirect to docs
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


# ---------------------------------------------------------------------------
# Global health check (also at /api/analytics/health via analytics router)
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
