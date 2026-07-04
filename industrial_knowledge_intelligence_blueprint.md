# Industrial Knowledge Intelligence Platform
## Complete Architectural Blueprint & Project Plan
### ET AI Hackathon 2026 — Problem Statement 8

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Module Breakdown](#3-module-breakdown)
4. [AI Model Stack](#4-ai-model-stack)
5. [Tech Stack](#5-tech-stack)
6. [Data Flow & Pipeline Design](#6-data-flow--pipeline-design)
7. [Document & Drawing Intelligence](#7-document--drawing-intelligence)
8. [Database Design](#8-database-design)
9. [API Design](#9-api-design)
10. [Frontend Architecture](#10-frontend-architecture)
11. [Build Plan & Timeline](#11-build-plan--timeline)
12. [Demo Strategy](#12-demo-strategy)
13. [Judging Criteria Coverage](#13-judging-criteria-coverage)
14. [Setup & Installation](#14-setup--installation)

---

## 1. Project Overview

### Problem Being Solved

Industrial plants operate across 7–12 disconnected document systems — P&IDs in one place, maintenance work orders in another, operating procedures in a third, inspection records in a fourth, regulatory submissions scattered across email archives. A 2024 McKinsey survey found professionals in asset-intensive industries spend 35% of their working hours just searching for information.

This fragmentation causes:
- 18–22% of unplanned downtime events (NASSCOM-EY study)
- Compliance gaps discovered only during audits, not before
- Loss of institutional knowledge as experienced engineers retire
- Root causes of failures missed because no single person sees the full picture

### What This Platform Does

An AI-powered Industrial Knowledge Intelligence platform that ingests heterogeneous documents — engineering drawings, maintenance records, safety procedures, inspection reports, operating instructions — and makes their collective intelligence queryable, actionable, and continuously updated at the point of need.

### Why This Wins

Every competing team will build a basic chatbot over PDFs. This platform differentiates through:

- **Knowledge graph layer** — Neo4j connecting equipment → failures → procedures → regulations → personnel across all documents
- **Vision intelligence** — P&ID drawing analysis via local vision model, tags cross-referenced with maintenance history
- **Hybrid retrieval** — semantic + keyword search fused with Reciprocal Rank Fusion, not naive vector search
- **Agentic compliance scanning** — regulation-to-procedure mapping with auto-generated audit packages
- **100% local inference** — Ollama on RTX 4060, zero API costs, zero internet dependency during demo

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  Chat UI │ Doc Manager │ Graph Explorer │ Compliance Dashboard  │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP / SSE (streaming)
┌──────────────────────────▼──────────────────────────────────────┐
│                      BACKEND (FastAPI)                          │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  RAG Query      │  │  Ingestion   │  │  Agentic Task     │  │
│  │  Handler        │  │  Pipeline    │  │  Runner           │  │
│  │  (hybrid search)│  │  (async)     │  │  (RCA, compliance)│  │
│  └────────┬────────┘  └──────┬───────┘  └─────────┬─────────┘  │
└───────────┼──────────────────┼─────────────────────┼────────────┘
            │                  │                      │
┌───────────▼──────────────────▼──────────────────── ▼────────────┐
│                        AI LAYER (Ollama)                        │
│                                                                 │
│   llama3.1:8b-instruct-q4_K_M    │    minicpm-v (vision)       │
│   (RAG, extraction, reasoning)    │    (P&ID, drawings, scans)  │
│                                   │                             │
│   nomic-embed-text (embeddings)                                 │
└──────────────────┬──────────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────┐
│                      KNOWLEDGE STORE                            │
│                                                                 │
│  ChromaDB (vectors)  │  Neo4j AuraDB (graph)  │  SQLite (meta) │
└─────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

- **Async-first** — document ingestion runs in background tasks, never blocking the UI
- **Model swap on demand** — Ollama unloads LLM and loads vision model when an image is uploaded (8GB VRAM managed automatically)
- **Persistent storage** — ChromaDB writes to disk; SQLite is file-based; Neo4j on AuraDB free cloud tier. Pre-ingest all demo documents so day-of demo has zero ingestion latency
- **Streaming responses** — all LLM output streamed via Server-Sent Events so answers appear token-by-token in the UI

---

## 3. Module Breakdown

### Module 1 — Universal Document Ingestion Engine

The intake pipeline that transforms any industrial document into queryable knowledge.

**Supported formats:**
- Digital PDFs (manuals, SOPs, reports) → PyMuPDF + Docling
- Scanned PDFs / photographed docs → pdf2image + Tesseract OCR (fallback: minicpm-v)
- Excel / CSV (maintenance logs, inspection checklists) → openpyxl
- DOCX (procedures, work orders, RCA reports) → python-docx
- Images of drawings (P&IDs, flow diagrams) → minicpm-v vision

**Processing steps for every document:**
1. Format detection → route to correct parser
2. Layout analysis (headings, tables, paragraphs separated)
3. Chunk at 512 tokens with 128-token overlap
4. Tag each chunk with metadata: filename, page, section, doc_type, date
5. Entity extraction via llama3.1:8b → JSON output of equipment tags, dates, personnel, regulatory refs, failure modes
6. Embed each chunk via nomic-embed-text → store in ChromaDB
7. Write entities and relationships to Neo4j knowledge graph
8. Register document in SQLite with ingestion status

---

### Module 2 — Expert Knowledge Copilot (RAG Chat)

The primary user interface — a conversational AI that answers operational and maintenance queries across all ingested documents.

**How retrieval works (hybrid, not naive):**

```
User query
    │
    ├──► Dense vector search (ChromaDB) ──► top-8 semantic matches
    │
    ├──► Sparse BM25 keyword search ──────► top-8 keyword matches
    │
    └──► Reciprocal Rank Fusion ──────────► merged top-6 results
                                                │
                                         llama3.1:8b
                                         synthesises answer
                                         with inline citations
```

**Why hybrid matters:** Pure semantic search misses exact equipment tag matches (e.g. "P-101" embedded in a dense paragraph). Pure keyword search misses conceptual queries ("pump failures caused by thermal stress"). Fusion gets both.

**Features:**
- Source citations on every answer (Document name, Page X, Section Y)
- Confidence badge (High / Medium / Low) based on retrieval score spread
- Low-confidence answers trigger "suggest uploading more documents"
- Streaming token-by-token output via SSE
- Mobile-first field technician mode: large tap targets, voice input via Web Speech API, short-form answers by default

**Example queries the system handles:**
- "When was heat exchanger E-301 last inspected and what was found?"
- "Which equipment has the highest failure frequency in the last 12 months?"
- "What is the OISD-mandated inspection interval for pressure vessels?"
- "Show me all maintenance work orders for pump P-101"
- "What are the restart procedures after a compressor trip?"

---

### Module 3 — Maintenance Intelligence & RCA Agent

An agentic system that reasons across the full document corpus to surface maintenance insights no individual team member could find manually.

**Equipment failure timeline builder:**
For any equipment tag, the agent pulls all work orders, inspection reports, and incident logs across the entire corpus — sorted chronologically — and annotates patterns. Example output: "Pump P-101 has had 3 mechanical seal failures in 18 months, always 2–4 weeks after high-vibration alerts in the sensor log."

**Root Cause Analysis (RCA) copilot:**
When a failure is reported, the agent:
1. Retrieves similar past failures from the knowledge base
2. Surfaces OEM-recommended diagnostic checks
3. Generates a pre-filled 5-Why tree with historical context
4. Engineer reviews and confirms rather than starting from scratch
5. Completed RCA is saved as a structured document and re-ingested

**Predictive maintenance scheduler:**
Based on failure patterns + OEM service intervals, generates a risk-ranked maintenance queue:
- `CRITICAL` — overdue interval + past failure history
- `HIGH` — approaching interval + similar failure pattern observed
- `MEDIUM` — approaching interval, no concerning pattern
- `LOW` — interval not due, no anomalies

Output: printable/exportable PM schedule with evidence links to source documents.

---

### Module 4 — Compliance & Regulatory Gap Detector

**Pre-loaded regulatory corpus:**
- OISD Standards (Std 117, 118, 141, 150, 155, 163)
- Factory Act 1948 (relevant sections)
- PESO guidelines
- DGMS regulations (for applicable facilities)

**Regulation-to-procedure mapper:**
The agent maps each regulation clause to the plant's actual SOPs and inspection records. Gaps are classified:
- `CRITICAL` — no procedure exists for a mandatory requirement
- `MAJOR` — procedure exists but last inspection is overdue per regulation
- `MINOR` — procedure exists, inspection current, but documentation incomplete

**Audit evidence package generator:**
On demand, compiles a compliance dossier:
- For each regulation clause: relevant procedure + most recent inspection record + personnel sign-off
- Exported as structured PDF with citations
- Saves days of manual pre-audit preparation

---

### Module 5 — P&ID & Drawing Intelligence

**Processing pipeline for engineering drawings:**

```
Upload drawing (PNG/JPG/PDF)
        │
        ▼
Convert to 300 DPI PNG (pdf2image)
        │
        ▼
Tile large drawings into 1024×1024px sections (20% overlap)
        │
        ▼
Each tile → minicpm-v with structured extraction prompt
        │
        ▼
Parse JSON response → validate tag formats (regex)
        │
        ▼
Deduplicate tags across tiles
        │
        ▼
Cross-reference with existing Neo4j nodes
(drawing tells you connections; documents tell you failure history)
        │
        ▼
Store structured data + embed text summary in ChromaDB
        │
        ▼
Frontend overlays extracted tags on original drawing image
```

**What the vision model extracts:**
- Equipment tags (P-101, V-205, E-301, R-102, C-401)
- Instrument tags (FIC-201, TT-105, PT-203, LIC-301)
- Pipe connections (from → to, line type)
- Valve tags (HV-201, SV-105, PSV-301)
- Title block information (drawing number, revision, date)

**Post-extraction intelligence:**
Users can ask natural language questions about the drawing:
- "What equipment is downstream of pump P-101?"
- "Which instruments are on the cooling water circuit for E-301?"
- "What valves isolate reactor R-102?"

These answers combine drawing topology data AND maintenance history from other documents.

---

### Module 6 — Lessons Learned & Failure Intelligence Engine

**Recurring pattern detector:**
Periodically scans all incident reports, near-miss logs, and non-conformance records. Clusters events by equipment type, failure mode, and shift pattern. Example output: "7 of 9 seal failures on centrifugal pumps occurred within 72 hours of a dry-run incident. The restart procedure (SOP-MNT-047) does not include a pre-start lubrication check."

**Proactive risk push alerts:**
When new conditions match a historical failure pattern, pushes a warning to the relevant team: "Conditions on Compressor C-102 match the pre-failure signature seen in Incident Report IR-089 (March 2022). Recommend inspection of suction strainer before next startup."

---

## 4. AI Model Stack

### Primary LLM — `llama3.1:8b-instruct-q4_K_M`

| Property | Value |
|---|---|
| VRAM usage | ~4.9 GB |
| Context window | 128K tokens |
| Quantisation | Q4_K_M (best quality/size tradeoff) |
| Inference speed | ~35–50 tokens/sec on RTX 4060 |
| Use cases | RAG Q&A, entity extraction, compliance analysis, RCA generation, JSON output |

Pull command:
```bash
ollama pull llama3.1:8b
```

### Vision Model — `minicpm-v`

| Property | Value |
|---|---|
| VRAM usage | ~4.5 GB |
| Loaded | On demand (swaps with primary LLM) |
| Swap time | ~8–12 seconds |
| Use cases | P&ID analysis, scanned document transcription, drawing tag extraction |

Pull command:
```bash
ollama pull minicpm-v
```

### Embedding Model — `nomic-embed-text`

| Property | Value |
|---|---|
| VRAM usage | ~274 MB |
| Dimensions | 768 |
| Runs alongside | llama3.1:8b simultaneously |
| Use cases | All chunk embeddings, query embeddings for retrieval |

Pull command:
```bash
ollama pull nomic-embed-text
```

### VRAM Budget (RTX 4060 8GB)

```
llama3.1:8b-q4_K_M    ████████████████████████░░░░░░░░   4.9 GB
nomic-embed-text       █░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0.3 GB
OS + display driver    ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0.9 GB
Free buffer            ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   1.9 GB
─────────────────────────────────────────────────────── 8.0 GB total

Vision swap (minicpm-v replaces llama3.1:8b):
minicpm-v              ████████████████████░░░░░░░░░░░░   4.5 GB
OS + display driver    ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0.9 GB
Free buffer            ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   2.6 GB
```

---

## 5. Tech Stack

### Operating System

**Ubuntu 22.04 LTS** (recommended) or WSL2 on Windows 11

Reasons: native CUDA support, one-command package installs for Tesseract/poppler, no WDDM GPU overhead, all Python ML packages work without workarounds. Inference is ~10–15% faster vs Windows due to WDDM scheduler.

### Backend

| Component | Technology | Purpose |
|---|---|---|
| Web framework | FastAPI (Python 3.11) | REST API + SSE streaming |
| LLM client | `ollama` Python SDK | Call llama3.1:8b and minicpm-v |
| RAG orchestration | LangChain | Pipeline management |
| Async tasks | FastAPI BackgroundTasks | Non-blocking ingestion |
| PDF parsing | PyMuPDF (`fitz`) | Digital PDF text extraction |
| Layout analysis | Docling | Structure-aware parsing |
| OCR | pytesseract + Tesseract | Scanned document text |
| Image conversion | pdf2image + poppler | PDF page → PNG for vision |
| Excel parsing | openpyxl | Maintenance log sheets |
| DOCX parsing | python-docx | Procedure documents |
| Keyword search | rank-bm25 | BM25 sparse retrieval |
| Result fusion | Custom RRF | Merge dense + sparse results |
| Data validation | Pydantic v2 | Request/response schemas |

### AI & Storage

| Component | Technology | Purpose |
|---|---|---|
| LLM + Vision | Ollama (local) | All model inference |
| Vector store | ChromaDB (persistent) | Chunk embeddings + metadata |
| Knowledge graph | Neo4j AuraDB Free | Entity-relationship graph |
| Relational DB | SQLite + SQLAlchemy | Document registry, audit logs |

### Frontend

| Component | Technology | Purpose |
|---|---|---|
| Framework | React 18 + TypeScript | UI |
| Styling | Tailwind CSS | Design system |
| Graph visualisation | react-force-graph | Interactive knowledge graph |
| PDF viewer | react-pdf | Inline document preview |
| Voice input | Web Speech API | Field technician mode |
| HTTP client | Axios | API calls |
| SSE streaming | Native EventSource | Token streaming from backend |

### DevOps

| Component | Technology | Purpose |
|---|---|---|
| Demo tunnel | ngrok (free) | Expose localhost to judges |
| Frontend deploy | Vercel (free) | React hosting |
| Backend deploy | Run locally | Most reliable for live demo |
| Version control | Git + GitHub | Code management |

---

## 6. Data Flow & Pipeline Design

### Ingestion Pipeline (async, runs on upload)

```
User uploads file
        │
        ▼
┌── Format Detection ──────────────────────────────────────┐
│   .pdf → is_scanned? → branch                            │
│   .xlsx / .csv → openpyxl parser                        │
│   .docx → python-docx parser                            │
│   image → vision pipeline directly                      │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌── Text Extraction ────────────────────────────────────────┐
│   Digital PDF: PyMuPDF → raw text + page metadata        │
│   Scanned PDF: pdf2image → Tesseract → text              │
│               if OCR quality < threshold → minicpm-v     │
│   Excel: row-by-row text with column headers as keys     │
│   DOCX: paragraph + table text with heading hierarchy    │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌── Layout Analysis (Docling) ──────────────────────────────┐
│   Identify: headings, paragraphs, tables, figures        │
│   Assign section tags to each text block                 │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌── Chunking ───────────────────────────────────────────────┐
│   512 tokens per chunk, 128-token overlap                │
│   Metadata per chunk: {                                  │
│     doc_id, filename, page, section,                     │
│     doc_type, date_ingested, chunk_index                 │
│   }                                                      │
└──────────────────────────────────────────────────────────┘
        │
        ├──► nomic-embed-text → 768-dim vector → ChromaDB
        │
        ▼
┌── Entity Extraction (llama3.1:8b) ────────────────────────┐
│   Prompt: extract JSON {                                 │
│     equipment_tags: [],   # P-101, V-205                 │
│     instrument_tags: [],  # FIC-201, TT-105              │
│     dates: [],            # maintenance dates            │
│     personnel: [],        # engineer names               │
│     measurements: {},     # {tag: value, unit}           │
│     regulatory_refs: [],  # OISD Std 117 Clause 8.3      │
│     failure_modes: []     # seal failure, bearing wear   │
│   }                                                      │
└──────────────────────────────────────────────────────────┘
        │
        ▼
┌── Knowledge Graph Write (Neo4j) ──────────────────────────┐
│   Equipment nodes: MERGE (e:Equipment {tag: "P-101"})    │
│   Relationships:                                         │
│     (:Equipment)-[:HAS_FAILURE_MODE]->(:FailureMode)     │
│     (:Procedure)-[:GOVERNS]->(:Equipment)                │
│     (:Regulation)-[:APPLIES_TO]->(:Process)              │
│     (:Inspection)-[:COVERS]->(:Equipment)                │
│     (:WorkOrder)-[:REFERENCES]->(:Equipment)             │
└──────────────────────────────────────────────────────────┘
        │
        ▼
SQLite: UPDATE documents SET status='complete', chunk_count=N
```

### Query Pipeline (real-time, streamed)

```
User query: "When was E-301 last inspected and what was found?"
        │
        ├──► Entity detection: "E-301" detected
        │           │
        │           ▼
        │    Neo4j: MATCH (e:Equipment {tag:"E-301"})
        │           RETURN linked doc_ids, failure_modes, procedures
        │
        ├──► Embed query → nomic-embed-text → 768-dim vector
        │           │
        │           ▼
        │    ChromaDB: query(embedding, where={doc_id: in linked_ids}, n=8)
        │    → top-8 semantic matches
        │
        ├──► BM25: search("E-301 inspected last") → top-8 keyword matches
        │
        ▼
Reciprocal Rank Fusion: merge and re-rank → top-6 final chunks
        │
        ▼
llama3.1:8b:
  system: "Answer using only the provided context. Always cite sources."
  context: [chunk1 (page 4, Inspection Report 2024-03), chunk2 ...]
  user: "When was E-301 last inspected and what was found?"
        │
        ▼
Streamed SSE response → React UI renders token-by-token
        │
        ▼
UI shows: answer + clickable source badges
User clicks badge → PDF viewer opens at exact page
```

---

## 7. Document & Drawing Intelligence

### Drawing Analysis — Detailed Flow

```python
# drawing_analyzer.py

import ollama, base64, json, re
from pdf2image import convert_from_path
from pathlib import Path

EXTRACTION_PROMPT = """You are an engineering P&ID drawing analyst.
Extract ALL visible tags from this drawing.
Return ONLY valid JSON — no explanation, no markdown.
Format:
{
  "equipment": ["P-101", "V-205"],
  "instruments": ["FIC-201", "TT-105"],
  "connections": [{"from": "P-101", "to": "V-205", "type": "process"}],
  "valves": ["HV-201"],
  "title_block": {"drawing_no": "", "revision": "", "date": ""}
}"""

def load_image_b64(path: str) -> list[str]:
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        pages = convert_from_path(path, dpi=300)
        return [img_to_b64(p) for p in pages]
    return [img_to_b64(path)]

def img_to_b64(img) -> str:
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def analyze_drawing(image_path: str) -> dict:
    tiles = load_image_b64(image_path)
    all_results = []
    for tile in tiles:
        resp = ollama.chat(
            model="minicpm-v",
            messages=[{
                "role": "user",
                "content": EXTRACTION_PROMPT,
                "images": [tile]
            }],
            options={"temperature": 0.1}
        )
        raw = resp['message']['content']
        clean = re.sub(r'```json|```', '', raw).strip()
        try:
            all_results.append(json.loads(clean))
        except json.JSONDecodeError:
            pass  # log and continue with other tiles
    return merge_and_deduplicate(all_results)

def merge_and_deduplicate(results: list[dict]) -> dict:
    merged = {"equipment": [], "instruments": [], "connections": [], "valves": []}
    for r in results:
        for key in merged:
            merged[key].extend(r.get(key, []))
    merged["equipment"]   = list(set(merged["equipment"]))
    merged["instruments"] = list(set(merged["instruments"]))
    merged["valves"]      = list(set(merged["valves"]))
    seen, deduped = set(), []
    for c in merged["connections"]:
        k = (c.get("from"), c.get("to"))
        if k not in seen:
            seen.add(k)
            deduped.append(c)
    merged["connections"] = deduped
    return merged
```

### What minicpm-v Can and Cannot Do

**Reliable:**
- Reading alphanumeric equipment and instrument tags
- Identifying standard ISA instrument bubbles
- Detecting pipe connections between labelled equipment
- Reading title block text
- Transcribing clear handwritten annotations

**Unreliable (handle gracefully):**
- Very dense drawings with 200+ tags — tile and merge
- Scans below 150 DPI — require high-res input
- Exact pixel coordinates of tags — approximate only
- Distinguishing line types (process vs utility) in greyscale — prompt explicitly

---

## 8. Database Design

### ChromaDB (Vector Store)

Collection: `industrial_docs`

Each document in the collection:
```json
{
  "id": "doc_abc123_chunk_047",
  "embedding": [0.023, -0.145, ...],
  "document": "The mechanical seal on pump P-101 was found to be worn...",
  "metadata": {
    "doc_id": "doc_abc123",
    "filename": "inspection_report_2024_03.pdf",
    "page": 4,
    "section": "Findings and Recommendations",
    "doc_type": "inspection_report",
    "date_ingested": "2025-01-15",
    "entity_tags": ["P-101"],
    "chunk_index": 47
  }
}
```

### Neo4j Knowledge Graph

Node types and relationships:

```cypher
// Node types
(:Equipment  {tag: "P-101", name: "Feed Pump", area: "Unit 2"})
(:Instrument {tag: "FIC-201", type: "Flow Indicator Controller"})
(:Procedure  {id: "SOP-MNT-047", title: "Centrifugal Pump Startup"})
(:Regulation {id: "OISD-117-8.3.2", text: "Pressure vessel inspection interval..."})
(:Inspection {id: "INS-2024-034", date: "2024-03-15", inspector: "R. Sharma"})
(:WorkOrder  {id: "WO-2024-1123", type: "corrective", date: "2024-03-20"})
(:FailureMode {name: "mechanical seal failure"})
(:Document   {id: "doc_abc123", filename: "inspection_report_2024_03.pdf"})

// Relationships
(e:Equipment)-[:HAS_FAILURE_MODE {count: 3}]->(f:FailureMode)
(e:Equipment)-[:CONNECTED_TO    {type: "process", drawing: "DWG-P-001"}]->(e2:Equipment)
(p:Procedure)-[:GOVERNS          ]->(e:Equipment)
(r:Regulation)-[:APPLIES_TO      ]->(e:Equipment)
(i:Inspection)-[:COVERS          {findings: "seal wear"}]->(e:Equipment)
(w:WorkOrder )-[:REFERENCES      ]->(e:Equipment)
(d:Document  )-[:MENTIONS        ]->(e:Equipment)
(e:Equipment)-[:INSTRUMENTED_BY  ]->(inst:Instrument)
```

### SQLite Schema

```sql
CREATE TABLE documents (
    id          TEXT PRIMARY KEY,
    filename    TEXT NOT NULL,
    file_type   TEXT NOT NULL,
    doc_type    TEXT,           -- 'inspection_report', 'sop', 'manual', 'drawing'
    status      TEXT DEFAULT 'pending',  -- 'pending', 'processing', 'complete', 'failed'
    chunk_count INTEGER DEFAULT 0,
    entity_count INTEGER DEFAULT 0,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

CREATE TABLE audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT NOT NULL,  -- 'query', 'ingestion', 'compliance_scan', 'rca'
    details     TEXT,           -- JSON
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE compliance_reports (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    regulation_id TEXT,
    status      TEXT,           -- 'compliant', 'gap_critical', 'gap_major', 'gap_minor'
    evidence    TEXT,           -- JSON list of supporting doc_ids
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 9. API Design

### Endpoints

#### Document Management

```
POST   /api/documents/upload
       Body: multipart/form-data {file, doc_type}
       Response: {doc_id, status: "processing"}

GET    /api/documents
       Response: [{doc_id, filename, status, chunk_count, entity_count}]

GET    /api/documents/{doc_id}/status
       Response: {doc_id, status, progress_pct, chunk_count}

DELETE /api/documents/{doc_id}
       Response: {deleted: true}
```

#### Chat & RAG

```
POST   /api/chat/query
       Body: {query: str, mode: "detailed"|"brief"}
       Response: StreamingResponse (SSE)
       Stream format: data: {"token": "...", "done": false}
       Final:         data: {"token": "", "done": true, "sources": [...]}

GET    /api/chat/history
       Response: [{role, content, sources, timestamp}]
```

#### Drawing Analysis

```
POST   /api/drawings/analyze
       Body: multipart/form-data {file}
       Response: {
         drawing_id,
         equipment: [],
         instruments: [],
         connections: [],
         valves: [],
         cross_references: {  // matched with existing knowledge base
           "P-101": {known: true, last_inspection: "2024-03-15", failure_count: 3}
         }
       }
```

#### Maintenance Intelligence

```
GET    /api/maintenance/equipment/{tag}/timeline
       Response: {tag, events: [{date, type, description, doc_id}]}

POST   /api/maintenance/rca
       Body: {equipment_tag: str, failure_description: str}
       Response: StreamingResponse (SSE) — RCA report streamed token-by-token

GET    /api/maintenance/schedule
       Response: [{tag, priority, next_due, overdue_by, evidence_links}]
```

#### Compliance

```
POST   /api/compliance/scan
       Body: {regulation_set: ["OISD-117", "Factory-Act"]}
       Response: StreamingResponse (SSE) — gap report streamed

GET    /api/compliance/report/latest
       Response: {generated_at, gaps: [{regulation, status, description, evidence}]}

POST   /api/compliance/audit-package
       Response: {download_url}  — triggers PDF generation
```

#### Knowledge Graph

```
GET    /api/graph/equipment/{tag}
       Response: {node, relationships: [{type, target_tag, properties}]}

GET    /api/graph/overview
       Response: {nodes: [{id, label, type}], edges: [{source, target, type}]}
       Used by react-force-graph for visualisation
```

---

## 10. Frontend Architecture

### Page Structure

```
App
├── Layout (sidebar nav + header)
├── /chat          → Chat interface (primary)
├── /documents     → Document manager (upload, status, list)
├── /drawings      → Drawing upload + tag overlay viewer
├── /graph         → Knowledge graph explorer (react-force-graph)
├── /maintenance   → Equipment timeline + PM schedule
├── /compliance    → Gap report + audit package generator
└── /field         → Mobile-optimised field technician mode
```

### Chat Interface Components

```
ChatPage
├── MessageList
│   ├── UserMessage
│   └── AssistantMessage
│       ├── StreamingText (SSE consumer)
│       └── SourceCitations
│           └── CitationBadge (click → opens PDF at page)
├── QueryInput
│   ├── TextArea
│   ├── VoiceInputButton (Web Speech API)
│   └── SendButton
└── ConfidenceIndicator (High / Medium / Low badge)
```

### Knowledge Graph Explorer

Uses `react-force-graph` with:
- Node colour by type: Equipment (blue), Instrument (teal), Procedure (amber), Regulation (purple), Inspection (green)
- Edge labels showing relationship type
- Click on any node → pre-fills chat with query about that entity
- Filter panel: show/hide node types, filter by equipment area

### Drawing Tag Overlay

After drawing analysis:
- Original drawing image displayed at full width
- Extracted tags overlaid as clickable badges at approximate positions
- Clicking a tag → shows sidebar with: last inspection date, failure history, linked procedures, compliance status

---

## 11. Build Plan & Timeline

Assuming a 48-hour hackathon. Adjust proportionally for longer windows.

### Phase 1 — Core MVP (Hours 0–12)

**Goal: Working RAG chat over uploaded documents**

- [ ] Project scaffold: FastAPI backend + React frontend + CORS
- [ ] Ollama connection: test llama3.1:8b chat and nomic-embed-text embeddings
- [ ] ChromaDB setup: persistent client, collection creation
- [ ] PDF ingestion: PyMuPDF → chunking → embeddings → ChromaDB
- [ ] Basic RAG: query → vector search → llama3.1:8b → response
- [ ] SSE streaming: stream tokens to React frontend
- [ ] Document upload UI: drag-and-drop, status indicator
- [ ] Chat UI: message list, input, streaming text render

**Checkpoint:** Upload a PDF, ask a question, get a cited answer streaming in real-time.

---

### Phase 2 — Hybrid Retrieval + Graph (Hours 12–24)

**Goal: Production-quality retrieval + knowledge graph**

- [ ] BM25 index: build alongside ChromaDB during ingestion
- [ ] RRF fusion: merge dense + sparse results
- [ ] Entity extraction: llama3.1:8b → JSON → parse equipment/date/regulatory entities
- [ ] Neo4j AuraDB: connect, write equipment nodes and document relationships
- [ ] Source citations: attach doc/page metadata to every answer
- [ ] Graph explorer UI: react-force-graph with node types and click-to-query
- [ ] Equipment timeline: pull all events for a given tag from Neo4j + ChromaDB

**Checkpoint:** Query returns hybrid results with citations. Graph shows entity relationships. Click an equipment node to query its history.

---

### Phase 3 — Drawing Intelligence + Compliance (Hours 24–36)

**Goal: The two most visually impressive demo features**

- [ ] Drawing upload endpoint: receive image/PDF
- [ ] pdf2image + minicpm-v pipeline: extract tags as JSON
- [ ] Tag validation: regex check, deduplication across tiles
- [ ] Neo4j cross-reference: link drawing tags to existing nodes
- [ ] Drawing viewer UI: original image + clickable tag overlays
- [ ] Regulatory corpus: ingest OISD / Factory Act excerpts as special doc type
- [ ] Compliance scanner: regulation → procedure mapper via llama3.1:8b
- [ ] Gap report UI: colour-coded Critical / Major / Minor table
- [ ] Audit package: PDF export of evidence per regulation clause

**Checkpoint:** Upload P&ID → see tags appear on drawing. Run compliance scan → see gap report with evidence links.

---

### Phase 4 — Polish + Demo Prep (Hours 36–48)

**Goal: Impress judges in 5 minutes**

- [ ] Mobile/field mode: responsive layout, large targets, voice input
- [ ] PM schedule: risk-ranked maintenance queue with export
- [ ] RCA agent: agentic 5-Why generation for reported failures
- [ ] Pre-ingest all demo documents overnight (no ingestion latency on demo day)
- [ ] ngrok tunnel: expose local backend to judges' devices
- [ ] Error handling: graceful fallbacks if Ollama model swap is slow
- [ ] Demo script: rehearse the 5-minute judge walkthrough 3 times
- [ ] Backup: screen-recorded video of every demo step

---

## 12. Demo Strategy

### 5-Minute Judge Walkthrough

**Minute 0:30 — Live upload (builds trust)**
Drag 3 pre-prepared PDFs into the UI:
- A centrifugal pump maintenance manual (150 pages)
- An inspection report with equipment tags
- OISD Standard 117 excerpt

Show the real-time ingestion progress bar. Mention: "This is processing, embedding, and building a knowledge graph in real-time on a local GPU — no cloud APIs."

**Minute 1:30 — The killer cross-document query**
Ask: "Which equipment has had the most failures, and is its maintenance overdue per OISD standards?"

Watch the system cross-reference the maintenance manual, inspection history, and regulatory document simultaneously. Point out the source citations: "Every claim is cited to a specific page. Click this badge — it opens the source document at exactly that page."

**Minute 2:30 — Knowledge graph**
Switch to the graph view. Show the animated node-link graph: equipment nodes connected to failure modes, procedures, regulations, personnel. Click pump P-101's node — chat pre-fills with a query about it. Say: "This is the institutional memory of your plant, made visual and queryable."

**Minute 3:30 — Compliance gap scan**
Click "Run Compliance Audit → OISD-117." Show the gap report streaming in live: "OISD Std 117 Clause 8.3.2: No inspection record found for pressure vessels in last 12 months. Status: CRITICAL." Then click "Generate Audit Package" — a PDF evidence dossier is produced in seconds.

**Minute 4:30 — P&ID vision**
Upload a clean P&ID image. Show tag extraction: "E-301, FIC-201, P-101 appearing as nodes..." Ask: "What instruments are on the cooling water circuit for E-301?" — the answer combines drawing topology AND maintenance history. Say: "This drawing was just uploaded. The system connected it to existing maintenance records automatically."

### What to Say When Judges Ask "How Does It Work?"

> "Every document is processed locally on a GPU — no data leaves this machine, no API keys, no cloud costs. We use a quantised Llama 3.1 model for reasoning, a separate vision model for engineering drawings, and a knowledge graph database that links every entity across every document. The retrieval combines semantic search and keyword search — the same approach production RAG systems at scale use."

---

## 13. Judging Criteria Coverage

| Criterion | Weight | How This Platform Addresses It |
|---|---|---|
| **Innovation** | 25% | Cross-document synthesis + knowledge graph + vision AI + hybrid retrieval combined. No other team will have the graph layer. |
| **Business Impact** | 25% | Directly solves the 35% time-on-search problem. Measurable: query answered in seconds vs hours of manual search. Compliance audit prep reduced from days to minutes. |
| **Technical Excellence** | 20% | Hybrid RAG (not naive vector search), knowledge graph with typed relationships, agentic multi-step compliance scanning, vision model for structured extraction, streaming inference. |
| **Scalability** | 15% | Modular pipeline design. ChromaDB → Qdrant/Pinecone for production. SQLite → PostgreSQL. Local Ollama → vLLM cluster. Architecture doesn't change — only the backends. |
| **User Experience** | 15% | Streaming responses, source citations with one-click document jump, mobile field mode with voice input, graph explorer with click-to-query, PM schedule export. |

### Key Metrics to State During Demo

- Query answered: **< 5 seconds** end-to-end
- Source citations: **100%** of answers (no hallucination without basis)
- Document types supported: **5** (PDF, DOCX, XLSX, CSV, image)
- Regulatory standards covered: **6** (OISD-117, 118, 141, 150, 155, Factory Act)
- Knowledge graph: **entity extraction from every chunk**
- Drawing analysis: **equipment + instrument + connection + valve tags**

---

## 14. Setup & Installation

### System Requirements

- OS: Ubuntu 22.04 LTS (or WSL2 on Windows 11)
- RAM: 16 GB
- GPU: Nvidia RTX 4060 8GB (CUDA 12.x)
- Storage: 50 GB free (models ~11 GB + documents + databases)
- Python: 3.11+
- Node.js: 18+

### Step 1 — Install Ollama and pull models

```bash
curl -fsSL https://ollama.com/install.sh | sh

# pull all required models (do this on good WiFi, ~11 GB total)
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama pull minicpm-v

# verify GPU inference is working
ollama run llama3.1:8b "say hello"
# look for "GPU layers: 33" in output — confirms CUDA is active
```

### Step 2 — Clone and set up the backend

```bash
git clone https://github.com/YOUR_USERNAME/industrial-knowledge-platform
cd industrial-knowledge-platform/backend

python -m venv venv
source venv/bin/activate

pip install fastapi uvicorn pydantic
pip install ollama chromadb
pip install langchain langchain-community
pip install pymupdf pytesseract pdf2image
pip install python-docx openpyxl
pip install rank-bm25
pip install neo4j sqlalchemy
pip install python-multipart aiofiles

# Ubuntu system packages
sudo apt install -y tesseract-ocr poppler-utils

# create .env
cat > .env << EOF
OLLAMA_BASE_URL=http://localhost:11434
NEO4J_URI=neo4j+s://YOUR_AURADB_URI
NEO4J_USER=neo4j
NEO4J_PASSWORD=YOUR_PASSWORD
CHROMA_PATH=./chroma_db
SQLITE_PATH=./industrial_knowledge.db
EOF

# start the backend
uvicorn main:app --reload --port 8000
```

### Step 3 — Set up the frontend

```bash
cd ../frontend
npm install
npm run dev
# → http://localhost:3000
```

### Step 4 — Set up Neo4j AuraDB

1. Go to [console.neo4j.io](https://console.neo4j.io)
2. Create a free instance (select "AuraDB Free")
3. Download the connection credentials
4. Paste URI and password into `.env`

### Step 5 — Expose for demo (ngrok)

```bash
# install ngrok
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# expose backend
ngrok http 8000
# copy the https://xxxx.ngrok.io URL → set as REACT_APP_API_URL in frontend
```

### Pre-Demo Checklist

- [ ] All 3 Ollama models pulled and verified with `ollama list`
- [ ] `nvidia-smi` shows GPU with free VRAM
- [ ] `ollama run llama3.1:8b "test"` responds in < 5 seconds
- [ ] Neo4j AuraDB instance is running (console.neo4j.io)
- [ ] All demo documents pre-ingested (run ingestion the night before)
- [ ] Frontend connects to backend successfully
- [ ] ngrok tunnel is up and URL shared to judges' devices
- [ ] Demo script rehearsed at least 3 times
- [ ] Screen-recorded backup video ready
- [ ] Laptop plugged into power (LLM inference drains battery fast)
- [ ] Laptop is NOT doing Windows/system updates during demo

---

---

## 15. Complete Project File Structure

```
industrial-knowledge-platform/
│
├── backend/
│   ├── main.py                        # FastAPI app entry point
│   ├── .env                           # environment variables (never commit)
│   ├── requirements.txt
│   │
│   ├── core/
│   │   ├── config.py                  # settings loaded from .env
│   │   ├── ollama_client.py           # wrapper for llama3.1:8b + minicpm-v + embeddings
│   │   └── database.py                # SQLite + ChromaDB + Neo4j connections
│   │
│   ├── ingestion/
│   │   ├── pipeline.py                # orchestrates the full ingestion flow
│   │   ├── parsers/
│   │   │   ├── pdf_parser.py          # PyMuPDF + Docling
│   │   │   ├── ocr_parser.py          # Tesseract + pdf2image
│   │   │   ├── excel_parser.py        # openpyxl
│   │   │   └── docx_parser.py         # python-docx
│   │   ├── chunker.py                 # 512-token chunks with 128-token overlap
│   │   ├── embedder.py                # nomic-embed-text via Ollama
│   │   └── entity_extractor.py        # llama3.1:8b JSON extraction
│   │
│   ├── retrieval/
│   │   ├── vector_store.py            # ChromaDB read/write
│   │   ├── bm25_index.py              # rank-bm25 keyword search
│   │   └── rrf_fusion.py              # Reciprocal Rank Fusion merger
│   │
│   ├── graph/
│   │   ├── neo4j_client.py            # Neo4j AuraDB driver
│   │   ├── graph_builder.py           # write nodes and relationships
│   │   └── graph_query.py             # equipment timeline, cross-ref queries
│   │
│   ├── agents/
│   │   ├── rag_agent.py               # hybrid retrieval → llama3.1:8b → stream
│   │   ├── rca_agent.py               # multi-step RCA generation
│   │   ├── compliance_agent.py        # regulation-to-procedure mapper
│   │   └── pattern_agent.py           # failure pattern detector
│   │
│   ├── drawing/
│   │   ├── analyzer.py                # minicpm-v P&ID extraction pipeline
│   │   ├── tiler.py                   # split large drawings into tiles
│   │   └── validator.py               # regex tag validation + deduplication
│   │
│   └── routers/
│       ├── documents.py               # /api/documents/*
│       ├── chat.py                    # /api/chat/*
│       ├── drawings.py                # /api/drawings/*
│       ├── maintenance.py             # /api/maintenance/*
│       ├── compliance.py              # /api/compliance/*
│       └── graph.py                   # /api/graph/*
│
├── frontend/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── api/
│   │   │   ├── client.ts              # axios base config
│   │   │   ├── documents.ts
│   │   │   ├── chat.ts                # SSE streaming hook
│   │   │   ├── drawings.ts
│   │   │   ├── maintenance.ts
│   │   │   └── compliance.ts
│   │   │
│   │   ├── components/
│   │   │   ├── layout/
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   └── Header.tsx
│   │   │   ├── chat/
│   │   │   │   ├── ChatPage.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── AssistantMessage.tsx
│   │   │   │   ├── StreamingText.tsx  # consumes SSE token stream
│   │   │   │   ├── SourceCitations.tsx
│   │   │   │   └── VoiceInput.tsx     # Web Speech API
│   │   │   ├── documents/
│   │   │   │   ├── DocumentManager.tsx
│   │   │   │   ├── UploadDropzone.tsx
│   │   │   │   └── DocumentCard.tsx
│   │   │   ├── graph/
│   │   │   │   ├── GraphExplorer.tsx  # react-force-graph
│   │   │   │   ├── NodePanel.tsx      # sidebar on node click
│   │   │   │   └── GraphFilters.tsx
│   │   │   ├── drawings/
│   │   │   │   ├── DrawingUpload.tsx
│   │   │   │   ├── DrawingViewer.tsx  # image + tag overlays
│   │   │   │   └── TagBadge.tsx
│   │   │   ├── maintenance/
│   │   │   │   ├── EquipmentTimeline.tsx
│   │   │   │   └── PMSchedule.tsx
│   │   │   └── compliance/
│   │   │       ├── ComplianceDashboard.tsx
│   │   │       ├── GapReport.tsx
│   │   │       └── AuditPackageButton.tsx
│   │   │
│   │   ├── hooks/
│   │   │   ├── useSSEStream.ts        # generic SSE consumer hook
│   │   │   ├── useVoiceInput.ts
│   │   │   └── useGraph.ts
│   │   │
│   │   └── types/
│   │       ├── document.ts
│   │       ├── chat.ts
│   │       ├── graph.ts
│   │       └── compliance.ts
│
├── data/
│   ├── demo_documents/                # pre-prepared demo PDFs (not committed)
│   └── regulatory/                    # OISD excerpts, Factory Act sections
│
├── chroma_db/                         # ChromaDB persistent storage (gitignored)
├── industrial_knowledge.db            # SQLite file (gitignored)
│
├── docker-compose.yml                 # optional: containerise for deployment
├── .gitignore
└── README.md
```

---

## 16. Core Code — Key Implementations

### `core/ollama_client.py` — Unified model interface

```python
import ollama
import json
import re
from typing import Generator

CHAT_MODEL    = "llama3.1:8b"
VISION_MODEL  = "minicpm-v"
EMBED_MODEL   = "nomic-embed-text"

def chat_stream(system: str, user: str) -> Generator[str, None, None]:
    """Stream tokens from llama3.1:8b."""
    stream = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ],
        stream=True,
        options={"temperature": 0.2, "num_ctx": 8192}
    )
    for chunk in stream:
        yield chunk['message']['content']

def chat_json(system: str, user: str) -> dict:
    """Call llama3.1:8b and parse JSON response. Used for entity extraction."""
    resp = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user}
        ],
        options={"temperature": 0.1}
    )
    raw = resp['message']['content']
    clean = re.sub(r'```json|```', '', raw).strip()
    return json.loads(clean)

def vision_analyze(image_b64: str, prompt: str) -> str:
    """Send image to minicpm-v. Ollama auto-swaps models."""
    resp = ollama.chat(
        model=VISION_MODEL,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [image_b64]
        }],
        options={"temperature": 0.1}
    )
    return resp['message']['content']

def embed(text: str) -> list[float]:
    """Generate embedding via nomic-embed-text."""
    resp = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return resp["embedding"]
```

---

### `retrieval/rrf_fusion.py` — Hybrid retrieval

```python
from retrieval.vector_store import semantic_search
from retrieval.bm25_index   import keyword_search

def reciprocal_rank_fusion(
    query: str,
    doc_id_filter: list[str] | None = None,
    top_k: int = 6,
    rrf_k: int = 60
) -> list[dict]:
    """
    Merge semantic and keyword results using Reciprocal Rank Fusion.
    RRF score = sum(1 / (k + rank)) across both ranked lists.
    """
    semantic_results = semantic_search(query, n=10, doc_ids=doc_id_filter)
    keyword_results  = keyword_search(query, n=10, doc_ids=doc_id_filter)

    scores: dict[str, float] = {}
    docs:   dict[str, dict]  = {}

    for rank, result in enumerate(semantic_results):
        chunk_id = result["id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (rrf_k + rank + 1)
        docs[chunk_id] = result

    for rank, result in enumerate(keyword_results):
        chunk_id = result["id"]
        scores[chunk_id] = scores.get(chunk_id, 0) + 1 / (rrf_k + rank + 1)
        docs[chunk_id] = result

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [docs[cid] for cid, _ in ranked[:top_k]]
```

---

### `agents/rag_agent.py` — Full RAG query handler

```python
from retrieval.rrf_fusion  import reciprocal_rank_fusion
from graph.graph_query     import get_linked_doc_ids
from core.ollama_client    import chat_stream
from typing import Generator

RAG_SYSTEM = """You are an expert industrial knowledge assistant.
Answer questions using ONLY the provided document excerpts.
Always cite your sources using [Document: filename, Page: N] format.
If the context doesn't contain enough information, say so clearly.
Never invent facts not present in the context."""

def query_stream(user_query: str) -> Generator[dict, None, None]:
    # 1. Extract equipment tags from query (simple regex)
    import re
    tags = re.findall(r'\b[A-Z]{1,3}-\d{2,4}\b', user_query)

    # 2. Get linked doc IDs from graph if tags found
    doc_filter = None
    if tags:
        doc_filter = get_linked_doc_ids(tags)

    # 3. Hybrid retrieval
    chunks = reciprocal_rank_fusion(user_query, doc_id_filter=doc_filter)

    # 4. Build context string with source labels
    context_parts = []
    sources = []
    for i, chunk in enumerate(chunks):
        meta = chunk["metadata"]
        label = f"[Source {i+1}: {meta['filename']}, Page {meta['page']}]"
        context_parts.append(f"{label}\n{chunk['document']}")
        sources.append({
            "label": f"Source {i+1}",
            "filename": meta["filename"],
            "page": meta["page"],
            "section": meta.get("section", ""),
            "doc_id": meta["doc_id"]
        })

    context = "\n\n---\n\n".join(context_parts)
    prompt  = f"Context:\n{context}\n\nQuestion: {user_query}"

    # 5. Stream answer tokens
    for token in chat_stream(RAG_SYSTEM, prompt):
        yield {"token": token, "done": False}

    # 6. Send sources as final payload
    yield {"token": "", "done": True, "sources": sources}
```

---

### `routers/chat.py` — Streaming SSE endpoint

```python
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from agents.rag_agent import query_stream
import json

router = APIRouter(prefix="/api/chat")

class QueryRequest(BaseModel):
    query: str
    mode: str = "detailed"

@router.post("/query")
async def chat_query(req: QueryRequest):
    def event_generator():
        for payload in query_stream(req.query):
            yield f"data: {json.dumps(payload)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # disable nginx buffering
        }
    )
```

---

### `hooks/useSSEStream.ts` — React SSE consumer

```typescript
import { useState, useCallback } from "react";

interface StreamSource {
  label: string;
  filename: string;
  page: number;
  section: string;
  doc_id: string;
}

export function useSSEStream() {
  const [text, setText]       = useState("");
  const [sources, setSources] = useState<StreamSource[]>([]);
  const [loading, setLoading] = useState(false);

  const query = useCallback(async (userQuery: string) => {
    setText("");
    setSources([]);
    setLoading(true);

    const resp = await fetch("/api/chat/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: userQuery }),
    });

    const reader = resp.body!.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const lines = decoder.decode(value).split("\n");
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const payload = JSON.parse(line.slice(6));

        if (!payload.done) {
          setText(prev => prev + payload.token);
        } else {
          setSources(payload.sources ?? []);
          setLoading(false);
        }
      }
    }
  }, []);

  return { text, sources, loading, query };
}
```

---

### `ingestion/entity_extractor.py` — Entity extraction from chunks

```python
from core.ollama_client import chat_json

EXTRACTION_SYSTEM = """You are an industrial document parser.
Extract named entities from the given text.
Return ONLY valid JSON. No explanation. No markdown fences."""

EXTRACTION_TEMPLATE = """Extract all entities from this industrial document excerpt.
Return JSON exactly in this format:
{{
  "equipment_tags":    [],   // e.g. ["P-101", "V-205"]
  "instrument_tags":  [],   // e.g. ["FIC-201", "TT-105"]
  "dates":            [],   // ISO format strings
  "personnel":        [],   // engineer/technician names
  "measurements":     [],   // e.g. [{{"tag":"pressure","value":12.5,"unit":"bar"}}]
  "regulatory_refs":  [],   // e.g. ["OISD Std 117 Clause 8.3.2"]
  "failure_modes":    []    // e.g. ["mechanical seal failure", "bearing overheating"]
}}

Text:
{chunk}"""

def extract_entities(chunk: str) -> dict:
    prompt = EXTRACTION_TEMPLATE.format(chunk=chunk[:3000])  # cap token usage
    try:
        result = chat_json(EXTRACTION_SYSTEM, prompt)
        return result
    except Exception:
        # return empty structure on parse failure — ingestion continues
        return {
            "equipment_tags": [], "instrument_tags": [], "dates": [],
            "personnel": [], "measurements": [], "regulatory_refs": [], "failure_modes": []
        }
```

---

## 17. Knowledge Graph — Cypher Reference

### Queries used by the application

```cypher
-- Get all events for an equipment tag (timeline)
MATCH (e:Equipment {tag: $tag})-[:COVERED_BY]->(i:Inspection)
RETURN i.date, i.findings, i.doc_id
ORDER BY i.date DESC

-- Get all documents mentioning an equipment tag
MATCH (d:Document)-[:MENTIONS]->(e:Equipment {tag: $tag})
RETURN d.filename, d.doc_type, d.date_ingested

-- Find equipment with most failure modes (for risk ranking)
MATCH (e:Equipment)-[r:HAS_FAILURE_MODE]->(f:FailureMode)
RETURN e.tag, count(f) AS failure_count
ORDER BY failure_count DESC
LIMIT 10

-- Get downstream equipment from a given tag (from P&ID connections)
MATCH (e:Equipment {tag: $tag})-[:CONNECTED_TO*1..3]->(downstream:Equipment)
RETURN DISTINCT downstream.tag, downstream.name

-- Find equipment missing inspection coverage (compliance gap)
MATCH (e:Equipment)
WHERE NOT (e)<-[:COVERS]-(:Inspection {year: 2024})
RETURN e.tag, e.name

-- Get regulation clauses with no matching procedures
MATCH (r:Regulation)
WHERE NOT (r)-[:COVERED_BY]->(:Procedure)
RETURN r.id, r.clause, r.requirement
```

---

## 18. Evaluation Metrics — What to Measure and Show Judges

The hackathon evaluates on specific technical metrics. Prepare these numbers before demo day.

### Metric 1 — Query Answer Quality

Run 10 test queries over your pre-ingested demo documents before the hackathon. For each query:
- Note whether the answer is correct (based on what you know the document says)
- Note whether the citation is accurate (page number matches)
- Target: >80% correct answers with valid citations

Present this as: "We tested 10 domain-expert queries. 9 of 10 answers were correct with valid source citations."

### Metric 2 — Time-to-Answer

Measure from "send query" to "last token streamed":
- Hybrid retrieval: ~0.3 seconds
- LLM inference (first token): ~1.5 seconds
- Full answer (200 tokens): ~4–6 seconds

Present this as: "Average query answered in under 6 seconds on local GPU hardware."

### Metric 3 — Drawing Tag Extraction Accuracy

Test minicpm-v on your demo P&ID before the event:
- Count total visible tags manually
- Count correctly extracted tags
- Target: >85% recall on a clean 300 DPI drawing

Present as: "Drawing analysis extracted 34 of 38 equipment and instrument tags with no internet connection."

### Metric 4 — Compliance Coverage

Count how many OISD clauses are mapped vs total clauses in your regulatory corpus. Present as: "Compliance scanner covers X regulatory clauses across Y OISD standards."

### Metric 5 — Cross-Document Synthesis

Show a query whose answer requires pulling from at least 3 different documents. This is the hardest metric for any competing system to match. Prepare one such query in advance and rehearse the answer.

---

## 19. Potential Judge Questions & Answers

**"How is this different from just ChatGPT with file upload?"**
> ChatGPT's file analysis is single-session, single-file, and uses a cloud API. Our system ingests any number of documents permanently, builds a knowledge graph that links entities across all of them, runs entirely locally on-premise with no data leaving the facility, and can cross-reference a maintenance log with an inspection report with a P&ID drawing simultaneously. That cross-document reasoning is architecturally impossible in a simple file-upload chat.

**"What happens when the document corpus grows to thousands of files?"**
> The architecture scales horizontally. ChromaDB can be swapped for Qdrant or Weaviate without changing the retrieval logic. Neo4j AuraDB scales to millions of nodes on paid tiers. The Ollama local inference can be replaced with a vLLM server cluster. SQLite becomes PostgreSQL. The application code doesn't change — only the storage backends.

**"How do you handle hallucinations?"**
> Three mechanisms: (1) the system prompt strictly instructs the model to answer only from provided context and say "I don't know" otherwise. (2) Every answer includes source citations — the user can verify any claim in one click. (3) Confidence scoring based on retrieval score spread — low-confidence answers are flagged explicitly rather than presented with false certainty.

**"Why local models instead of GPT-4 or Gemini?"**
> Industrial facilities often have strict data governance policies — maintenance records, P&IDs, and inspection reports contain proprietary plant data that cannot be sent to external APIs. Running inference locally means zero data egress, compliance with data residency requirements, and no per-query API costs at scale. This is not a limitation — it's a feature that makes the system deployable in real industrial environments.

**"What's the accuracy of the P&ID vision extraction?"**
> On a clean 300 DPI P&ID with standard ISA symbols, minicpm-v achieves approximately 85–90% tag recall. For production use, this would be combined with a human-in-the-loop review step where extracted tags are confirmed before being written to the knowledge graph. The system is designed to assist the expert, not replace the verification step.

---

## 20. Scalability Roadmap (for the architecture slide)

Show judges the production path — this proves the system isn't just a hackathon prototype.

```
HACKATHON (today)              PILOT (3 months)           PRODUCTION (12 months)
─────────────────              ────────────────           ──────────────────────
Ollama local GPU          →    vLLM server cluster   →    Fine-tuned domain model
ChromaDB local disk       →    Qdrant distributed    →    Qdrant + caching layer
SQLite file               →    PostgreSQL RDS        →    PostgreSQL + read replicas
Neo4j AuraDB Free         →    Neo4j AuraDB Pro      →    Neo4j Enterprise cluster
FastAPI single process    →    FastAPI + Celery       →    Kubernetes + HPA
React localhost           →    Vercel / Nginx         →    Private cloud deployment
Manual doc upload         →    API integrations       →    Real-time SCADA/ERP feeds
```

The codebase supports this progression through environment variables and pluggable backends — no architectural rewrites required.

---

*Blueprint version 1.0 — ET AI Hackathon 2026*
*Platform: Industrial Knowledge Intelligence*
*Problem Statement 8 — Industrial Intelligence / Document Management / Knowledge Engineering*
*Hardware target: Ubuntu 22.04, 16GB RAM, Intel i7-13620H, Nvidia RTX 4060 8GB*
*Total API cost: Rs 0 — 100% local inference via Ollama*
