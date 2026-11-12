import {
  BarChart as ReBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { CHART_COLORS } from '../../lib/utils'

interface BarChartProps {
  data: { name: string; value: number }[]
  color?: string
  height?: number
  multiColor?: boolean
  unit?: string
}

export function BarChart({
  data,
  color = '#8b5cf6',
  height = 220,
  multiColor = false,
  unit = '',
}: BarChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ReBarChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
        <XAxis
          dataKey="name"
          tick={{ fill: '#8892a4', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: '#8892a4', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip
          contentStyle={{ background: '#1c2333', border: '1px solid #2d3748', borderRadius: 8 }}
          labelStyle={{ color: '#e2e8f0' }}
          itemStyle={{ color: '#8892a4' }}
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          formatter={(v: any) => [`${v ?? ''}${unit}`, 'Count']}
        />
        <Bar dataKey="value" radius={[4, 4, 0, 0]} fill={color}>
          {multiColor &&
            data.map((_, i) => (
              <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
            ))}
        </Bar>
      </ReBarChart>
    </ResponsiveContainer>
  )
}
