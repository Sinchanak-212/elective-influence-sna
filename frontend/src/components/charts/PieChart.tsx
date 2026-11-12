import {
  PieChart as RePieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { CHART_COLORS } from '../../lib/utils'

interface PieChartProps {
  data: { name: string; value: number }[]
  height?: number
  innerRadius?: number
}

export function PieChart({ data, height = 220, innerRadius = 50 }: PieChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <RePieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="45%"
          innerRadius={innerRadius}
          outerRadius={80}
          paddingAngle={3}
        >
          {data.map((_, i) => (
            <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#1c2333', border: '1px solid #2d3748', borderRadius: 8 }}
          itemStyle={{ color: '#e2e8f0' }}
        />
        <Legend
          wrapperStyle={{ fontSize: 11, color: '#8892a4' }}
          iconType="circle"
          iconSize={8}
        />
      </RePieChart>
    </ResponsiveContainer>
  )
}
