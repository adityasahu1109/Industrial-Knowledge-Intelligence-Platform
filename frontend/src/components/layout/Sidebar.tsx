import { NavLink } from 'react-router-dom'
import { MessageSquare, FileText, Activity, ShieldAlert, GitBranch, PenTool } from 'lucide-react'

export function Sidebar() {
  const navItems = [
    { to: '/chat', icon: <MessageSquare size={20} />, label: 'Intelligence Chat' },
    { to: '/documents', icon: <FileText size={20} />, label: 'Document Base' },
    { to: '/graph', icon: <GitBranch size={20} />, label: 'Knowledge Graph' },
    { to: '/drawings', icon: <PenTool size={20} />, label: 'Drawing Analysis', disabled: true },
    { to: '/maintenance', icon: <Activity size={20} />, label: 'Maintenance', disabled: true },
    { to: '/compliance', icon: <ShieldAlert size={20} />, label: 'Compliance', disabled: true },
  ]

  return (
    <aside className="w-64 border-r border-white/10 bg-surface-alt/30 flex flex-col shrink-0">
      <div className="p-4 flex-1">
        <div className="text-xs font-semibold text-text-muted uppercase tracking-wider mb-4 px-2">Navigation</div>
        <nav className="flex flex-col gap-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.disabled ? '#' : item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                  item.disabled 
                    ? 'opacity-40 cursor-not-allowed' 
                    : isActive 
                      ? 'bg-primary/10 text-primary font-medium' 
                      : 'hover:bg-white/5 text-text-muted hover:text-text'
                }`
              }
              onClick={(e) => {
                if (item.disabled) e.preventDefault()
              }}
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </aside>
  )
}
