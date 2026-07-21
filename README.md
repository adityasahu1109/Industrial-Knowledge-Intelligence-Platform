# 🏭 Industrial Knowledge Intelligence Platform (IKIP)

### *AI for Industrial Knowledge Intelligence: Unified Asset & Operations Brain*

**Hackathon:** ET AI Hackathon 2026 — Problem Statement #8  
**Theme:** Industrial Intelligence · Document Management · Knowledge Engineering · Quality

---

## The Problem We're Solving

Every large industrial plant — whether it's a refinery, a power station, or a manufacturing facility — runs on paper. Decades of it. Maintenance logs buried in filing cabinets. P&ID drawings scattered across shared drives. Safety procedures in one system, inspection reports in another, and operating instructions in a third. A 2024 McKinsey survey found that engineers spend **35% of their working hours** just *searching* for information that already exists somewhere in their own organisation.

This isn't just an inconvenience. It's dangerous.

When a maintenance technician can't quickly find the failure history of a pressure vessel, they make decisions without context. When an operator can't cross-reference an SOP with the latest inspection findings, safety gaps go unnoticed. When a senior engineer retires, **decades of undocumented knowledge walk out the door with them** — and it never comes back.

BIS Research estimates that this knowledge fragmentation contributes to **18–22% of unplanned downtime** in Indian heavy industry. With 25% of India's experienced industrial engineers set to retire in the next decade, the clock is ticking.

**Knowledge fragmentation in industrial operations is not a file management problem. It is a safety problem, a quality problem, and an operational efficiency problem — and it compounds over time.**

---

## How IKIP Solves It

IKIP is a **locally-hosted, fully offline AI platform** that turns your scattered industrial documents into a unified, queryable intelligence layer. You upload your documents — PDFs, Word files, Excel sheets, engineering drawings — and the system automatically:

1. **Reads and understands them** — parsing text, extracting entities, and classifying each document by type (inspection report, SOP, manual, drawing, etc.)
2. **Builds a searchable knowledge base** — chunking documents into semantically meaningful pieces and embedding them into a vector database for instant retrieval
3. **Constructs a Knowledge Graph** — extracting equipment tags, personnel, processes, and relationships, then wiring them together in Neo4j so you can *see* how your plant's assets connect
4. **Answers your questions in plain English** — using Retrieval-Augmented Generation (RAG) with hybrid search (semantic + keyword) to give precise, source-cited answers from your own documents
5. **Audits your compliance** — comparing your operational documents clause-by-clause against regulatory standards and generating detailed gap analysis reports with remediation plans
6. **Analyses engineering drawings** — using computer vision to extract equipment tags, connections, and topology from P&IDs, Process Flow Diagrams, Block Flow Diagrams, and other industrial schematics

**Zero cloud dependencies.** Every AI model runs locally on your machine through Ollama. Your sensitive industrial data never leaves your network.

---

## Key Features

| Feature | What It Does |
|---|---|
| 🤖 **Intelligence Chat** | Ask natural language questions across your entire document corpus. Get streaming answers with clickable source citations pointing back to the exact document and page. |
| 📄 **Smart Document Ingestion** | Drag-and-drop upload with automatic AI classification. Supports PDF, DOCX, XLSX, PNG, and JPEG. Multi-file batch upload with real-time progress tracking. |
| 🔍 **Hybrid Search (RAG)** | Combines semantic vector search (ChromaDB + nomic-embed-text) with keyword search (BM25) using Reciprocal Rank Fusion for the best of both worlds. |
| 🕸️ **Knowledge Graph** | Interactive force-directed graph visualization of extracted entities — equipment, personnel, procedures, and their relationships — powered by Neo4j. |
| 🖼️ **Drawing Vision Analyzer** | Feeds engineering schematics through a tiled vision model to extract equipment tags, instruments, valves, and piping connections. Supports P&IDs, PFDs, block flow diagrams, electrical schematics, HVAC layouts, and more. |
| ✅ **Compliance Gap Scanner** | Upload a regulatory standard (OSHA, ISO, Factory Act, or your own custom standard) and the system automatically audits your operational documents clause-by-clause, scoring compliance and generating PDF reports with detailed remediation plans. |
| 🔒 **Data Isolation** | Regulatory standards uploaded for compliance scanning are kept strictly isolated from the operational RAG chat — preventing regulatory text from polluting everyday Q&A answers. |
| 🛡️ **Smart Guardrails** | AI-powered image classification rejects irrelevant uploads (photos, screenshots, non-industrial images) while intelligently accepting all types of industrial schematics. |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite + Tailwind)         │
│                                                              │
│   Intelligence    Document    Knowledge    Drawing   Compliance│
│      Chat          Base        Graph      Analysis  Dashboard │
└───────┬──────────────┬───────────┬──────────┬──────────┬─────┘
        │              │           │          │          │
        ▼              ▼           ▼          ▼          ▼
