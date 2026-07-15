# Industrial Knowledge Intelligence Platform - Backend

This is the FastAPI backend for the Industrial Knowledge Intelligence Platform. It orchestrates document ingestion, LLM interaction via Ollama, and vector/graph storage.

## Key Architectures

### 1. Ingestion Pipeline (`ingestion/`)
- Handles background tasks triggered by uploads.
- **Parsing**: Extracts text from PDFs (OCR fallback), Word Docs, and Excel sheets.
- **Chunking**: Splits parsed documents into semantic chunks.
- **Embedding**: Converts chunks into dense vectors using Ollama (`nomic-embed-text`) and stores them in ChromaDB.
- **Entity Extraction**: Slowly processes chunks in the background using an LLM to extract Named Entities and pushes them into Neo4j.

### 2. Retrieval Systems (`retrieval/`)
- **Vector Store**: Semantic similarity search using ChromaDB.
- **BM25**: Keyword search implemented in-memory for hybrid RAG search.

### 3. Agent Subsystems (`agents/`)
- **RAG Agent**: Uses hybrid search to provide context-aware chat responses using `llama3.1:8b`.
- **Compliance Agent**: Uses local retrieval to perform dynamic, clause-by-clause regulatory scans against uploaded operational documents.
- **Graph Agent**: Uses Neo4j to generate Cypher queries and traverse relationships for root cause analysis (RCA).

## Running the Server

Make sure you have activated the virtual environment and installed the requirements.

```bash
cd backend

# Create and activate virtual env
python -m venv venv
.\venv\Scripts\activate   # (Windows)
# source venv/bin/activate # (Unix)

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI app (Hot-reload)
uvicorn main:app --reload
```

The API docs will be available at `http://localhost:8000/docs`.
