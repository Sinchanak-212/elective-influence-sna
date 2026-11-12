import { useState } from 'react'
import { api, type RecommendationItem, isApiError } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { LoadingState, EmptyState, UnverifiedNote } from '../components/ui/States'
import { InterpretationNote } from '../components/ui/States'
import { Search, AlertTriangle } from 'lucide-react'

const BRANCHES = ['CSE', 'ECE', 'ME', 'EE', 'IT', 'CE', 'Other']
const YEARS = ['1', '2', '3', '4']

export function ElectiveFinder() {
  const [branch, setBranch] = useState('')
  const [year, setYear] = useState('')
  const [interestInput, setInterestInput] = useState('')
  const [interests, setInterests] = useState<string[]>([])
  const [results, setResults] = useState<RecommendationItem[] | null>(null)
  const [meta, setMeta] = useState<{ note: string | null; methodNote: string | null; fallback: string | null; unverified: string | null } | null>(null)
  const [loading, setLoading] = useState(false)
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  function addInterest() {
    const v = interestInput.trim().toLowerCase()
    if (v && !interests.includes(v)) setInterests(prev => [...prev, v])
    setInterestInput('')
  }

  async function search() {
    setLoading(true)
    setErrorMsg(null)
    try {
      const res = await api.recommendations({
        branch: branch || undefined,
        year: year || undefined,
        interests,
        max_results: 8,
      })
      setResults(res.recommendations)
      setMeta({
        note: res.fallback_note,
        methodNote: res.methodology_note,
        fallback: res.fallback_note,
        unverified: res.unverified_catalogue_note,
      })
    } catch (e) {
      setErrorMsg(e instanceof Error && isApiError(e) ? e.message : isApiError(e) ? e.message : 'Request failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <PageHeader
        title="Elective Finder"
        description="Rule-based recommendation — backend powered, not ML"
      />

      <Card className="mb-5">
        <CardHeader><CardTitle>Your Profile</CardTitle></CardHeader>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <label className="mb-1 block text-xs text-[#8892a4]">Branch</label>
            <select
              value={branch}
              onChange={e => setBranch(e.target.value)}
              className="w-full rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] outline-none focus:border-[#8b5cf6]"
            >
              <option value="">Any</option>
              {BRANCHES.map(b => <option key={b}>{b}</option>)}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs text-[#8892a4]">Year</label>
            <select
              value={year}
              onChange={e => setYear(e.target.value)}
              className="w-full rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] outline-none focus:border-[#8b5cf6]"
            >
              <option value="">Any</option>
              {YEARS.map(y => <option key={y}>{y}</option>)}
            </select>
          </div>
          <div className="sm:col-span-2">
            <label className="mb-1 block text-xs text-[#8892a4]">Your Interests</label>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="e.g. AI, data, robotics…"
                value={interestInput}
                onChange={e => setInterestInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && addInterest()}
                className="flex-1 rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] placeholder-[#8892a4] outline-none focus:border-[#8b5cf6]"
              />
              <Button size="sm" variant="secondary" onClick={addInterest}>Add</Button>
            </div>
            {interests.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {interests.map(i => (
                  <button
                    key={i}
                    onClick={() => setInterests(prev => prev.filter(x => x !== i))}
                    className="flex items-center gap-1 rounded-full border border-[#8b5cf6]/30 bg-[#8b5cf6]/10 px-2 py-0.5 text-xs text-[#a78bfa] hover:border-red-500/40 hover:text-red-400"
                  >
                    {i} ×
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
        <div className="mt-4 flex justify-end">
          <Button onClick={search} disabled={loading || interests.length === 0}>
            <Search className="h-4 w-4" />
            {loading ? 'Searching…' : 'Find Electives'}
          </Button>
        </div>
      </Card>

      {errorMsg && (
        <div className="mb-4 flex gap-2 rounded-lg border border-red-500/20 bg-red-500/5 p-3">
          <AlertTriangle className="h-4 w-4 shrink-0 text-red-400" />
          <p className="text-xs text-red-300">{errorMsg}</p>
        </div>
      )}

      {loading && <LoadingState message="Finding matches…" />}

      {!loading && results !== null && (
        <>
          {results.length === 0 ? (
            <EmptyState message={meta?.fallback ?? 'No matches found. Try different interests.'} />
          ) : (
            <div className="space-y-3">
              {results.map(r => (
                <Card key={r.elective_id}>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-[#e2e8f0]">{r.elective_name}</p>
                        {!r.data_verified && <Badge variant="amber" size="xs">Unverified</Badge>}
                        <Badge variant="purple" size="xs">Score {r.score}</Badge>
                      </div>
                      <ul className="mt-2 space-y-0.5">
                        {r.match_reasons.map((reason, i) => (
                          <li key={i} className="flex items-start gap-1.5 text-xs text-[#8892a4]">
                            <span className="mt-0.5 text-[#22d3ee]">✓</span> {reason}
                          </li>
                        ))}
                      </ul>
                      {r.warnings.map((w, i) => (
                        <div key={i} className="mt-1 flex items-start gap-1.5 text-xs text-amber-300">
                          <AlertTriangle className="mt-0.5 h-3 w-3 shrink-0" /> {w}
                        </div>
                      ))}
                    </div>
                    <div className="text-right text-xs text-[#8892a4]">
                      {r.difficulty_level && <div>Difficulty: {r.difficulty_level}</div>}
                      {r.expected_workload_hours_per_week && <div>~{r.expected_workload_hours_per_week} hrs/wk</div>}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}

          {meta?.unverified && <UnverifiedNote note={meta.unverified} />}
          {meta?.methodNote && <InterpretationNote note={meta.methodNote} />}
        </>
      )}
    </div>
  )
}
