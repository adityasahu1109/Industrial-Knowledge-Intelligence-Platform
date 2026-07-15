import { useState, useEffect } from 'react';
import { Target, ChevronDown, CheckCircle2, Play, Image as ImageIcon, Loader2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

interface DrawingViewerProps {
  initialDrawingId?: string;
}

export function DrawingViewer({ initialDrawingId }: DrawingViewerProps) {
  const [drawings, setDrawings] = useState<any[]>([]);
  const [selectedDrawingId, setSelectedDrawingId] = useState<string | null>(() => sessionStorage.getItem('active_drawing_viewer_id') || initialDrawingId || null);
  const [drawingData, setDrawingData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch list of drawings
    fetch('http://localhost:8000/api/documents')
      .then(res => res.json())
      .then(data => {
        const d = data.filter((doc: any) => 
          doc.status === 'complete' && 
          ['p&id', 'pfd', 'pid', 'generic_drawing'].includes(doc.doc_type?.toLowerCase())
        );
        setDrawings(d);
        if (!selectedDrawingId && d.length > 0) {
          // Do not auto-select if we just want them to choose, or auto-select first
        }
      })
      .catch(err => console.error("Failed to load drawings list", err));
  }, []);

  useEffect(() => {
    if (selectedDrawingId) {
      loadDrawingData(selectedDrawingId);
    }
  }, [selectedDrawingId]);

  const loadDrawingData = async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`http://localhost:8000/api/drawings/${id}`);
      if (!res.ok) throw new Error("Failed to load drawing data");
      const data = await res.json();
      setDrawingData(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDrawing = (id: string) => {
    setSelectedDrawingId(id);
    if (id) {
      sessionStorage.setItem('active_drawing_viewer_id', id);
    }
    if (id !== selectedDrawingId) {
      setDrawingData(null);
    }
  };

  const imageSrc = drawingData ? `http://localhost:8000/uploads/${drawingData.drawing_id}.png` : null;

  return (
    <div className="max-w-7xl mx-auto h-full flex flex-col p-6">
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-semibold mb-1">Drawing Vision Analysis</h1>
          <p className="text-text-muted text-sm">
            View extracted components, overarching system analysis, and graph relationships from processed P&IDs.
          </p>
        </div>
        
        <div className="relative min-w-[250px]">
          <select 
            className="w-full bg-surface-alt border border-border rounded-lg px-4 py-2 appearance-none cursor-pointer focus:outline-none focus:ring-1 focus:ring-primary text-sm font-medium"
            value={selectedDrawingId || ""}
            onChange={(e) => handleSelectDrawing(e.target.value)}
          >
            <option value="" disabled>Select a drawing...</option>
            {drawings.map(d => (
              <option key={d.id} value={d.doc_id}>{d.filename}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 text-text-muted pointer-events-none" size={16} />
        </div>
      </div>

      <div className="flex flex-1 gap-6 min-h-0">
        {/* Left Side: Metadata & Viewer */}
        <div className="flex-1 bg-surface-alt border border-border rounded-xl flex flex-col overflow-hidden relative">
          <div className="p-4 border-b border-border bg-surface flex gap-6 text-sm">
            <div><span className="text-text-dim uppercase text-[10px] block font-bold tracking-wider">Drawing No.</span><span className="font-mono text-primary">{drawingData?.drawing_number || 'N/A'}</span></div>
            <div><span className="text-text-dim uppercase text-[10px] block font-bold tracking-wider">Revision</span><span className="font-mono">{drawingData?.revision || 'N/A'}</span></div>
            <div><span className="text-text-dim uppercase text-[10px] block font-bold tracking-wider">Unit/Area</span><span className="font-mono">{drawingData?.unit_area || 'N/A'}</span></div>
          </div>
          <div className="flex-1 overflow-auto p-4 flex flex-col gap-4 bg-surface-raised/30">
             {drawingData?.overall_analysis && (
               <div className="bg-primary/5 border border-primary/20 rounded-lg p-6 mb-2 shadow-sm">
                 <h4 className="text-base font-bold text-primary mb-4 flex items-center gap-2 border-b border-primary/10 pb-2">
                   <Target size={16} /> AI System Analysis
                 </h4>
                 <div className="chat-prose">
                   <ReactMarkdown>
                     {drawingData.overall_analysis}
                   </ReactMarkdown>
                 </div>
               </div>
             )}
             
             {imageSrc ? (
               <div className="flex-1 flex items-center justify-center p-4 border border-border/50 rounded-xl bg-surface/50">
                 <img 
                    src={imageSrc} 
                    alt="P&ID Schematic" 
                    className="max-w-full object-contain rounded-lg shadow-sm"
                    onError={(e) => {
                        // Fallback to jpg
                        (e.target as HTMLImageElement).src = imageSrc.replace('.png', '.jpg');
                    }}
                 />
               </div>
             ) : (
               <div className="flex-1 flex items-center justify-center">
                 <div className="text-center text-text-dim border-2 border-dashed border-border/50 rounded-xl p-12 w-full max-w-lg">
                    <ImageIcon size={48} className="mx-auto mb-4 opacity-50" />
                    <p>Select a drawing to view.</p>
                 </div>
               </div>
             )}
          </div>
        </div>

        {/* Right Side: Extraction Results */}
        <div className="w-96 bg-surface-alt border border-border rounded-xl flex flex-col overflow-hidden">
          <div className="p-4 border-b border-border flex items-center justify-between bg-surface-alt/80">
            <h3 className="font-semibold flex items-center gap-2 text-sm">
              <Target size={16} className="text-primary" />
              Extracted Components
            </h3>
            {drawingData?.components && <span className="bg-primary/10 text-primary px-2 py-0.5 rounded text-[10px] font-bold">{drawingData.components.length} found</span>}
          </div>
          
          <div className="flex-1 overflow-y-auto p-4">
            {loading ? (
              <div className="h-full flex flex-col items-center justify-center text-text-dim text-center space-y-4">
                <Loader2 size={32} className="animate-spin text-primary" />
                <p className="font-medium text-text text-sm">Loading drawing data...</p>
              </div>
            ) : error ? (
              <div className="p-4 bg-critical/10 text-critical border border-critical/20 rounded-lg text-sm">{error}</div>
            ) : !drawingData ? (
              <div className="h-full flex flex-col items-center justify-center text-text-dim text-center opacity-60 text-sm">
                Select a drawing from the dropdown to view its components.
              </div>
            ) : drawingData.components?.length === 0 ? (
              <div className="text-center p-6 text-text-dim text-sm bg-surface rounded-lg border border-border">
                No equipment tags extracted.
              </div>
            ) : (
              <div className="space-y-3">
                {drawingData.components.map((comp: any, idx: number) => {
                  const isKnown = drawingData.cross_references?.[comp.tag]?.known;
                  return (
                  <div key={idx} className={`bg-surface p-3 rounded-lg border ${isKnown ? 'border-primary/40 shadow-sm shadow-primary/5' : 'border-border'} hover:border-primary/60 transition-all group`}>
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-bold text-text group-hover:text-primary transition-colors">
                          {comp.tag}
                        </span>
                        {isKnown && (
                          <span className="flex items-center gap-1 text-[10px] text-status-success bg-status-success/10 px-1.5 py-0.5 rounded border border-status-success/20">
                            <CheckCircle2 size={10} /> Known in Graph
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] uppercase tracking-wider font-semibold text-text-dim bg-surface-raised px-1.5 py-0.5 rounded">
                        {comp.type}
                      </span>
                    </div>
                    {isKnown && (
                      <div className="mt-3 pt-2 border-t border-border/50">
                        <a href="/graph" className="text-xs text-primary hover:underline flex items-center gap-1 font-medium">
                          View in Graph Explorer <Play size={10} />
                        </a>
                      </div>
                    )}
                  </div>
                )})}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
