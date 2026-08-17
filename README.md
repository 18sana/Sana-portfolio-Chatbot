# AI Portfolio Chatbot

Production-grade personal AI representative for recruiters: hybrid RAG, LangGraph orchestration, JD fit-matching, provider-portable LLMs, and a non-generic Next.js frontend.

**Status: Phases 0–10 implemented** (GitHub Actions deferred).  
**Blueprint:** [`docs/SYSTEM_PLAN.md`](docs/SYSTEM_PLAN.md) · **Design:** [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md) · **Deploy (this stack):** [`docs/DEPLOY_VERCEL_RENDER_SUPABASE.md`](docs/DEPLOY_VERCEL_RENDER_SUPABASE.md) · **Vercel notes:** [`docs/VERCEL_DEPLOY.md`](docs/VERCEL_DEPLOY.md)

## Quick start

```bash
# Infra
cp .env.example .env
docker compose up -d

# Backend
cd backend
cp .env.example .env   # set OPENAI_API_KEY / ADMIN_API_KEY
uv sync --extra dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd ../frontend
cp .env.example .env.local
pnpm install
pnpm dev
```

- API docs: http://localhost:8000/docs  
- App: http://localhost:3000  

## Provider swap (no code changes)

```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-5
ANTHROPIC_API_KEY=...
```

## Tests

```bash
cd backend && uv run pytest
cd frontend && pnpm test:e2e   # requires app running + playwright install
```

## Phase map

| Phase | Focus |
|---|---|
| 0 | Scaffold |
| 1 | LLM/Embedding providers + fallback |
| 2 | Models, Alembic, ingestion |
| 3 | Hybrid retrieval |
| 4 | LangGraph chat + groundedness |
| 5 | JD match + injection hardening |
| 6 | API, auth, rate limits, logging |
| 7 | Design system + UI |
| 8 | Security checklist |
| 9 | Evals + tracing hooks |
| 10 | Docker + deploy guides |
