import chromadb
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import uuid
from core.config import SQLITE_PATH, CHROMA_PATH

# --- SQLite Setup ---
SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    doc_type = Column(String, nullable=True) # 'inspection_report', 'sop', 'manual', 'drawing'
    status = Column(String, default='pending') # 'pending', 'processing', 'complete', 'failed'
    chunk_count = Column(Integer, default=0)
    entity_count = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Optional field to store error details if status is failed
    error_details = Column(String, nullable=True)

class AuditLog(Base):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False) # 'query', 'ingestion', 'compliance_scan', 'rca'
    details = Column(String, nullable=True) # JSON
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplianceReport(Base):
    __tablename__ = "compliance_reports"

    id = Column(Integer, primary_key=True, index=True)
    regulation_id = Column(String, nullable=True)
    status = Column(String, nullable=True) # 'compliant', 'gap_critical', 'gap_major', 'gap_minor'
    evidence = Column(String, nullable=True) # JSON list of supporting doc_ids
    generated_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    """Create all SQLite tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ SQLite tables created")

def get_db():
    """Dependency to get a SQLite session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ChromaDB Setup ---
chroma_client = None

def get_collection():
    """Get the ChromaDB collection."""
    global chroma_client
    if chroma_client is None:
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    
    # get_or_create ensures it exists
    collection = chroma_client.get_or_create_collection(
        name="industrial_docs",
        metadata={"hnsw:space": "cosine"}
    )
    return collection
