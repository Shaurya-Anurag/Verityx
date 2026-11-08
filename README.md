# Verityx

**Trust is not default.** Question. Verify. Understand.

Verityx is an independent freshness-verification product. It will identify time-sensitive claims, retrieve current evidence, compare claims with evidence, and explain whether they are current, potentially stale, contradicted, or unresolved.

## Current status

The first release is a responsive React + TypeScript + Vite frontend shell. It includes the Verityx visual identity, classical statue hero artwork, claim-entry interface, freshness overview, recent-analysis area, evidence timeline, system-status panel and illustrative claim records.

The frontend is currently a visual/product shell. It does **not** yet perform live claim extraction, Tavily searches or Bifrost inference. Preview records are explicitly marked illustrative; no fake freshness scores are shown.

## Run

Requirements: Node.js 20+.

```bash
cd frontend
npm install
npm run dev
```

Build with `npm run build`.

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
