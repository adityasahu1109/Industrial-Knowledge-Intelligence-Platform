import { useState, useRef, useEffect } from 'react';
import { MessageList } from './MessageList';
import { useSSEStream } from '../../hooks/useSSEStream';
import type { ChatMessage } from '../../types/chat';
import { Send, Mic, Hexagon } from 'lucide-react';

export function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const { text: streamingText, sources: streamingSources, loading, query } = useSSEStream();
  const endRef = useRef<HTMLDivElement>(null);

  // Auto-scroll
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingText]);

  const handleSend = async (userQuery: string) => {
    if (!userQuery.trim() || loading) return;

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

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend(input.trim());
    setInput('');
  };

  return (
    <div className="h-full flex flex-col relative">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8">
          <Hexagon size={64} className="text-primary opacity-20 mb-6" strokeWidth={1} />
          <h2 className="text-xl font-semibold text-text-dim mb-8">Industrial Knowledge Intelligence</h2>
          
          <div className="flex flex-col gap-3 w-full max-w-lg">
            {[
              "When was P-101 last inspected?",
              "What are the safety procedures for heat exchangers?",
              "Show maintenance history for pump equipment"
            ].map((suggestedQuery, i) => (
              <button
                key={i}
                onClick={() => {
                  setInput(suggestedQuery);
                  handleSend(suggestedQuery);
                }}
                className="px-4 py-3 bg-surface-raised border border-border rounded-xl text-sm text-text-muted hover:border-primary/50 hover:text-primary hover:bg-primary/5 transition-all text-left"
              >
                {suggestedQuery}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <MessageList 
          messages={messages} 
          loading={loading} 
          streamingText={streamingText}
          streamingSources={streamingSources}
        />
      )}
      <div ref={endRef} />

      <div className="p-4 bg-surface-alt shrink-0 border-t border-border z-10 sticky bottom-0">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Query knowledge base (e.g., 'When was P-101 last inspected?')"
            className="w-full bg-surface border border-border rounded-xl py-3.5 pl-5 pr-24 text-sm focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/20 text-text placeholder-text-muted transition-all"
            disabled={loading}
          />
          <div className="absolute right-2 flex items-center gap-1">
            <button 
              type="button"
              className="p-2 text-text-muted hover:text-text hover:bg-surface-hover rounded-lg transition-colors"
              title="Voice Input (Phase 4)"
            >
              <Mic size={18} />
            </button>
            <button 
              type="submit"
              disabled={loading || !input.trim()}
              className="p-2 bg-primary text-surface rounded-lg hover:bg-primary/90 disabled:opacity-50 transition-colors font-medium"
            >
              <Send size={18} />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
