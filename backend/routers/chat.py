from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text as sql_text
from core.database import get_db, Message, SessionLocal
from agents.rag_agent import query_stream
import uuid
import json
import time
import asyncio
from typing import Dict, List, Set

router = APIRouter(prefix="/api/chat", tags=["chat"])

# In-memory tracking
active_queues: Dict[str, List[asyncio.Queue]] = {}
cancelled_message_ids: Set[str] = set()
active_buffers: Dict[str, str] = {}

# Registry to prevent GC of background tasks
_background_tasks: Set[asyncio.Task] = set()

def init_chat_loop():
    pass  # No longer needed

class QueryRequest(BaseModel):
    session_id: str
    query: str
    mode: str = "detailed"

def publish_to_queues(message_id: str, payload: dict):
    """Thread-safe publish to all active subscriber queues."""
    if message_id in active_queues:
        for q in active_queues[message_id]:
            q.put_nowait(payload)

async def generate_and_persist(message_id: str, query: str):
    """
    Run Ollama generation (synchronous/blocking) in a thread executor,
    bridging tokens one-at-a-time into the async event loop via a queue.
    """
    loop = asyncio.get_running_loop()
    db = SessionLocal()
    token_queue: asyncio.Queue = asyncio.Queue()
    
    full_content = ""
    buffer = ""
    last_flush = time.monotonic()
    active_buffers[message_id] = ""
    
    def _blocking_generate():
        """Runs in thread: feeds payloads into the async queue one at a time."""
        try:
            for payload in query_stream(query):
                loop.call_soon_threadsafe(token_queue.put_nowait, payload)
            # Signal completion
            loop.call_soon_threadsafe(token_queue.put_nowait, None)
        except Exception as e:
            loop.call_soon_threadsafe(token_queue.put_nowait, {"type": "error", "error": str(e), "done": True})
    
    # Start the blocking generator in a thread
    loop.run_in_executor(None, _blocking_generate)
    
    try:
        while True:
            payload = await token_queue.get()
            if payload is None:
                break
            
            # Check cancellation
            if message_id in cancelled_message_ids:
                db.execute(
                    sql_text("UPDATE messages SET content = :content, status = 'interrupted', updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                    {"content": full_content, "id": message_id}
                )
                db.commit()
                publish_to_queues(message_id, {"type": "done", "done": True, "interrupted": True})
                cancelled_message_ids.discard(message_id)
                return

            token = payload.get("token", "")
            buffer += token
            full_content += token
            active_buffers[message_id] = full_content
            
            # Publish live to SSE subscribers
            publish_to_queues(message_id, payload)
            
            if payload.get("done") is True:
                db.execute(
                    sql_text("UPDATE messages SET content = :content, status = 'done', sources = :sources, attachments = :attachments, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                    {"content": full_content, "sources": json.dumps(payload.get("sources", [])), "attachments": json.dumps(payload.get("attachments", [])), "id": message_id}
                )
                db.commit()
                break
            
            # Batch DB flush
            now = time.monotonic()
            if now - last_flush > 0.3 or len(buffer) > 20:
                db.execute(
                    sql_text("UPDATE messages SET content = :content, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                    {"content": full_content, "id": message_id}
                )
                db.commit()
                buffer = ""
                last_flush = now
                
    except Exception as e:
        import traceback
        traceback.print_exc()
        try:
            db.execute(
                sql_text("UPDATE messages SET content = :content, status = 'interrupted', updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                {"content": full_content, "id": message_id}
            )
            db.commit()
        except:
            pass
        publish_to_queues(message_id, {"type": "error", "error": str(e), "done": True})
    finally:
        db.close()
        active_buffers.pop(message_id, None)


@router.post("/send")
async def chat_send(req: QueryRequest, db: Session = Depends(get_db)):
    """Insert messages into DB, kick off async generation, return message_id immediately."""
    user_msg_id = str(uuid.uuid4())
    assistant_msg_id = str(uuid.uuid4())
    
    user_msg = Message(id=user_msg_id, session_id=req.session_id, role="user", content=req.query, status="done")
    assistant_msg = Message(id=assistant_msg_id, session_id=req.session_id, role="assistant", content="", status="generating")
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()
    
    # Schedule the coroutine on the event loop — NOT in a thread
    task = asyncio.create_task(generate_and_persist(assistant_msg_id, req.query))
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    
    return {"message_id": assistant_msg_id}


@router.get("/stream/{message_id}")
async def stream_message(message_id: str, request: Request, cursor: int = 0, db: Session = Depends(get_db)):
    """Connect to live SSE stream for a message. Supports catch-up via cursor."""
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        return {"error": "Message not found"}
        
    async def event_generator():
        # 1. Catch-up from DB + active buffer
        content = msg.content or ""
        status = msg.status
        
        if message_id in active_buffers:
            content = active_buffers[message_id]
            status = "generating"
        
        if len(content) > cursor:
            yield f"data: {json.dumps({'type': 'catchup', 'token': content[cursor:]})}\n\n"
            
        if status in ['done', 'interrupted']:
            payload = {"type": "done", "done": True, "interrupted": (status == 'interrupted')}
            if msg.sources:
                try: payload["sources"] = json.loads(msg.sources)
                except: pass
            if msg.attachments:
                try: payload["attachments"] = json.loads(msg.attachments)
                except: pass
            yield f"data: {json.dumps(payload)}\n\n"
            return
            
        # 2. Subscribe to live tokens
        q: asyncio.Queue = asyncio.Queue()
        if message_id not in active_queues:
            active_queues[message_id] = []
        active_queues[message_id].append(q)
        
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(q.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                yield f"data: {json.dumps(payload)}\n\n"
                if payload.get("done") is True or payload.get("type") in ["done", "error"]:
                    break
        finally:
            if message_id in active_queues and q in active_queues[message_id]:
                active_queues[message_id].remove(q)
                if not active_queues[message_id]:
                    del active_queues[message_id]
                    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
    )


@router.post("/cancel/{message_id}")
def cancel_message(message_id: str):
    cancelled_message_ids.add(message_id)
    return {"status": "cancelling"}


@router.get("/history/{session_id}")
def get_history(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at.asc()).all()
    results = []
    for m in messages:
        sources, attachments = [], []
        if m.sources:
            try: sources = json.loads(m.sources)
            except: pass
        if m.attachments:
            try: attachments = json.loads(m.attachments)
            except: pass
        results.append({
            "id": m.id, "role": m.role, "content": m.content,
            "status": m.status, "sources": sources, "attachments": attachments,
            "created_at": m.created_at.isoformat()
        })
    return {"messages": results}
