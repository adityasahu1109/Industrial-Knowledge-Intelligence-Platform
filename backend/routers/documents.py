from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db, Document, get_collection
from ingestion.pipeline import ingest
from core.config import UPLOAD_DIR
import uuid
import os

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Form("auto"),
    category: str = Form("operational"),
    db: Session = Depends(get_db)
):
    from core.database import Job
    doc_id = str(uuid.uuid4())
    job_id = str(uuid.uuid4())
    filename = file.filename
    ext = filename.lower().split('.')[-1]
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.{ext}")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
        
    # Create DB record
    db_doc = Document(
        id=doc_id,
        filename=filename,
        file_type=ext,
        doc_type=doc_type,
        category=category,
        status="pending"
    )
    db.add(db_doc)
    
    db_job = Job(id=job_id, type="document_upload", status="running", accumulated_output="")
    db.add(db_job)
    db.commit()
    
    # Launch async ingestion
    background_tasks.add_task(ingest, file_path, doc_id, doc_type, category, filename, job_id)
    
    return {"doc_id": doc_id, "job_id": job_id, "status": "processing"}

@router.get("")
def list_documents(category: str = None, db: Session = Depends(get_db)):
    query = db.query(Document)
    if category:
        query = query.filter(Document.category == category)
    docs = query.order_by(Document.uploaded_at.desc()).all()
    return [{"doc_id": d.id, "filename": d.filename, "doc_type": d.doc_type, "category": d.category, "status": d.status, "chunk_count": d.chunk_count, "entity_count": d.entity_count} for d in docs]

@router.get("/{doc_id}/status")
def get_document_status(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"doc_id": doc.id, "status": doc.status, "chunk_count": doc.chunk_count}

from fastapi.responses import FileResponse

@router.get("/{doc_id}/content")
def get_document_content(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.{doc.file_type}")
    
    # If it was a PDF drawing, we might have converted it to a PNG during ingestion
    if doc.file_type == 'pdf':
        png_path = os.path.join(UPLOAD_DIR, f"{doc_id}.png")
        if os.path.exists(png_path):
            return FileResponse(png_path)
            
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
        
    return FileResponse(file_path)

@router.delete("/{doc_id}")
def delete_document(doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Remove from Chroma
    collection = get_collection()
    collection.delete(where={"doc_id": doc_id})
    
    # Remove file
    file_path = os.path.join(UPLOAD_DIR, f"{doc_id}.{doc.file_type}")
    if os.path.exists(file_path):
        os.remove(file_path)
        
    # Remove from SQLite
    db.delete(doc)
    db.commit()
    
    # Remove from Neo4j (Knowledge Graph)
    try:
        from graph.neo4j_client import neo4j_client
        if neo4j_client.test_connection():
            # Delete relationships created by this doc
            neo4j_client.run_query("MATCH ()-[r]-() WHERE r.doc_id = $doc_id DELETE r", {"doc_id": doc_id})
            # Delete nodes created by this doc
            neo4j_client.run_query("MATCH (n) WHERE n.doc_id = $doc_id DETACH DELETE n", {"doc_id": doc_id})
    except Exception as e:
        print(f"Failed to delete graph data for {doc_id}: {e}")
        
    return {"deleted": True}
