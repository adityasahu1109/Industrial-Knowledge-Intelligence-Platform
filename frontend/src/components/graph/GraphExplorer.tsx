import { useEffect, useState, useRef } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { fetchJson } from '../../api/client';
import { Network, Activity } from 'lucide-react';

export function GraphExplorer() {
  const [data, setData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const fgRef = useRef<any>();
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

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

  return (
    <div className="h-full flex flex-col bg-surface-alt rounded-xl border border-border overflow-hidden">
      <div className="flex items-center justify-between px-5 py-3 border-b border-border bg-surface-alt z-10 relative">
        <div className="flex items-center gap-3">
          <Network className="w-4 h-4 text-data" />
          <h2 className="text-sm font-semibold text-text">Knowledge Graph Explorer</h2>
        </div>
        
        {/* Legend */}
        <div className="flex items-center gap-4 text-[10px] uppercase tracking-wider text-text-dim font-medium">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-data"></span> Equipment
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-critical"></span> Event
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-warning"></span> Date
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-primary"></span> Other
          </div>
        </div>
      </div>
      
      <div ref={containerRef} className="flex-1 relative bg-surface">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-text-dim">
            <Activity className="w-5 h-5 animate-pulse mr-2" /> Loading graph...
          </div>
        ) : data.nodes.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-text-dim">
            No graph data found. Wait for ingestion entity extraction.
          </div>
        ) : (
          <ForceGraph2D
            ref={fgRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={data}
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
              if (fgRef.current) {
                fgRef.current.centerAt(node.x, node.y, 1000);
                fgRef.current.zoom(8, 2000);
              }
            }}
          />
        )}
      </div>
    </div>
  );
}
