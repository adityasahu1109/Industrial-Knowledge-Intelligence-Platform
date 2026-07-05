import { Filter } from 'lucide-react';

interface GraphFiltersProps {
  hiddenLabels: string[];
  toggleLabel: (label: string) => void;
}

export function GraphFilters({ hiddenLabels, toggleLabel }: GraphFiltersProps) {
  const labels = [
    { name: 'Equipment', color: 'bg-[#818cf8]' },
    { name: 'Event', color: 'bg-[#ef4444]' },
    { name: 'Date', color: 'bg-[#f59e0b]' }
  ];

  return (
    <div className="absolute top-4 left-4 z-20 bg-surface-raised border border-border rounded-lg shadow-lg p-3 w-48">
      <div className="flex items-center gap-2 text-xs font-semibold text-text mb-3 border-b border-border pb-2">
        <Filter size={14} className="text-primary" />
        Filter Nodes
      </div>
      <div className="space-y-2">
        {labels.map((lbl) => {
          const isHidden = hiddenLabels.includes(lbl.name);
          return (
            <label key={lbl.name} className="flex items-center justify-between text-xs cursor-pointer group">
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${lbl.color} ${isHidden ? 'opacity-30' : 'opacity-100'}`}></span>
                <span className={`${isHidden ? 'text-text-dim' : 'text-text'} group-hover:text-primary transition-colors`}>
                  {lbl.name}
                </span>
              </div>
              <input 
                type="checkbox" 
                className="hidden" 
                checked={!isHidden} 
                onChange={() => toggleLabel(lbl.name)} 
              />
              <div className={`w-7 h-4 rounded-full transition-colors relative ${!isHidden ? 'bg-primary' : 'bg-surface-alt border border-border'}`}>
                <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${!isHidden ? 'left-3.5' : 'left-0.5'}`}></div>
              </div>
            </label>
          );
        })}
      </div>
    </div>
  );
}
