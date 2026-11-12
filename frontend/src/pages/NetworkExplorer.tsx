import { useState } from 'react'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { StatCard } from '../components/ui/StatCard'
import { NetworkGraph } from '../components/network/NetworkGraph'
import { LoadingState, ErrorState, DataUnavailableState, InterpretationNote } from '../components/ui/States'
import { formatFloat } from '../lib/utils'
import { Network, GitBranch, Zap, Layers } from 'lucide-react'

const THRESHOLDS = [0.3, 0.5, 0.6] as const
type Threshold = (typeof THRESHOLDS)[number]

export function NetworkExplorer() {
  const [threshold, setThreshold] = useState<Threshold>(0.5)
  const { data, status, error } = useApi(() => api.analytics.network(threshold), [threshold])

  return (
    <div>
      <PageHeader
        title="Social Network Explorer"
        description="Profile-similarity graph at configurable thresholds"
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
        <LoadingState message="Building network…" />
      ) : status === 'unavailable' ? (
        <DataUnavailableState />
      ) : status === 'error' ? (
        <ErrorState message={error ?? 'Failed to load network'} />
      ) : (
        <>
          {/* KPIs */}
          <div className="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-6">
            <StatCard label="Nodes" value={data!.graph_summary.node_count} icon={<Network className="h-4 w-4" />} accent="purple" />
            <StatCard label="Edges" value={data!.graph_summary.edge_count} icon={<Zap className="h-4 w-4" />} accent="indigo" />
            <StatCard label="Density" value={formatFloat(data!.graph_summary.density)} icon={<Layers className="h-4 w-4" />} accent="cyan" />
            <StatCard label="Components" value={data!.graph_summary.connected_component_count} icon={<GitBranch className="h-4 w-4" />} accent="green" />
            <StatCard label="Largest Component" value={data!.graph_summary.largest_component_size} sub="nodes" accent="amber" />
            <StatCard label="Isolated" value={data!.graph_summary.isolated_node_count} sub="nodes" accent="indigo" />
          </div>

          {/* Graph */}
          <Card className="mb-4">
            <CardHeader>
              <CardTitle>Similarity Graph — threshold {threshold.toFixed(2)}</CardTitle>
              <span className="text-xs text-[#8892a4]">Node size = degree centrality · Color = branch</span>
            </CardHeader>
            <NetworkGraph nodes={data!.nodes} edges={data!.edges} height={500} />
          </Card>

          {/* Node table */}
          <Card>
            <CardHeader><CardTitle>Node Metrics</CardTitle></CardHeader>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-[#2d3748] text-[#8892a4]">
                    <th className="pb-2 text-left font-semibold">ID</th>
                    <th className="pb-2 text-left font-semibold">Branch</th>
                    <th className="pb-2 text-left font-semibold">Year</th>
                    <th className="pb-2 text-left font-semibold">Subject</th>
                    <th className="pb-2 text-right font-semibold">Degree</th>
                    <th className="pb-2 text-right font-semibold">Degree Centrality</th>
                    <th className="pb-2 text-right font-semibold">Betweenness</th>
                    <th className="pb-2 text-right font-semibold">Closeness</th>
                  </tr>
                </thead>
                <tbody>
                  {data!.nodes.map(n => (
                    <tr key={n.id} className="border-b border-[#2d3748]/50 hover:bg-[#2d3748]/30">
                      <td className="py-1.5 font-mono text-[#22d3ee]">{n.id}</td>
                      <td className="py-1.5 text-[#e2e8f0]">{n.branch}</td>
                      <td className="py-1.5 text-[#8892a4]">{n.year}</td>
                      <td className="py-1.5 text-[#8892a4]">{n.preferred_subject_category}</td>
                      <td className="py-1.5 text-right text-[#e2e8f0]">{n.metrics.degree}</td>
                      <td className="py-1.5 text-right text-[#8892a4]">{formatFloat(n.metrics.degree_centrality)}</td>
                      <td className="py-1.5 text-right text-[#8892a4]">{formatFloat(n.metrics.betweenness_centrality)}</td>
                      <td className="py-1.5 text-right text-[#8892a4]">{formatFloat(n.metrics.closeness_centrality)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          <InterpretationNote note={data!.interpretation_note} />
        </>
      )}
    </div>
  )
}
