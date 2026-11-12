# API Contract — Elective Influence Analytics

**Base URL (development):** `http://localhost:8000`  
**OpenAPI docs:** `http://localhost:8000/docs`  
**Version:** 1.0.0

---

## General conventions

| Property | Value |
|---|---|
| Content-Type | `application/json` |
| CORS | `localhost:3000`, `localhost:5173` by default; extend via `CORS_ORIGINS` env var |
| Auth | None in v1 (planner uses client-token; no session auth) |
| Errors | `{ "detail": { "error": "<code>", ... } }` |
| Analytics without CSV | `503` with `error: data_unavailable` |
| Unknown IDs | `404` with `error: not_found` |
| Validation failure | `422` (FastAPI default) |

---

## Health

### `GET /api/health`

```json
{ "status": "ok", "version": "1.0.0" }
```

---

## Analytics

All analytics endpoints require `data/raw/survey_responses_anonymized.csv`.  
When absent they return `503`:

```json
{
  "detail": {
    "error": "data_unavailable",
    "message": "Survey data file not found. Place survey_responses_anonymized.csv in data/raw/."
  }
}
```

### `GET /api/analytics/overview`

Aggregate cohort counts. No respondent-level data.

```json
{
  "cohort": "engineering_only",
  "total_respondents": 24,
  "note": "...",
  "branches": { "CSE": 10, "ECE": 7, ... },
  "years": { "3": 14, "4": 10 },
  "preferred_subject_categories": { "CS": 8, ... },
  "primary_reasons": { "Interest": 15, ... }
}
```

### `GET /api/analytics/network?threshold=0.50`

Query params: `threshold` ∈ `{0.30, 0.50, 0.60}` (default `0.50`)

```json
{
  "threshold": 0.5,
  "graph_summary": {
    "node_count": 24,
    "edge_count": 42,
    "density": 0.1522,
    "connected_component_count": 3,
    "largest_component_size": 18,
    "isolated_node_count": 2
  },
  "interpretation_note": "...",
  "nodes": [
    {
      "id": "ENG_001",
      "branch": "CSE",
      "year": "3",
      "preferred_subject_category": "CS",
      "component_id": 0,
      "is_isolated": false,
      "metrics": {
        "degree": 5,
        "degree_centrality": 0.2174,
        "betweenness_centrality": 0.045,
        "closeness_centrality": 0.391,
        "weighted_degree_strength": 2.34
      }
    }
  ],
  "edges": [
    {
      "source": "ENG_001",
      "target": "ENG_007",
      "weight": 0.72,
      "shared_attributes": "branch+subject"
    }
  ]
}
```

Invalid threshold → `422`:

```json
{ "detail": { "error": "invalid_threshold", "valid_values": [0.3, 0.5, 0.6] } }
```

### `GET /api/analytics/communities?threshold=0.50`

Same `threshold` param as `/network`.

```json
{
  "threshold": 0.5,
  "interpretation_note": "...",
  "algorithms": [
    {
      "algorithm": "louvain",
      "community_count": 4,
      "weighted_modularity": 0.312,
      "communities": [
        {
          "community_id": 0,
          "size": 8,
          "dominant_subject": "CS",
          "dominant_subject_share": 0.75,
          "dominant_branch": "CSE",
          "dominant_branch_share": 0.625,
          "weighted_modularity": 0.312
        }
      ]
    }
  ],
  "attribute_mixing": [
    {
      "attribute": "preferred_subject_category",
      "matching_edge_fraction": 0.57,
      "weighted_categorical_assortativity": 0.21,
      "assortativity_defined": true
    }
  ]
}
```

### `GET /api/analytics/threshold-sensitivity`

```json
{
  "thresholds": [
    {
      "threshold": 0.3,
      "is_primary": false,
      "node_count": 24,
      "edge_count": 98,
      "density": 0.3551,
      "connected_component_count": 1,
      "largest_component_size": 24,
      "isolated_node_count": 0
    }
  ]
}
```

### `GET /api/analytics/peer-discussion`

```json
{
  "discussion_status": [
    { "category": "Yes", "response_class": "positive", "count": 14, "percent": 58.3, "denominator": 24 }
  ],
  "best_friend_same_elective": [...],
  "best_friend_choice_reason": [...],
  "best_friend_marks_range": [...],
  "discussion_vs_friend_same_elective": {
    "test_used": "Fisher exact (two-sided)",
    "test_statistic": 3.21,
    "p_value": 0.09,
    "sample_size": 22,
    "denominator": 24,
    "note": "..."
  },
  "interpretation_note": "..."
}
```

### `GET /api/analytics/academic`

```json
{
  "academic_outcome": [...],
  "course_difficulty": [...],
  "final_score_range": [...],
  "study_hours_per_week": [...],
  "score_met_expectations": [...],
  "ordinal_associations": [
    {
      "analysis": "difficulty_vs_study_hours",
      "sample_size": 22,
      "denominator": 24,
      "excluded_count": 2,
      "spearman_rho": 0.31,
      "p_value": 0.17,
      "p_value_method": "permutation"
    }
  ],
  "interpretation_note": "..."
}
```

