import { useState, useCallback, useRef } from "react";
import type { StreamSource } from "../types/chat";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export function useSSEStream() {
  const [text, setText] = useState("");
  const [sources, setSources] = useState<StreamSource[]>([]);
  const [loading, setLoading] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const query = useCallback(async (userQuery: string): Promise<{text: string, sources: StreamSource[]}> => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    setText("");
    setSources([]);
    setLoading(true);
    let finalText = "";
    let finalSources: StreamSource[] = [];

    try {
      const resp = await fetch(`${API_URL}/chat/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery, mode: "detailed" }),
        signal: abortControllerRef.current.signal
      });

      if (!resp.ok) {
        throw new Error(`HTTP error ${resp.status}`);
      }

      const reader = resp.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const lines = decoder.decode(value).split("\n");
        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          
          const payloadStr = line.slice(6).trim();
          if (!payloadStr) continue;
          
          try {
            const payload = JSON.parse(payloadStr);

            if (!payload.done) {
              finalText += payload.token;
              setText(finalText);
            } else {
              finalSources = payload.sources ?? [];
              setSources(finalSources);
            }
          } catch (e) {
            console.error("Error parsing SSE payload:", e, payloadStr);
          }
        }
      }
    } catch (e: any) {
      if (e.name !== 'AbortError') {
        console.error("Chat error:", e);
        finalText += "\n\n**Error:** Failed to communicate with the intelligence engine.";
        setText(finalText);
      }
    } finally {
      setLoading(false);
    }
    return { text: finalText, sources: finalSources };
  }, []);

  return { text, sources, loading, query };
}
