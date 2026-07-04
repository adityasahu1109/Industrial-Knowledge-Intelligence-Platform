from fastapi import APIRouter
from graph.graph_builder import get_graph_data

router = APIRouter(prefix="/api/graph", tags=["graph"])

@router.get("/")
def get_graph():
    """Returns nodes and links for the Knowledge Graph visualization."""
    return get_graph_data()
