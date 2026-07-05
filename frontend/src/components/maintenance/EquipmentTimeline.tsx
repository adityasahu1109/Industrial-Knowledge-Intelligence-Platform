import { useEffect, useState } from 'react';
import { fetchJson } from '../../api/client';
import { Calendar, Clock, Activity } from 'lucide-react';

interface TimelineEvent {
  event: string;
  relation: string;
  date: string;
  doc_id: string;
}

interface EquipmentTimelineProps {
  equipmentId: string;
}

export function EquipmentTimeline({ equipmentId }: EquipmentTimelineProps) {
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchJson(`/maintenance/${encodeURIComponent(equipmentId)}/timeline`)
      .then((data) => setTimeline(data.timeline || []))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [equipmentId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-6 text-text-dim">
        <Activity className="w-4 h-4 animate-pulse mr-2" /> Loading timeline...
      </div>
    );
  }

  if (timeline.length === 0) {
    return (
      <div className="text-center p-6 text-text-dim text-xs">
        No maintenance history found.
      </div>
    );
  }

  // Sort timeline roughly by date if possible
  const sortedTimeline = [...timeline].sort((a, b) => {
    if (a.date === "Unknown Date") return 1;
    if (b.date === "Unknown Date") return -1;
    return new Date(b.date).getTime() - new Date(a.date).getTime();
  });

  return (
    <div className="relative pl-4 mt-4 border-l border-border/50 space-y-6">
      {sortedTimeline.map((item, idx) => (
        <div key={idx} className="relative">
          <span className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-primary border-2 border-surface-raised" />
          
          <div className="text-xs text-text-dim mb-1 flex items-center gap-1.5">
            <Calendar size={12} className="text-data" /> {item.date}
          </div>
          
          <div className="bg-surface p-3 rounded border border-border">
            <div className="text-sm font-medium text-text mb-1">
              {item.event}
            </div>
            <div className="text-[10px] text-primary/70 uppercase tracking-wide font-mono flex items-center gap-1">
              <Clock size={10} /> {item.relation.replace(/_/g, ' ')}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
