from retrieval.vector_store import semantic_search
from retrieval.bm25_index import search as keyword_search
from retrieval.rrf_fusion import rrf_fusion
from core.ollama_client import chat_stream
from typing import Generator

RAG_SYSTEM = """You are a helpful, conversational expert industrial knowledge assistant.
Answer questions naturally, but base your answers ONLY on the provided document excerpts.
When you use information from a source, cite it inline using markdown links with the source number like this: [[1]](#source-1). 
If the context doesn't contain enough information, say so clearly but politely.
Never invent facts not present in the context."""

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
        label = f"Source {i+1}: {meta.get('filename', 'Unknown')}, Page {meta.get('page', 'Unknown')}"
        context_parts.append(f"[{label}]\n{chunk['document']}")
        
        filename = meta.get("filename", "Unknown")
        sources.append({
            "label": f"Source {i+1}",
            "filename": filename,
            "page": meta.get("page", 1),
            "section": meta.get("section", ""),
            "doc_id": meta.get("doc_id", "")
        })

    context = "\n\n---\n\n".join(context_parts)
    prompt = f"Context:\n{context}\n\nQuestion: {user_query}"
    
    # Check if query is graph-oriented
    attachments = []
    if "downstream" in user_query.lower() or "connect" in user_query.lower():
        # Example graph attachment for topology queries
        attachments.append({
            "type": "subgraph",
            "nodes": [
                {"id": "P-101", "name": "P-101", "label": "Equipment"},
                {"id": "HV-201", "name": "HV-201", "label": "Equipment"},
                {"id": "E-301", "name": "E-301", "label": "Equipment"}
            ],
            "links": [
                {"source": "P-101", "target": "HV-201", "type": "FLOWS_TO"},
                {"source": "HV-201", "target": "E-301", "type": "FLOWS_TO"}
            ],
            "focus_node": "P-101"
        })
        
    # Check for drawing sources
    import os
    for src in sources:
        fname = src['filename'].lower()
        if fname.endswith(('.png', '.jpg', '.jpeg', '.webp')) or 'drawing' in src.get('doc_type', '').lower():
            ext = os.path.splitext(fname)[1]
            if not ext: ext = ".png"
            doc_id = src.get('doc_id')
            url = f"/uploads/{doc_id}{ext}" if doc_id else f"/uploads/{src['filename']}"
            
            # Avoid duplicate attachments
            if not any(a.get('source_doc') == src['filename'] for a in attachments):
                attachments.append({
                    "type": "image",
                    "url": url,
                    "caption": f"{src['filename']} - referenced in answer",
                    "source_doc": src['filename']
                })
    
    # 3. Stream answer tokens
    for token in chat_stream(RAG_SYSTEM, prompt):
        yield {"token": token, "done": False}
        
    # 4. Send sources and attachments as final payload
    yield {"token": "", "done": True, "sources": sources, "attachments": attachments}
