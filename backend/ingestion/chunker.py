def chunk_text(text: str, chunk_size: int = 512, overlap: int = 128) -> list[str]:
    """
    Simple whitespace-based chunker. 
    Assumes ~4 chars per token.
    """
    chars_per_token = 4
    chunk_chars = chunk_size * chars_per_token
    overlap_chars = overlap * chars_per_token

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_chars
        # Try to find a nice breaking point (newline or space) near the end
        if end < text_len:
            # Look back up to 100 chars for a newline
            newline_pos = text.rfind('\n', start, end)
            if newline_pos != -1 and newline_pos > start + chunk_chars // 2:
                end = newline_pos + 1
            else:
                # Look for a space
                space_pos = text.rfind(' ', start, end)
                if space_pos != -1 and space_pos > start + chunk_chars // 2:
                    end = space_pos + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        start = end - overlap_chars
        if start < 0:
            start = 0
        if end >= text_len:
            break

    return chunks

def chunk_document(pages: list[dict], doc_metadata: dict, chunk_size: int = 512, overlap: int = 128) -> list[dict]:
    """
    Takes parsed pages and chunks them, attaching metadata to each chunk.
    pages format: [{"text": "...", "page": 1, "section": "..."}]
    Returns list of dicts with 'text' and 'metadata'.
    """
    all_chunks = []
    chunk_index = 0

    for page in pages:
        text_chunks = chunk_text(page["text"], chunk_size, overlap)
        
        for text_chunk in text_chunks:
            meta = doc_metadata.copy()
            meta.update({
                "page": page.get("page", 1),
                "section": page.get("section", ""),
                "chunk_index": chunk_index
            })
            
            all_chunks.append({
                "text": text_chunk,
                "metadata": meta,
                "id": f"{doc_metadata['doc_id']}_chunk_{chunk_index}"
            })
            chunk_index += 1

    return all_chunks
