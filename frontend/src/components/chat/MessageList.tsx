import type { ChatMessage } from '../../types/chat';
import { StreamingText } from './StreamingText';
import { FileText, Terminal } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';

interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
  streamingText: string;
  streamingSources: any[];
}

export function MessageList({ messages, loading, streamingText, streamingSources }: MessageListProps) {
  
  // Helper to format timestamp from id
  const formatTime = (id: string) => {
    const d = new Date(parseInt(id));
    if (isNaN(d.getTime())) return 'just now';
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-6">
      {messages.map((msg) => (
        <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          {msg.role === 'assistant' && (
            <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary shrink-0 border border-primary/20">
              <Terminal size={16} />
            </div>
          )}
          
          <div className="flex flex-col gap-1 max-w-[80%]">
            <div className={`p-4 ${
              msg.role === 'user' 
                ? 'bg-surface-raised border border-border rounded-2xl rounded-tr-sm text-text' 
                : 'bg-surface-alt border border-border rounded-2xl rounded-tl-sm text-text'
            }`}>
              <div className="prose prose-invert max-w-none text-sm">
                {msg.role === 'assistant' ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
              
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-border flex flex-wrap gap-2">
                  {msg.sources.map((src, i) => (
                    <button key={i} className="inline-flex items-center gap-1 text-[11px] font-mono bg-surface-raised border border-border px-2 py-0.5 rounded text-data hover:border-data/50 transition-colors">
                      <FileText size={12} />
                      <span>{src.filename} (p. {src.page})</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            
            <div className={`text-[10px] text-text-dim ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
              {formatTime(msg.id)}
            </div>
          </div>
        </div>
      ))}
      
      {/* Streaming Assistant Message */}
      {loading && (
        <div className="flex gap-4 justify-start">
          <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center text-primary shrink-0 border border-primary/20">
            <Terminal size={16} />
          </div>
          <div className="flex flex-col gap-1 max-w-[80%]">
            <div className="p-4 bg-surface-alt border border-border rounded-2xl rounded-tl-sm text-text">
              <StreamingText text={streamingText} loading={loading} />
              
              {streamingSources && streamingSources.length > 0 && (
                <div className="mt-4 pt-3 border-t border-border flex flex-wrap gap-2">
                  {streamingSources.map((src, i) => (
                    <button key={i} className="inline-flex items-center gap-1 text-[11px] font-mono bg-surface-raised border border-border px-2 py-0.5 rounded text-data hover:border-data/50 transition-colors">
                      <FileText size={12} />
                      <span>{src.filename} (p. {src.page})</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
            <div className="text-[10px] text-text-dim text-left">generating...</div>
          </div>
        </div>
      )}
    </div>
  );
}
