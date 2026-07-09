import { Bell, Search, LogOut, User } from 'lucide-react'
import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, { title: string; subtitle: string }> = {
  '/chat': { title: 'Intelligence Chat', subtitle: 'Query your industrial knowledge base' },
  '/documents': { title: 'Document Base', subtitle: 'Manage ingested manuals, reports, and procedures' },
  '/graph': { title: 'Knowledge Graph', subtitle: 'Explore entity relationships and connections' },
}

export function Header() {
  const location = useLocation()
  const current = pageTitles[location.pathname] || { title: 'Platform', subtitle: 'Industrial Knowledge Intelligence' }

  const dateOptions: Intl.DateTimeFormatOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
  const formattedDate = new Date().toLocaleDateString('en-US', dateOptions);

  return (
    <header className="h-[64px] bg-surface-alt border-b border-border px-8 flex items-center justify-between shrink-0 z-10 shadow-sm sticky top-0">
      <div className="flex flex-col justify-center">
        <h1 className="text-base font-semibold text-text">{current.title}</h1>
        <p className="text-xs text-text-muted">{formattedDate}</p>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-[13px] text-text-muted bg-surface px-4 py-1.5 rounded-full border border-border">
          <span className="w-2 h-2 rounded-full bg-status-success"></span>
          System Online
        </div>
      </div>
    </header>
  )
}
