import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { BarChart } from '../components/charts/BarChart'
import { LoadingState, ErrorState, DataUnavailableState, InterpretationNote } from '../components/ui/States'
import { distToChartData, formatFloat } from '../lib/utils'

export function PeerDiscussion() {
  const { data, status, error } = useApi(() => api.analytics.peerDiscussion())

  return (
    <div>
      <PageHeader
        title="Peer Discussion Analysis"
        description="Self-reported elective discussion behaviour and best-friend patterns"
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
              <CardHeader><CardTitle>Discussed Elective with Friends</CardTitle></CardHeader>
              <BarChart data={distToChartData(data!.discussion_status)} color="#8b5cf6" height={180} />
            </Card>
            <Card>
              <CardHeader><CardTitle>Best Friend Chose Same Elective</CardTitle></CardHeader>
              <BarChart data={distToChartData(data!.best_friend_same_elective)} color="#22d3ee" height={180} />
            </Card>
            <Card>
              <CardHeader><CardTitle>Best Friend's Marks Range</CardTitle></CardHeader>
              <BarChart data={distToChartData(data!.best_friend_marks_range)} color="#6366f1" height={180} />
            </Card>
            <Card>
              <CardHeader><CardTitle>Best Friend Choice Reason</CardTitle></CardHeader>
              <BarChart data={distToChartData(data!.best_friend_choice_reason)} color="#34d399" height={180} />
            </Card>
          </div>

          {/* Statistical test */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle>Statistical Test: Discussion vs Friend Same Elective</CardTitle>
            </CardHeader>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                { label: 'Test', value: data!.discussion_vs_friend_same_elective.test_used },
                { label: 'Test Statistic', value: formatFloat(data!.discussion_vs_friend_same_elective.test_statistic) },
                { label: 'p-value', value: formatFloat(data!.discussion_vs_friend_same_elective.p_value) },
                { label: 'Sample Size', value: `${data!.discussion_vs_friend_same_elective.sample_size} / ${data!.discussion_vs_friend_same_elective.denominator}` },
              ].map(item => (
                <div key={item.label} className="rounded-lg border border-[#2d3748] p-3">
                  <p className="text-xs text-[#8892a4]">{item.label}</p>
                  <p className="mt-1 text-sm font-semibold text-[#e2e8f0]">{item.value}</p>
                </div>
              ))}
            </div>
            <p className="mt-3 text-xs text-[#8892a4]">{data!.discussion_vs_friend_same_elective.note}</p>
          </Card>

          <InterpretationNote note={data!.interpretation_note} />
        </>
      )}
    </div>
  )
}
