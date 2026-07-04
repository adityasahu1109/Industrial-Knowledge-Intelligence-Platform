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
    
    // Poll for updates if any document is processing
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

  return (
    <div className="max-w-5xl mx-auto h-full flex flex-col gap-6 p-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold mb-1">Knowledge Base</h1>
          <p className="text-text-muted text-sm">Manage ingested manuals, procedures, and reports.</p>
        </div>
        <button onClick={loadDocuments} className="p-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors" title="Refresh">
          <RefreshCw size={18} />
        </button>
      </div>

      <UploadDropzone onUploadSuccess={loadDocuments} />

      <div className="bg-surface-alt/50 border border-white/10 rounded-2xl overflow-hidden flex-1 flex flex-col">
        <div className="grid grid-cols-12 gap-4 p-4 border-b border-white/10 text-sm font-medium text-text-muted bg-white/5">
          <div className="col-span-5">Filename</div>
          <div className="col-span-3">Status</div>
          <div className="col-span-2 text-right">Chunks</div>
          <div className="col-span-2 text-center">Actions</div>
        </div>
        
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center text-text-muted">Loading...</div>
          ) : documents.length === 0 ? (
            <div className="p-8 text-center text-text-muted">No documents uploaded yet.</div>
          ) : (
            documents.map(doc => (
              <div key={doc.doc_id} className="grid grid-cols-12 gap-4 p-4 border-b border-white/5 items-center hover:bg-white/5 transition-colors">
                <div className="col-span-5 flex items-center gap-3 truncate">
                  <FileText size={18} className="text-primary shrink-0" />
                  <span className="truncate" title={doc.filename}>{doc.filename}</span>
                </div>
                
                <div className="col-span-3 flex items-center gap-2 text-sm">
                  {doc.status === 'complete' && <><CheckCircle size={14} className="text-primary" /> Complete</>}
                  {doc.status === 'processing' && <><Loader2 size={14} className="text-accent animate-spin" /> Processing...</>}
                  {doc.status === 'pending' && <><Loader2 size={14} className="text-text-muted" /> Queued</>}
                  {doc.status === 'failed' && <><AlertCircle size={14} className="text-danger" /> Failed</>}
                </div>
                
                <div className="col-span-2 text-right text-sm text-text-muted">
                  {doc.chunk_count > 0 ? doc.chunk_count : '-'}
                </div>
                
                <div className="col-span-2 flex justify-center">
                  <button 
                    onClick={() => handleDelete(doc.doc_id)}
                    className="p-1.5 text-text-muted hover:text-danger hover:bg-danger/10 rounded-md transition-colors"
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
