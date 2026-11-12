"""
API integration tests.

Run with:
    pytest api/tests/ -v

These tests use FastAPI's TestClient (synchronous HTTPX).  Analytics endpoints
that require the survey CSV will return 503 when the file is absent; the tests
assert on that graceful failure rather than skipping.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure project root is on sys.path before importing main
import sys
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import app  # noqa: E402

client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_root_health(self):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_analytics_health(self):
        r = client.get("/api/analytics/health")
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# Analytics — graceful degradation when CSV is absent
# ---------------------------------------------------------------------------

class TestAnalytics:
    def test_overview_without_csv(self):
        r = client.get("/api/analytics/overview")
        assert r.status_code in (200, 503)
        if r.status_code == 503:
            assert r.json()["detail"]["error"] == "data_unavailable"

    def test_network_valid_threshold(self):
        r = client.get("/api/analytics/network?threshold=0.50")
        assert r.status_code in (200, 503)

    def test_network_invalid_threshold(self):
        r = client.get("/api/analytics/network?threshold=0.99")
        assert r.status_code == 422
        body = r.json()
        assert body["detail"]["error"] == "invalid_threshold"

    def test_communities_valid_threshold(self):
        r = client.get("/api/analytics/communities?threshold=0.30")
        assert r.status_code in (200, 503)

    def test_communities_invalid_threshold(self):
        r = client.get("/api/analytics/communities?threshold=0.75")
        assert r.status_code == 422

    def test_threshold_sensitivity(self):
        r = client.get("/api/analytics/threshold-sensitivity")
        assert r.status_code in (200, 503)

    def test_peer_discussion(self):
        r = client.get("/api/analytics/peer-discussion")
        assert r.status_code in (200, 503)

    def test_academic(self):
        r = client.get("/api/analytics/academic")
        assert r.status_code in (200, 503)


# ---------------------------------------------------------------------------
# Electives
# ---------------------------------------------------------------------------

class TestElectives:
    def test_list_electives(self):
        r = client.get("/api/electives")
        assert r.status_code == 200
        body = r.json()
        assert "electives" in body
        assert "count" in body
        assert isinstance(body["electives"], list)

    def test_get_known_elective(self):
        # Assumes EL001 is in the catalogue; skip gracefully if catalogue is empty
        r_list = client.get("/api/electives")
        electives = r_list.json().get("electives", [])
        if not electives:
            pytest.skip("Catalogue is empty; nothing to fetch by ID")
        eid = electives[0]["id"]
        r = client.get(f"/api/electives/{eid}")
        assert r.status_code == 200
        assert r.json()["id"] == eid

    def test_get_unknown_elective(self):
        r = client.get("/api/electives/DOES_NOT_EXIST")
        assert r.status_code == 404
        assert r.json()["detail"]["error"] == "not_found"

    def test_materials_known(self):
        r_list = client.get("/api/electives")
        electives = r_list.json().get("electives", [])
        if not electives:
            pytest.skip("Catalogue is empty")
        eid = electives[0]["id"]
        r = client.get(f"/api/electives/{eid}/materials")
        assert r.status_code == 200
        body = r.json()
        assert "materials" in body
        assert "materials_available" in body

    def test_materials_unknown(self):
        r = client.get("/api/electives/DOES_NOT_EXIST/materials")
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Planner
# ---------------------------------------------------------------------------

class TestPlanner:
    @pytest.fixture()
    def token(self) -> str:
        return uuid.uuid4().hex  # 32 hex chars — valid token format

    def test_create_profile(self, token):
        r = client.post("/api/planner/profile", json={"token": token})
        assert r.status_code == 201
        assert r.json()["token"] == token

    def test_create_profile_duplicate(self, token):
        client.post("/api/planner/profile", json={"token": token})
        r = client.post("/api/planner/profile", json={"token": token})
        assert r.status_code == 409

    def test_get_profile(self, token):
        client.post("/api/planner/profile", json={
            "token": token,
            "branch": "CSE",
            "year": "3",
            "interests": ["AI", "data"],
        })
        r = client.get(f"/api/planner/profile/{token}")
        assert r.status_code == 200
        body = r.json()
        assert body["branch"] == "CSE"
        assert "AI" in body["interests"]

    def test_get_missing_profile(self, token):
        r = client.get(f"/api/planner/profile/{token}")
        assert r.status_code == 404

    def test_update_profile(self, token):
        client.post("/api/planner/profile", json={"token": token})
        r = client.patch(f"/api/planner/profile/{token}", json={
            "token": token,
            "branch": "ECE",
            "year": "4",
            "interests": ["embedded", "IoT"],
        })
        assert r.status_code == 200
        updated = client.get(f"/api/planner/profile/{token}").json()
        assert updated["branch"] == "ECE"

    def test_shortlist(self, token):
        client.post("/api/planner/profile", json={"token": token})
        r = client.put(
            f"/api/planner/profile/{token}/shortlist",
            json={"elective_ids": ["EL001", "EL003"]},
        )
        assert r.status_code == 200
        got = client.get(f"/api/planner/profile/{token}/shortlist").json()
        assert set(got["shortlisted_electives"]) == {"EL001", "EL003"}

    def test_comparison(self, token):
        client.post("/api/planner/profile", json={"token": token})
        r = client.post(
            f"/api/planner/profile/{token}/comparisons",
            json={"elective_ids": ["EL001", "EL002"]},
        )
        assert r.status_code == 200
        got = client.get(f"/api/planner/profile/{token}/comparisons").json()
        assert len(got["saved_comparisons"]) >= 1

    def test_comparison_too_few(self, token):
        client.post("/api/planner/profile", json={"token": token})
        r = client.post(
            f"/api/planner/profile/{token}/comparisons",
            json={"elective_ids": ["EL001"]},  # only one
        )
        assert r.status_code == 422

    def test_delete_profile(self, token):
        client.post("/api/planner/profile", json={"token": token})
        r = client.delete(f"/api/planner/profile/{token}")
        assert r.status_code == 200
        r2 = client.get(f"/api/planner/profile/{token}")
        assert r2.status_code == 404

    def test_invalid_token(self):
        r = client.post("/api/planner/profile", json={"token": "x"})  # too short
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

class TestRecommendations:
    def test_recommendation_with_interests(self):
        r = client.post("/api/recommendations", json={
            "interests": ["data", "AI", "statistics"],
            "preferred_subject_areas": ["data"],
        })
        assert r.status_code == 200
        body = r.json()
        assert "recommendations" in body
        assert "count" in body
        assert "methodology_note" in body

    def test_recommendation_no_match(self):
        r = client.post("/api/recommendations", json={
            "interests": ["quantum_physics_xyz_no_match"],
        })
        assert r.status_code == 200
        body = r.json()
        # Catalogue either empty or fallback_note set
        if body["count"] == 0:
            assert body["fallback_note"] is not None

    def test_recommendation_exclude_completed(self):
        r = client.post("/api/recommendations", json={
            "interests": ["data", "AI"],
            "completed_electives": ["EL001"],
        })
        assert r.status_code == 200
        ids = [rec["elective_id"] for rec in r.json()["recommendations"]]
        assert "EL001" not in ids

    def test_recommendation_max_results(self):
        r = client.post("/api/recommendations", json={
            "interests": ["data", "AI", "programming", "networking", "hardware"],
            "max_results": 2,
        })
        assert r.status_code == 200
        assert len(r.json()["recommendations"]) <= 2

    def test_recommendation_invalid_max(self):
        r = client.post("/api/recommendations", json={
            "interests": ["data"],
            "max_results": 0,
        })
        assert r.status_code == 422
