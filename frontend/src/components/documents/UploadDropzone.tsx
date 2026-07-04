import { useState, useRef } from 'react';
import { UploadCloud, AlertCircle, Loader2 } from 'lucide-react';
import { fetchJson } from '../../api/client';

export function UploadDropzone({ onUploadSuccess }: { onUploadSuccess: () => void }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await handleUpload(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async (file: File) => {
    // Only PDF for Phase 1
    if (file.type !== "application/pdf") {
      setError("Only PDF files are supported currently.");
      return;
    }
    
    setError(null);
    setUploading(true);
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("doc_type", "manual"); // Default for now
    
    try {
      await fetchJson("/documents/upload", {
        method: "POST",
        body: formData,
      });
      onUploadSuccess();
    } catch (err: any) {
      setError(err.message || "Failed to upload document");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div 
      className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
        isDragging 
          ? 'border-primary bg-primary/5 scale-[1.01]' 
          : 'border-border bg-surface-alt/30 hover:border-primary/30 hover:bg-primary/5'
      }`}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <input 
        type="file" 
        ref={fileInputRef}
        onChange={(e) => e.target.files && handleUpload(e.target.files[0])} 
        className="hidden" 
        accept="application/pdf"
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
      
      <h3 className="text-lg font-medium mb-1 text-text-muted">
        {uploading ? 'Uploading and processing...' : 'Drag & drop industrial documents'}
      </h3>
      <p className="text-xs text-text-dim mb-4">
        {error ? <span className="text-critical">{error}</span> : 'PDF files up to 50MB'}
      </p>
      
      <button 
        disabled={uploading}
        className="px-5 py-2 bg-surface-raised border border-border rounded-lg text-sm text-text-muted hover:text-text hover:border-border-active transition-all disabled:opacity-50"
      >
        Select Files
      </button>
    </div>
  );
}
