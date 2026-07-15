# Industrial Knowledge Intelligence Platform

> **AI for Industrial Knowledge Intelligence: Unified Asset & Operations Brain**
>
> A locally-hosted, AI-powered platform that ingests industrial documents (manuals, inspection reports, maintenance logs), builds a searchable knowledge base with vector embeddings, constructs a Knowledge Graph of equipment relationships, and provides an intelligent RAG-powered chat interface — all running 100% offline with zero cloud dependencies.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐ │
│  │  Document   │  │    Chat    │  │  Knowledge Graph    │ │
│  │  Manager    │  │  Interface │  │    Explorer          │ │
│  └─────┬──────┘  └─────┬──────┘  └─────────┬───────────┘ │
└────────┼───────────────┼────────────────────┼────────────┘
         │               │                    │
         ▼               ▼                    ▼
┌──────────────────────────────────────────────────────────┐
│                 Backend (FastAPI + Python)                │
│  ┌─────────────┐  ┌──────────┐  ┌──────────────────────┐ │
│  │  Ingestion   │  │   RAG    │  │  Entity Extraction   │ │
│  │  Pipeline    │  │  Agent   │  │       Agent          │ │
│  └──────┬──────┘  └────┬─────┘  └──────────┬───────────┘ │
│         │              │                    │             │
│    ┌────▼────┐    ┌────▼────┐         ┌────▼────┐        │
│    │ChromaDB │    │ Ollama  │         │  Neo4j  │        │
│    │(Vectors)│    │ (LLM)   │         │ (Graph) │        │
│    └─────────┘    └─────────┘         └─────────┘        │
└──────────────────────────────────────────────────────────┘
```

| Component | Technology | Purpose |
|---|---|---|
| **Frontend** | React 19, Vite 8, TypeScript, Tailwind CSS 4 | UI for document management, chat, and graph visualization |
| **Backend** | FastAPI, Python 3.14 | REST API, ingestion pipeline, RAG orchestration, Compliance Scanning |
| **LLM** | Ollama (llama3.1:8b, nomic-embed-text) | Local inference for chat, embeddings, and entity extraction |
| **Vector DB** | ChromaDB (embedded) | Stores operational documents and dynamically uploaded regulatory standards |
| **Graph DB** | Neo4j (Docker) | Stores extracted entities and relationships as a Knowledge Graph |
| **Metadata DB** | SQLite | Tracks document upload status, categories, chunk counts, metadata |

### Key Features
- **Dynamic RAG Chat:** Converses natively with your operational manuals, SOPs, and inspection reports.
- **Compliance Gap Scanner:** Upload custom Regulatory Standards (e.g., OSHA, ISO) and the system automatically audits your operational base clause-by-clause against it.
- **Drawing Topology Analyzer:** Ingests P&ID / PFD schematics to extract equipment tags and connection pipelines into a Knowledge Graph.

---

## Prerequisites

Make sure the following are installed on your machine before proceeding:

| Tool | Version | Download |
|---|---|---|
| **Python** | 3.12+ | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 20+ | [nodejs.org](https://nodejs.org/) |
| **Ollama** | Latest | [ollama.com](https://ollama.com/download) |
| **Docker Desktop** | Latest | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Git** | Latest | [git-scm.com](https://git-scm.com/) |

---

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "Industrial Knowledge Intelligence Platform"
```

### 2. Pull Required Ollama Models

Open a terminal and pull all three required models. These will download once and persist locally:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama pull minicpm-v
```

> **Note:** `llama3.1:8b` is ~4.7 GB, `nomic-embed-text` is ~274 MB, `minicpm-v` is ~5.1 GB. Ensure you have sufficient disk space.

### 3. Start Neo4j (Docker)

```bash
docker-compose up -d
```

This starts a Neo4j container with:
- **Browser UI:** http://localhost:7474 (username: `neo4j`, password: `industrial2026`)
- **Bolt Protocol:** `bolt://localhost:7687`
- Data is persisted in a Docker volume (`neo4j_data`) and survives container restarts.

### 4. Set Up the Backend

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file inside the `backend/` directory:

```bash
# backend/.env
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_PATH=./chroma_db
SQLITE_PATH=./industrial_knowledge.db
UPLOAD_DIR=./uploads
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=industrial2026
```

### 6. Start the Backend Server

```bash
cd backend
.\venv\Scripts\Activate.ps1   # Activate venv if not already
uvicorn main:app --reload
```

The API will be running at **http://localhost:8000**.

### 7. Set Up and Start the Frontend

Open a **new terminal**:

```bash
cd frontend
npm install
npm run dev
```

The UI will be running at **http://localhost:5173** (or the next available port).

---

## Usage

