import { Bell, Settings } from 'lucide-react'
import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/chat': { title: 'Intelligence Chat', subtitle: 'Query your industrial knowledge base' },
  '/documents': { title: 'Document Base', subtitle: 'Manage ingested manuals, reports, and procedures' },
  '/graph': { title: 'Knowledge Graph', subtitle: 'Explore entity relationships and connections' },
}

export function Header() {
  const location = useLocation()
  const current = pageTitles[location.pathname] || { title: 'Platform', subtitle: 'Industrial Knowledge Intelligence' }

  return (
    <header className="h-14 bg-surface border-b border-border px-6 flex items-center justify-between shrink-0 z-10">
      <div className="flex flex-col justify-center">
        <h1 className="text-sm font-semibold text-text">{current.title}</h1>
        <p className="text-xs text-text-dim">{current.subtitle}</p>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-xs text-text-dim">
          <span className="w-2 h-2 rounded-full bg-operational"></span>
          System Online
        </div>
        
        <div className="flex items-center gap-2 border-l border-border pl-4 ml-2">
          <button className="text-text-muted hover:text-text transition-colors">
            <Bell size={16} />
          </button>
          <button className="text-text-muted hover:text-text transition-colors">
            <Settings size={16} />
          </button>
        </div>
      </div>
    </header>
  )
}
