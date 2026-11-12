import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { BarChart } from '../components/charts/BarChart'
import { LoadingState, ErrorState, DataUnavailableState, InterpretationNote } from '../components/ui/States'
import { formatFloat, formatPct } from '../lib/utils'

const THRESHOLDS = [0.3, 0.5, 0.6] as const
type Threshold = (typeof THRESHOLDS)[number]

export function CommunityAnalysis() {
  const [threshold, setThreshold] = useState<Threshold>(0.5)
  const { data, status, error } = useApi(() => api.analytics.communities(threshold), [threshold])

  return (
    <div>
      <PageHeader
        title="Community Analysis"
        description="Louvain and greedy modularity community detection"
        actions={
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#8892a4]">Threshold:</span>
            {THRESHOLDS.map(t => (
              <button
                key={t}
                onClick={() => setThreshold(t)}
                className={`rounded-lg px-3 py-1.5 text-sm font-medium transition-colors ${
                  threshold === t
                    ? 'bg-[#8b5cf6] text-white'
                    : 'border border-[#2d3748] text-[#8892a4] hover:text-[#e2e8f0]'
                }`}
              >
                {t.toFixed(2)}
              </button>
            ))}
          </div>
        }
      />

      {status === 'loading' || status === 'idle' ? (
        <LoadingState />
      ) : status === 'unavailable' ? (
        <DataUnavailableState />
      ) : status === 'error' ? (
        <ErrorState message={error ?? 'Failed to load communities'} />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {data!.algorithms.map(algo => (
              <Card key={algo.algorithm}>
                <CardHeader>
                  <CardTitle>{algo.algorithm} algorithm</CardTitle>
                  <span className="text-xs text-[#8892a4]">
                    {algo.community_count} communities · modularity {formatFloat(algo.weighted_modularity)}
                  </span>
                </CardHeader>
                <BarChart
                  data={algo.communities.map(c => ({ name: `C${c.community_id}`, value: c.size }))}
                  color="#8b5cf6"
                  height={160}
                />
                <div className="mt-3 space-y-2">
                  {algo.communities.map(c => (
                    <div key={c.community_id} className="flex items-center justify-between rounded-lg border border-[#2d3748] px-3 py-2">
                      <div className="flex items-center gap-3">
                        <span className="text-xs font-mono text-[#22d3ee]">C{c.community_id}</span>
                        <span className="text-xs text-[#8892a4]">{c.size} members</span>
                        <Badge variant="purple">{c.dominant_subject}</Badge>
                        <Badge variant="indigo">{c.dominant_branch}</Badge>
                      </div>
                      <div className="text-right text-xs text-[#8892a4]">
                        <div>Subject share: {formatPct(c.dominant_subject_share != null ? c.dominant_subject_share * 100 : null)}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>

          {/* Attribute mixing */}
          <Card className="mt-4">
            <CardHeader><CardTitle>Attribute Mixing</CardTitle></CardHeader>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-[#2d3748] text-[#8892a4]">
                  <th className="pb-2 text-left font-semibold">Attribute</th>
                  <th className="pb-2 text-right font-semibold">Matching Edge Fraction</th>
                  <th className="pb-2 text-right font-semibold">Weighted Assortativity</th>
                  <th className="pb-2 text-center font-semibold">Defined</th>
                </tr>
              </thead>
              <tbody>
                {data!.attribute_mixing.map(m => (
                  <tr key={m.attribute} className="border-b border-[#2d3748]/50">
                    <td className="py-1.5 text-[#e2e8f0]">{m.attribute}</td>
                    <td className="py-1.5 text-right text-[#8892a4]">{formatFloat(m.matching_edge_fraction)}</td>
                    <td className="py-1.5 text-right text-[#8892a4]">{formatFloat(m.weighted_categorical_assortativity)}</td>
                    <td className="py-1.5 text-center">
                      <Badge variant={m.assortativity_defined ? 'green' : 'red'}>
                        {m.assortativity_defined ? 'Yes' : 'No'}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>

          <InterpretationNote note={data!.interpretation_note} />
        </>
      )}
    </div>
  )
}
