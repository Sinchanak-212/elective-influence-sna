import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { BarChart } from '../components/charts/BarChart'
import { PieChart } from '../components/charts/PieChart'
import { LoadingState, ErrorState, DataUnavailableState, InterpretationNote } from '../components/ui/States'
import { recordToChartData } from '../lib/utils'

export function ResearchAnalytics() {
  const overview = useApi(() => api.analytics.overview())

  if (overview.status === 'loading' || overview.status === 'idle') return <LoadingState />
  if (overview.status === 'unavailable') return (
    <div>
      <PageHeader title="Research Analytics" description="Survey distributions across the 24-respondent cohort" />
      <DataUnavailableState />
    </div>
  )
  if (overview.status === 'error') return <ErrorState message={overview.error ?? 'Failed to load'} />

  const d = overview.data!

  return (
    <div>
      <PageHeader
        title="Research Analytics"
        description="Survey distributions across the 24-respondent engineering cohort"
      />

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Branch Distribution</CardTitle></CardHeader>
          <BarChart data={recordToChartData(d.branches)} multiColor height={200} />
        </Card>
        <Card>
          <CardHeader><CardTitle>Year Distribution</CardTitle></CardHeader>
          <BarChart data={recordToChartData(d.years)} color="#22d3ee" height={200} />
        </Card>
        <Card>
          <CardHeader><CardTitle>Preferred Subject Category</CardTitle></CardHeader>
          <PieChart data={recordToChartData(d.preferred_subject_categories)} height={260} />
        </Card>
        <Card>
          <CardHeader><CardTitle>Primary Reason for Elective Choice</CardTitle></CardHeader>
          <BarChart data={recordToChartData(d.primary_reasons)} color="#6366f1" height={200} />
        </Card>
      </div>

      <InterpretationNote note={d.note} />
    </div>
  )
}
