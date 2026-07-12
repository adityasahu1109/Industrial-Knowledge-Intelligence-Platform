import { useState, useRef, useEffect } from 'react';
import ForceGraph2D from 'react-force-graph-2d';

export function AttachmentViewer({ attachment }: { attachment: any }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 400, height: 300 });

  useEffect(() => {
    if (attachment.type === 'subgraph' && containerRef.current) {
      const observer = new ResizeObserver(entries => {
        setDimensions({
          width: entries[0].contentRect.width,
          height: entries[0].contentRect.height
        });
      });
      observer.observe(containerRef.current);
      return () => observer.disconnect();
    }
  }, [attachment.type]);

  if (attachment.type === 'image') {
    return (
      <div className="mt-4 rounded-xl overflow-hidden border border-border bg-surface-alt">
        <img 
          src={`http://localhost:8000${attachment.url}`} 
          alt={attachment.caption} 
          className="w-full max-h-64 object-contain bg-slate-900"
        />
        <div className="px-3 py-2 text-[10px] uppercase tracking-wider text-text-dim border-t border-border font-medium">
          {attachment.caption}
        </div>
      </div>
    );
  }

  if (attachment.type === 'subgraph') {
    return (
      <div className="mt-4 border border-border rounded-xl overflow-hidden bg-surface-alt">
        <div className="px-3 py-2 text-[10px] uppercase tracking-wider text-text-dim border-b border-border font-medium bg-surface">
          Related Topology
        </div>
        <div ref={containerRef} className="h-[250px] w-full relative">
          <ForceGraph2D
            width={dimensions.width}
            height={dimensions.height}
            graphData={{
              nodes: attachment.nodes,
              links: attachment.links
            }}
            nodeLabel="name"
            nodeColor={(n: any) => n.id === attachment.focus_node ? '#f59e0b' : '#818cf8'}
            linkColor={() => '#475569'}
            nodeRelSize={6}
            nodeCanvasObjectMode={() => 'after'}
            nodeCanvasObject={(node: any, ctx, globalScale) => {
              if (globalScale >= 1.5) {
                const label = node.name;
                const fontSize = 12 / globalScale;
                ctx.font = `${fontSize}px Sans-Serif`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
                ctx.fillText(label, node.x, node.y + (6 + fontSize));
              }
            }}
            linkDirectionalArrowLength={3.5}
            linkDirectionalArrowRelPos={1}
            d3AlphaDecay={0.02}
            d3VelocityDecay={0.3}
          />
        </div>
      </div>
    );
  }

  return null;
}
