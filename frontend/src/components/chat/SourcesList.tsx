import { useState } from 'react';
import { FileText, ChevronDown, ChevronUp } from 'lucide-react';

interface Source {
  label: string;
  filename: string;
  page: number | string;
  section?: string;
  doc_id?: string;
}

interface SourcesListProps {
  sources: Source[];
}

export function SourcesList({ sources }: SourcesListProps) {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-4 pt-3 border-t border-border">
      <button 
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-2 text-xs font-medium text-text-dim hover:text-text transition-colors"
      >
        <FileText size={14} />
        {sources.length} {sources.length === 1 ? 'Source' : 'Sources'} Consulted
        {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
      </button>
      
      {expanded && (
        <div className="mt-3 flex flex-col gap-2">
          {sources.map((src, i) => (
            <div key={i} className="flex items-start gap-2 text-[12px] bg-surface-raised border border-border p-2 rounded">
              <span className="font-mono text-primary font-bold min-w-[24px]">[{i + 1}]</span>
              <div className="flex-1 overflow-hidden">
                <div className="truncate text-text font-medium" title={src.filename}>{src.filename}</div>
                <div className="text-text-dim mt-0.5">Page {src.page}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
