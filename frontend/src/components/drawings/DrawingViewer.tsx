import { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, Loader2, Target, CheckCircle2, AlertCircle, Play } from 'lucide-react';
import { fetchJson } from '../../api/client';

export function DrawingViewer() {
  const [imageSrc, setImageSrc] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState<any[] | null>(null);
  const [crossRefs, setCrossRefs] = useState<Record<string, any>>({});
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      setError("Please upload an image file (PNG, JPG)");
      return;
    }

    // Display image locally
    const objectUrl = URL.createObjectURL(file);
    setImageSrc(objectUrl);
    setResults(null);
    setCrossRefs({});
    setError(null);
    
    // Upload and analyze
    setAnalyzing(true);
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const data = await fetchJson('/drawings/analyze', {
        method: 'POST',
        body: formData,
      });
      setResults(data.components || []);
      setCrossRefs(data.cross_references || {});
    } catch (err: any) {
      setError(err.message || "Failed to analyze drawing");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto h-full flex flex-col p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold mb-1">Drawing Vision Analysis</h1>
        <p className="text-text-muted text-sm">
          Upload P&ID schematics and blueprints. The AI vision model will automatically identify and extract equipment tags and cross-reference them with the Knowledge Graph.
        </p>
      </div>

      <div className="flex flex-1 gap-6 min-h-0">
        {/* Left Side: Image Viewer */}
        <div className="flex-1 bg-surface-alt border border-border rounded-xl flex flex-col overflow-hidden relative">
          {!imageSrc ? (
            <div className="flex-1 flex items-center justify-center">
              <div 
                className="text-center p-10 border-2 border-dashed border-border rounded-xl hover:border-primary/50 hover:bg-primary/5 cursor-pointer transition-all"
                onClick={() => fileInputRef.current?.click()}
              >
                <div className="flex justify-center mb-4">
                  <UploadCloud size={48} className="text-primary/70" />
                </div>
                <h3 className="text-lg font-medium text-text mb-1">Upload P&ID Diagram</h3>
                <p className="text-xs text-text-dim">Supports PNG, JPG (High resolution recommended)</p>
              </div>
            </div>
          ) : (
            <div className="flex-1 relative overflow-auto p-4 flex items-center justify-center bg-surface">
              <button 
                onClick={() => fileInputRef.current?.click()}
                className="absolute top-4 right-4 bg-surface-raised border border-border px-3 py-1.5 rounded-lg text-xs font-medium hover:text-primary transition-colors z-10 shadow-sm flex items-center gap-2"
              >
                <UploadCloud size={14} /> Upload New
              </button>
              <img 
                src={imageSrc} 
                alt="P&ID Diagram" 
                className="max-w-full h-auto max-h-[80vh] object-contain shadow-lg rounded-lg border border-border/50"
              />
            </div>
          )}
          
          <input 
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept="image/*"
            onChange={handleFileChange}
          />
        </div>

        {/* Right Side: Extraction Results */}
        <div className="w-96 bg-surface-alt border border-border rounded-xl flex flex-col overflow-hidden">
          <div className="p-4 border-b border-border flex items-center justify-between bg-surface-alt/80">
            <h3 className="font-semibold flex items-center gap-2 text-sm">
              <Target size={16} className="text-primary" />
              Extracted Components
            </h3>
            {results && <span className="bg-primary/10 text-primary px-2 py-0.5 rounded text-[10px] font-bold">{results.length} found</span>}
          </div>
          
          <div className="flex-1 overflow-y-auto p-4">
            {analyzing ? (
              <div className="h-full flex flex-col items-center justify-center text-text-dim text-center space-y-4">
                <Loader2 size={32} className="animate-spin text-primary" />
                <div>
                  <p className="font-medium text-text">Analyzing schematic...</p>
                  <p className="text-xs mt-1">minicpm-v is extracting equipment tags</p>
                </div>
              </div>
            ) : error ? (
              <div className="p-4 bg-critical/10 text-critical border border-critical/20 rounded-lg flex items-start gap-3">
                <AlertCircle size={18} className="shrink-0 mt-0.5" />
                <div className="text-sm">{error}</div>
              </div>
            ) : !results ? (
              <div className="h-full flex flex-col items-center justify-center text-text-dim text-center space-y-3 opacity-60">
                <ImageIcon size={32} />
                <p className="text-sm">Upload an image to see extracted equipment</p>
              </div>
            ) : results.length === 0 ? (
              <div className="text-center p-6 text-text-dim text-sm bg-surface rounded-lg border border-border">
                No equipment tags could be identified in this image.
              </div>
            ) : (
              <div className="space-y-3">
                {results.map((comp, idx) => {
                  const isKnown = crossRefs[comp.tag]?.known;
                  return (
                  <div key={idx} className={`bg-surface p-3 rounded-lg border ${isKnown ? 'border-primary/40 shadow-sm shadow-primary/5' : 'border-border'} hover:border-primary/60 transition-all group`}>
                    <div className="flex items-start justify-between mb-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-sm font-bold text-text group-hover:text-primary transition-colors">
                          {comp.tag}
                        </span>
                        {isKnown && (
                          <span className="flex items-center gap-1 text-[10px] text-operational bg-operational/10 px-1.5 py-0.5 rounded border border-operational/20">
                            <CheckCircle2 size={10} /> Known
                          </span>
                        )}
                      </div>
                      <span className="text-[10px] uppercase tracking-wider font-semibold text-text-dim bg-surface-raised px-1.5 py-0.5 rounded">
                        {comp.type}
                      </span>
                    </div>
                    {comp.description && (
                      <p className="text-xs text-text-muted mt-1.5 leading-relaxed">
                        {comp.description}
                      </p>
                    )}
                    {isKnown && (
                      <div className="mt-3 pt-2 border-t border-border/50">
                        <a href="/maintenance" className="text-xs text-primary hover:underline flex items-center gap-1 font-medium">
                          View Timeline <Play size={10} />
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
