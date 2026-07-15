import traceback
from datetime import datetime
import base64
from core.database import SessionLocal, Document
from ingestion.parsers.pdf_parser import parse_pdf, is_scanned
from ingestion.chunker import chunk_document
from ingestion.embedder import embed_chunks
from retrieval.vector_store import add_chunks
from graph.graph_builder import store_entities_in_graph
from drawing.analyzer import extract_drawing_data
from graph.neo4j_client import neo4j_client
from core.database import Drawing, DrawingTag

def process_drawing(file_path: str, doc_id: str, doc_type: str, filename: str, db):
    """Processes a drawing, extracts tags, writes to Neo4j and ChromaDB."""
    ext = file_path.lower().split('.')[-1]
    
    if ext == 'pdf':
        import fitz
        doc = fitz.open(file_path)
        page = doc[0]
        # Use high resolution DPI for analysis
        pix = page.get_pixmap(dpi=150)
        # Create a new PNG file path in the same directory
        png_path = file_path.replace('.pdf', '.png')
        pix.save(png_path)
        with open(png_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
    else:
        with open(file_path, "rb") as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
    
    # 1. Analyze image to get tags, title block, connections
    results = extract_drawing_data(base64_image)
    
    title_block = results.get("title_block", {})
    components = results.get("components", [])
    connections = results.get("connections", [])
    overall_analysis = results.get("overall_analysis", "")
    
    # 2. Save Drawing to SQLite
    db_drawing = Drawing(
        id=doc_id, 
        filename=filename,
        drawing_number=title_block.get('drawing_number', ''),
        revision=title_block.get('revision', ''),
        unit_area=title_block.get('unit_area', ''),
        overall_analysis=overall_analysis
    )
    db.add(db_drawing)
    components = results.get("components", [])
    connections = results.get("connections", [])
    
    # 3. Embed Drawing Summary to ChromaDB
    summary_parts = [f"Drawing {filename}"]
    if title_block.get('drawing_number'):
        summary_parts.append(f"Number: {title_block['drawing_number']}")
    if title_block.get('revision'):
        summary_parts.append(f"Rev: {title_block['revision']}")
    if title_block.get('title'):
        summary_parts.append(f"Title: {title_block['title']}")
    
    summary_str = ", ".join(summary_parts) + ". "
    if components:
        tags = [c['tag'] for c in components]
        summary_str += f"Shows components: {', '.join(tags)}."
        
    overall_analysis = results.get("overall_analysis", "")
    if overall_analysis:
        summary_str += f"\n\nAnalysis: {overall_analysis}"
        
    doc_metadata = {
        "doc_id": doc_id,
        "filename": filename,
        "doc_type": doc_type,
        "date_ingested": datetime.utcnow().isoformat()
    }
    
    # Chunking just the summary
    chunks = [{
        "id": f"{doc_id}_chunk_0",
        "text": summary_str, 
        "metadata": {**doc_metadata, "chunk_index": 0}
    }]
    embeddings = embed_chunks(chunks)
    add_chunks(chunks, embeddings)
    
    # 4. Neo4j Integration
    driver = neo4j_client.driver
    if driver:
        with driver.session() as session:
            # Create Drawing Node
            session.run("""
                MERGE (d:Drawing {id: $id})
                SET d.filename = $filename,
                    d.drawing_number = $drawing_number,
                    d.revision = $revision,
                    d.unit_area = $unit_area,
                    d.overall_analysis = $overall_analysis
            """, id=doc_id, filename=filename, 
                 drawing_number=title_block.get('drawing_number', ''),
                 revision=title_block.get('revision', ''),
                 unit_area=title_block.get('unit_area', ''),
                 overall_analysis=overall_analysis)
            
            # Create Equipment Nodes & Relations
            for comp in components:
                tag = comp["tag"]
                # Save Tag to SQLite
                db_tag = DrawingTag(drawing_id=doc_id, tag=tag, type=comp.get("type"))
                db.add(db_tag)
                
                session.run("""
                    MERGE (e:Equipment {tag: $tag})
                    MERGE (d:Drawing {id: $id})
                    MERGE (d)-[:SHOWS]->(e)
                """, tag=tag, id=doc_id)
                
            # Create Topology Edges (ONLY for P&ID / PFD)
            if doc_type.lower() in ["p&id", "pfd", "pid"]:
                for conn in connections:
                    session.run("""
                        MERGE (e1:Equipment {tag: $from_tag})
                        MERGE (e2:Equipment {tag: $to_tag})
                        MERGE (e1)-[:CONNECTED_TO {type: $c_type}]->(e2)
                    """, from_tag=conn["from"], to_tag=conn["to"], c_type=conn["type"])
    
    return len(chunks)

def ingest(file_path: str, doc_id: str, doc_type: str, category: str, filename: str, job_id: str):
    """
    Background task to parse, chunk, embed, and index a document.
    """
    from core.database import Job
    from routers.jobs import publish_sync
    import json
    
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first() if job_id else None
    
    def log_progress(msg: str):
        print(msg)
        if job:
            payload = {"type": "progress", "message": msg}
            payload_str = json.dumps(payload)
            job.accumulated_output = (job.accumulated_output or '') + payload_str + '\n'
            db.commit()
            publish_sync(job_id, payload)
            
    def finish_job(status: str, result: dict = None):
        if job:
            job.status = status
            if result:
                job.result_json = json.dumps(result)
            db.commit()
            payload = {"type": "done" if status == "done" else "error", "done": True, "result": result}
            publish_sync(job_id, payload)
    db = SessionLocal()
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        db.close()
        return

    try:
        # 1. Update status
        doc.status = 'processing'
        db.commit()
        
        ext = file_path.lower().split('.')[-1]
        
        if category == "standard":
            doc_type = "standard"
            doc.doc_type = "standard"
            db.commit()
            log_progress("Standard uploaded. Skipping auto-classification.")
        else:
            # Determine the doc_type automatically
            print(f"Auto-classifying document: {filename}...")
            from ingestion.classifier import classify_document
            predicted_doc_type = classify_document(file_path, filename)
            
            print(f"Classification result for {filename}: {predicted_doc_type}")
            
            # Update the DB record with the discovered doc_type
            doc.doc_type = predicted_doc_type
            db.commit()
            
            doc_type = predicted_doc_type
            
            log_progress(f"Document classified as: {doc_type}")
        
        # Branch 1: Drawing Analysis
        if ext in ['png', 'jpg', 'jpeg'] or doc_type in ["p&id", "pfd", "pid"]:
            log_progress("Analyzing drawing components and topology...")
            if doc_type.lower() in ["unsupported", "other"]:
                raise ValueError("Unsupported drawing type.")
                
            chunk_count = process_drawing(file_path, doc_id, doc_type, filename, db)
            doc.chunk_count = chunk_count
            doc.status = 'complete'
            doc.completed_at = datetime.utcnow()
            db.commit()
            log_progress(f"Drawing Ingestion complete for {filename} -- graph ready")
            finish_job("done", {"message": "Drawing successfully processed"})
            return
            
        # Branch 2: Standard Text Parsing
        log_progress("Parsing text document...")
        pages = []
        if ext == 'pdf':
            if is_scanned(file_path):
                from ingestion.parsers.ocr_parser import parse_ocr_pdf
                pages = parse_ocr_pdf(file_path)
            else:
                pages = parse_pdf(file_path)
        elif ext == 'xlsx':
            from ingestion.parsers.excel_parser import parse_excel
            pages = parse_excel(file_path)
        elif ext == 'docx':
            from ingestion.parsers.docx_parser import parse_docx
            pages = parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
            
        # 3. Chunking
        doc_metadata = {
            "doc_id": doc_id,
            "filename": filename,
            "doc_type": doc_type,
            "category": category,
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
        
        # 6. Mark complete IMMEDIATELY
        doc.status = 'complete'
        doc.completed_at = datetime.utcnow()
        db.commit()
        log_progress(f"Ingestion complete for {filename} ({len(chunks)} chunks) -- chat ready")
        
        # 7. Entity extraction (non-blocking background stage)
        try:
            log_progress(f"[Stage 2] Extracting entities for {len(chunks)} chunks...")
            batch_size = 3
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                combined_text = "\n\n".join([c['text'] for c in batch])
                try:
                    store_entities_in_graph(doc_id, combined_text)
                except Exception as e:
                    print(f"Warning: Entity extraction failed for batch {i}: {e}")
            log_progress(f"[Stage 2] Graph population complete for {filename}")
        except Exception as e:
            log_progress(f"[Stage 2] Entity extraction failed for {filename}: {e}")
            
        finish_job("done", {"message": "Document successfully processed"})
        
    except Exception as e:
        log_progress(f"Ingestion failed for {filename}: {e}")
        traceback.print_exc()
        doc.status = 'failed'
        doc.error_details = str(e)
        db.commit()
        finish_job("failed", {"error": str(e)})
    finally:
        db.close()
