from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.rag_agent import query_stream
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])

class QueryRequest(BaseModel):
    query: str
    mode: str = "detailed"

@router.post("/query")
async def chat_query(req: QueryRequest):
    def event_generator():
        for payload in query_stream(req.query):
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # disable nginx buffering
        }
    )
