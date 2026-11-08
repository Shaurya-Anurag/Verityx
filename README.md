# Verityx

**Trust is not default.** Question. Verify. Understand.

Verityx is an independent freshness-verification product. It will identify time-sensitive claims, retrieve current evidence, compare claims with evidence, and explain whether they are current, potentially stale, contradicted, or unresolved.

## Current status

The app now includes a React + TypeScript dashboard and a FastAPI backend with Tavily evidence retrieval, optional Bifrost-assisted assessment, SQLite analysis history, monitor watchlists, document text extraction, audit log, insights and integration health checks.

Live evidence retrieval requires a Tavily API key. Semantic claim assessment requires a configured Bifrost OpenAI-compatible endpoint and model. Without Bifrost, Verityx stores retrieved evidence but returns `insufficient_evidence` rather than fabricating a verdict. Monitor definitions persist, but scheduled rechecks are not yet implemented.

## Run

Requirements: Node.js 20+.

```bash
cd frontend
npm install
npm run dev
```

Build with `npm run build`.\n\n## Backend\n\nSee [backend/README.md](backend/README.md). Create `backend/.env` from `.env.example`, install `backend/requirements.txt`, then run `uvicorn app.main:app --reload --port 8030` from the `backend/` directory. API docs: `http://127.0.0.1:8030/docs`.

## Planned architecture

- `frontend/`: React application (current).
- `backend/`: FastAPI API, claim extraction, freshness classification, evidence retrieval, scoring and persistence (next).
- `integrations/vulnflow/`: thin adapter for VulnFlow.

Dependency direction: `VulnFlow -> Verityx`. The Verityx core must never import VulnFlow modules.

## Integrations

- **Bifrost:** model gateway for structured claim extraction and evidence synthesis.
- **Tavily:** live evidence retrieval.
- **VulnFlow:** optional downstream consumer through a versioned integration boundary.

## Classification principles

- **Current:** current evidence supports the claim within its relevant time window.
- **Potentially stale:** the claim is time-sensitive and evidence indicates it may have changed or needs rechecking.
- **Contradicted:** credible current evidence conflicts with the claim. This is not automatically the same as stale.
- **Insufficient evidence:** available sources do not support a defensible conclusion.

A freshness score is not a probability that a claim is true. Every assessment must expose evidence, timestamps, source quality and reasons.

## Brand

Ink/charcoal surfaces, warm parchment typography, burnt vermilion accent, editorial serif headlines, neutral sans-serif UI, monospaced evidence metadata, classical marble and archival textures.

## License

Not selected yet.
