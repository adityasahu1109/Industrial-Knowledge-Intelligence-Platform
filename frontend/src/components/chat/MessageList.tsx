import type { ChatMessage } from '../../types/chat';
import { StreamingText } from './StreamingText';
import { Terminal, AlertCircle, RefreshCw, XCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { SourcesList } from './SourcesList';
import { CitationLink } from './CitationLink';
import { AttachmentViewer } from './AttachmentViewer';

interface MessageListProps {
  messages: ChatMessage[];
  loading?: boolean;
  streamingText?: string;
  streamingSources?: any[];
  streamingAttachments?: any[];
  hasMore?: boolean;
  onLoadMore?: () => void;
  onCancel?: () => void;
}

const normalizeCitations = (text: string) => {
  if (!text) return text;
  let normalized = text.replace(/\[Source\s*(\d+)[^\]]*\]/gi, '[$1](#source-$1)');
  normalized = normalized.replace(/Source\s*(\d+)\s*\([^\)]+\)/gi, '[$1](#source-$1)');
  return normalized;
};

export function MessageList({ messages, hasMore, onLoadMore, onCancel }: MessageListProps) {
  
  // Helper to format timestamp from id
  const formatTime = (timeStr?: string, id?: string) => {
    if (timeStr) {
        return new Date(timeStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    if (id) {
        const d = new Date(parseInt(id));
        if (!isNaN(d.getTime())) return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    return 'just now';
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-6">
      {hasMore && (
        <div className="flex justify-center py-2">
          <button 
            onClick={onLoadMore} 
            className="text-xs text-primary hover:underline bg-surface px-4 py-1.5 rounded-full border border-border"
          >
            Load previous messages
          </button>
        </div>
      )}
      
      {messages.map((msg) => (
        <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          {msg.role === 'assistant' && (
            <div className={`w-8 h-8 rounded flex items-center justify-center shrink-0 border ${
              msg.status === 'interrupted' 
                ? 'bg-red-500/10 text-red-500 border-red-500/20' 
                : 'bg-primary/10 text-primary border-primary/20'
            }`}>
              {msg.status === 'interrupted' ? <AlertCircle size={16} /> : <Terminal size={16} />}
            </div>
          )}
          
          <div className="flex flex-col gap-1 max-w-[80%]">
            <div className={`p-4 ${
              msg.role === 'user' 
                ? 'bg-surface-raised border border-border rounded-2xl rounded-tr-sm text-text' 
                : msg.status === 'interrupted'
                  ? 'bg-red-500/5 border border-red-500/20 rounded-2xl rounded-tl-sm text-text'
                  : 'bg-surface-alt border border-border rounded-2xl rounded-tl-sm text-text'
            }`}>
              <div className="prose prose-slate max-w-none text-sm leading-relaxed prose-pre:bg-slate-900 prose-pre:text-slate-50 prose-a:text-primary">
                {msg.role === 'assistant' ? (
                  msg.status === 'generating' ? (
                    <StreamingText text={msg.content} loading={true} sources={msg.sources || []} />
                  ) : (
                    <ReactMarkdown 
                      remarkPlugins={[remarkGfm, remarkBreaks]}
                      components={{
                        a: (props) => <CitationLink {...props} sources={msg.sources} />
                      }}
                    >
                      {normalizeCitations(msg.content)}
                    </ReactMarkdown>
                  )
                ) : (
                  msg.content
                )}
              </div>
              
              <SourcesList sources={msg.sources || []} />
              
              {msg.attachments?.map((att, idx) => (
                <AttachmentViewer key={idx} attachment={att} />
              ))}

              {msg.status === 'interrupted' && (
                <div className="mt-4 pt-4 border-t border-red-500/20 text-sm text-red-500/80 flex items-center gap-2">
                  <AlertCircle size={14} />
                  Generation stopped
                </div>
              )}
            </div>
            
            <div className={`text-[10px] text-text-dim flex items-center gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {formatTime(msg.created_at, msg.id)}
              {msg.status === 'generating' && (
                <>
                  <span>•</span>
                  <span className="text-primary animate-pulse">generating...</span>
                  {onCancel && (
                    <button onClick={onCancel} className="ml-2 flex items-center gap-1 text-red-400 hover:text-red-500 transition-colors bg-red-400/10 px-1.5 py-0.5 rounded">
                      <XCircle size={10} /> Stop
                    </button>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