---

## Electives

### `GET /api/electives`

```json
{
  "count": 5,
  "catalogue_note": "...",
  "electives": [
    {
      "id": "EL001",
      "code": null,
      "name": "Machine Learning",
      "description": null,
      "topics": [],
      "prerequisites": [],
      "difficulty_level": null,
      "expected_workload_hours_per_week": null,
      "assessment_pattern": null,
      "skills_gained": [],
      "suitable_interests": ["data", "AI", "statistics", "programming"],
      "career_areas": [],
      "materials": [],
      "data_verified": false
    }
  ]
}
```

### `GET /api/electives/{elective_id}`

Returns the elective object or `404`.

### `GET /api/electives/{elective_id}/materials`

```json
{
  "elective_id": "EL001",
  "elective_name": "Machine Learning",
  "materials_available": false,
  "materials_note": "No verified materials have been added for this elective yet.",
  "materials": []
}
```

---

## Planner

> **Storage note:** Profiles are stored in `data/planner/profiles.json`.  
> This is a development-only file store, not an authenticated user system.  
> Do not store real student IDs, names, or contact details.  
> The client must generate and persist the token (UUID recommended).

### `POST /api/planner/profile`

**Request:**

```json
{
  "token": "550e8400e29b41d4a716446655440000",
  "alias": "Student A",
  "branch": "CSE",
  "year": "3",
  "interests": ["AI", "data", "programming"],
  "preferred_subject_areas": ["CS"],
  "completed_electives": []
}
```

**Response `201`:**

```json
{ "created": true, "token": "550e8400e29b41d4a716446655440000" }
```

**`409`** — token already exists.

### `GET /api/planner/profile/{token}`

Returns full profile or `404`.

### `PATCH /api/planner/profile/{token}`

Same body as POST. Replaces mutable fields. Token in path must match body.

### `DELETE /api/planner/profile/{token}`

```json
{ "deleted": true, "token": "..." }
```

### `PUT /api/planner/profile/{token}/shortlist`

```json
{ "elective_ids": ["EL001", "EL003"] }
```

**Response:**

```json
{ "token": "...", "shortlisted_electives": ["EL001", "EL003"] }
```

### `GET /api/planner/profile/{token}/shortlist`

```json
{ "token": "...", "shortlisted_electives": ["EL001", "EL003"] }
```

### `POST /api/planner/profile/{token}/comparisons`

```json
{ "elective_ids": ["EL001", "EL002"] }
```

**Response:**

```json
{ "token": "...", "comparison_index": 0, "elective_ids": ["EL001", "EL002"] }
```

### `GET /api/planner/profile/{token}/comparisons`

```json
{ "token": "...", "saved_comparisons": [["EL001", "EL002"]] }
```

---

## Recommendations

### `POST /api/recommendations`

**Request:**

```json
{
  "branch": "CSE",
  "year": "3",
  "interests": ["AI", "data", "statistics"],
  "preferred_subject_areas": ["CS"],
  "completed_electives": ["EL005"],
  "max_results": 5
}
```

**Response:**

```json
{
  "recommendations": [
    {
      "elective_id": "EL001",
      "elective_name": "Machine Learning",
      "code": null,
      "score": 4,
      "data_verified": false,
      "match_reasons": [
        "Matches your interest(s): ai, data, statistics.",
        "Aligns with your preferred subject area(s): cs."
      ],
      "warnings": [],
      "topics": [],
      "skills_gained": [],
      "career_areas": [],
      "difficulty_level": null,
      "expected_workload_hours_per_week": null,
      "prerequisites": [],
      "materials_available": false
    }
  ],
  "count": 1,
  "catalogue_available": true,
  "unverified_catalogue_note": "1 of 1 result(s) are from unverified catalogue entries...",
  "methodology_note": "Matching is rule-based: electives are ranked by overlap between your stated interests and the elective's suitable_interests tags...",
  "fallback_note": null
}
```

**When catalogue is empty:**

```json
{
  "recommendations": [],
  "count": 0,
  "catalogue_available": false,
  "fallback_note": "No elective catalogue data is available yet. Populate data/catalogue/electives.json...",
  "methodology_note": null
}
```

---

## Frontend integration checklist

- [ ] Read `CORS_ORIGINS` from an env file (e.g. `.env.local`), not hardcoded.
- [ ] Generate a UUID token in the browser and persist it in `localStorage` (or a cookie).  Warn the user clearly that this is not a secure account — clearing storage loses their saved data.
- [ ] Treat any `data_verified: false` field on an elective as provisional.
- [ ] Handle `503` from analytics gracefully (show "Research data loading…" or "Data not available on this instance").
- [ ] Display `methodology_note` and `interpretation_note` on analytics and recommendation views.
- [ ] Do not display raw respondent IDs as names.
