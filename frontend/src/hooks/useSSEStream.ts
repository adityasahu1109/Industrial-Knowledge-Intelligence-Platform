import { useState, useCallback, useRef, useEffect } from "react";
import type { StreamSource } from "../types/chat";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export function useSSEStream() {
  const [text, setText] = useState("");
  const [sources, setSources] = useState<StreamSource[]>([]);
  const [loading, setLoading] = useState(false);
  const [attachments, setAttachments] = useState<any[]>([]);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = useCallback(async (jobId: string, onComplete?: (text: string, sources: StreamSource[], attachments: any[]) => void) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setLoading(true);
    let finalText = "";
    let finalSources: StreamSource[] = [];
    let finalAttachments: any[] = [];

    try {
      const resp = await fetch(`${API_URL}/jobs/${jobId}/stream`, {
        signal: abortControllerRef.current.signal
      });

      if (!resp.ok) {
        throw new Error(`HTTP error ${resp.status}`);
      }

      const reader = resp.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || ""; // Keep incomplete line in buffer

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          
          const payloadStr = line.slice(6).trim();
          if (!payloadStr) continue;
          
          try {
            const payload = JSON.parse(payloadStr);

            if (!payload.done && payload.type !== 'done' && payload.type !== 'error') {
              if (payload.token) {
                finalText += payload.token;
                setText(finalText);
              }
            } else {
              if (payload.sources) {
                finalSources = payload.sources;
                setSources(finalSources);
              }
              if (payload.attachments) {
                finalAttachments = payload.attachments;
                setAttachments(finalAttachments);
              }
            }
          } catch (e) {
            console.error("Error parsing SSE payload:", e, payloadStr);
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        console.error("Stream error:", e);
        finalText += "\n\n**Error:** Connection lost.";
        setText(finalText);
      }
    } finally {
      setLoading(false);
      sessionStorage.removeItem('active_chat_job');
      if (onComplete) {
        onComplete(finalText, finalSources, finalAttachments);
      }
    }
  }, []);

  useEffect(() => {
    const activeJob = sessionStorage.getItem('active_chat_job');
    if (activeJob) {
      startStream(activeJob);
    }
  }, [startStream]);

  const query = useCallback(async (userQuery: string): Promise<void> => {
    setText("");
    setSources([]);
    setAttachments([]);
    setLoading(true);

    try {
      const resp = await fetch(`${API_URL}/chat/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery, mode: "detailed" })
      });

      if (!resp.ok) throw new Error("Failed to start chat job");
      const data = await resp.json();
      sessionStorage.setItem('active_chat_job', data.job_id);
      
      return new Promise((resolve) => {
        startStream(data.job_id, (finalText, finalSources, finalAttachments) => {
          resolve(); // Let the caller know we're done, but we don't return the data via promise since it might cross tab boundaries
        });
      });
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  }, [startStream]);

  return { text, sources, attachments, loading, query, setText, setSources, setAttachments };
}
