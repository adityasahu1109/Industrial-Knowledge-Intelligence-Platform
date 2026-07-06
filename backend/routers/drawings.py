from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import base64
from drawing.analyzer import extract_equipment_from_image
from core.database import get_db, Drawing, DrawingTag
from graph.neo4j_client import neo4j_client
from sqlalchemy.orm import Session
import os
import uuid

router = APIRouter(prefix="/api/drawings", tags=["drawings"])

@router.post("/analyze")
async def analyze_drawing(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image (PNG/JPEG)")
        
    try:
        content = await file.read()
        base64_image = base64.b64encode(content).decode('utf-8')
        
        # 1. Analyze image to get tags
        results = extract_equipment_from_image(base64_image)
        
        # 2. Save Drawing to SQLite
        drawing_id = str(uuid.uuid4())
        db_drawing = Drawing(id=drawing_id, filename=file.filename)
        db.add(db_drawing)
        
        cross_references = {}
        driver = neo4j_client.driver
        
        if driver:
            with driver.session() as session:
                # 3. Create Drawing Node
                session.run("MERGE (d:Drawing {id: $id, filename: $filename})", id=drawing_id, filename=file.filename)
                
                for comp in results:
                    tag = comp["tag"]
                    
                    # Save Tag to SQLite
                    db_tag = DrawingTag(drawing_id=drawing_id, tag=tag, type=comp.get("type"), description=comp.get("description"))
                    db.add(db_tag)
                    
                    # Cross-reference with Neo4j Equipment nodes
                    res = session.run("MATCH (e:Equipment {tag: $tag}) RETURN e", tag=tag).data()
                    if res:
                        cross_references[tag] = {"known": True, "details": res[0]["e"]}
                        
                    # Create Graph Relationship
                    session.run("""
                        MERGE (e:Equipment {tag: $tag})
                        MERGE (d:Drawing {id: $id})
                        MERGE (d)-[:CONTAINS]->(e)
                    """, tag=tag, id=drawing_id)
                
        db.commit()
        
        return {
            "drawing_id": drawing_id,
            "filename": file.filename, 
            "components": results,
            "cross_references": cross_references
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
