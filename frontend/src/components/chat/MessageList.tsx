import type { ChatMessage } from '../../types/chat';
import { StreamingText } from './StreamingText';
import { Terminal } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { SourcesList } from './SourcesList';
import { CitationLink } from './CitationLink';
import { AttachmentViewer } from './AttachmentViewer';

interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
  streamingText: string;
  streamingSources: any[];
  streamingAttachments: any[];
  hasMore?: boolean;
  onLoadMore?: () => void;
}

export function MessageList({ messages, loading, streamingText, streamingSources, streamingAttachments, hasMore, onLoadMore }: MessageListProps) {
  
  // Helper to format timestamp from id
  const formatTime = (id: string) => {
    const d = new Date(parseInt(id));
    if (isNaN(d.getTime())) return 'just now';
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
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
              <div className="chat-prose">
                {msg.role === 'assistant' ? (
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm, remarkBreaks]}
                    components={{
                      a: (props) => <CitationLink {...props} sources={msg.sources} />
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
              
              <SourcesList sources={msg.sources || []} />
              
              {msg.attachments?.map((att, idx) => (
                <AttachmentViewer key={idx} attachment={att} />
              ))}
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
          <div className="flex flex-col gap-1 max-w-[80%] w-full">
            <div className="p-4 bg-surface-alt border border-border rounded-2xl rounded-tl-sm text-text w-full">
              <StreamingText text={streamingText} loading={loading} sources={streamingSources || []} />
              
              <SourcesList sources={streamingSources || []} />
              
              {streamingAttachments?.map((att, idx) => (
                <AttachmentViewer key={idx} attachment={att} />
              ))}
            </div>
            <div className="text-[10px] text-text-dim text-left">generating...</div>
          </div>
        </div>
      )}
    </div>
  );
}
