from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from core.database import get_db, Job
import json
import asyncio
from typing import Dict, List

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

main_loop = None
active_histories: Dict[str, str] = {}
active_queues: Dict[str, List[asyncio.Queue]] = {}

def init_jobs_loop():
    global main_loop
    main_loop = asyncio.get_event_loop()

def publish_sync(job_id: str, payload: dict):
    if job_id not in active_histories:
        active_histories[job_id] = ""
    active_histories[job_id] += json.dumps(payload) + "\n"

    if job_id in active_queues and main_loop:
        for q in active_queues[job_id]:
            main_loop.call_soon_threadsafe(q.put_nowait, payload)

def clear_active_history(job_id: str):
    if job_id in active_histories:
        del active_histories[job_id]

@router.get("/{job_id}/stream")
async def stream_job(job_id: str, request: Request, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return {"error": "Job not found"}

    # If job is already finished, return the full history
    if job.status in ['done', 'failed']:
        def done_generator():
            history = active_histories.get(job_id)
            if history:
                for line in history.split('\n'):
                    if line.strip():
                        yield f"data: {line}\n\n"
            elif job.accumulated_output:
                for line in job.accumulated_output.split('\n'):
                    if line.strip():
                        yield f"data: {line}\n\n"
            elif job.result_json:
                yield f"data: {job.result_json}\n\n"
                
        return StreamingResponse(
            done_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}
        )

    # Otherwise stream
    async def event_generator():
        # Flush accumulated in-memory history
        history = active_histories.get(job_id)
        if not history:
            db_job = db.query(Job).filter(Job.id == job_id).first()
            if db_job and db_job.accumulated_output:
                history = db_job.accumulated_output
                
        if history:
            for line in history.split('\n'):
                if line.strip():
                    try:
                        yield f"data: {line}\n\n"
                    except:
                        pass
        
        q = asyncio.Queue()
        if job_id not in active_queues:
            active_queues[job_id] = []
        active_queues[job_id].append(q)
        
        try:
            while True:
                if await request.is_disconnected():
                    break
                payload = await q.get()
                yield f"data: {json.dumps(payload)}\n\n"
                
                # Check for termination
                if payload.get("done") is True or payload.get("type") in ["done", "error"]:
                    break
        except asyncio.CancelledError:
            pass
        finally:
            if job_id in active_queues and q in active_queues[job_id]:
                active_queues[job_id].remove(q)
                if not active_queues[job_id]:
                    del active_queues[job_id]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )
