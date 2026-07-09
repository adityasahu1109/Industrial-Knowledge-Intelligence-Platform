import { NavLink } from 'react-router-dom'
import { MessageSquare, FileText, Activity, ShieldAlert, GitBranch, PenTool, Hexagon } from 'lucide-react'

export function Sidebar() {
  return (
    <aside className="w-[256px] bg-[#002A54] text-white flex flex-col shrink-0 shadow-lg z-20">
      {/* Brand Area */}
      <div className="px-6 py-6 border-b border-white/10">
        <div className="flex items-center gap-2 mb-1">
          <Hexagon className="text-white" size={24} strokeWidth={2.5} />
          <h1 className="font-bold text-lg tracking-tight text-white">IKIP</h1>
        </div>
        <p className="text-[11px] text-white/70 leading-tight uppercase tracking-wider mt-2">
          Industrial Knowledge<br/>Intelligence Platform
        </p>
      </div>

      <div className="flex-1 overflow-y-auto py-4">
        {/* Operations Section */}
        <div className="text-[10px] font-semibold uppercase tracking-[0.15em] text-white/50 px-6 pt-2 pb-3">
          Operations
        </div>
        <nav className="flex flex-col mb-4">
          <NavLink
            to="/chat"
            className={({ isActive }) =>
              `flex items-center gap-3 px-6 py-3 text-[13px] transition-colors ${
                isActive 
                  ? 'bg-white/10 text-white font-medium border-l-4 border-status-success' 
                  : 'border-l-4 border-transparent text-white/70 hover:text-white hover:bg-white/5'
              }`
            }
          >
            <MessageSquare size={18} />
            Intelligence Chat
          </NavLink>
          <NavLink
            to="/documents"
            className={({ isActive }) =>
              `flex items-center gap-3 px-6 py-3 text-[13px] transition-colors ${
                isActive 
                  ? 'bg-white/10 text-white font-medium border-l-4 border-status-success' 
                  : 'border-l-4 border-transparent text-white/70 hover:text-white hover:bg-white/5'
              }`
            }
          >
            <FileText size={18} />
            Document Base
          </NavLink>
          <NavLink
            to="/graph"
            className={({ isActive }) =>
              `flex items-center gap-3 px-6 py-3 text-[13px] transition-colors ${
                isActive 
                  ? 'bg-white/10 text-white font-medium border-l-4 border-status-success' 
                  : 'border-l-4 border-transparent text-white/70 hover:text-white hover:bg-white/5'
              }`
            }
          >
            <GitBranch size={18} />
            Knowledge Graph
          </NavLink>
        </nav>

        {/* Analysis Section */}
        <div className="text-[10px] font-semibold uppercase tracking-[0.15em] text-white/50 px-6 pt-4 pb-3">
          Analysis
        </div>
        <nav className="flex flex-col gap-0.5">
          <NavLink
            to="/drawings"
            className={({ isActive }) =>
              `flex items-center gap-3 px-6 py-3 text-[13px] transition-colors ${
                isActive 
                  ? 'bg-white/10 text-white font-medium border-l-4 border-status-success' 
                  : 'border-l-4 border-transparent text-white/70 hover:text-white hover:bg-white/5'
              }`
            }
          >
            <PenTool size={18} />
            Drawing Analysis
          </NavLink>
          
          <NavLink
            to="/compliance"
            className={({ isActive }) =>
              `flex items-center gap-3 px-6 py-3 text-[13px] transition-colors ${
                isActive 
                  ? 'bg-white/10 text-white font-medium border-l-4 border-status-success' 
                  : 'border-l-4 border-transparent text-white/70 hover:text-white hover:bg-white/5'
              }`
            }
          >
            <ShieldAlert size={18} />
            Compliance
          </NavLink>
        </nav>
      </div>

      {/* Bottom Status */}
      <div className="mt-auto px-6 py-4 border-t border-white/10 flex items-center justify-between bg-black/10">
        <div className="flex items-center gap-2 text-[11px] text-white/70">
          <span className="w-2 h-2 rounded-full bg-status-success"></span>
          Connected
        </div>
        <span className="text-[11px] font-mono text-white/30">v1.0.0</span>
      </div>
    </aside>
  )
}
