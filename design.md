# IKIP Frontend Design Document

**Industrial Knowledge Intelligence Platform — Frontend Architecture & Design Reference**

---

## 1. Overview

IKIP is a React + TypeScript single-page application built on **Vite** with **Tailwind CSS v4**. It serves as the operational dashboard for engineers and compliance officers interacting with an AI-powered industrial knowledge base. The UI presents a professional, data-dense interface inspired by industrial control dashboards — clean, readable, and information-forward.

---

## 2. Technology Stack

| Layer | Technology |
|---|---|
| Framework | React 19 |
| Language | TypeScript ~6.0 |
| Build Tool | Vite 8 |
| Routing | React Router DOM v7 |
| Styling | Tailwind CSS v4 (`@import "tailwindcss"`) |
| Typography plugin | `@tailwindcss/typography` |
| Icons | Lucide React |
| Graph Visualization | `react-force-graph-2d` + `d3-force` |
| Markdown Rendering | `react-markdown` + `remark-gfm` + `remark-breaks` |
| Linter | OxLint |

---

## 3. Design Philosophy

The visual language of IKIP is built around three principles:

1. **Industrial Clarity** — High information density without visual clutter. Every element earns its place.
2. **Semantic Color** — Colors carry real-world meaning (operational/warning/critical), not arbitrary decoration.
3. **Dual-Mode Fidelity** — Both light and dark modes are first-class; neither is an afterthought.

---

## 4. Color System

Colors are defined as CSS custom properties in `src/index.css` under `@layer base` and surfaced to Tailwind through a `@theme` block. There are two themes: a **Premium Industrial Light Mode** (default) and a **Glassmorphic Dark Mode**.

### Light Mode (`:root`)

| Token | Hex | Role |
|---|---|---|
| `--surface` | `#f8fafc` | Page background |
| `--surface-alt` | `#f1f5f9` | Sidebar, cards, panels |
| `--surface-raised` | `#ffffff` | Elevated elements (modal, input) |
| `--surface-hover` | `#e2e8f0` | Interactive hover state |
| `--border` | `#cbd5e1` | Subtle dividers |
| `--border-active` | `#94a3b8` | Focused / active borders |
| `--text` | `#0f172a` | Primary body text |
| `--text-muted` | `#475569` | Secondary labels |
| `--text-dim` | `#94a3b8` | Tertiary, timestamps, hints |
| `--primary` | `#0284c7` | Brand accent, links, active states |
| `--primary-muted` | `#e0f2fe` | Primary tint backgrounds |
| `--operational` | `#059669` | System OK / Compliant |
| `--warning` | `#d97706` | Attention needed / Partial |
| `--critical` | `#dc2626` | Failure / Gap / Error |
| `--data` | `#4f46e5` | Knowledge graph / data-heavy UI |

### Dark Mode (`.dark`)

| Token | Hex | Role |
|---|---|---|
| `--surface` | `#0a0e1a` | Deep navy page background |
| `--surface-alt` | `#111827` | Panel backgrounds |
| `--surface-raised` | `#1a2035` | Elevated cards |
| `--surface-hover` | `#1e2a3f` | Hover state |
| `--border` | `#1e293b` | Subtle borders |
| `--border-active` | `#334155` | Active/focus borders |
| `--text` | `#e2e8f0` | Primary text |
| `--text-muted` | `#64748b` | Secondary |
| `--text-dim` | `#475569` | Tertiary |
| `--primary` | `#22d3ee` | Cyan accent |
| `--primary-muted` | `#0e7490` | Tint backgrounds |
| `--operational` | `#10b981` | Green |
| `--warning` | `#f59e0b` | Amber |
| `--critical` | `#ef4444` | Red |
| `--data` | `#818cf8` | Indigo-lavender for graph |

> **Theme toggling** is managed in `App.tsx` via a `useState<'light' | 'dark'>` that adds/removes the `.dark` class from `document.documentElement`. A Moon/Sun toggle button lives in the `Header`.

---

## 5. Typography

| Token | Value |
|---|---|
| `--font-sans` | `'Inter', system-ui, sans-serif` |
| `--font-mono` | `'JetBrains Mono', 'Fira Code', monospace` |

- **Sans-serif** (`Inter`) is used for all UI chrome, labels, and body copy.
- **Monospace** (`JetBrains Mono`) is used for technical values: equipment tag IDs, chunk counts, version numbers, and compliance scores.
- Font is applied globally via `body { @apply font-sans antialiased; }`.

