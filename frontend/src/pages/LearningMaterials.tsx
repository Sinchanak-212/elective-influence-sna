import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { LoadingState, ErrorState, EmptyState } from '../components/ui/States'
import { FileText, AlertTriangle } from 'lucide-react'

export function LearningMaterials() {
  const { data: catalogue, status, error } = useApi(() => api.electives.list())
  const [selected, setSelected] = useState<string>('')

  const elective = catalogue?.electives.find(e => e.id === selected)

  return (
    <div>
      <PageHeader
        title="Learning Materials"
        description="Verified learning resources for each elective"
      />

      {status === 'loading' || status === 'idle' ? (
        <LoadingState />
      ) : status === 'error' ? (
        <ErrorState message={error ?? 'Failed'} />
      ) : (
        <>
          <Card className="mb-5">
            <CardHeader><CardTitle>Select Elective</CardTitle></CardHeader>
            <select
              value={selected}
              onChange={e => setSelected(e.target.value)}
              className="w-full max-w-sm rounded-lg border border-[#2d3748] bg-[#0d1117] px-3 py-2 text-sm text-[#e2e8f0] outline-none focus:border-[#8b5cf6]"
            >
              <option value="">— Choose an elective —</option>
              {catalogue!.electives.map(e => (
                <option key={e.id} value={e.id}>{e.name}</option>
              ))}
            </select>
          </Card>

          {!selected ? (
            <EmptyState message="Select an elective above to view its learning materials." />
          ) : (
            <ElectiveMaterials electiveId={selected} name={elective?.name ?? selected} />
          )}
        </>
      )}
    </div>
  )
}

function ElectiveMaterials({ electiveId, name }: { electiveId: string; name: string }) {
  const { data, status, error } = useApi(() => api.electives.materials(electiveId), [electiveId])

  if (status === 'loading' || status === 'idle') return <LoadingState />
  if (status === 'error') return <ErrorState message={error ?? 'Failed'} />

  return (
    <Card>
      <CardHeader>
        <CardTitle>{name} — Materials</CardTitle>
      </CardHeader>
      {!data!.materials_available ? (
        <div className="flex items-start gap-2 rounded-lg border border-amber-500/20 bg-amber-500/5 p-3">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
          <p className="text-xs text-amber-200/80">
            {data!.materials_note ?? 'No verified materials available yet.'}
          </p>
        </div>
      ) : (
        <ul className="space-y-2">
          {(data!.materials as { title?: string; url?: string; type?: string }[]).map((m, i) => (
            <li key={i} className="flex items-start gap-3 rounded-lg border border-[#2d3748] p-3">
              <FileText className="mt-0.5 h-4 w-4 shrink-0 text-[#8b5cf6]" />
              <div>
                <p className="text-sm text-[#e2e8f0]">{m.title ?? 'Untitled'}</p>
                {m.type && <p className="text-xs text-[#8892a4]">{m.type}</p>}
                {m.url && (
                  <a href={m.url} target="_blank" rel="noopener noreferrer"
                    className="text-xs text-[#22d3ee] hover:underline">{m.url}</a>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  )
}
