from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from core.database import get_db, Job
from agents.rag_agent import query_stream
import uuid
import json
from routers.jobs import publish_sync

router = APIRouter(prefix="/api/chat", tags=["chat"])

class QueryRequest(BaseModel):
    query: str
    mode: str = "detailed"

def run_chat_job(job_id: str, query: str):
    from core.database import SessionLocal
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    
    accumulated = []
    try:
        token_count = 0
        for payload in query_stream(query):
            # publish to active listeners
            publish_sync(job_id, payload)
            
            # accumulate in memory via publish_sync automatically!
            # we just need to build the final string for the DB
            accumulated.append(json.dumps(payload))
            
            if payload.get("type") == "done" or payload.get("done") is True:
                job.accumulated_output = "\n".join(accumulated)
                job.status = "done"
                job.result_json = json.dumps(payload)
                db.commit()
                # Clear active history since it's now in the DB
                from routers.jobs import clear_active_history
                clear_active_history(job_id)
                break
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Chat job failed: {e}")
        error_payload = {"type": "error", "error": str(e), "done": True}
        job.status = "failed"
        job.result_json = json.dumps(error_payload)
        try:
            db.commit()
        except:
            db.rollback()
        publish_sync(job_id, error_payload)
    finally:
        db.close()

@router.post("/query")
def chat_query(req: QueryRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    job = Job(id=job_id, type="chat", status="running")
    db.add(job)
    db.commit()
    
    background_tasks.add_task(run_chat_job, job_id, req.query)
    
    return {"job_id": job_id}

