import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHROMA_PATH = BASE_DIR / os.getenv("CHROMA_PATH", "./chroma_db")
SQLITE_PATH = BASE_DIR / os.getenv("SQLITE_PATH", "./industrial_knowledge.db")
UPLOAD_DIR = BASE_DIR / os.getenv("UPLOAD_DIR", "./uploads")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "industrial2026")
