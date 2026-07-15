# Industrial Knowledge Intelligence Platform - Frontend

This is the frontend client for the Industrial Knowledge Intelligence Platform, built with React 19, Vite, TypeScript, and Tailwind CSS.

## Key Modules

- **Chat Interface**: Located in `src/components/chat/`. Implements real-time Markdown streaming and custom citation handling (`[1](#source-1)`).
- **Document Manager**: Located in `src/components/documents/`. Handles Drag-and-Drop uploads, isolating standard regulations from operational data.
- **Compliance Dashboard**: Located in `src/components/compliance/`. Interacts with the backend to trigger and poll clause-by-clause standard audits.
- **Knowledge Graph Explorer**: Located in `src/components/graph/`. Uses D3 or React Flow to visualize entity relationships pulled from Neo4j.

## Development Server

To run the frontend locally:

```bash
# 1. Install dependencies
npm install

# 2. Run the Vite dev server
npm run dev
```

The application will be available at `http://localhost:5173`.

## Styling & Theming

The platform implements a highly polished, professional "BHEL" industrial theme:
- The design system tokens (colors, radii, shadows) are defined in `src/index.css`.
- We use Tailwind CSS v4 alongside `@tailwindcss/typography` for rich chat prose rendering.
- Ensure strict adherence to the defined CSS variables (`--color-primary`, `--color-surface`, etc.) to maintain the premium dark/light mode experience.
