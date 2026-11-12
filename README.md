# Verityx

**Trust is not default.** Question. Verify. Understand.

Verityx is an independent freshness-verification product. It will identify time-sensitive claims, retrieve current evidence, compare claims with evidence, and explain whether they are current, potentially stale, contradicted, or unresolved.

## Current status

The app includes a React + TypeScript dashboard and a FastAPI backend with Tavily evidence retrieval, optional Bifrost-assisted assessment, SQLite analysis history, monitor watchlists, document text extraction, an audit log, insights and integration health checks.

Live evidence retrieval requires a Tavily API key. Semantic claim assessment requires a configured Bifrost OpenAI-compatible endpoint and model. Without Bifrost, Verityx stores retrieved evidence but returns `insufficient_evidence` rather than fabricating a verdict. Monitor definitions persist, but scheduled rechecks are not implemented.

## Run

Requirements: Node.js 20+ and Python 3.12+.

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

Production frontend build:

```bash
npm ci
npm run build
```

Backend:

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
# Create .env from .env.example and configure provider credentials.
uvicorn app.main:app --reload --port 8030
```

API docs: `http://127.0.0.1:8030/docs`.

## Validation

From `backend/`:

```bash
python -m compileall -q app
python -m unittest discover -s tests -v
```

GitHub Actions runs the frontend production build and backend contract tests on pushes and pull requests. The tests use mocked Bifrost responses; they do not require provider credentials.

## Integrations

- **Bifrost:** model gateway for structured claim extraction and evidence synthesis.
- **Tavily:** live evidence retrieval.
- **VulnFlow:** optional downstream consumer through a versioned integration boundary.

Dependency direction: `VulnFlow -> Verityx`. The Verityx core must never import VulnFlow modules.

## Classification principles

- **Current:** current evidence supports the claim within its relevant time window.
- **Potentially stale:** the claim is time-sensitive and evidence indicates it may have changed or needs rechecking.
- **Contradicted:** credible current evidence conflicts with the claim. This is not automatically the same as stale.
- **Insufficient evidence:** available sources do not support a defensible conclusion.

A freshness score is not a probability that a claim is true. Assessments should expose evidence, timestamps, source quality and reasons. The current model-assisted score is preliminary and requires further independent validation.

## Known limitations

- Monitor definitions are persisted, but there is no scheduler or automatic recheck worker.
- Document inspection currently extracts and previews supported UTF-8 text files (TXT, MD, CSV and JSON); it is not OCR or a full document-understanding pipeline.
- Assessment quality depends on retrieved evidence and the configured model. Provider availability and model latency affect analysis.
- A successful API response is not proof that a verdict is factually correct; review the cited evidence.

## Brand

Ink/charcoal surfaces, warm parchment typography, burnt vermilion accent, editorial serif headlines, neutral sans-serif UI, monospaced evidence metadata, classical marble and archival textures.

## License

Not selected yet.
