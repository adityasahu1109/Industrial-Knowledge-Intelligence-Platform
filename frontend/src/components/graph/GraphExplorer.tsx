import { useEffect, useState, useRef, useMemo } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { fetchJson } from '../../api/client';
import { Network, Activity } from 'lucide-react';
import { NodePanel } from './NodePanel';
import { GraphFilters } from './GraphFilters';

export function GraphExplorer() {
  const [data, setData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const fgRef = useRef<any>();
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [hiddenLabels, setHiddenLabels] = useState<string[]>([]);

  useEffect(() => {
    fetchJson('/graph')
      .then(setData)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(entries => {
      setDimensions({
        width: entries[0].contentRect.width,
        height: entries[0].contentRect.height
      });
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const toggleLabel = (label: string) => {
    setHiddenLabels(prev => 
      prev.includes(label) ? prev.filter(l => l !== label) : [...prev, label]
    );
  };

  const filteredData = useMemo(() => {
    const nodes = data.nodes.filter((n: any) => !hiddenLabels.includes(n.label));
    const nodeIds = new Set(nodes.map((n: any) => n.id));
    const links = data.links.filter((l: any) => {
      const sourceId = typeof l.source === 'object' ? l.source.id : l.source;
      const targetId = typeof l.target === 'object' ? l.target.id : l.target;
      return nodeIds.has(sourceId) && nodeIds.has(targetId);
    });
    return { nodes, links };
  }, [data, hiddenLabels]);

  return (
    <div className="h-full flex flex-col bg-surface-alt rounded-xl border border-border overflow-hidden relative">
      <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-surface-alt z-10 relative">
        <div className="flex items-center gap-3">
          <Network className="w-4 h-4 text-data" />
          <h2 className="text-sm font-semibold text-text">Knowledge Graph Explorer</h2>
        </div>
        
        {/* Legend */}
        <div className="flex items-center gap-4 text-[10px] uppercase tracking-wider text-text-dim font-medium">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#818cf8]"></span> Equipment
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#ef4444]"></span> Event
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#f59e0b]"></span> Date
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#22d3ee]"></span> Other
          </div>
        </div>
      </div>
      
      <div ref={containerRef} className="flex-1 relative bg-surface overflow-hidden">
        <GraphFilters hiddenLabels={hiddenLabels} toggleLabel={toggleLabel} />
        
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-text-dim">
            <Activity className="w-5 h-5 animate-pulse mr-2" /> Loading graph...
          </div>
        ) : filteredData.nodes.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-text-dim">
            No visible nodes. Wait for ingestion or change filters.
          </div>
        ) : (
          <ForceGraph2D
            ref={fgRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={filteredData}
            nodeLabel="name"
            nodeColor={(n: any) => n.label === 'Equipment' ? '#818cf8' : (n.label === 'Event' ? '#ef4444' : (n.label === 'Date' ? '#f59e0b' : '#22d3ee'))}
            linkColor={() => '#1e293b'}
            nodeRelSize={6}
            nodeCanvasObjectMode={() => 'after'}
            nodeCanvasObject={(node: any, ctx, globalScale) => {
              if (globalScale >= 1.5) {
                const label = node.name;
                const fontSize = 12 / globalScale;
                ctx.font = `${fontSize}px Sans-Serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = 'rgba(226, 232, 240, 0.8)';
                ctx.fillText(label, node.x, node.y + (6 + fontSize));
              }
            }}
            linkLabel={(link: any) => link.type || 'RELATED_TO'}
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            onNodeClick={(node: any) => {
              setSelectedNodeId(node.name);
              if (fgRef.current) {
                fgRef.current.centerAt(node.x, node.y, 1000);
                fgRef.current.zoom(8, 2000);
              }
            }}
          />
        )}
        
        {selectedNodeId && (
          <NodePanel nodeId={selectedNodeId} onClose={() => setSelectedNodeId(null)} />
        )}
      </div>
    </div>
  );
}
