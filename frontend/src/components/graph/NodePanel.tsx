import { useEffect, useState } from 'react';
import { X, Network, Server, ArrowRight } from 'lucide-react';
import { fetchJson } from '../../api/client';
import { EquipmentTimeline } from '../maintenance/EquipmentTimeline';

interface NodePanelProps {
  nodeId: string;
  onClose: () => void;
}

export function NodePanel({ nodeId, onClose }: NodePanelProps) {
  const [details, setDetails] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    fetchJson(`/graph/node/${encodeURIComponent(nodeId)}`)
      .then(setDetails)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [nodeId]);

  return (
    <div className="absolute top-0 right-0 h-full w-80 bg-surface-raised border-l border-border shadow-2xl flex flex-col z-20 transform transition-transform duration-300">
      <div className="p-4 border-b border-border flex items-center justify-between bg-surface-alt">
        <h3 className="font-semibold text-text flex items-center gap-2">
          <Server size={16} className="text-primary" />
          Node Details
        </h3>
        <button onClick={onClose} className="text-text-dim hover:text-text">
          <X size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {loading ? (
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-border rounded w-1/2"></div>
            <div className="h-20 bg-border rounded"></div>
          </div>
        ) : !details ? (
          <div className="text-text-dim text-sm text-center">Node not found.</div>
        ) : (
          <>
            <div>
              <div className="text-[10px] uppercase tracking-wider text-primary font-bold mb-1">
                {details.label}
              </div>
              <h2 className="text-xl font-bold text-text mb-4 break-words">
                {details.name}
              </h2>
            </div>

            {details.label === 'Equipment' && (
              <div>
                <h4 className="text-sm font-semibold text-text border-b border-border pb-2 mb-3">
                  Maintenance Timeline
                </h4>
                <EquipmentTimeline equipmentId={details.id} />
              </div>
            )}

            <div>
              <h4 className="text-sm font-semibold text-text flex items-center gap-2 border-b border-border pb-2 mb-3">
                <Network size={14} /> Connections
              </h4>
              <div className="space-y-2">
                {details.connections.length === 0 ? (
                  <p className="text-xs text-text-dim">No direct connections.</p>
                ) : (
                  details.connections.map((conn: any, idx: number) => (
                    <div key={idx} className="bg-surface p-2 rounded border border-border text-xs flex items-start gap-2">
                      <ArrowRight size={12} className="text-data shrink-0 mt-0.5" />
                      <div>
                        <div className="text-[10px] text-text-dim font-mono mb-0.5">
                          {conn.type}
                        </div>
                        <div className="text-text font-medium break-words">
                          {conn.name}
                        </div>
                        <div className="text-[10px] text-primary mt-1">
                          {conn.label}
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
