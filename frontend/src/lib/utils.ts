import { clsx, type ClassValue } from 'clsx'

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs)
}

export function formatPct(value: number | null | undefined, decimals = 1): string {
  if (value == null) return '—'
  return `${value.toFixed(decimals)}%`
}

export function formatFloat(value: number | null | undefined, decimals = 3): string {
  if (value == null) return '—'
  return value.toFixed(decimals)
}

/** Convert snake_case to Title Case */
export function toTitle(s: string): string {
  return s.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}

/** Record<string,number> → [{name, value}] sorted descending */
export function recordToChartData(
  record: Record<string, number>
): { name: string; value: number }[] {
  return Object.entries(record)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
}

/** DistributionRow[] → [{name, value}] */
export function distToChartData(
  rows: { category: string; count: number }[]
): { name: string; value: number }[] {
  return rows.map(r => ({ name: r.category, value: r.count }))
}

export const CHART_COLORS = [
  '#8b5cf6', '#6366f1', '#22d3ee', '#34d399', '#f59e0b',
  '#f87171', '#a78bfa', '#67e8f9', '#86efac', '#fcd34d',
]
