from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from core.database import init_db
from core.ollama_client import verify_models
from routers import documents, chat, graph, maintenance
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs("./uploads", exist_ok=True)
    init_db()
    verify_models()
    yield
    # Shutdown

app = FastAPI(title="Industrial Knowledge Intelligence API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(graph.router)
app.include_router(maintenance.router)
