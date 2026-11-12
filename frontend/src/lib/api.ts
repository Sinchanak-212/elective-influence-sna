/**
 * Centralized API service layer.
 * All backend calls go through here — no fetch() calls in components.
 *
 * Base URL is read from VITE_API_BASE_URL env var (default: /api via Vite proxy).
 * In production set VITE_API_BASE_URL=http://localhost:8000
 */

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

// ─── Generic fetch helper ────────────────────────────────────────────────────

export interface ApiError {
  name: 'ApiError'
  status: number
  code: string
  message: string
}

export function makeApiError(status: number, code: string, message: string): ApiError {
  return { name: 'ApiError', status, code, message }
}

export function isApiError(e: unknown): e is ApiError {
  return typeof e === 'object' && e !== null && (e as ApiError).name === 'ApiError'
}

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    let code = 'unknown_error'
    let message = `HTTP ${res.status}`
    try {
      const body = await res.json()
      code = body?.detail?.error ?? code
      message = body?.detail?.message ?? message
    } catch { /* ignore parse error */ }
    throw makeApiError(res.status, code, message)
  }
  return res.json() as Promise<T>
}

// ─── Types ───────────────────────────────────────────────────────────────────

export interface HealthResponse {
  status: string
  version: string
}

export interface OverviewResponse {
  cohort: string
  total_respondents: number
  note: string
  branches: Record<string, number>
  years: Record<string, number>
  preferred_subject_categories: Record<string, number>
  primary_reasons: Record<string, number>
}

export interface NodeMetrics {
  degree: number
  degree_centrality: number | null
  betweenness_centrality: number | null
  closeness_centrality: number | null
  weighted_degree_strength: number | null
}

export interface NetworkNode {
  id: string
  branch: string
  year: string
  preferred_subject_category: string
  component_id: number
  is_isolated: boolean
  metrics: NodeMetrics
}

export interface NetworkEdge {
  source: string
  target: string
  weight: number | null
  shared_attributes: string
}

export interface GraphSummary {
  node_count: number
  edge_count: number
  density: number | null
  connected_component_count: number
  largest_component_size: number
  isolated_node_count: number
}

export interface NetworkResponse {
  threshold: number
  graph_summary: GraphSummary
  interpretation_note: string
  nodes: NetworkNode[]
  edges: NetworkEdge[]
}

export interface Community {
  community_id: number
  size: number
  dominant_subject: string
  dominant_subject_share: number | null
  dominant_branch: string
  dominant_branch_share: number | null
  weighted_modularity: number | null
}

export interface AlgorithmResult {
  algorithm: string
  community_count: number
  weighted_modularity: number | null
  communities: Community[]
}

export interface AttributeMixing {
  attribute: string
  matching_edge_fraction: number | null
  weighted_categorical_assortativity: number | null
  assortativity_defined: boolean
}

export interface CommunitiesResponse {
  threshold: number
  interpretation_note: string
  algorithms: AlgorithmResult[]
  attribute_mixing: AttributeMixing[]
}

export interface ThresholdRow {
  threshold: number
  is_primary: boolean
  node_count: number
  edge_count: number
  density: number | null
  connected_component_count: number
  largest_component_size: number
  isolated_node_count: number
}

export interface ThresholdSensitivityResponse {
  thresholds: ThresholdRow[]
}

export interface DistributionRow {
  category: string
  response_class: string
  count: number
  percent: number | null
  denominator: number
}

export interface StatTest {
  test_used: string
  test_statistic: number | null
  p_value: number | null
  sample_size: number
  denominator: number
  note: string
}

export interface PeerDiscussionResponse {
  discussion_status: DistributionRow[]
  best_friend_same_elective: DistributionRow[]
  best_friend_choice_reason: DistributionRow[]
  best_friend_marks_range: DistributionRow[]
  discussion_vs_friend_same_elective: StatTest
  interpretation_note: string
}

export interface OrdinalAssociation {
  analysis: string
  sample_size: number
  denominator: number
  excluded_count: number
  spearman_rho: number | null
  p_value: number | null
  p_value_method: string
}

export interface AcademicResponse {
  academic_outcome: DistributionRow[]
  course_difficulty: DistributionRow[]
  final_score_range: DistributionRow[]
  study_hours_per_week: DistributionRow[]
  score_met_expectations: DistributionRow[]
  ordinal_associations: OrdinalAssociation[]
  interpretation_note: string
}

