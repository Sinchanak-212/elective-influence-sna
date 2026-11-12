import { useParams, Link } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { LoadingState, ErrorState } from '../components/ui/States'
import { ChevronLeft } from 'lucide-react'

export function ElectiveDetail() {
  const { id } = useParams<{ id: string }>()
  const { data, status, error } = useApi(() => api.electives.get(id!), [id])

  if (status === 'loading' || status === 'idle') return <LoadingState />
  if (status === 'error') return <ErrorState message={error ?? 'Elective not found'} />

  const e = data!

  return (
    <div>
      <Link to="/electives" className="mb-4 inline-flex items-center gap-1 text-xs text-[#8892a4] hover:text-[#8b5cf6]">
        <ChevronLeft className="h-3 w-3" /> Back to Electives
      </Link>

      <PageHeader
        title={e.name}
        description={e.code ?? undefined}
        actions={!e.data_verified ? <Badge variant="amber">Unverified — provisional data</Badge> : <Badge variant="green">Verified</Badge>}
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Overview</CardTitle></CardHeader>
          <dl className="space-y-2 text-sm">
            {[
              { label: 'Difficulty', value: e.difficulty_level },
              { label: 'Workload', value: e.expected_workload_hours_per_week ? `~${e.expected_workload_hours_per_week} hrs/week` : null },
              { label: 'Assessment', value: e.assessment_pattern },
            ].map(({ label, value }) => (
              <div key={label} className="flex gap-2">
                <dt className="w-28 shrink-0 text-[#8892a4]">{label}</dt>
                <dd className="text-[#e2e8f0]">{value ?? <span className="italic text-[#8892a4]">Not verified yet</span>}</dd>
              </div>
            ))}
          </dl>
        </Card>

        <Card>
          <CardHeader><CardTitle>Prerequisites</CardTitle></CardHeader>
          {e.prerequisites.length > 0 ? (
            <ul className="space-y-1 text-sm text-[#e2e8f0]">
              {e.prerequisites.map(p => <li key={p} className="flex items-center gap-2"><span className="text-[#8b5cf6]">•</span>{p}</li>)}
            </ul>
          ) : (
            <p className="text-xs italic text-[#8892a4]">No prerequisites listed or not verified.</p>
          )}
        </Card>

        <Card>
          <CardHeader><CardTitle>Topics Covered</CardTitle></CardHeader>
          {e.topics.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {e.topics.map(t => <Badge key={t} variant="indigo">{t}</Badge>)}
            </div>
          ) : <p className="text-xs italic text-[#8892a4]">Not verified yet.</p>}
        </Card>

        <Card>
          <CardHeader><CardTitle>Skills Gained</CardTitle></CardHeader>
          {e.skills_gained.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {e.skills_gained.map(s => <Badge key={s} variant="green">{s}</Badge>)}
            </div>
          ) : <p className="text-xs italic text-[#8892a4]">Not verified yet.</p>}
        </Card>

        <Card>
          <CardHeader><CardTitle>Suitable Interests</CardTitle></CardHeader>
          <div className="flex flex-wrap gap-1.5">
            {e.suitable_interests.map(i => <Badge key={i} variant="purple">{i}</Badge>)}
          </div>
        </Card>

        <Card>
          <CardHeader><CardTitle>Career Areas</CardTitle></CardHeader>
          {e.career_areas.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {e.career_areas.map(c => <Badge key={c} variant="cyan">{c}</Badge>)}
            </div>
          ) : <p className="text-xs italic text-[#8892a4]">Not verified yet.</p>}
        </Card>
      </div>
    </div>
  )
}
