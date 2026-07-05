def rrf_fusion(semantic_results: list[dict], bm25_results: list[dict], k: int = 60, n: int = 8) -> list[dict]:
    """
    Fuses semantic and keyword search results using Reciprocal Rank Fusion (RRF).
    semantic_results: List of chunk dicts
    bm25_results: List of dicts {"chunk": chunk_dict, "score": float}
    """
    rrf_scores = {}
    fused_results = {}
    
    # Process semantic results
    for rank, chunk in enumerate(semantic_results):
        chunk_id = chunk["id"]
        rrf_scores[chunk_id] = 1.0 / (k + rank + 1)
        fused_results[chunk_id] = chunk
        
    # Process BM25 results
    for rank, item in enumerate(bm25_results):
        chunk = item["chunk"]
        chunk_id = chunk["id"]
        score = 1.0 / (k + rank + 1)
        
        if chunk_id in rrf_scores:
            rrf_scores[chunk_id] += score
        else:
            rrf_scores[chunk_id] = score
            fused_results[chunk_id] = chunk
            
    # Sort by fused score
    sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
    # Return top n chunks
    return [fused_results[chunk_id] for chunk_id in sorted_ids[:n]]
