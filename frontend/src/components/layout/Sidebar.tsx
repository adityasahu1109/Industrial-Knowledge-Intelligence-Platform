import { NavLink } from 'react-router-dom'
import { MessageSquare, FileText, Activity, ShieldAlert, GitBranch, PenTool, Hexagon } from 'lucide-react'

export function Sidebar() {
  return (
    <aside className="w-64 bg-surface-alt border-r border-border flex flex-col shrink-0">
      {/* Brand Area */}
      <div className="px-5 py-6 border-b border-border">
        <div className="flex items-center gap-2 mb-1">
          <Hexagon className="text-primary" size={24} strokeWidth={2.5} />
          <h1 className="font-bold text-lg tracking-tight text-text">IKIP</h1>
        </div>
        <p className="text-xs text-text-dim leading-tight">
          Industrial Knowledge<br />Intelligence Platform
        </p>
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Operations Section */}
        <div className="text-[10px] font-semibold uppercase tracking-[0.15em] text-text-dim px-5 pt-5 pb-2">
          Operations
        </div>
        <nav className="flex flex-col">
          <NavLink
            to="/chat"
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-2.5 text-sm transition-colors ${
                isActive 
                  ? 'border-l-2 border-primary bg-primary/5 text-primary font-medium' 
                  : 'border-l-2 border-transparent text-text-muted hover:text-text hover:bg-surface-hover'
              }`
            }
          >
            <MessageSquare size={18} />
            Intelligence Chat
          </NavLink>
          <NavLink
            to="/documents"
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-2.5 text-sm transition-colors ${
                isActive 
                  ? 'border-l-2 border-primary bg-primary/5 text-primary font-medium' 
                  : 'border-l-2 border-transparent text-text-muted hover:text-text hover:bg-surface-hover'
              }`
            }
          >
            <FileText size={18} />
            Document Base
          </NavLink>
          <NavLink
            to="/graph"
            className={({ isActive }) =>
              `flex items-center gap-3 px-5 py-2.5 text-sm transition-colors ${
                isActive 
                  ? 'border-l-2 border-primary bg-primary/5 text-primary font-medium' 
                  : 'border-l-2 border-transparent text-text-muted hover:text-text hover:bg-surface-hover'
              }`
            }
          >
            <GitBranch size={18} />
            Knowledge Graph
          </NavLink>
        </nav>

        {/* Analysis Section */}
        <div className="text-[10px] font-semibold uppercase tracking-[0.15em] text-text-dim px-5 pt-6 pb-2">
          Analysis
        </div>
        <nav className="flex flex-col gap-0.5">
          {[
            { icon: <PenTool size={18} />, label: 'Drawing Analysis' },
            { icon: <Activity size={18} />, label: 'Maintenance' },
            { icon: <ShieldAlert size={18} />, label: 'Compliance' },
          ].map((item, i) => (
            <div key={i} className="flex items-center justify-between px-5 py-2.5 text-sm opacity-40 cursor-not-allowed border-l-2 border-transparent">
              <div className="flex items-center gap-3 text-text-muted">
                {item.icon}
                {item.label}
              </div>
              <span className="text-[10px] bg-surface-raised px-1.5 py-0.5 rounded text-text-dim border border-border">
                Soon
              </span>
            </div>
          ))}
        </nav>
      </div>

      {/* Bottom Status */}
      <div className="mt-auto px-5 py-4 border-t border-border flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-text-dim">
          <span className="w-2 h-2 rounded-full bg-operational"></span>
          Ollama: Connected
        </div>
        <span className="text-xs font-mono text-text-dim opacity-50">v0.1.0</span>
      </div>
    </aside>
  )
}
