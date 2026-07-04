from retrieval.vector_store import semantic_search
from core.ollama_client import chat_stream
from typing import Generator

RAG_SYSTEM = """You are an expert industrial knowledge assistant.
Answer questions using ONLY the provided document excerpts.
Always cite your sources using [Document: filename, Page: N] format.
If the context doesn't contain enough information, say so clearly.
Never invent facts not present in the context."""

def query_stream(user_query: str) -> Generator[dict, None, None]:
    # 1. Phase 1: Simple semantic search
    chunks = semantic_search(user_query, n=8)
    
    # 2. Build context string with source labels
    context_parts = []
    sources = []
    
    for i, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        label = f"[Source {i+1}: {meta.get('filename', 'Unknown')}, Page {meta.get('page', 'Unknown')}]"
        context_parts.append(f"{label}\n{chunk['document']}")
        sources.append({
            "label": f"Source {i+1}",
            "filename": meta.get("filename", "Unknown"),
            "page": meta.get("page", 1),
            "section": meta.get("section", ""),
            "doc_id": meta.get("doc_id", "")
        })
        
    context = "\n\n---\n\n".join(context_parts)
    prompt = f"Context:\n{context}\n\nQuestion: {user_query}"
    
    # 3. Stream answer tokens
    for token in chat_stream(RAG_SYSTEM, prompt):
        yield {"token": token, "done": False}
        
    # 4. Send sources as final payload
    yield {"token": "", "done": True, "sources": sources}
