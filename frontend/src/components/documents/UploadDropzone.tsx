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
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await handleUploadAll(Array.from(e.dataTransfer.files));
    }
  };

  const handleUploadAll = async (files: File[]) => {
    const allowedTypes = [
      "application/pdf", 
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ];
    
    const validFiles = files.filter(f => allowedTypes.includes(f.type) || f.name.endsWith('.pdf') || f.name.endsWith('.docx') || f.name.endsWith('.xlsx'));
    
    if (validFiles.length === 0) {
      setError("Only PDF, DOCX, and XLSX files are supported.");
      return;
    }
    if (validFiles.length !== files.length) {
      setError("Some files were skipped (unsupported format).");
    } else {
      setError(null);
    }
    
    setUploading(true);
    
    // Upload sequentially to avoid overloading the backend/UI
    for (const file of validFiles) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", "manual");
      
      try {
        await fetchJson("/documents/upload", {
          method: "POST",
          body: formData,
        });
      } catch (err: any) {
        console.error("Failed to upload", file.name, err);
      }
    }
    
    setUploading(false);
    onUploadSuccess();
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
        onChange={(e) => e.target.files && handleUploadAll(Array.from(e.target.files))} 
        className="hidden" 
        accept=".pdf,.docx,.xlsx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
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
      
      <h3 className="text-lg font-medium mb-1 text-text-muted">
        {uploading ? 'Uploading and processing...' : 'Drag & drop industrial documents'}
      </h3>
      <p className="text-xs text-text-dim mb-4">
        {error ? <span className="text-critical">{error}</span> : 'PDF, DOCX, XLSX files up to 50MB'}
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
