import traceback
from datetime import datetime
from core.database import SessionLocal, Document
from ingestion.parsers.pdf_parser import parse_pdf, is_scanned
from ingestion.chunker import chunk_document
from ingestion.embedder import embed_chunks
from retrieval.vector_store import add_chunks
from graph.graph_builder import store_entities_in_graph

def ingest(file_path: str, doc_id: str, doc_type: str, filename: str):
    """
    Orchestrates the full ingestion flow.
    Runs as a background task.
    """
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        db.close()
        return

    try:
        # 1. Update status
        doc.status = 'processing'
        db.commit()
        
        # 2. Format detection & parsing
        ext = file_path.lower().split('.')[-1]
        pages = []
        
        if ext == 'pdf':
            # Phase 1: assume digital PDF
            pages = parse_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        # 3. Chunking
        doc_metadata = {
            "doc_id": doc_id,
            "filename": filename,
            "doc_type": doc_type,
            "date_ingested": datetime.utcnow().isoformat()
        }
        chunks = chunk_document(pages, doc_metadata)
        doc.chunk_count = len(chunks)
        db.commit()
        
        if not chunks:
            raise ValueError("No text extracted from document")
            
        # 4. Embed chunks
        embeddings = embed_chunks(chunks)
        
        # 5. Store in ChromaDB
        add_chunks(chunks, embeddings)
        
        # 5.5 Extract Entities and build Knowledge Graph
        print(f"Extracting entities for {len(chunks)} chunks...")
        # Batch chunks to reduce LLM calls
        batch_size = 3
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]
            combined_text = "\n\n".join([c['text'] for c in batch])
            try:
                store_entities_in_graph(doc_id, combined_text)
            except Exception as e:
                print(f"Warning: Entity extraction failed for batch {i}: {e}")
            print(f"Entities extracted for {min(i+batch_size, len(chunks))}/{len(chunks)} chunks...")
        
        # 6. Mark complete
        doc.status = 'complete'
        doc.completed_at = datetime.utcnow()
        db.commit()
        print(f"Ingestion complete for {filename} ({len(chunks)} chunks)")
        
    except Exception as e:
        print(f"Ingestion failed for {filename}: {e}")
        traceback.print_exc()
        doc.status = 'failed'
        doc.error_details = str(e)
        db.commit()
    finally:
        db.close()
