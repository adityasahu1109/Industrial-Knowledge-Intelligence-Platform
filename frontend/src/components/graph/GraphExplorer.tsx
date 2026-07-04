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
    <div className="h-full flex flex-col bg-gray-900 rounded-lg border border-gray-800 overflow-hidden shadow-xl">
      <div className="flex items-center gap-3 p-4 border-b border-gray-800 bg-gray-900/50">
        <Network className="w-5 h-5 text-indigo-400" />
        <h2 className="text-lg font-semibold text-gray-100">Knowledge Graph Explorer</h2>
      </div>
      
      <div ref={containerRef} className="flex-1 relative bg-[#0a0a0a]">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            <Activity className="w-6 h-6 animate-pulse mr-2" /> Loading graph...
          </div>
        ) : data.nodes.length === 0 ? (
          <div className="absolute inset-0 flex items-center justify-center text-gray-500">
            No graph data found. Wait for ingestion entity extraction.
          </div>
        ) : (
          <ForceGraph2D
            ref={fgRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={data}
            nodeLabel="name"
            nodeColor={(n: any) => n.label === 'Equipment' ? '#6366f1' : (n.label === 'Event' ? '#ef4444' : '#14b8a6')}
            linkColor={() => '#334155'}
            nodeRelSize={6}
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
