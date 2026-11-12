import { cn } from '../../lib/utils'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'purple' | 'indigo' | 'cyan' | 'green' | 'amber' | 'red' | 'gray'
  size?: 'sm' | 'xs'
}

const variants = {
  purple: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
  indigo: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30',
  cyan: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
  green: 'bg-green-500/15 text-green-300 border-green-500/30',
  amber: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
  red: 'bg-red-500/15 text-red-300 border-red-500/30',
  gray: 'bg-gray-500/15 text-gray-300 border-gray-500/30',
}

export function Badge({ children, variant = 'gray', size = 'sm' }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border font-medium',
        size === 'sm' ? 'px-2.5 py-0.5 text-xs' : 'px-1.5 py-0.5 text-[10px]',
        variants[variant]
      )}
    >
      {children}
    </span>
  )
}
