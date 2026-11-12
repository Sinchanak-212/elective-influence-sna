import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  BarChart2,
  Network,
  Users,
  SlidersHorizontal,
  MessageSquare,
  GraduationCap,
  BookOpen,
  Search,
  GitCompare,
  ClipboardList,
  FileText,
  Info,
  ChevronLeft,
  ChevronRight,
  Zap,
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '../../lib/utils'

const sections = [
  {
    label: 'Dashboard',
    items: [
      { to: '/', icon: LayoutDashboard, label: 'Overview' },
    ],
  },
  {
    label: 'Research Analytics',
    items: [
      { to: '/analytics', icon: BarChart2, label: 'Research Analytics' },
      { to: '/network', icon: Network, label: 'Network Explorer' },
      { to: '/communities', icon: Users, label: 'Community Analysis' },
      { to: '/threshold', icon: SlidersHorizontal, label: 'Threshold Sensitivity' },
      { to: '/peer-discussion', icon: MessageSquare, label: 'Peer Discussion' },
      { to: '/academic', icon: GraduationCap, label: 'Academic Insights' },
    ],
  },
  {
    label: 'Elective Assistant',
    items: [
      { to: '/electives', icon: BookOpen, label: 'Explore Electives' },
      { to: '/finder', icon: Search, label: 'Elective Finder' },
      { to: '/compare', icon: GitCompare, label: 'Compare Electives' },
      { to: '/planner', icon: ClipboardList, label: 'My Planner' },
      { to: '/materials', icon: FileText, label: 'Learning Materials' },
    ],
  },
  {
    label: 'About',
    items: [
      { to: '/about', icon: Info, label: 'About & Methodology' },
    ],
  },
]

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <aside
      className={cn(
        'relative flex h-screen flex-col border-r border-[#2d3748] bg-[#161b27] transition-all duration-200',
        collapsed ? 'w-16' : 'w-60'
      )}
    >
      {/* Logo */}
      <div className={cn('flex items-center gap-2 px-4 py-5', collapsed && 'justify-center px-0')}>
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-[#8b5cf6] to-[#22d3ee]">
          <Zap className="h-4 w-4 text-white" />
        </div>
        {!collapsed && (
          <div>
            <p className="text-xs font-bold tracking-tight text-[#e2e8f0]">Elective</p>
            <p className="text-xs font-bold tracking-tight text-[#8b5cf6]">Influence Analytics</p>
          </div>
        )}
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto px-2 pb-4">
        {sections.map(section => (
          <div key={section.label} className="mb-4">
            {!collapsed && (
              <p className="mb-1 px-3 text-[10px] font-semibold uppercase tracking-widest text-[#8892a4]">
                {section.label}
              </p>
            )}
            {section.items.map(item => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                    collapsed && 'justify-center px-0',
                    isActive
                      ? 'bg-[#8b5cf6]/15 text-[#8b5cf6]'
                      : 'text-[#8892a4] hover:bg-[#2d3748] hover:text-[#e2e8f0]'
                  )
                }
                title={collapsed ? item.label : undefined}
              >
                <item.icon className="h-4 w-4 shrink-0" />
                {!collapsed && item.label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-7 flex h-6 w-6 items-center justify-center rounded-full border border-[#2d3748] bg-[#161b27] text-[#8892a4] hover:text-[#e2e8f0]"
      >
        {collapsed ? <ChevronRight className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
      </button>
    </aside>
  )
}
