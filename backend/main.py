from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from core.database import init_db
from core.ollama_client import verify_models
from routers import documents, chat, graph, maintenance, drawings, compliance
import os

# Ensure vector store and DB are initialized
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs("./uploads", exist_ok=True)
    # Verify Ollama on startup
    verify_models()
    yield
    # Shutdown

app = FastAPI(title="Industrial Knowledge API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(graph.router)
app.include_router(maintenance.router)
app.include_router(drawings.router)
app.include_router(compliance.router)
