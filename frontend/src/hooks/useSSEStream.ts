import { useState, useCallback, useRef } from "react";
import type { StreamSource } from "../types/chat";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

interface StreamHandlers {
  onToken?: (token: string) => void;
  onDone?: (sources: StreamSource[], attachments: any[]) => void;
  onError?: (error: Error) => void;
}

function parseSSELines(buffer: string, handlers: StreamHandlers): string {
  const lines = buffer.split("\n");
  const remaining = lines.pop() || "";

  for (const line of lines) {
    if (!line.startsWith("data: ")) continue;
    const payloadStr = line.slice(6).trim();
    if (!payloadStr) continue;
    
    try {
      const payload = JSON.parse(payloadStr);
      if (payload.type === 'catchup' || (payload.token && !payload.done && payload.type !== 'done' && payload.type !== 'error')) {
        handlers.onToken?.(payload.token);
      } else if (payload.done || payload.type === 'done') {
        handlers.onDone?.(payload.sources || [], payload.attachments || []);
      } else if (payload.type === 'error') {
        handlers.onError?.(new Error(payload.error || "Unknown error"));
      }
    } catch (e) {
      console.error("SSE parse error:", e, payloadStr);
    }
  }
  return remaining;
}

export function useSSEStream() {
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = useCallback(async (messageId: string, cursor: number, handlers: StreamHandlers) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();
    setLoading(true);

    try {
      const resp = await fetch(`${API_URL}/chat/stream/${messageId}?cursor=${cursor}`, {
        signal: abortControllerRef.current.signal
      });
      if (!resp.ok) throw new Error(`HTTP error ${resp.status}`);

      const reader = resp.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        buffer = parseSSELines(buffer, handlers);
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        console.error("Stream error:", e);
        handlers.onError?.(e);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const cancelStream = useCallback(async (messageId: string) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    try {
      await fetch(`${API_URL}/chat/cancel/${messageId}`, { method: "POST" });
    } catch (e) {
      console.error("Failed to cancel message", e);
    }
  }, []);

  return { startStream, cancelStream, loading };
}
