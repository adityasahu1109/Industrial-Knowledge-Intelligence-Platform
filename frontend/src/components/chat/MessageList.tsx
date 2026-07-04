import type { ChatMessage } from '../../types/chat';
import { StreamingText } from './StreamingText';
import { FileText, User, Terminal } from 'lucide-react';

interface MessageListProps {
  messages: ChatMessage[];
  loading: boolean;
  streamingText: string;
  streamingSources: any[];
}

export function MessageList({ messages, loading, streamingText, streamingSources }: MessageListProps) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-6">
      {messages.length === 0 && (
        <div className="flex flex-col items-center justify-center h-full text-text-muted space-y-4">
          <Terminal size={48} className="opacity-20" />
          <p>Ask a question about the plant equipment, procedures, or compliance.</p>
        </div>
      )}
      
      {messages.map((msg) => (
        <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
          {msg.role === 'assistant' && (
            <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center text-primary shrink-0">
              <Terminal size={16} />
            </div>
          )}
          
          <div className={`max-w-[80%] rounded-2xl p-4 ${
            msg.role === 'user' 
              ? 'bg-primary/20 text-text rounded-tr-sm border border-primary/30' 
              : 'bg-white/5 backdrop-blur-md text-text rounded-tl-sm border border-white/10'
          }`}>
            <div className="prose prose-invert max-w-none text-sm">
              {msg.content}
            </div>
            
            {msg.sources && msg.sources.length > 0 && (
              <div className="mt-4 pt-3 border-t border-white/10 flex flex-wrap gap-2">
                {msg.sources.map((src, i) => (
                  <button key={i} className="flex items-center gap-1.5 text-xs bg-white/5 hover:bg-white/10 border border-white/10 px-2 py-1 rounded-md transition-colors text-text-muted hover:text-text">
                    <FileText size={12} />
                    <span>{src.filename} (p. {src.page})</span>
                  </button>
                ))}
              </div>
            )}
          </div>
          
          {msg.role === 'user' && (
            <div className="w-8 h-8 rounded bg-white/10 flex items-center justify-center text-text-muted shrink-0">
              <User size={16} />
            </div>
          )}
        </div>
      ))}
      
      {/* Streaming Assistant Message */}
      {(loading || streamingText) && (
        <div className="flex gap-4 justify-start">
          <div className="w-8 h-8 rounded bg-primary/20 flex items-center justify-center text-primary shrink-0">
            <Terminal size={16} />
          </div>
          <div className="max-w-[80%] rounded-2xl p-4 bg-white/5 backdrop-blur-md text-text rounded-tl-sm border border-white/10">
            <StreamingText text={streamingText} loading={loading} />
          </div>
        </div>
      )}
    </div>
  );
}
