from core.ollama_client import embed

def embed_chunks(chunks: list[dict]) -> list[list[float]]:
    """
    Generates embeddings for a list of chunk dictionaries.
    chunks format: [{"text": "...", "metadata": {}, "id": "..."}]
    Returns list of embeddings.
    """
    embeddings = []
    # Process sequentially since Ollama doesn't batch natively
    # In a real production setup with vLLM, this would be batched.
    for i, chunk in enumerate(chunks):
        # Print progress every 10 chunks for large docs
        if i > 0 and i % 10 == 0:
            print(f"Embedded {i}/{len(chunks)} chunks...")
        
        emb = embed(chunk["text"])
        embeddings.append(emb)
        
    return embeddings