┌──────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + Python)                    │
│                                                              │
│   RAG Agent    Ingestion    Entity       Drawing    Compliance │
│  (Streaming)   Pipeline    Extractor    Analyzer     Agent    │
│                                                              │
│   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌───────────┐  │
│   │ChromaDB │   │ SQLite  │   │  Neo4j  │   │  Ollama   │  │
│   │(Vectors)│   │(Metadata│   │ (Graph) │   │  (Local   │  │
│   │         │   │  & Jobs)│   │         │   │   LLMs)   │  │
│   └─────────┘   └─────────┘   └─────────┘   └───────────┘  │
└──────────────────────────────────────────────────────────────┘
```

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | React 19, Vite 8, TypeScript, Tailwind CSS 4 | Five-page SPA with real-time SSE streaming, force-graph visualization, and PDF report export |
| **Backend** | FastAPI, Python, SQLAlchemy | REST API with 7 router modules, background job system, and SSE event broadcasting |
| **LLM Engine** | Ollama (llama3.1:8b) | Chat, entity extraction, compliance analysis, document classification — all local |
| **Embedding** | Ollama (nomic-embed-text) | 768-dimensional embeddings for semantic search |
| **Vision** | Ollama (qwen2.5vl:7b) | Engineering drawing analysis, image classification, tile-based component extraction |
| **Vector DB** | ChromaDB (embedded) | Stores document chunks with metadata for semantic retrieval |
| **Graph DB** | Neo4j (Docker) | Stores equipment entities, relationships, and drawing topology as a Knowledge Graph |
| **Metadata DB** | SQLite (WAL mode) | Tracks documents, jobs, compliance reports, chat sessions, and drawing metadata |

---

## Prerequisites

Before setting up IKIP, make sure you have the following installed:

| Tool | Minimum Version | What It's For | Download |
|---|---|---|---|
| **Python** | 3.12+ | Backend server and AI pipeline | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 20+ | Frontend build toolchain | [nodejs.org](https://nodejs.org/) |
| **Ollama** | Latest | Runs AI models locally on your machine | [ollama.com](https://ollama.com/download) |
| **Docker Desktop** | Latest | Runs the Neo4j graph database container | [docker.com](https://www.docker.com/products/docker-desktop/) |
| **Git** | Latest | Version control | [git-scm.com](https://git-scm.com/) |

> **Hardware:** We recommend at least **16 GB RAM** and a modern CPU. A dedicated GPU is not required — Ollama runs on CPU — but a CUDA-compatible GPU will significantly speed up inference.

---

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd "Industrial Knowledge Intelligence Platform"
```

### Step 2: Pull the AI Models

Open a terminal and download all three required Ollama models. These download once and persist locally:

```bash
ollama pull llama3.1:8b          # ~4.7 GB — Chat, reasoning, entity extraction
ollama pull nomic-embed-text     # ~274 MB — Document embeddings for search
ollama pull qwen2.5vl:7b         # ~5.1 GB — Vision model for drawing analysis
```

> **Tip:** You can check which models are already downloaded with `ollama list`.

### Step 3: Start Neo4j via Docker

From the project root directory:

```bash
docker-compose up -d
```