1. **Upload Documents** — Go to the Documents page and drag & drop PDF files. The ingestion pipeline will automatically parse, chunk, embed, and extract entities.
2. **Chat with your Data** — Go to the Chat page and ask natural language questions. The RAG agent retrieves relevant chunks from ChromaDB and generates answers using Ollama.
3. **Explore the Knowledge Graph** — Go to the Graph Explorer to visualize extracted entities and their relationships. Zoom in to see node labels.

---

## Project Structure

```
Industrial Knowledge Intelligence Platform/
├── backend/
│   ├── agents/                 # AI agents (RAG, entity extraction)
│   │   ├── rag_agent.py        # Retrieval-Augmented Generation agent
│   │   └── entity_extractor.py # LLM-based entity extraction
│   ├── core/                   # Core configuration and clients
│   │   ├── config.py           # Environment variable loading
│   │   ├── database.py         # SQLite setup (SQLAlchemy)
│   │   └── ollama_client.py    # Ollama API wrapper (chat, embed, JSON)
│   ├── graph/                  # Knowledge Graph layer
│   │   ├── neo4j_client.py     # Neo4j driver wrapper
│   │   └── graph_builder.py    # Entity → Neo4j MERGE logic
│   ├── ingestion/              # Document processing pipeline
│   │   ├── pipeline.py         # Orchestrator (parse → chunk → embed → graph)
│   │   ├── chunker.py          # Text chunking with overlap
│   │   ├── embedder.py         # Batch embedding via Ollama
│   │   └── parsers/
│   │       └── pdf_parser.py   # PDF text extraction (PyMuPDF)
│   ├── retrieval/
│   │   └── vector_store.py     # ChromaDB vector operations
│   ├── routers/                # FastAPI route handlers
│   │   ├── documents.py        # Upload, list, delete documents
│   │   ├── chat.py             # SSE-streaming chat endpoint
│   │   └── graph.py            # Graph data API
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables (not committed)
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts       # Fetch wrapper for backend API
│   │   ├── components/
│   │   │   ├── chat/           # Chat UI (ChatPage, MessageList, StreamingText)
│   │   │   ├── documents/      # Document management (DocumentManager, UploadDropzone)
│   │   │   ├── graph/          # Knowledge Graph (GraphExplorer with react-force-graph-2d)
│   │   │   └── layout/         # App shell (Sidebar, Layout)
│   │   ├── hooks/
│   │   │   └── useSSEStream.ts # SSE streaming hook for chat
│   │   ├── types/
│   │   │   └── chat.ts         # TypeScript type definitions
│   │   ├── App.tsx             # Root component with routing
│   │   ├── index.css           # Tailwind CSS + design tokens
│   │   └── main.tsx            # React entry point
│   ├── package.json
│   └── vite.config.ts
│
├── docker-compose.yml          # Neo4j container definition
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## Useful Commands

### Daily Development

```bash
# Start everything (run in separate terminals):
docker-compose up -d                           # 1. Neo4j
cd backend && .\venv\Scripts\Activate.ps1 && uvicorn main:app --reload   # 2. Backend
cd frontend && npm run dev                     # 3. Frontend
```

### Stopping Services

```bash
# Stop frontend/backend: Ctrl+C in their respective terminals

# Stop Neo4j (preserves data):
docker-compose down

# Stop Neo4j AND delete all graph data:
docker-compose down -v
```

### Ollama Model Management

```bash
ollama list                    # See all downloaded models
ollama pull llama3.1:8b        # Download/update a model
ollama rm <model-name>         # Remove a model
ollama ps                      # See currently loaded models
```

### Database Management

```bash
# Clear Neo4j graph (from backend directory, venv activated):
python -c "from graph.neo4j_client import neo4j_client; neo4j_client.run_query('MATCH (n) DETACH DELETE n')"

# Delete ChromaDB vectors:
# Simply delete the backend/chroma_db/ directory

# Reset SQLite:
# Delete backend/industrial_knowledge.db (auto-recreated on startup)
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `CHROMA_PATH` | `./chroma_db` | ChromaDB storage directory |
| `SQLITE_PATH` | `./industrial_knowledge.db` | SQLite database file path |
| `UPLOAD_DIR` | `./uploads` | Uploaded file storage |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j Bolt connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `industrial2026` | Neo4j password |

---

## Tech Stack

- **Frontend:** React 19 · TypeScript · Vite 8 · Tailwind CSS 4 · react-force-graph-2d · react-markdown · Lucide Icons
- **Backend:** FastAPI · Python · SQLAlchemy · ChromaDB · PyMuPDF
- **AI/ML:** Ollama (llama3.1:8b, nomic-embed-text, minicpm-v) · RAG · Entity Extraction
- **Infrastructure:** Docker · Neo4j · SQLite

---

## License

This project was built for the **ET AI Hackathon 2026** — Problem Statement 6: *AI for Industrial Knowledge Intelligence*.