---

## 6. Layout Architecture

The app uses a **fixed full-height shell** with no page scrolling at the root level. Scrolling is isolated inside individual page content areas.

```
┌─────────────────────────────────────────────────────────┐
│  <Sidebar> w-64             │  <Header> h-14             │
│  ─────────────────          │  ──────────────────────    │
│  Brand (IKIP + Hexagon)     │  Page Title + Subtitle     │
│                             │  [Status] [Moon] [Bell] ⚙  │
│  OPERATIONS                 ├────────────────────────────│
│  ▸ Intelligence Chat        │                            │
│  ▸ Document Base            │   <main> (flex-1 overflow) │
│  ▸ Knowledge Graph          │                            │
│                             │   Route-rendered page      │
│  ANALYSIS                   │   component fills here     │
│  ▸ Drawing Analysis         │                            │
│  ▸ Compliance               │                            │
│  ─ Maintenance (Soon)       │                            │
│                             │                            │
│  ● Ollama: Connected  v0.1  │                            │
└─────────────────────────────┴────────────────────────────┘
```

### Sidebar (`components/layout/Sidebar.tsx`)
- **Width:** `w-64` (fixed, non-collapsible at present)
- **Brand area:** `Hexagon` icon (Lucide) + "IKIP" wordmark + subtitle
- **Navigation sections:** "Operations" and "Analysis" — each prefixed with a `10px` uppercase tracking label
- **Active state:** `border-l-2 border-primary bg-primary/5 text-primary font-medium`
- **Inactive state:** `border-l-2 border-transparent text-text-muted hover:text-text hover:bg-surface-hover`
- **Disabled items** (e.g., Maintenance): `opacity-40 cursor-not-allowed` + a `"Soon"` badge
- **Footer:** Live `● Ollama: Connected` status dot + version string

### Header (`components/layout/Header.tsx`)
- **Height:** `h-14` with `border-b border-border`
- **Left:** Dynamic page title/subtitle derived from `useLocation()` against a `pageTitles` lookup map
- **Right:** System status indicator, theme toggle, notification bell, settings icon
- Status indicator is a `w-2 h-2 rounded-full bg-operational` green dot + "System Online" label

---

## 7. Routing & Pages

| Route | Component | Description |
|---|---|---|
| `/` | → redirect to `/chat` | Default landing |
| `/chat` | `ChatPage` | AI query interface |
| `/documents` | `DocumentManager` | Knowledge base file manager |
| `/graph` | `GraphExplorer` | Interactive force-directed knowledge graph |
| `/drawings` | `DrawingViewer` | P&ID / PFD analysis viewer |
| `/compliance` | `ComplianceDashboard` | Regulatory compliance gap scanner |

---

## 8. Pages — Design Details

### 8.1 Intelligence Chat (`/chat`)

**Empty State**
- Centered layout with a large faded `Hexagon` icon (`opacity-20`)
- Headline: "Industrial Knowledge Intelligence"
- 3 suggested query buttons: pill-shaped cards with hover `border-primary/50 bg-primary/5`

**Active Chat**
- Scrollable message feed (`space-y-6`)
- **User messages**: right-aligned, `bg-surface-raised border-border rounded-2xl rounded-tr-sm`
- **Assistant messages**: left-aligned, `bg-surface-alt border-border rounded-2xl rounded-tl-sm`, preceded by a `Terminal` icon avatar in a `bg-primary/10 border-primary/20` square badge
- Markdown rendered via `react-markdown` with `remarkGfm` + `remarkBreaks`
- Citations rendered via `CitationLink` component (custom `<a>` override)
- Source documents listed below message via `SourcesList`
- **Streaming state**: Live token-by-token text via `StreamingText` with a "generating..." sub-label

**Input Bar** (sticky bottom)
- Full-width rounded input field: `bg-surface border-border rounded-xl py-3.5`
- Focus ring: `focus:border-primary/50 focus:ring-1 focus:ring-primary/20`
- Action buttons inside input: `Mic` (voice, Phase 4 placeholder) + `Send` (`bg-primary text-surface`)
- Disabled state when streaming: `opacity-50`

---

### 8.2 Document Base (`/documents`)

