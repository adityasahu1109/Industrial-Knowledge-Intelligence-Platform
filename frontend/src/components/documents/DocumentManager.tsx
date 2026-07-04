import { useState, useEffect } from 'react';
import { UploadDropzone } from './UploadDropzone';
import { fetchJson } from '../../api/client';
import type { DocumentItem } from '../../types/document';
import { FileText, Trash2, CheckCircle, AlertCircle, Loader2, RefreshCw } from 'lucide-react';

export function DocumentManager() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadDocuments = async () => {
    try {
      const data = await fetchJson('/documents');
      setDocuments(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocuments();
    
    const interval = setInterval(() => {
      setDocuments(prev => {
        if (prev.some(d => d.status === 'processing' || d.status === 'pending')) {
          loadDocuments();
        }
        return prev;
      });
    }, 3000);
    
    return () => clearInterval(interval);
  }, []);

  const handleDelete = async (docId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return;
    
    try {
      await fetchJson(`/documents/${docId}`, { method: 'DELETE' });
      loadDocuments();
    } catch (e) {
      console.error(e);
    }
  };

  // Stats calculation
  const totalDocs = documents.length;
  const totalChunks = documents.reduce((acc, doc) => acc + (doc.chunk_count || 0), 0);
  const completedDocs = documents.filter(d => d.status === 'complete').length;
  const processingDocs = documents.filter(d => d.status === 'processing' || d.status === 'pending').length;

  return (
    <div className="max-w-6xl mx-auto h-full flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold mb-1">Knowledge Base</h1>
          <p className="text-text-muted text-sm">Manage ingested manuals, procedures, and reports.</p>
        </div>
        <button onClick={loadDocuments} className="p-2 bg-surface-alt border border-border rounded-lg hover:bg-surface-hover hover:border-border-active transition-colors" title="Refresh">
          <RefreshCw size={18} className="text-text-muted" />
        </button>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-surface-alt border border-border rounded-xl p-4">
          <div className="text-2xl font-semibold font-mono text-text">{totalDocs}</div>
          <div className="text-[10px] text-text-dim uppercase tracking-wider mt-1">Total Documents</div>
        </div>
        <div className="bg-surface-alt border border-border rounded-xl p-4">
          <div className="text-2xl font-semibold font-mono text-text">{totalChunks}</div>
          <div className="text-[10px] text-text-dim uppercase tracking-wider mt-1">Data Chunks</div>
        </div>
        <div className="bg-surface-alt border border-border rounded-xl p-4">
          <div className="text-2xl font-semibold font-mono text-operational">{completedDocs}</div>
          <div className="text-[10px] text-text-dim uppercase tracking-wider mt-1">Complete</div>
        </div>
        <div className="bg-surface-alt border border-border rounded-xl p-4">
          <div className="text-2xl font-semibold font-mono text-warning">{processingDocs}</div>
          <div className="text-[10px] text-text-dim uppercase tracking-wider mt-1">Processing</div>
        </div>
      </div>

      <UploadDropzone onUploadSuccess={loadDocuments} />

      <div className="bg-surface-alt border border-border rounded-xl overflow-hidden flex-1 flex flex-col">
        <div className="grid grid-cols-12 gap-4 p-4 border-b border-border text-[11px] uppercase tracking-wider text-text-dim bg-surface-alt">
          <div className="col-span-5 font-semibold">Filename</div>
          <div className="col-span-3 font-semibold">Status</div>
          <div className="col-span-2 text-right font-semibold">Chunks</div>
          <div className="col-span-2 text-center font-semibold">Actions</div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-12 flex flex-col items-center justify-center text-text-dim">
              <Loader2 size={32} className="animate-spin mb-4 opacity-50" />
              <span>Loading document base...</span>
            </div>
          ) : documents.length === 0 ? (
            <div className="p-12 text-center text-text-muted">No documents uploaded yet.</div>
          ) : (
            documents.map(doc => (
              <div key={doc.doc_id} className="grid grid-cols-12 gap-4 p-4 border-b border-border/50 items-center hover:bg-surface-hover transition-colors">
                <div className="col-span-5 flex items-center gap-3 truncate">
                  <FileText size={18} className="text-primary shrink-0 opacity-80" />
                  <span className="truncate text-sm font-medium" title={doc.filename}>{doc.filename}</span>
                </div>
                
                <div className="col-span-3 flex items-center gap-2">
                  {doc.status === 'complete' && <span className="inline-flex items-center gap-1.5 bg-operational/10 text-operational border border-operational/20 px-2.5 py-0.5 rounded-full text-[11px] font-medium"><CheckCircle size={12} /> Complete</span>}
                  {doc.status === 'processing' && <span className="inline-flex items-center gap-1.5 bg-warning/10 text-warning border border-warning/20 px-2.5 py-0.5 rounded-full text-[11px] font-medium"><Loader2 size={12} className="animate-spin" /> Processing</span>}
                  {doc.status === 'pending' && <span className="inline-flex items-center gap-1.5 bg-text-dim/10 text-text-muted border border-text-dim/20 px-2.5 py-0.5 rounded-full text-[11px] font-medium"><Loader2 size={12} /> Queued</span>}
                  {doc.status === 'failed' && <span className="inline-flex items-center gap-1.5 bg-critical/10 text-critical border border-critical/20 px-2.5 py-0.5 rounded-full text-[11px] font-medium"><AlertCircle size={12} /> Failed</span>}
                </div>
                
                <div className="col-span-2 text-right text-sm text-text-muted font-mono">
                  {doc.chunk_count > 0 ? doc.chunk_count : '-'}
                </div>
                
                <div className="col-span-2 flex justify-center">
                  <button 
                    onClick={() => handleDelete(doc.doc_id)}
                    className="p-1.5 text-text-muted hover:text-critical hover:bg-critical/10 rounded-md transition-colors"
                    title="Delete"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
