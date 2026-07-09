import { Link } from 'lucide-react';

interface CitationLinkProps {
  href?: string;
  children?: React.ReactNode;
  sources?: any[];
}

export function CitationLink({ href, children, sources = [] }: CitationLinkProps) {
  // Check if it's a source citation link (e.g. #source-1)
  if (href?.startsWith('#source-')) {
    const sourceIndex = parseInt(href.replace('#source-', '')) - 1;
    const source = sources[sourceIndex];
    
    return (
      <span className="group relative inline-flex items-center justify-center translate-y-[-2px] mx-1">
        <span className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-primary/20 text-primary cursor-help hover:bg-primary hover:text-white transition-colors">
          <Link size={10} strokeWidth={3} />
        </span>
        
        {/* Tooltip */}
        {source && (
          <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-[250px] opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
            <span className="block bg-surface-raised border border-border text-text text-xs p-2 rounded shadow-lg">
              <strong className="block text-primary mb-1">Source {sourceIndex + 1}</strong>
              <span className="block truncate">{source.filename}</span>
              <span className="block text-text-dim mt-0.5">Page {source.page}</span>
            </span>
            {/* Arrow */}
            <span className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-border" />
          </span>
        )}
      </span>
    );
  }

  // Standard link fallback
  return (
    <a href={href} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
      {children}
    </a>
  );
}
