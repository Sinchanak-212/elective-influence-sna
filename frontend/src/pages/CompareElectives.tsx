import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { api, type Elective } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { Button } from '../components/ui/Button'
import { LoadingState, ErrorState, EmptyState } from '../components/ui/States'
import { X } from 'lucide-react'

export function CompareElectives() {
  const { data: catalogue, status, error } = useApi(() => api.electives.list())
  const [selected, setSelected] = useState<string[]>([])

  function toggle(id: string) {
    setSelected(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : prev.length < 4 ? [...prev, id] : prev
    )
  }

  const comparisons: (Elective | undefined)[] = selected.map(id =>
    catalogue?.electives.find(e => e.id === id)
  )

  if (status === 'loading' || status === 'idle') return <LoadingState />
  if (status === 'error') return <ErrorState message={error ?? 'Failed'} />

  const electives = catalogue!.electives

  return (
    <div>
      <PageHeader
        title="Compare Electives"
        description="Select up to 4 electives to compare side-by-side"
        actions={
          selected.length > 0 && (
            <Button variant="ghost" size="sm" onClick={() => setSelected([])}>
              <X className="h-3 w-3" /> Clear
            </Button>
          )
        }
      />

      {/* Selector */}
      <Card className="mb-5">
        <CardHeader>
          <CardTitle>Choose Electives ({selected.length}/4)</CardTitle>
        </CardHeader>
        <div className="flex flex-wrap gap-2">
          {electives.map(e => (
            <button
              key={e.id}
              onClick={() => toggle(e.id)}
              className={`rounded-lg border px-3 py-1.5 text-sm transition-colors ${
                selected.includes(e.id)
                  ? 'border-[#8b5cf6] bg-[#8b5cf6]/15 text-[#a78bfa]'
                  : 'border-[#2d3748] text-[#8892a4] hover:border-[#8b5cf6]/50 hover:text-[#e2e8f0]'
              } ${!selected.includes(e.id) && selected.length >= 4 ? 'opacity-40 cursor-not-allowed' : ''}`}
              disabled={!selected.includes(e.id) && selected.length >= 4}
            >
              {e.name}
            </button>
          ))}
        </div>
      </Card>

      {selected.length < 2 ? (
        <EmptyState message="Select at least 2 electives to compare." />
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[#2d3748]">
                <th className="pb-3 text-left text-xs font-semibold uppercase tracking-widest text-[#8892a4]">Field</th>
                {comparisons.map(e => e && (
                  <th key={e.id} className="pb-3 text-left">
                    <div className="text-sm font-semibold text-[#e2e8f0]">{e.name}</div>
                    {!e.data_verified && <Badge variant="amber" size="xs">Unverified</Badge>}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                { label: 'Code', key: 'code' as keyof Elective },
                { label: 'Difficulty', key: 'difficulty_level' as keyof Elective },
                { label: 'Workload (hrs/wk)', key: 'expected_workload_hours_per_week' as keyof Elective },
                { label: 'Assessment', key: 'assessment_pattern' as keyof Elective },
              ].map(row => (
                <tr key={row.label} className="border-b border-[#2d3748]/50">
                  <td className="py-2 text-xs text-[#8892a4]">{row.label}</td>
                  {comparisons.map((e, i) => e && (
                    <td key={i} className="py-2 text-[#e2e8f0]">
                      {String(e[row.key] ?? '—')}
                    </td>
                  ))}
                </tr>
              ))}
              <tr className="border-b border-[#2d3748]/50">
                <td className="py-2 text-xs text-[#8892a4]">Prerequisites</td>
                {comparisons.map((e, i) => e && (
                  <td key={i} className="py-2">
                    {e.prerequisites.length > 0
                      ? e.prerequisites.map(p => <Badge key={p} variant="red" size="xs">{p}</Badge>)
                      : <span className="text-xs text-[#8892a4]">None listed</span>}
                  </td>
                ))}
              </tr>
              <tr className="border-b border-[#2d3748]/50">
                <td className="py-2 text-xs text-[#8892a4]">Interests</td>
                {comparisons.map((e, i) => e && (
                  <td key={i} className="py-2">
                    <div className="flex flex-wrap gap-1">
                      {e.suitable_interests.map(s => <Badge key={s} variant="indigo" size="xs">{s}</Badge>)}
                    </div>
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-2 text-xs text-[#8892a4]">Skills Gained</td>
                {comparisons.map((e, i) => e && (
                  <td key={i} className="py-2">
                    {e.skills_gained.length > 0
                      ? <div className="flex flex-wrap gap-1">{e.skills_gained.map(s => <Badge key={s} variant="green" size="xs">{s}</Badge>)}</div>
                      : <span className="text-xs text-[#8892a4]">Not verified</span>}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