**Stats Bar** — 4 metric cards in a `grid grid-cols-4` layout:
- Total Documents, Data Chunks, Complete (green), Processing (amber)
- Values in `font-mono text-2xl`; labels in `text-[10px] uppercase tracking-wider`

**Upload Dropzone** (`UploadDropzone.tsx`)
- `border-2 border-dashed rounded-xl` area
- Drag-active: `border-primary bg-primary/5 scale-[1.01]`
- Idle: `border-border bg-surface-alt/30 hover:border-primary/30`
- Accepts: PDF, DOCX, XLSX, PNG, JPG (multi-file)
- Auto-classification badge shown above the zone

**Document Table**
- 12-column CSS grid: `[5] Filename | [3] Status | [2] Chunks | [2] Actions`
- Sticky header with `shadow-sm z-10`
- Bulk selection via custom checkboxes (`bg-primary border-primary` when checked)
- Status badges as `rounded-full` inline pills: Complete (operational/green), Processing (warning/amber + animated spin), Queued (dim), Failed (critical/red)
- Delete action: hover-to-red trash icon (`hover:text-critical hover:bg-critical/10`)

---

### 8.3 Knowledge Graph (`/graph`)

- **Full canvas**: `react-force-graph-2d` fills the entire page area; layout is `h-full` with no padding
- **Toolbar** (top bar): Graph title + entity type legend (color-coded dots)
- **Filter panel** (`GraphFilters.tsx`): Toggle visibility of node label categories
- **Node colors** by entity label:
  - Equipment → `#818cf8` (indigo/data)
  - Event → `#ef4444` (critical red)
  - Date → `#f59e0b` (warning amber)
  - Other → `#22d3ee` (cyan/primary-dark)
- **Labels**: Only shown at zoom >= 1.5 to prevent clutter
- **Link arrows**: directional, `length=3.5`
- **Click behavior**: Centers and zooms to node (zoom level 8, 2s), opens `NodePanel` side drawer
- **NodePanel** (`NodePanel.tsx`): Slide-in overlay panel showing node metadata and relationships

---

### 8.4 Drawing Vision Analysis (`/drawings`)

Layout: **Left panel (flex-1) + Right panel (w-96)**

**Left panel — Metadata strip + Viewer**
- Metadata strip: Drawing No. (monospace primary color), Revision, Unit/Area — `text-[10px] uppercase tracking-wider` labels
- AI System Analysis block: `bg-primary/5 border-primary/20 rounded-lg` card with `Target` icon and markdown-rendered narrative
- Drawing image: renders PNG from `/uploads/{drawing_id}.png`, falls back to `.jpg` on error

**Right panel — Extracted Components**
- Header: `Target` icon + count badge `bg-primary/10 text-primary`
- Per-component cards: `font-mono font-bold` tag + `uppercase` type badge
- "Known in Graph" indicator: `bg-operational/10 text-operational` badge with `CheckCircle2`
- Cross-link: "View in Graph Explorer" anchor for known entities
- **Drawing selector**: `<select>` dropdown (top-right) filtered to `p&id`, `pfd`, `pid` document types with status `complete`

---

### 8.5 Compliance Gap Scanner (`/compliance`)

Layout: **Left 1/3 (config + history) + Right 2/3 (report)**

**Left — Scan Configuration**
- `ShieldAlert` icon header
- Standard selector: OISD Standard 117, Factory Act 1948
- Document filter: All / Manuals / Procedures / Inspection Reports
- **Run Scan button**: `bg-primary/10 text-primary border-primary/20` with `Play` icon; shows `Loader2 animate-spin` when scanning
- Recent Scans list: Up to 5 entries persisted in `localStorage`. Each shows standard name + date + score (color-coded by threshold)

**Right — Report View**

*Empty state:* Centered `ShieldAlert` icon + instructional copy

*Scanning state:* Large `Loader2 animate-spin text-primary` with status copy

*Error state:* `bg-critical/10 border-critical/20` error card with `AlertTriangle` icon

*Report state (active):*
- **Score dial**: SVG radial progress ring. Ring color interpolates: green >=85%, amber >=60%, red <60%
- **Score value** displayed in center using `font-mono text-3xl font-bold`
- **Metadata chips**: Scanned document count + scan date
- **Clause accordion list** (`space-y-3`):
  - Each clause is a collapsible card (`ChevronRight` → `ChevronDown`)
  - Status badge: `bg-operational/10` (Compliant / N/A), `bg-warning/10` (Partial), `bg-critical/10` (Gap) with matching icon
  - Expanded view sections: Finding Summary, Cited Evidence (monospace source + quoted excerpt), Required Action (amber warning box with `AlertTriangle`)
