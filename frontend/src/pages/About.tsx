import { PageHeader } from '../components/layout/PageHeader'
import { Card, CardHeader, CardTitle } from '../components/ui/Card'
import { Badge } from '../components/ui/Badge'

export function About() {
  return (
    <div>
      <PageHeader
        title="About & Methodology"
        description="Research design, limitations, and privacy"
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader><CardTitle>Study Overview</CardTitle></CardHeader>
          <p className="text-sm text-[#8892a4] leading-relaxed">
            This dashboard presents an exploratory Social Network Analysis of elective preferences
            and self-reported peer discussion among engineering students. The dataset consists of
            24 engineering respondents from a single cohort.
          </p>
          <p className="mt-3 text-sm text-[#8892a4] leading-relaxed">
            The analysis covers four priority areas: (1) similarity network construction,
            (2) community detection, (3) peer discussion patterns, and (4) academic outcomes.
          </p>
        </Card>

        <Card>
          <CardHeader><CardTitle>Network Construction</CardTitle></CardHeader>
          <p className="text-sm text-[#8892a4] leading-relaxed">
            Edges connect respondents whose profiles are similar above a configurable threshold.
            Profile similarity is a weighted combination of:
          </p>
          <ul className="mt-3 space-y-1.5 text-sm">
            {[
              { label: 'Preferred subject category', weight: '0.50' },
              { label: 'Branch', weight: '0.20' },
              { label: 'Primary reason', weight: '0.20' },
              { label: 'Year', weight: '0.10' },
            ].map(item => (
              <li key={item.label} className="flex items-center justify-between rounded border border-[#2d3748] px-3 py-1.5">
                <span className="text-[#8892a4]">{item.label}</span>
                <Badge variant="purple">{item.weight}</Badge>
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <CardHeader><CardTitle>Important Limitations</CardTitle></CardHeader>
          <ul className="space-y-2 text-sm text-[#8892a4]">
            {[
              'Similarity edges are inferred from shared attributes, NOT observed friendships or peer-influence ties.',
              'The survey does not identify discussion partners — no observed peer-influence network can be constructed.',
              'Sample size is 24 respondents. All statistics are descriptive. Cross-sectional design; associations are not causal.',
              'Sparse expected counts prevent formal chi-square tests for most cross-tabulations.',
              'Spearman estimates are exploratory with permutation p-values.',
              'Community detection finds groups in the inferred similarity graph, not observed social groups.',
            ].map((point, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#8b5cf6]" />
                {point}
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <CardHeader><CardTitle>Privacy & Data Handling</CardTitle></CardHeader>
          <ul className="space-y-2 text-sm text-[#8892a4]">
            {[
              'No respondent-level data is exposed through any API endpoint.',
              'Node IDs are anonymised codes (ENG_001 etc.) — not names.',
              'The raw survey CSV is excluded from the repository.',
              'The student planner uses a client-generated pseudonymous token only.',
              'No real student IDs, names, or contact details should be stored in the planner.',
            ].map((point, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-[#22d3ee]" />
                {point}
              </li>
            ))}
          </ul>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Elective Assistant Disclaimer</CardTitle></CardHeader>
          <p className="text-sm text-[#8892a4] leading-relaxed">
            The elective catalogue entries are placeholder records until verified against the
            institution's official syllabus or academic handbook. Fields shown as null have not
            been confirmed. The recommendation engine is rule-based (interest-tag overlap) and
            does not use machine learning. The 24-response survey is not used as a predictive
            recommendation model. Recommendations are not scientifically validated and should be
            one input among several when choosing an elective.
          </p>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader><CardTitle>Tech Stack</CardTitle></CardHeader>
          <div className="flex flex-wrap gap-2">
            {['React 19', 'TypeScript', 'Vite', 'Tailwind CSS v4', 'Recharts', 'Cytoscape.js', 'React Router v6', 'FastAPI', 'Python 3.10'].map(t => (
              <Badge key={t} variant="indigo">{t}</Badge>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}
