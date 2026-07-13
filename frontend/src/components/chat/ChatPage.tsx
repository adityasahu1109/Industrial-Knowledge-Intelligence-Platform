import { useState, useRef, useEffect } from 'react';
import { MessageList } from './MessageList';
import { useSSEStream } from '../../hooks/useSSEStream';
import type { ChatMessage } from '../../types/chat';
import { Send, Mic, Hexagon } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export function ChatPage() {
  const [sessionId] = useState<string>(() => {
    let sid = sessionStorage.getItem('chat_session_id');
    if (!sid) {
      sid = crypto.randomUUID();
      sessionStorage.setItem('chat_session_id', sid);
    }
    return sid;
  });

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [displayLimit, setDisplayLimit] = useState(10);
  const [input, setInput] = useState('');
  const [isInitializing, setIsInitializing] = useState(true);
  const [activeMessageId, setActiveMessageId] = useState<string | null>(null);
  
  const { startStream, cancelStream, loading } = useSSEStream();
  const endRef = useRef<HTMLDivElement>(null);

  // Initial load — fetch history, reconnect if a message is still generating
  useEffect(() => {
    async function loadHistory() {
      try {
        const resp = await fetch(`${API_URL}/chat/history/${sessionId}`);
        if (resp.ok) {
          const data = await resp.json();
          setMessages(data.messages);
          
          const generating = data.messages.find((m: ChatMessage) => m.status === 'generating' && m.role === 'assistant');
          if (generating) {
            setActiveMessageId(generating.id);
            startStream(generating.id, generating.content.length, {
              onToken: (token) => {
                setMessages(prev => prev.map(m => 
                  m.id === generating.id ? { ...m, content: m.content + token, status: 'generating' } : m
                ));
              },
              onDone: (sources, attachments) => {
                setMessages(prev => prev.map(m => 
                  m.id === generating.id ? { ...m, sources, attachments, status: 'done' } : m
                ));
                setActiveMessageId(null);
              },
              onError: () => {
                setMessages(prev => prev.map(m => 
                  m.id === generating.id ? { ...m, status: 'interrupted' } : m
                ));
                setActiveMessageId(null);
              }
            });
          }
        }
      } catch (e) {
        console.error("Failed to load history", e);
      } finally {
        setIsInitializing(false);
      }
    }
    loadHistory();
  }, [sessionId]);

  // Auto-scroll
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (userQuery: string) => {
    if (!userQuery.trim() || loading) return;
    const queryStr = userQuery.trim();
    setInput('');

    try {
      // POST /send — returns { message_id } immediately
      const resp = await fetch(`${API_URL}/chat/send`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, query: queryStr, mode: "detailed" })
      });
      if (!resp.ok) throw new Error("Failed to send message");
      const data = await resp.json();
      const messageId = data.message_id;

      // Optimistic UI
      setMessages(prev => [
        ...prev,
        { id: crypto.randomUUID(), role: 'user', content: queryStr, status: 'done' },
        { id: messageId, role: 'assistant', content: '', status: 'generating' }
      ]);
      setActiveMessageId(messageId);

      // GET /stream/{message_id} — connect to live SSE
      startStream(messageId, 0, {
        onToken: (token) => {
          setMessages(prev => prev.map(m => 
            m.id === messageId ? { ...m, content: m.content + token } : m
          ));
        },
        onDone: (sources, attachments) => {
          setMessages(prev => prev.map(m => 
            m.id === messageId ? { ...m, sources, attachments, status: 'done' } : m
          ));
          setActiveMessageId(null);
        },
        onError: () => {
          setMessages(prev => prev.map(m => 
            m.id === messageId ? { ...m, status: 'interrupted' } : m
          ));
          setActiveMessageId(null);
        }
      });
    } catch (e) {
      console.error(e);
    }
  };

  const handleCancel = () => {
    if (activeMessageId) {
      cancelStream(activeMessageId);
      setActiveMessageId(null);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSend(input);
  };

  if (isInitializing) {
    return <div className="h-full flex items-center justify-center text-text-dim">Loading session...</div>;
  }

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
                onClick={() => handleSend(suggestedQuery)}
                className="px-4 py-3 bg-surface-raised border border-border rounded-xl text-sm text-text-muted hover:border-primary/50 hover:text-primary hover:bg-primary/5 transition-all text-left"
              >
                {suggestedQuery}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <MessageList 
          messages={messages.slice(-displayLimit)} 
          hasMore={messages.length > displayLimit}
          onLoadMore={() => setDisplayLimit(prev => prev + 10)}
          onCancel={handleCancel}
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
