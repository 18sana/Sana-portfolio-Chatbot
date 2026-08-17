# Deployment guide (Phase 10)

GitHub Actions are deferred (no GitHub for now). Deploy manually with the pieces below.

## Local infra

```bash
docker compose up -d
cd backend && uv sync --extra dev && uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
cd ../frontend && pnpm dev
```

## Backend (Render / Railway)

1. Use `backend/Dockerfile`.
2. Set env from `backend/.env.example` (especially `DATABASE_URL`, `REDIS_URL`, `ADMIN_API_KEY`, LLM keys).
3. Run migrate on release: `alembic upgrade head`.
4. Health check: `GET /health`.

## Frontend (Vercel)

1. Root directory: `frontend`.
2. Build: `pnpm install && pnpm build`.
3. Env: `NEXT_PUBLIC_API_BASE_URL=https://<backend-host>`.

## Database (Neon / Supabase)

1. Enable `vector` extension.
2. Point `DATABASE_URL` to the pooled asyncpg URL (`postgresql+asyncpg://...`).
3. Run Alembic migrations from CI/release or a one-off job.

## Redis (Upstash)

Set `REDIS_URL` to the Upstash Redis URL. Rate limiting degrades to in-memory if Redis is down (single instance only).

## Post-deploy smoke checklist

- [ ] `/health` returns postgres/redis ok (or documents degradation)
- [ ] Admin profile create with `X-Admin-Api-Key`
- [ ] Document upload + chunk count > 0
- [ ] `/chat` SSE streams tokens
- [ ] `/jd-match` returns structured score
- [ ] Frontend loads, theme toggles, chat + JD panels work
- [ ] Swap `LLM_PROVIDER`/`LLM_MODEL`, restart, confirm `/chat` still works
