import { useState, useRef, useEffect } from 'react';
import { MessageList } from './MessageList';
import { useSSEStream } from '../../hooks/useSSEStream';
import type { ChatMessage } from '../../types/chat';
import { Send, Mic } from 'lucide-react';

export function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const { text: streamingText, sources: streamingSources, loading, query } = useSSEStream();
  const endRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingText]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userQuery = input.trim();
    setInput('');
    
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'user',
      content: userQuery
    }]);

    const result = await query(userQuery);
    
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'assistant',
      content: result.text,
      sources: result.sources
    }]);
  };

  return (
    <div className="h-full flex flex-col relative">
      <MessageList 
        messages={messages} 
        loading={loading} 
        streamingText={streamingText}
        streamingSources={streamingSources}
      />
      <div ref={endRef} />

      <div className="p-4 bg-surface shrink-0 border-t border-white/5 z-10 sticky bottom-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Query knowledge base (e.g., 'When was P-101 last inspected?')"
            className="w-full bg-white/5 border border-white/10 rounded-xl py-3 pl-4 pr-24 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 text-text placeholder-text-muted transition-all"
            disabled={loading}
          />
          <div className="absolute right-2 flex items-center gap-1">
            <button 
              type="button"
              className="p-2 text-text-muted hover:text-text hover:bg-white/10 rounded-lg transition-colors"
              title="Voice Input (Phase 4)"
            >
              <Mic size={18} />
            </button>
            <button 
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2 bg-primary text-surface rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors"
            >
              <Send size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
