# Verityx API

FastAPI service for evidence retrieval, AI-assisted freshness assessment, history and monitors.

## Setup
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8030
```
Edit .env and add TAVILY_API_KEY. For semantic assessment configure BIFROST_BASE_URL, BIFROST_API_KEY (if required), and BIFROST_MODEL. API docs at /docs.

Without Bifrost, Verityx retrieves and stores evidence but deliberately returns insufficient_evidence rather than inventing a verdict. Monitors are persisted watch definitions; automatic scheduled rechecks are not yet implemented.
