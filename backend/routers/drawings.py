from fastapi import APIRouter, Depends, HTTPException
from core.database import get_db, Drawing, DrawingTag
from sqlalchemy.orm import Session
from graph.neo4j_client import neo4j_client

router = APIRouter(prefix="/api/drawings", tags=["drawings"])

@router.get("")
def list_drawings(db: Session = Depends(get_db)):
    """List all processed drawings."""
    drawings = db.query(Drawing).order_by(Drawing.uploaded_at.desc()).all()
    return [{"id": d.id, "filename": d.filename, "uploaded_at": d.uploaded_at} for d in drawings]

@router.get("/{drawing_id}")
def get_drawing(drawing_id: str, db: Session = Depends(get_db)):
    """Get a specific drawing and its extracted tags."""
    drawing = db.query(Drawing).filter(Drawing.id == drawing_id).first()
    if not drawing:
        raise HTTPException(status_code=404, detail="Drawing not found")
        
    tags = db.query(DrawingTag).filter(DrawingTag.drawing_id == drawing_id).all()
    
    components = [{"tag": t.tag, "type": t.type, "description": t.description} for t in tags]
    
    # Check graph for known cross-references
    cross_references = {}
    driver = neo4j_client.driver
    if driver:
        with driver.session() as session:
            for comp in components:
                tag = comp["tag"]
                res = session.run("MATCH (e:Equipment {tag: $tag}) RETURN e", tag=tag).data()
                if res:
                    cross_references[tag] = {"known": True, "details": res[0]["e"]}
                    
    return {
        "drawing_id": drawing.id,
        "filename": drawing.filename,
        "drawing_number": drawing.drawing_number,
        "revision": drawing.revision,
        "unit_area": drawing.unit_area,
        "overall_analysis": drawing.overall_analysis,
        "components": components,
        "cross_references": cross_references
    }
