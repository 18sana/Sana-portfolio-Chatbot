# Deploy: Vercel + Render + Supabase (+ Gemini)

Target stack:

```
Browser → Vercel (Next.js)
              │
              ▼
         Render (FastAPI Docker)
              │
              ▼
         Supabase Postgres (+ pgvector)
```

Redis is optional (in-memory rate limits on one Render instance).

---

## 1. Supabase (database)

1. Create a project at [supabase.com](https://supabase.com).
2. **SQL Editor** → run:
   ```sql
   create extension if not exists vector;
   ```
3. **Project Settings → Database** → copy the connection string.
4. Convert to async SQLAlchemy form:
   - From: `postgresql://postgres:...@db.xxxxx.supabase.co:5432/postgres`
   - To:   `postgresql+asyncpg://postgres:...@db.xxxxx.supabase.co:5432/postgres`
5. Prefer the **Session / direct** host for Alembic migrations (not the pooler) if migrations hang.
6. If the password has special characters, URL-encode them (`@` → `%40`, etc.).

---

## 2. Render (backend)

1. New → **Web Service** → connect this repo.
2. Settings:
   - **Root Directory:** `backend`
   - **Runtime:** Docker (`backend/Dockerfile`)
   - **Health check path:** `/health`
3. Environment variables (set in Render dashboard — never commit secrets):

| Key | Value |
|-----|--------|
| `DATABASE_URL` | Supabase URL with `postgresql+asyncpg://...` |
| `GOOGLE_API_KEY` | Your Gemini / Google AI Studio key |
| `ADMIN_API_KEY` | Long random secret (`openssl rand -hex 32`) |
| `CORS_ORIGINS` | `https://YOUR_APP.vercel.app` (add custom domain later) |
| `LLM_PROVIDER` | `gemini` |
| `LLM_MODEL` | `gemini-3.6-flash` |
| `EMBEDDING_PROVIDER` | `gemini` |
| `EMBEDDING_MODEL` | `gemini-embedding-001` |
| `EMBEDDING_DIMENSIONS` | `1536` |
| `APP_ENV` | `production` |
| `REDIS_URL` | leave empty / omit |

The container runs `alembic upgrade head` then Uvicorn on `$PORT`.

4. Deploy → open `https://YOUR_SERVICE.onrender.com/health`  
   Expect `postgres: ok` (redis may be `unavailable` — fine).

---

## 3. Vercel (frontend)

1. Import the same repo in Vercel.
2. **Root Directory:** `frontend`
3. Env:

| Key | Value |
|-----|--------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://YOUR_SERVICE.onrender.com` |
| `NEXT_PUBLIC_APP_NAME` | `Sana Asiwal` |

4. Deploy → open the Vercel URL and test Chat / Fit / Meet / Inbox.

After you get the Vercel URL, update Render `CORS_ORIGINS` to match exactly (no trailing slash).

---

## 4. After deploy — load your knowledge base

Chat is empty until you ingest docs:

1. Create profile (once):

```bash
curl -X POST "$API/admin/profile" \
  -H "X-Admin-Api-Key: $ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Sana Asiwal","headline":"Software Developer","email":"sanaasiwal18@gmail.com","location":"Indore, India"}'
```

2. Save the returned `id`, then upload resume:

```bash
curl -X POST "$API/admin/documents" \
  -H "X-Admin-Api-Key: $ADMIN_API_KEY" \
  -F "profile_id=PROFILE_UUID" \
  -F "title=Resume" \
  -F "source_type=resume" \
  -F "file=@/path/to/resume.pdf"
```

Upload project write-ups the same way with `source_type=project`.

Private inbox: `https://YOUR_APP.vercel.app/inbox` + `ADMIN_API_KEY`.

---

## 5. Gemini notes

- Use a key from [Google AI Studio](https://aistudio.google.com/apikey).
- Embeddings use `gemini-embedding-001` at **1536** dims to match the DB schema.
- If chat fails with auth errors, regenerate the key and update Render env (do not paste keys into GitHub/chat).

---

## Checklist

- [ ] Supabase `vector` extension enabled
- [ ] Render `/health` → postgres ok
- [ ] Vercel `NEXT_PUBLIC_API_BASE_URL` points at Render
- [ ] Render `CORS_ORIGINS` includes Vercel URL
- [ ] Profile + resume ingested
- [ ] Chat streams on production
- [ ] `/inbox` unlocks with admin key
