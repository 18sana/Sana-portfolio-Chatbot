# Deploying this stack (Vercel + Docker reality)

## Short answer

**Vercel does not run your Docker Compose stack.**  
Use Vercel for the **Next.js frontend only**. Run the **FastAPI backend + Postgres + Redis** elsewhere.

```
Browser
   │
   ▼
Vercel (frontend)  ──HTTPS──►  Render/Railway (FastAPI Docker)
                                    │
                         Neon/Supabase (Postgres+pgvector)
                         Upstash (Redis)
```

## Why not all-on-Vercel?

| Piece | Where | Why |
|---|---|---|
| Next.js UI | **Vercel** | Native fit; no Docker needed |
| FastAPI | **Render / Railway** (`backend/Dockerfile`) | Long-running Python, SSE streaming, Alembic |
| Postgres+pgvector | **Neon or Supabase** | Managed DB; enable `vector` |
| Redis | **Upstash** | Rate limits; Vercel/serverless-friendly URL |

Vercel is optimized for frontend/serverless Node — not for hosting Postgres containers or a persistent FastAPI+Docker Compose app.

## Frontend → Vercel

1. Push repo to GitHub (when you’re ready).
2. Import project in Vercel → Root Directory = `frontend`.
3. Build: `pnpm install && pnpm build` (auto-detected).
4. Env vars:
   - `NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com`
   - `NEXT_PUBLIC_APP_NAME=Sana Asiwal`
5. Deploy.

## Backend → Render or Railway

1. Use `backend/Dockerfile`.
2. Set env from `backend/.env.example` (especially keys + `DATABASE_URL` + `REDIS_URL` + `ADMIN_API_KEY` + `CORS_ORIGINS=https://your-app.vercel.app`).
3. Release command: `alembic upgrade head`
4. Health: `GET /health`

## Local Docker (dev only)

`docker compose` runs **Postgres + Redis** on your machine. Backend/frontend still run on the host. That Compose file is **not** what you deploy to Vercel.

## Checklist after deploy

- [ ] Frontend loads on `*.vercel.app`
- [ ] Browser network tab: `/chat` hits backend URL (not localhost)
- [ ] CORS allows the Vercel origin
- [ ] Admin upload + chat work with production keys
