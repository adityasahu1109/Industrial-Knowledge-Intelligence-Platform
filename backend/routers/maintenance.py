from fastapi import APIRouter
from graph.graph_query import get_equipment_timeline

router = APIRouter(prefix="/api/maintenance", tags=["maintenance"])

@router.get("/{equipment_id}/timeline")
def get_timeline(equipment_id: str):
    """Returns chronological events for a specific equipment from the Knowledge Graph."""
    timeline = get_equipment_timeline(equipment_id)
    return {"equipment_id": equipment_id, "timeline": timeline}
