from retrieval.vector_store import get_collection
from rank_bm25 import BM25Okapi
import re

# We will cache the BM25 index in memory for this simple implementation
_bm25_index = None
_corpus_chunks = []

def tokenize(text: str) -> list[str]:
    """Simple whitespace and punctuation tokenizer."""
    text = text.lower()
    return [word for word in re.split(r'\W+', text) if word]

def build_index():
    """Builds the BM25 index from all documents in ChromaDB."""
    global _bm25_index, _corpus_chunks
    collection = get_collection()
    
    # Get all documents
    results = collection.get()
    
    _corpus_chunks = []
    if results and results.get("ids"):
        for i in range(len(results["ids"])):
            _corpus_chunks.append({
                "id": results["ids"][i],
                "document": results["documents"][i],
                "metadata": results["metadatas"][i]
            })
            
    if not _corpus_chunks:
        return
        
    tokenized_corpus = [tokenize(chunk["document"]) for chunk in _corpus_chunks]
    _bm25_index = BM25Okapi(tokenized_corpus)
    print(f"BM25 Index built with {len(_corpus_chunks)} chunks.")

def search(query: str, n: int = 8) -> list[dict]:
    """Searches the BM25 index for the query."""
    global _bm25_index, _corpus_chunks
    
    if _bm25_index is None:
        build_index()
        
    if _bm25_index is None or not _corpus_chunks:
        return []
        
    tokenized_query = tokenize(query)
    doc_scores = _bm25_index.get_scores(tokenized_query)
    
    # Get top n indices
    top_n_indices = sorted(range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True)[:n]
    
    results = []
    for idx in top_n_indices:
        if doc_scores[idx] > 0:
            results.append({
                "chunk": _corpus_chunks[idx],
                "score": doc_scores[idx]
            })
            
    return results
