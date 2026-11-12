import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'
import { LineChart } from '../components/charts/LineChart'
import { LoadingState, ErrorState, DataUnavailableState } from '../components/ui/States'
import { formatFloat } from '../lib/utils'

export function ThresholdSensitivity() {
  const { data, status, error } = useApi(() => api.analytics.thresholdSensitivity())

  return (
    <div>
      <PageHeader
        title="Threshold Sensitivity"
        description="How the similarity graph changes at thresholds 0.30, 0.50, 0.60"
      />

      {status === 'loading' || status === 'idle' ? (
        <LoadingState />
      ) : status === 'unavailable' ? (
        <DataUnavailableState />
      ) : status === 'error' ? (
        <ErrorState message={error ?? 'Failed'} />
      ) : (
        <>
          <div className="mb-4 grid grid-cols-1 gap-4 md:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Edge Count vs Threshold</CardTitle></CardHeader>
              <LineChart
                data={data!.thresholds.map(r => ({ threshold: r.threshold.toFixed(2), edges: r.edge_count }))}
                lines={[{ key: 'edges', color: '#8b5cf6', label: 'Edges' }]}
                xKey="threshold"
                height={200}
              />
            </Card>
            <Card>
              <CardHeader><CardTitle>Graph Density vs Threshold</CardTitle></CardHeader>
              <LineChart
                data={data!.thresholds.map(r => ({ threshold: r.threshold.toFixed(2), density: r.density ?? 0 }))}
                lines={[{ key: 'density', color: '#22d3ee', label: 'Density' }]}
                xKey="threshold"
                height={200}
              />
            </Card>
            <Card>
              <CardHeader><CardTitle>Isolated Nodes vs Threshold</CardTitle></CardHeader>
              <LineChart
                data={data!.thresholds.map(r => ({ threshold: r.threshold.toFixed(2), isolated: r.isolated_node_count }))}
                lines={[{ key: 'isolated', color: '#f87171', label: 'Isolated nodes' }]}
                xKey="threshold"
                height={200}
              />
            </Card>
            <Card>
              <CardHeader><CardTitle>Connected Components</CardTitle></CardHeader>
              <LineChart
                data={data!.thresholds.map(r => ({ threshold: r.threshold.toFixed(2), components: r.connected_component_count }))}
                lines={[{ key: 'components', color: '#6366f1', label: 'Components' }]}
                xKey="threshold"
                height={200}
              />
            </Card>
          </div>

          <Card>
            <CardHeader><CardTitle>Comparison Table</CardTitle></CardHeader>
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-[#2d3748] text-[#8892a4]">
                  <th className="pb-2 text-left font-semibold">Threshold</th>
                  <th className="pb-2 text-right font-semibold">Nodes</th>
                  <th className="pb-2 text-right font-semibold">Edges</th>
                  <th className="pb-2 text-right font-semibold">Density</th>
                  <th className="pb-2 text-right font-semibold">Components</th>
                  <th className="pb-2 text-right font-semibold">Largest Component</th>
                  <th className="pb-2 text-right font-semibold">Isolated</th>
                  <th className="pb-2 text-center font-semibold">Primary</th>
                </tr>
              </thead>
              <tbody>
                {data!.thresholds.map(r => (
                  <tr key={r.threshold} className={`border-b border-[#2d3748]/50 ${r.is_primary ? 'bg-[#8b5cf6]/5' : ''}`}>
                    <td className="py-2 font-mono text-[#22d3ee]">{r.threshold.toFixed(2)}</td>
                    <td className="py-2 text-right text-[#e2e8f0]">{r.node_count}</td>
                    <td className="py-2 text-right text-[#e2e8f0]">{r.edge_count}</td>
                    <td className="py-2 text-right text-[#8892a4]">{formatFloat(r.density)}</td>
                    <td className="py-2 text-right text-[#8892a4]">{r.connected_component_count}</td>
                    <td className="py-2 text-right text-[#8892a4]">{r.largest_component_size}</td>
                    <td className="py-2 text-right text-[#8892a4]">{r.isolated_node_count}</td>
                    <td className="py-2 text-center">
                      {r.is_primary && <Badge variant="purple">Primary</Badge>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </>
      )}
    </div>
  )
}
