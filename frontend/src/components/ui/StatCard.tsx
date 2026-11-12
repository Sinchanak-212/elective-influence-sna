import type { ReactNode } from 'react'
import { cn } from '../../lib/utils'

interface StatCardProps {
  label: string
  value: string | number
  sub?: string
  icon?: ReactNode
  accent?: 'purple' | 'indigo' | 'cyan' | 'green' | 'amber'
}

const accentMap = {
  purple: 'text-[#8b5cf6]',
  indigo: 'text-[#6366f1]',
  cyan: 'text-[#22d3ee]',
  green: 'text-[#34d399]',
  amber: 'text-[#f59e0b]',
}

export function StatCard({ label, value, sub, icon, accent = 'purple' }: StatCardProps) {
  return (
    <div className="rounded-xl border border-[#2d3748] bg-[#1c2333] p-5">
      <div className="flex items-start justify-between">
        <p className="text-xs font-semibold uppercase tracking-widest text-[#8892a4]">{label}</p>
        {icon && <span className={cn('opacity-70', accentMap[accent])}>{icon}</span>}
      </div>
      <p className={cn('mt-2 text-3xl font-bold', accentMap[accent])}>{value}</p>
      {sub && <p className="mt-1 text-xs text-[#8892a4]">{sub}</p>}
    </div>
  )
}