This starts a Neo4j container with:
- **Browser UI:** [http://localhost:7474](http://localhost:7474) (username: `neo4j`, password: `industrial2026`)
- **Bolt Protocol:** `bolt://localhost:7687`
- Data is persisted in a Docker volume and survives container restarts.

### Step 4: Set Up the Backend

```bash
cd backend

# Create a Python virtual environment
python -m venv venv

# Activate it
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# macOS / Linux:
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

### Step 5: Configure Environment Variables

The backend ships with a pre-configured `.env` file. If you need to customise anything (e.g., Neo4j password), edit `backend/.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
CHROMA_PATH=./chroma_db
SQLITE_PATH=./industrial_knowledge.db
UPLOAD_DIR=./uploads
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=industrial2026
```

### Step 6: Start the Backend Server

```bash
cd backend
.\venv\Scripts\Activate.ps1   # Activate the venv if not already active
uvicorn main:app
```

The API will be running at **http://localhost:8000**. On startup, the server will automatically:
- Create the SQLite database and tables
- Initialize the ChromaDB vector store
- Verify that all required Ollama models are available

### Step 7: Start the Frontend

Open a **new terminal window**:

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at **http://localhost:5173**.

### ✅ You're Ready!

Open [http://localhost:5173](http://localhost:5173) in your browser. You should see the IKIP dashboard with the sidebar navigation.

---

## How to Use IKIP

### 1. Upload Documents

Navigate to **Document Base** in the sidebar. Drag and drop your files into the upload area — or click to browse. The system accepts:
- **PDF** — Technical manuals, inspection reports, SOPs
- **DOCX** — Word documents of any kind
- **XLSX** — Excel spreadsheets with tabular data
- **PNG / JPG** — Engineering drawings and schematics

Each file is automatically classified by the AI (inspection report, SOP, manual, P&ID, etc.) and processed through the ingestion pipeline. You can upload multiple files at once — they'll process sequentially with live progress updates.

**Category Selection:** Use the dropdown to choose between:
- **Operational Document** — Goes into the general knowledge base (searchable via chat)
- **Regulatory Standard** — Isolated for compliance scanning only (never mixed into chat answers)

### 2. Ask Questions via Chat

Navigate to **Intelligence Chat**. Type any question in plain English. The system will:
- Search across all your operational documents using hybrid semantic + keyword retrieval
- Stream the AI's answer in real time
- Show clickable source citations at the bottom of each response (filename, page number)

**Example queries:**
- *"What is the minimum thickness found on Pressure Vessel V-205?"*
- *"What safety precautions are required before an annual overhaul on Pump P-101?"*
- *"What was the root cause of the cooling efficiency drop on Heat Exchanger E-301?"*

### 3. Explore the Knowledge Graph

Navigate to **Knowledge Graph**. You'll see an interactive force-directed graph of all entities the AI has extracted — equipment tags, personnel, processes, and their relationships. Click on any node to see its details and connections.

### 4. Analyse Engineering Drawings

Navigate to **Drawing Analysis**. Select any uploaded drawing from the dropdown. The system shows:
- The original image
- Extracted drawing metadata (drawing number, revision, unit/area)
- A list of all detected components (equipment, instruments, valves)
- Cross-references against the Knowledge Graph

### 5. Run a Compliance Audit

Navigate to **Compliance**. Select a regulatory standard from the dropdown (pre-loaded standards or any standard you've uploaded as a "Regulatory Standard" document). Choose a document type filter if desired, then click **Run Scan**.

The system will:
- Parse the standard into individual clauses
- Search your operational documents for evidence relevant to each clause
- Use AI to evaluate compliance, identify gaps, and suggest remediation
- Generate a scored report with detailed findings
- Allow you to **export the full report as a PDF**

---

## Project Structure

```
Industrial Knowledge Intelligence Platform/
│
├── backend/                          # Python FastAPI Server
│   ├── agents/                       # AI Agent Modules
│   │   ├── rag_agent.py              #   → RAG chat with hybrid search + streaming
│   │   ├── entity_extractor.py       #   → LLM-based entity & relationship extraction
│   │   └── compliance_agent.py       #   → Clause-by-clause compliance auditor
│   ├── core/                         # Core Infrastructure
│   │   ├── config.py                 #   → Environment variable loading
│   │   ├── database.py               #   → SQLite + ChromaDB setup (SQLAlchemy ORM)
│   │   └── ollama_client.py          #   → Ollama API wrapper (chat, embed, vision, JSON)
│   ├── drawing/                      # Drawing Analysis
│   │   ├── analyzer.py               #   → Vision-based component extraction
│   │   └── tiler.py                  #   → Image tiling for high-resolution analysis
│   ├── graph/                        # Knowledge Graph
│   │   ├── neo4j_client.py           #   → Neo4j driver wrapper
│   │   └── graph_builder.py          #   → Entity → Neo4j MERGE logic
│   ├── ingestion/                    # Document Processing Pipeline
│   │   ├── pipeline.py               #   → Orchestrator (parse → chunk → embed → graph)
│   │   ├── classifier.py             #   → AI-powered document type classification
│   │   ├── chunker.py                #   → Text chunking with overlap
│   │   ├── embedder.py               #   → Batch embedding via Ollama
│   │   └── parsers/                  #   → Format-specific parsers
│   │       ├── pdf_parser.py         #       → PDF text extraction (PyMuPDF)
│   │       ├── docx_parser.py        #       → Word document parser (python-docx)
│   │       ├── excel_parser.py       #       → Excel spreadsheet parser (openpyxl)
│   │       └── ocr_parser.py         #       → OCR for scanned PDFs (Tesseract)
│   ├── retrieval/                    # Search & Retrieval
│   │   ├── vector_store.py           #   → ChromaDB semantic search with category filtering
│   │   ├── bm25_index.py             #   → BM25 keyword search index
│   │   └── rrf_fusion.py             #   → Reciprocal Rank Fusion (hybrid merge)
│   ├── routers/                      # FastAPI Route Handlers
│   │   ├── documents.py              #   → Upload, list, delete documents
│   │   ├── chat.py                   #   → SSE-streaming chat endpoint
│   │   ├── graph.py                  #   → Knowledge Graph data API
│   │   ├── drawings.py               #   → Drawing metadata & component API
│   │   ├── compliance.py             #   → Compliance scan + PDF report generation
│   │   ├── jobs.py                   #   → Background job system with SSE streaming
│   │   └── maintenance.py            #   → Equipment timeline tracking
│   ├── main.py                       # FastAPI app entry point
│   ├── requirements.txt              # Python dependencies (16 packages)
│   └── .env                          # Environment variables
│
├── frontend/                         # React + Vite SPA
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/                 #   → ChatPage, MessageList, StreamingText, AttachmentViewer
│   │   │   ├── documents/            #   → DocumentManager, UploadDropzone
│   │   │   ├── graph/                #   → GraphExplorer, GraphFilters, NodePanel
│   │   │   ├── drawings/             #   → DrawingViewer
│   │   │   ├── compliance/           #   → ComplianceDashboard
│   │   │   ├── layout/               #   → Sidebar, Header
│   │   │   └── maintenance/          #   → MaintenanceTimeline
│   │   ├── api/client.ts             #   → Fetch wrapper for backend API
│   │   ├── hooks/useSSEStream.ts     #   → SSE streaming hook
│   │   ├── types/chat.ts             #   → TypeScript type definitions
│   │   ├── App.tsx                   #   → Root component with routing (5 routes)
│   │   ├── index.css                 #   → Design system tokens + Tailwind config
│   │   └── main.tsx                  #   → React entry point
│   ├── package.json
│   └── vite.config.ts
│
├── data/
│   └── regulatory/                   # Pre-loaded regulatory standards
│       ├── factory_act_excerpt.md    #   → Factory Act 1948 (Sections 31, 41C)
│       └── oisd_117_excerpt.md       #   → OISD-117 Fire Protection Standard
│
├── test_documents/                   # Sample documents for testing & demo
│   ├── *.pdf                         #   → 5 industrial PDF reports
│   ├── *.docx                        #   → 5 detailed Word documents
│   └── *.png                         #   → 11 engineering schematics
│
├── docker-compose.yml                # Neo4j container definition
├── .gitignore                        # Git ignore rules
└── README.md                         # You are here
```

---

## Designed for Heavy Industry — Adaptable to Any Knowledge-Intensive Sector

IKIP was built with **heavy industry** in mind — oil & gas refineries, power plants, petrochemical complexes, and large-scale manufacturing facilities where the document burden is heaviest and the consequences of knowledge gaps are most severe.

But the underlying architecture is **domain-agnostic**. The AI doesn't hardcode any industry-specific rules — it learns from whatever documents you feed it. This means IKIP can be adapted to:

| Sector | How It Applies |
|---|---|
| **Oil & Gas / Petrochemicals** | P&ID analysis, equipment failure tracking, OISD/PESO compliance, maintenance work order intelligence |
| **Power Generation** | Turbine maintenance logs, boiler inspection reports, environmental compliance tracking |
| **Pharmaceuticals** | GMP documentation intelligence, batch record cross-referencing, FDA/WHO audit preparation |
| **Construction & Infrastructure** | Drawing revision management, safety compliance tracking, project document consolidation |
| **Aerospace & Defence** | Technical manual Q&A, component lifecycle tracking, airworthiness compliance |
| **Healthcare** | Clinical protocol management, equipment maintenance tracking, regulatory compliance (NABH/JCI) |
| **Mining & Metals** | Equipment inspection intelligence, DGMS compliance, safety incident pattern analysis |

The key insight is this: **any organisation that accumulates large volumes of technical documents and needs to make decisions based on them can benefit from IKIP.** The AI adapts to the vocabulary, structure, and relationships of whatever domain it's trained on.

---

## Daily Development Commands

```bash
# Start everything (run each in a separate terminal):
docker-compose up -d                                              # 1. Neo4j
cd backend && .\venv\Scripts\Activate.ps1 && uvicorn main:app   # 2. Backend
cd frontend && npm run dev                                        # 3. Frontend
```

---

## Complete Teardown — Removing IKIP from Your System

If you want to completely remove IKIP and all its data from your machine, follow these steps in order:

### 1. Stop All Running Services

```bash
# Stop frontend and backend: Press Ctrl+C in their respective terminals

# Stop and remove the Neo4j container + its data volume:
docker-compose down -v
```

### 2. Remove Downloaded AI Models (Optional)

If you no longer need the Ollama models and want to reclaim ~10 GB of disk space:

```bash
ollama rm llama3.1:8b
ollama rm nomic-embed-text
ollama rm qwen2.5vl:7b
```

> **Note:** This only removes the models IKIP uses. If you use Ollama for other projects, your other models are untouched.

### 3. Delete the Project Directory

```bash
# Navigate to the parent directory and delete the project
cd ..
Remove-Item -Recurse -Force "Industrial Knowledge Intelligence Platform"
```

### 4. Uninstall Global Tools (Optional)

If you installed Python, Node.js, Ollama, or Docker Desktop specifically for this project and don't need them for anything else, you can uninstall them through your operating system's standard uninstall process (Settings → Apps on Windows, or `brew uninstall` on macOS).

**That's it.** IKIP stores everything locally within the project directory — there are no hidden config files scattered across your system, no background services left running, and no cloud accounts to cancel.

---

## Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `CHROMA_PATH` | `./chroma_db` | ChromaDB vector store directory |
| `SQLITE_PATH` | `./industrial_knowledge.db` | SQLite database file path |
| `UPLOAD_DIR` | `./uploads` | Directory for uploaded files |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j Bolt connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | `industrial2026` | Neo4j password |

---

## Tech Stack

| Category | Technologies |
|---|---|
| **Frontend** | React 19 · TypeScript · Vite 8 · Tailwind CSS 4 · react-force-graph-2d · react-markdown · Lucide Icons |
| **Backend** | FastAPI · Python · SQLAlchemy · ChromaDB · PyMuPDF · python-docx · openpyxl |
| **AI / ML** | Ollama (llama3.1:8b, nomic-embed-text, qwen2.5vl:7b) · RAG · Hybrid Search · RRF · Entity Extraction · Vision Analysis |
| **Infrastructure** | Docker · Neo4j · SQLite (WAL mode) · Server-Sent Events (SSE) |

---

## Real-World Impact

The organisations that solve knowledge fragmentation first will have a structural advantage in how they operate, maintain, and improve their assets. IKIP is a step toward that future — turning passive document archives into an active, intelligent knowledge layer that:

- **Reduces information search time** from hours to seconds
- **Preserves institutional knowledge** before it walks out the door with retiring engineers
- **Catches compliance gaps** before regulators do
- **Connects the dots** across maintenance logs, drawings, and SOPs that no individual team member could connect alone
- **Runs entirely on-premise** — critical for industries where data sovereignty and air-gapped networks are non-negotiable

---

*Built for the ET AI Hackathon 2026 — Problem Statement #8: AI for Industrial Knowledge Intelligence*