- **Export PDF** button: top-right, `Download` icon — opens `/api/compliance/report/{id}/pdf` in new tab

---

## 9. Scrollbar Styling

Custom thin scrollbars for the industrial aesthetic:

```css
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border-active); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-dim); }
```

---

## 10. Component Inventory

```
src/
├── App.tsx                          # Root shell, theme state, routing
├── index.css                        # Design tokens + global base styles
│
├── components/
│   ├── layout/
│   │   ├── Header.tsx               # Top bar, page title, theme toggle
│   │   └── Sidebar.tsx              # Nav, brand, status footer
│   │
│   ├── chat/
│   │   ├── ChatPage.tsx             # Full chat UI container + input bar
│   │   ├── MessageList.tsx          # Message thread renderer
│   │   ├── StreamingText.tsx        # Live SSE text display
│   │   ├── CitationLink.tsx         # Custom <a> for inline source citations
│   │   └── SourcesList.tsx          # Source document chip list below messages
│   │
│   ├── documents/
│   │   ├── DocumentManager.tsx      # Stats + table + bulk actions
│   │   └── UploadDropzone.tsx       # Drag-and-drop file uploader
│   │
│   ├── graph/
│   │   ├── GraphExplorer.tsx        # Force-directed graph canvas
│   │   ├── GraphFilters.tsx         # Node label filter toggles
│   │   └── NodePanel.tsx            # Click-to-inspect node detail panel
│   │
│   ├── drawings/
│   │   └── DrawingViewer.tsx        # P&ID viewer + component extraction panel
│   │
│   └── compliance/
│       └── ComplianceDashboard.tsx  # Compliance scan UI + clause accordion
│
├── api/
│   └── client.ts                    # fetchJson helper (base URL: localhost:8000/api)
│
├── hooks/
│   └── useSSEStream.ts              # Server-Sent Events streaming hook for chat
│
└── types/
    ├── chat.ts                      # ChatMessage type
    └── document.ts                  # DocumentItem type
```

---

## 11. Design Patterns & Conventions

### Card Style
Standard raised surface card:
```
bg-surface-alt border border-border rounded-xl p-5 shadow-sm
```

### Status Badges (pill)
```
inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-medium
bg-{color}/10 text-{color} border border-{color}/20
```

### Section Labels
```
text-[10px] font-semibold uppercase tracking-[0.15em] text-text-dim
```

### Empty States
Centered icon (`opacity-20`) + heading + descriptive paragraph. Consistent across all pages.

### Loading States
`Loader2 animate-spin` from Lucide, sized contextually (`32px` for panels, `48px` for full-page).

### Interactive Elements
All interactive elements use `transition-colors` or `transition-all`. Hover states use either `hover:bg-surface-hover` for neutral or `hover:bg-primary/5 hover:border-primary/30` for primary-accented interactions.

### Error States
`bg-critical/10 text-critical border border-critical/20 rounded-xl` with `AlertTriangle` icon.

---

## 12. Planned / Future Sections

| Page | Status | Notes |
|---|---|---|
| Maintenance | Soon | Sidebar stub exists, route not yet created |
| Voice Input | Phase 4 | `Mic` button present in chat input, non-functional |
| Settings Page | TBD | Settings icon in header — no route yet |

---

## 13. Key Design Decisions

- **No page-level scroll** — The root layout is `flex h-screen overflow-hidden`. Each page component manages its own scrollable regions, keeping the sidebar and header always visible.
- **Semantic tokens over raw values** — All colors are referenced via CSS custom property tokens (e.g., `text-operational`, `bg-critical/10`). This makes theme switching trivial and keeps the palette consistent.
- **Monospace for data** — Any numeric or machine-generated value (tag IDs, scores, chunk counts, version strings) uses `font-mono` to visually distinguish data from prose.
- **Progressive disclosure in Compliance** — The accordion model prevents information overload; users expand only the clauses they care about.
- **Tailwind v4** — Uses the new `@import "tailwindcss"` + `@theme {}` syntax instead of `tailwind.config.js`.
