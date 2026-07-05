from fastapi import APIRouter, HTTPException
from graph.graph_builder import get_graph_data
from graph.graph_query import get_node_details

router = APIRouter(prefix="/api/graph", tags=["graph"])

@router.get("/")
def get_graph():
    """Returns nodes and links for the Knowledge Graph visualization."""
    return get_graph_data()

@router.get("/node/{node_id}")
def get_node(node_id: str):
    """Returns detailed information and connections for a specific node."""
    data = get_node_details(node_id)
    if not data:
        raise HTTPException(status_code=404, detail="Node not found")
    return data
