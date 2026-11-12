import { Users, Network, BookOpen, TrendingUp } from 'lucide-react'
import { useApi } from '../hooks/useApi'
import { api } from '../lib/api'
import { PageHeader } from '../components/layout/PageHeader'
import { StatCard } from '../components/ui/StatCard'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { BarChart } from '../components/charts/BarChart'
import { PieChart } from '../components/charts/PieChart'
import { LoadingState, ErrorState, DataUnavailableState, InterpretationNote } from '../components/ui/States'
import { recordToChartData } from '../lib/utils'

export function Overview() {
  const { data, status, error } = useApi(() => api.analytics.overview())

  if (status === 'loading' || status === 'idle') return <LoadingState message="Loading overview…" />
  if (status === 'unavailable') return (
    <div>
      <PageHeader title="Overview" description="Engineering student elective survey — 24 respondents" />
      <DataUnavailableState />
    </div>
  )
  if (status === 'error') return <ErrorState message={error ?? 'Failed to load overview'} />

  const d = data!
  const branchData = recordToChartData(d.branches)
  const subjectData = recordToChartData(d.preferred_subject_categories)
  const reasonData = recordToChartData(d.primary_reasons)
  const yearData = recordToChartData(d.years)

  return (
    <div>
      <PageHeader
        title="Overview"
        description="Engineering student elective survey — 24 respondents"
      />

      {/* KPIs */}
      <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total Respondents" value={d.total_respondents} sub="Engineering cohort" icon={<Users className="h-5 w-5" />} accent="purple" />
        <StatCard label="Branches" value={Object.keys(d.branches).length} sub="Distinct branches" icon={<Network className="h-5 w-5" />} accent="indigo" />
        <StatCard label="Subject Categories" value={Object.keys(d.preferred_subject_categories).length} sub="Preferred areas" icon={<BookOpen className="h-5 w-5" />} accent="cyan" />
        <StatCard label="Years" value={Object.keys(d.years).length} sub="Academic years" icon={<TrendingUp className="h-5 w-5" />} accent="green" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Respondents by Branch</CardTitle></CardHeader>
          <BarChart data={branchData} multiColor />
        </Card>
        <Card>
          <CardHeader><CardTitle>Preferred Subject Category</CardTitle></CardHeader>
          <PieChart data={subjectData} />
        </Card>
        <Card>
          <CardHeader><CardTitle>Primary Reason for Elective Choice</CardTitle></CardHeader>
          <BarChart data={reasonData} color="#6366f1" />
        </Card>
        <Card>
          <CardHeader><CardTitle>Year Distribution</CardTitle></CardHeader>
          <PieChart data={yearData} innerRadius={40} />
        </Card>
      </div>

      <InterpretationNote note={d.note} />
    </div>
  )
}
