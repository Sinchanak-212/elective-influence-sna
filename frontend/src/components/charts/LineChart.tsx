import {
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'

interface LineChartProps {
  data: Record<string, string | number>[]
  lines: { key: string; color: string; label?: string }[]
  height?: number
  xKey?: string
}

export function LineChart({
  data,
  lines,
  height = 220,
  xKey = 'name',
}: LineChartProps) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <ReLineChart data={data} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
        <XAxis
          dataKey={xKey}
          tick={{ fill: '#8892a4', fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis tick={{ fill: '#8892a4', fontSize: 11 }} axisLine={false} tickLine={false} />
        <Tooltip
          contentStyle={{ background: '#1c2333', border: '1px solid #2d3748', borderRadius: 8 }}
          labelStyle={{ color: '#e2e8f0' }}
          itemStyle={{ color: '#8892a4' }}
        />
        <Legend wrapperStyle={{ fontSize: 11, color: '#8892a4' }} />
        {lines.map(l => (
          <Line
            key={l.key}
            type="monotone"
            dataKey={l.key}
            stroke={l.color}
            name={l.label ?? l.key}
            strokeWidth={2}
            dot={{ fill: l.color, r: 4 }}
            activeDot={{ r: 6 }}
          />
        ))}
      </ReLineChart>
    </ResponsiveContainer>
  )
}