export interface Elective {
  id: string
  code: string | null
  name: string
  description: string | null
  topics: string[]
  prerequisites: string[]
  difficulty_level: string | null
  expected_workload_hours_per_week: number | null
  assessment_pattern: string | null
  skills_gained: string[]
  suitable_interests: string[]
  career_areas: string[]
  materials: unknown[]
  data_verified: boolean
}

export interface ElectivesResponse {
  count: number
  catalogue_note: string
  electives: Elective[]
}

export interface MaterialsResponse {
  elective_id: string
  elective_name: string
  materials_available: boolean
  materials_note: string | null
  materials: unknown[]
}

export interface PlannerProfile {
  token: string
  alias: string | null
  branch: string | null
  year: string | null
  interests: string[]
  preferred_subject_areas: string[]
  completed_electives: string[]
  shortlisted_electives: string[]
  saved_comparisons: string[][]
}

export interface RecommendationItem {
  elective_id: string
  elective_name: string
  code: string | null
  score: number
  data_verified: boolean
  match_reasons: string[]
  warnings: string[]
  topics: string[]
  skills_gained: string[]
  career_areas: string[]
  difficulty_level: string | null
  expected_workload_hours_per_week: number | null
  prerequisites: string[]
  materials_available: boolean
}

export interface RecommendationsResponse {
  recommendations: RecommendationItem[]
  count: number
  catalogue_available: boolean
  unverified_catalogue_note: string | null
  methodology_note: string | null
  fallback_note: string | null
}

export interface RecommendationRequest {
  branch?: string
  year?: string
  interests?: string[]
  preferred_subject_areas?: string[]
  completed_electives?: string[]
  max_results?: number
}

// ─── API functions ────────────────────────────────────────────────────────────

export const api = {
  health: () => request<HealthResponse>('/health'),

  analytics: {
    overview: () => request<OverviewResponse>('/analytics/overview'),
    network: (threshold = 0.5) =>
      request<NetworkResponse>(`/analytics/network?threshold=${threshold}`),
    communities: (threshold = 0.5) =>
      request<CommunitiesResponse>(`/analytics/communities?threshold=${threshold}`),
    thresholdSensitivity: () =>
      request<ThresholdSensitivityResponse>('/analytics/threshold-sensitivity'),
    peerDiscussion: () =>
      request<PeerDiscussionResponse>('/analytics/peer-discussion'),
    academic: () => request<AcademicResponse>('/analytics/academic'),
  },

  electives: {
    list: () => request<ElectivesResponse>('/electives'),
    get: (id: string) => request<Elective>(`/electives/${id}`),
    materials: (id: string) => request<MaterialsResponse>(`/electives/${id}/materials`),
  },

  planner: {
    create: (profile: Omit<PlannerProfile, 'shortlisted_electives' | 'saved_comparisons'>) =>
      request<{ created: boolean; token: string }>('/planner/profile', {
        method: 'POST',
        body: JSON.stringify(profile),
      }),
    get: (token: string) => request<PlannerProfile>(`/planner/profile/${token}`),
    update: (token: string, profile: Omit<PlannerProfile, 'shortlisted_electives' | 'saved_comparisons'>) =>
      request<{ updated: boolean; token: string }>(`/planner/profile/${token}`, {
        method: 'PATCH',
        body: JSON.stringify(profile),
      }),
    delete: (token: string) =>
      request<{ deleted: boolean; token: string }>(`/planner/profile/${token}`, {
        method: 'DELETE',
      }),
    getShortlist: (token: string) =>
      request<{ token: string; shortlisted_electives: string[] }>(`/planner/profile/${token}/shortlist`),
    updateShortlist: (token: string, elective_ids: string[]) =>
      request<{ token: string; shortlisted_electives: string[] }>(`/planner/profile/${token}/shortlist`, {
        method: 'PUT',
        body: JSON.stringify({ elective_ids }),
      }),
    addComparison: (token: string, elective_ids: string[]) =>
      request<{ token: string; comparison_index: number; elective_ids: string[] }>(
        `/planner/profile/${token}/comparisons`,
        { method: 'POST', body: JSON.stringify({ elective_ids }) }
      ),
    getComparisons: (token: string) =>
      request<{ token: string; saved_comparisons: string[][] }>(`/planner/profile/${token}/comparisons`),
  },

  recommendations: (body: RecommendationRequest) =>
    request<RecommendationsResponse>('/recommendations', {
      method: 'POST',
      body: JSON.stringify(body),
    }),
}
