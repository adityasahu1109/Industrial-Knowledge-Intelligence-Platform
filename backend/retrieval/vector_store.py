from core.database import get_collection
from core.ollama_client import embed

def add_chunks(chunks: list[dict], embeddings: list[list[float]]):
    """
    Adds chunks and embeddings to ChromaDB.
    """
    collection = get_collection()
    
    ids = [c["id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    
    # ChromaDB add handles batching internally, but we can just pass the whole list
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

def semantic_search(query: str, n: int = 8, doc_ids: list[str] = None) -> list[dict]:
    """
    Searches ChromaDB for the query.
    Returns list of dicts matching chunk format.
    """
    collection = get_collection()
    query_embedding = embed(query)
    
    where = None
    if doc_ids:
        if len(doc_ids) == 1:
            where = {"doc_id": doc_ids[0]}
        else:
            where = {"doc_id": {"$in": doc_ids}}
            
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n,
        where=where
    )
    
    formatted_results = []
    if not results["ids"] or len(results["ids"][0]) == 0:
        return formatted_results
        
    for i in range(len(results["ids"][0])):
        formatted_results.append({
            "id": results["ids"][0][i],
            "document": results["documents"][0][i],
            "metadata": results["metadatas"][0][i]
        })
        
    return formatted_results
