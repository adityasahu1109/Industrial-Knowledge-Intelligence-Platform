import { useState, useRef } from 'react';
import { UploadCloud, AlertCircle, Loader2, FileType } from 'lucide-react';
import { fetchJson } from '../../api/client';

export function UploadDropzone({ onUploadSuccess }: { onUploadSuccess: () => void }) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [docType, setDocType] = useState<string>("manual");
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
    
    for (const file of validFiles) {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", docType);
      
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
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-sm text-text-muted bg-surface-alt px-3 py-1.5 rounded-lg border border-border">
          <FileType size={16} />
          <span>Upload as:</span>
          <select 
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="bg-transparent border-none text-text focus:outline-none focus:ring-0 text-sm font-medium ml-1 cursor-pointer"
            disabled={uploading}
          >
            <option value="manual">Manual / Standard Text</option>
            <option value="sop">SOP (Standard Operating Procedure)</option>
            <option value="inspection_report">Inspection Report</option>
            <option value="p&id">Drawing - P&ID</option>
            <option value="pfd">Drawing - PFD</option>
            <option value="unsupported">Drawing - Other (Unsupported)</option>
          </select>
        </div>
      </div>
      
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
        
        <h3 className="text-lg font-medium mb-1 text-text-muted">
          {uploading ? 'Uploading and processing...' : 'Drag & drop industrial documents or drawings'}
        </h3>
        <p className="text-xs text-text-dim mb-4">
          {error ? <span className="text-critical">{error}</span> : 'PDF, DOCX, XLSX, PNG, JPG files'}
        </p>
        
        <button 
          disabled={uploading}
          className="px-5 py-2 bg-surface-raised border border-border rounded-lg text-sm text-text-muted hover:text-text hover:border-border-active transition-all disabled:opacity-50"
          onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
        >
          Select Files
        </button>
      </div>
    </div>
  );
}
