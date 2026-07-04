import { useState, useCallback } from "react";
import type { StreamSource } from "../types/chat";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export function useSSEStream() {
  const [text, setText] = useState("");
  const [sources, setSources] = useState<StreamSource[]>([]);
  const [loading, setLoading] = useState(false);

  const query = useCallback(async (userQuery: string) => {
    setText("");
    setSources([]);
    setLoading(true);

    try {
      const resp = await fetch(`${API_URL}/chat/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userQuery, mode: "detailed" }),
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
              setText(prev => prev + payload.token);
            } else {
              setSources(payload.sources ?? []);
              setLoading(false);
            }
          } catch (e) {
            console.error("Error parsing SSE payload:", e, payloadStr);
          }
        }
      }
    } catch (e) {
      console.error("Chat error:", e);
      setText((prev) => prev + "\n\n**Error:** Failed to communicate with the intelligence engine.");
      setLoading(false);
    }
  }, []);

  return { text, sources, loading, query };
}
