import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { LoadingState, ErrorState, EmptyState } from '../components/ui/States'
import { Search, ChevronRight, AlertTriangle } from 'lucide-react'

export function ExploreElectives() {
  const { data, status, error } = useApi(() => api.electives.list())
  const [query, setQuery] = useState('')

  const filtered = data?.electives.filter(e =>
    e.name.toLowerCase().includes(query.toLowerCase()) ||
    e.suitable_interests.some(i => i.toLowerCase().includes(query.toLowerCase()))
  ) ?? []

  return (
    <div>
      <PageHeader
        title="Explore Electives"
        description="Browse the elective catalogue"
      />

      {/* Search */}
      <div className="mb-5 flex items-center gap-3 rounded-xl border border-[#2d3748] bg-[#1c2333] px-4 py-2.5">
        <Search className="h-4 w-4 text-[#8892a4]" />
        <input
          type="text"
          placeholder="Search by name or interest…"
          value={query}
          onChange={e => setQuery(e.target.value)}
          className="flex-1 bg-transparent text-sm text-[#e2e8f0] placeholder-[#8892a4] outline-none"
        />
      </div>

      {/* Catalogue note */}
      {data && (
        <div className="mb-4 flex items-start gap-2 rounded-lg border border-[#2d3748] bg-[#2d3748]/30 p-3">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
          <p className="text-xs text-[#8892a4]">{data.catalogue_note}</p>
        </div>
      )}

      {status === 'loading' || status === 'idle' ? (
        <LoadingState />
      ) : status === 'error' ? (
        <ErrorState message={error ?? 'Failed to load electives'} />
      ) : filtered.length === 0 ? (
        <EmptyState message={query ? `No electives match "${query}".` : 'Catalogue is empty.'} />
      ) : (
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map(e => (
            <Link key={e.id} to={`/electives/${e.id}`}>
              <Card className="group h-full cursor-pointer transition-colors hover:border-[#8b5cf6]/50">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-semibold text-[#e2e8f0] group-hover:text-[#8b5cf6]">
                      {e.name}
                    </p>
                    {e.code && <p className="mt-0.5 text-xs text-[#8892a4]">{e.code}</p>}
                  </div>
                  <div className="flex items-center gap-2">
                    {!e.data_verified && <Badge variant="amber" size="xs">Unverified</Badge>}
                    <ChevronRight className="h-4 w-4 text-[#8892a4] group-hover:text-[#8b5cf6]" />
                  </div>
                </div>
                {e.description ? (
                  <p className="mt-2 line-clamp-2 text-xs text-[#8892a4]">{e.description}</p>
                ) : (
                  <p className="mt-2 text-xs italic text-[#8892a4]">No description available yet.</p>
                )}
                {e.suitable_interests.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {e.suitable_interests.slice(0, 4).map(i => (
                      <Badge key={i} variant="indigo" size="xs">{i}</Badge>
                    ))}
                  </div>
                )}
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
