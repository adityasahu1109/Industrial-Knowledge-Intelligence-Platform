import { Terminal } from 'lucide-react'

export function Header() {
  return (
    <header className="h-16 border-b border-white/10 bg-surface/50 backdrop-blur-md flex items-center justify-between px-6 shrink-0 z-10">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center text-primary">
          <Terminal size={18} />
        </div>
        <h1 className="font-semibold text-lg tracking-tight">Industrial Knowledge Intelligence</h1>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm text-text-muted">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-primary"></span>
          </span>
          System Online
        </div>
      </div>
    </header>
  )
}
