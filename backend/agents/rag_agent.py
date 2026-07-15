from retrieval.vector_store import semantic_search
from retrieval.bm25_index import search as keyword_search
from retrieval.rrf_fusion import rrf_fusion
from core.ollama_client import chat_stream
from typing import Generator

RAG_SYSTEM = """You are an expert industrial knowledge assistant.
Answer questions naturally, but base your answers ONLY on the provided document excerpts.
CRITICAL: When citing a source, you MUST use the exact markdown link format: [1](#source-1) where 1 is the source id.
DO NOT use text like "[Source 1]" or mention filenames in the text. Only use the markdown link format.
If the context doesn't contain enough information, say so clearly."""

def query_stream(user_query: str) -> Generator[dict, None, None]:
    # 1. Phase 1: Hybrid Search (Semantic + Keyword)
    semantic_chunks = semantic_search(user_query, n=8)
    keyword_chunks = keyword_search(user_query, n=8)
    
    chunks = rrf_fusion(semantic_chunks, keyword_chunks, n=8)
    
    # 2. Build context string with source labels
    context_parts = []
    sources = []
    
    for i, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        context_parts.append(f"<source id=\"{i+1}\">\n{chunk['document']}\n</source>")
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
