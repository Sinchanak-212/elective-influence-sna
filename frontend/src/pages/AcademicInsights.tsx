import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { BarChart } from '../components/charts/BarChart'
import { LoadingState, ErrorState, DataUnavailableState, InterpretationNote } from '../components/ui/States'
import { distToChartData, formatFloat } from '../lib/utils'

export function AcademicInsights() {
  const { data, status, error } = useApi(() => api.analytics.academic())

  return (
    <div>
      <PageHeader
        title="Academic Insights"
        description="Descriptive academic outcome distributions and exploratory statistics"
      />

      {status === 'loading' || status === 'idle' ? (
        <LoadingState />
      ) : status === 'unavailable' ? (
        <DataUnavailableState />
      ) : status === 'error' ? (
        <ErrorState message={error ?? 'Failed'} />
      ) : (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <Card>
              <CardHeader><CardTitle>Academic Outcome</CardTitle></CardHeader>
              <BarChart data={distToChartData(data!.academic_outcome)} multiColor height={180} />
            </Card>
            <Card>
              <CardHeader><CardTitle>Course Difficulty</CardTitle></CardHeader>
              <BarChart data={distToChartData(data!.course_difficulty)} color="#6366f1" height={180} />
            </Card>
            <Card>
              <CardHeader><CardTitle>Final Score Range</CardTitle></CardHeader>
              <BarChart data={distToChartData(data!.final_score_range)} color="#22d3ee" height={180} />
            </Card>
            <Card>
              <CardHeader><CardTitle>Study Hours per Week</CardTitle></CardHeader>
              <BarChart data={distToChartData(data!.study_hours_per_week)} color="#34d399" height={180} />
            </Card>
            <Card>
              <CardHeader><CardTitle>Score Met Expectations</CardTitle></CardHeader>
              <BarChart data={distToChartData(data!.score_met_expectations)} color="#f59e0b" height={180} />
            </Card>
          </div>

          {/* Ordinal associations */}
          {data!.ordinal_associations.length > 0 && (
            <Card className="mt-4">
              <CardHeader><CardTitle>Ordinal Associations (Spearman)</CardTitle></CardHeader>
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-[#2d3748] text-[#8892a4]">
                    <th className="pb-2 text-left font-semibold">Analysis</th>
                    <th className="pb-2 text-right font-semibold">n</th>
                    <th className="pb-2 text-right font-semibold">Excluded</th>
                    <th className="pb-2 text-right font-semibold">Spearman ρ</th>
                    <th className="pb-2 text-right font-semibold">p-value</th>
                    <th className="pb-2 text-left font-semibold">Method</th>
                  </tr>
                </thead>
                <tbody>
                  {data!.ordinal_associations.map(a => (
                    <tr key={a.analysis} className="border-b border-[#2d3748]/50">
                      <td className="py-1.5 text-[#e2e8f0]">{a.analysis.replace(/_/g, ' ')}</td>
                      <td className="py-1.5 text-right text-[#8892a4]">{a.sample_size}</td>
                      <td className="py-1.5 text-right text-[#8892a4]">{a.excluded_count}</td>
                      <td className="py-1.5 text-right font-mono text-[#22d3ee]">{formatFloat(a.spearman_rho)}</td>
                      <td className="py-1.5 text-right font-mono text-[#8892a4]">{formatFloat(a.p_value)}</td>
                      <td className="py-1.5 text-[#8892a4]">{a.p_value_method}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Card>
          )}

          <InterpretationNote note={data!.interpretation_note} />
        </>
      )}
    </div>
  )
}
