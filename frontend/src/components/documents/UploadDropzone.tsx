import { useState, useRef, useEffect } from 'react';
import { UploadCloud, AlertCircle, Loader2, FileType } from 'lucide-react';
import { fetchJson } from '../../api/client';

export function UploadDropzone({ onUploadSuccess }: { onUploadSuccess: () => void }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeJobId, setActiveJobId] = useState<string | null>(() => sessionStorage.getItem('active_upload_job'));
  const [jobStatus, setJobStatus] = useState<string>('Uploading and processing...');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (!activeJobId) return;
    
    let isMounted = true;
    const abortController = new AbortController();
    
    const streamProgress = async () => {
      setUploading(true);
      try {
        const resp = await fetch(`http://localhost:8000/api/jobs/${activeJobId}/stream`, {
          signal: abortController.signal
        });
        
        if (!resp.ok) throw new Error("Failed to stream job");
        
        const reader = resp.body!.getReader();
        const decoder = new TextDecoder();
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const lines = decoder.decode(value).split("\n");
          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const payloadStr = line.slice(6).trim();
            if (!payloadStr) continue;
            
            try {
              const payload = JSON.parse(payloadStr);
              if (payload.type === 'progress') {
                if (isMounted) setJobStatus(payload.message);
              } else if (payload.done || payload.type === 'done' || payload.type === 'error') {
                if (isMounted) {
                  setUploading(false);
                  sessionStorage.removeItem('active_upload_job');
                  setActiveJobId(null);
                  setJobStatus('Uploading and processing...');
                  onUploadSuccess();
                }
                return;
              }
            } catch (e) {
              console.error("Parse error", e);
            }
          }
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          console.error("Stream error", err);
          if (isMounted) {
             setUploading(false);
             sessionStorage.removeItem('active_upload_job');
             setActiveJobId(null);
             setJobStatus('Uploading and processing...');
             onUploadSuccess();
          }
        }
      }
    };
    
    streamProgress();
    
    return () => {
      isMounted = false;
      abortController.abort();
    };
  }, [activeJobId, onUploadSuccess]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await handleUploadAll(Array.from(e.dataTransfer.files));
    }
  };

  const handleUploadAll = async (files: File[]) => {
    if (activeJobId) return; // Prevent multiple concurrent uploads for now
    
    const allowedTypes = [
      "application/pdf", 
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "image/png",
      "image/jpeg",
      "image/jpg"
    ];
    
    const validFiles = files.filter(f => allowedTypes.includes(f.type) || f.name.endsWith('.pdf') || f.name.endsWith('.docx') || f.name.endsWith('.xlsx') || f.name.endsWith('.png') || f.name.endsWith('.jpg') || f.name.endsWith('.jpeg'));
    
    if (validFiles.length === 0) {
      setError("Only PDF, DOCX, XLSX, PNG, and JPG files are supported.");
      return;
    }
    if (validFiles.length !== files.length) {
      setError("Some files were skipped (unsupported format).");
    } else {
      setError(null);
    }
    
    setUploading(true);
    setJobStatus('Initializing upload...');
    
    for (const file of validFiles) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", "auto");
      
      try {
        const data = await fetchJson("/documents/upload", {
          method: "POST",
          body: formData,
        });
        
        if (data.job_id) {
          sessionStorage.setItem('active_upload_job', data.job_id);
          setActiveJobId(data.job_id);
          // Wait for this job to stream to completion via useEffect
          return; // only handle first file for simplicity in demo session system
        }
      } catch (err: any) {
        console.error("Failed to upload", file.name, err);
        setUploading(false);
      }
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-[11px] font-semibold tracking-wider text-text-muted bg-surface-page px-3 py-1.5 border border-border">
          <FileType size={14} />
          <span className="uppercase">Auto-classification Active</span>
        </div>
      </div>
      
      <div 
        className={`border border-dashed p-8 text-center transition-all cursor-pointer card shadow-none ${
          isDragging 
            ? 'border-primary bg-primary/5 scale-[1.01]' 
            : 'border-border bg-white hover:border-primary/50 hover:bg-slate-50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={(e) => e.target.files && handleUploadAll(Array.from(e.target.files))} 
          className="hidden" 
          accept=".pdf,.docx,.xlsx,.png,.jpg,.jpeg,image/png,image/jpeg,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          multiple
        />
        
        <div className="flex justify-center mb-4 text-text-dim">
          {uploading ? (
            <Loader2 size={48} className="animate-spin text-primary" />
          ) : error ? (
            <AlertCircle size={48} className="text-critical" />
          ) : (
            <UploadCloud size={48} className={isDragging ? 'text-primary transition-colors' : ''} />
          )}
        </div>
        
        <h3 className="text-[14px] font-semibold mb-1 text-text">
          {uploading ? jobStatus : 'Drag & drop industrial documents or drawings'}
        </h3>
        <p className="text-[11px] text-text-muted mb-4">
          {error ? <span className="text-status-error">{error}</span> : 'PDF, DOCX, XLSX, PNG, JPG files'}
        </p>
        <button 
          disabled={uploading}
          onClick={(e: React.MouseEvent) => { e.stopPropagation(); fileInputRef.current?.click(); }}
          className="px-6 py-2 bg-white border border-border rounded text-[13px] font-medium text-text hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          Select Files
        </button>
      </div>
    </div>
  );
}
