# AI Portfolio Chatbot — System Super Plan

> Living architecture + delivery blueprint.  
> Status: **Phases 0–10 implemented** · GitHub Actions deferred · Ops: start Docker, migrate, set API keys.  
> Repo: `~/ai-portfolio-chatbot` · No GitHub CI until you opt in.

---

## 1. Product vision

Build a **personal AI representative** that recruiters/HR talk to instead of skimming a PDF resume. It must:

1. Answer only from **your real documents** (resume, projects, achievements) — no invented employment history.
2. Accept a **job description** and return a structured fit report (score, matched skills, gaps, rationale).
3. Feel like a **portfolio product**, not a generic ChatGPT clone.
4. Be **provider-portable**: change LLM/embedding via env (API key + model id) with **zero business-logic edits**.
5. Be **production-grade**: auth on admin paths, rate limits, validation, prompt-injection hardening, observability, tests, deployable stack.

**North-star UX:** Visitor lands on a distinctive branded hero → opens chat as the primary interaction → can upload a JD and see a fit report → citations prove every claim.

---

## 2. Non-negotiable architecture principles

| Principle | Meaning in this system |
|---|---|
| Provider-agnostic core | All model I/O goes through `LLMProvider` / `EmbeddingProvider`. LiteLLM is an adapter, not the domain. |
| Env-only model swap | `LLM_PROVIDER` + `LLM_MODEL` (+ keys) change behavior. No `if provider == "openai"` in agents/API. |
| RAG, not context stuffing | Corpus lives in Postgres+pgvector; each turn retrieves top-k hybrid hits. |
| Structural groundedness | Post-generation verification node — not “please don’t lie” alone. |
| Orchestration as graphs | LangGraph for chat + JD subgraphs; explicit nodes, retries, streaming. |
| Fallback at the edge | Primary→fallback lives in provider factory/wrapper, never in route handlers. |
| Design before components | Phase 7 ships a signed-off design system before UI chrome. |
| Security by default | Uploaded JD/docs = untrusted data; admin endpoints keyed; rate limits real. |

---

## 3. What to use: RAG vs alternatives (decision)

### Recommended core: **Hybrid RAG + LangGraph agent**

| Approach | Use here? | Why |
|---|---|---|
| **Hybrid RAG** (dense + BM25/FTS) | **Yes — primary** | Portfolio corpus is small/medium, factual, needs citation. Hybrid beats pure vector on names, acronyms, exact skill strings. |
| Pure long-context stuffing | No as primary | Works for tiny resumes; breaks as projects/docs grow; weak citations; expensive; hard to update idempotently. |
| Fine-tuned model on your bio | Later optional | High cost/ops; stale quickly; still needs retrieval for new docs. Not MVP. |
| Knowledge graph (entities/relations) | **Phase 11+ optional** | Great for “who worked with X at Y” — overkill until corpus + query patterns justify it. |
| Multi-agent supervisor | Partial | Chat graph + JD subgraph is enough. Don’t add a swarm until tools multiply. |
| Agentic tool-use (web search, calendar) | **Out of scope for v1** | Portfolio bot should stay grounded in *your* docs, not the open web (hallucination + brand risk). |
| Reranker (cross-encoder / Cohere) | **Phase 3.5 / 9** | Worth adding when hybrid top-k is noisy; skip until evals show need. |

**Verdict:** Production path = **chunk → embed → hybrid retrieve → LangGraph generate → groundedness verify**, with JD as a separate structured subgraph. Same provider interfaces everywhere.

---

## 4. Target architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Next.js 15 (Vercel)                                            │
│  Design system · Chat (AI SDK SSE) · JD upload · Citations UI   │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS / SSE
┌────────────────────────────▼────────────────────────────────────┐
│  FastAPI (Render/Railway)                                       │
│  /chat (SSE) · /jd-match · /admin/* · /health                   │
│  Rate limit (Redis) · Auth (admin) · Validation · structlog     │
│                                                                 │
│  LangGraph                                                      │
│   Chat: retrieve → compose → generate(stream) → verify          │
│   JD:   sanitize → extract → retrieve profile → score → explain │
│                                                                 │
│  providers/  ← ONLY place that knows LiteLLM                    │
│   LLMProvider · EmbeddingProvider · Fallback* wrappers          │
└───────┬─────────────────────────┬─────────────────┬─────────────┘
        │                         │                 │
   Postgres+pgvector         Redis (Upstash)    LLM APIs via LiteLLM
   (Neon/Supabase)           cache + ratelimit  OpenAI/Anthropic/…
   profiles, docs, chunks,
   conversations, messages,
   jd_matches
```

### Backend module map (target)

```
backend/app/
  api/           # HTTP — thin
  core/          # config, logging, security, rate_limit
  providers/     # LLM/Embedding abstractions + LiteLLM + fallback
  db/            # SQLAlchemy models, session, repositories
  ingestion/     # extract → chunk → embed → upsert
  retrieval/     # hybrid search, optional rerank
  agents/        # LangGraph graphs, prompts, groundedness
  jd/            # JD subgraph + schemas
  evals/         # golden set harness (Phase 9)
  observability/ # Langfuse hooks (Phase 9)
```

---

## 5. Provider portability (your “never rewrite the system” requirement)

### Contract

```text
Business logic  →  LLMProvider / EmbeddingProvider
                      ↓
                 Factory (Settings from env)
                      ↓
                 LiteLLM adapter (+ Fallback wrapper)
                      ↓
                 Any LiteLLM-supported backend
```

### Env-only swap (examples)

```bash
# OpenAI
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-...

# Anthropic — same code paths
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-5
ANTHROPIC_API_KEY=sk-ant-...

# OpenRouter / local — use fully-qualified LiteLLM ids
LLM_PROVIDER=openrouter
LLM_MODEL=openrouter/auto
LLM_API_BASE=https://openrouter.ai/api/v1
```

Factory builds LiteLLM model id: `provider/model` (or trust `model` if it already contains `/`).

### Fallback chain (single place)

- `FallbackLLMProvider(primary, secondary)` in `providers/fallback.py`
- Factory wraps when `LLM_FALLBACK_*` set
- Call sites: **never** catch and retry another model
- Stream policy: fallback only if failure before first token

### Acceptance proof (Phase 1)

Automated test instantiates provider twice with different Settings/env → asserts `model_name` LiteLLM strings differ. Mock network. Manual `.env` flip is optional demo only.

---

## 6. Data model (Phase 2)

| Table | Purpose |
|---|---|
| `candidate_profile` | Canonical identity: name, headline, links, summary |
| `documents` | Source files (resume, project writeup); hash for idempotent re-ingest |
| `document_chunks` | Section-aware chunks + `embedding vector` + `tsvector` + metadata |
| `conversations` | Session threads |
| `messages` | Roles, content, citations JSON, token usage |
| `jd_matches` | Uploaded JD metadata + structured match result |

**Ingestion:** PDF (pymupdf) / DOCX / TXT → section-aware chunking → embed via `EmbeddingProvider` → upsert by content hash (no duplicate chunks on re-upload).

---

## 7. Feature catalog

### Tier A — Must ship (core product)

| Feature | Phase |
|---|---|
| Provider abstraction + fallback + env swap tests | 1 |
| Profile + document ingestion + migrations | 2 |
| Hybrid retrieval (pgvector + FTS) | 3 |
| Streaming chat agent + memory + groundedness | 4 |
| JD match subgraph + injection-safe prompts | 5 |
| Public API + admin CRUD + rate limits + logging | 6 |
| Distinctive UI: hero → chat → citations → JD report | 7 |
| Security hardening pass | 8 |
| Evals + cost/token logging + tracing hooks | 9 |
| Docker + deploy guides (Vercel / Render|Railway / Neon|Supabase / Upstash) | 10 |

### Tier B — Strong production extras (include in plan; schedule after A or late in A)

| Feature | Notes |
|---|---|
| Source citations in UI (expandable chunk quotes) | Phase 4 API + Phase 7 UI |
| Conversation share link / export transcript | Phase 6–7 |
| Admin document versioning + “last ingested” | Phase 2/6 |
| Soft rate limits + clear 429 UX | Phase 6–7 |
| Graceful degradation copy when LLM down | Phase 4/7 |
| Dark/light with intentional palette (not default purple AI) | Phase 7 |
| Playwright critical paths | Phase 7 |
| Golden-set regression evals in CI (when GitHub enabled) | Phase 9–10 |
| Langfuse-ready trace IDs | Phase 9 |

### Tier C — Differentiating (post-MVP, designed so they don’t force rewrites)

| Feature | Why later |
|---|---|
| Cross-encoder / hosted reranker | Add behind `retrieval/rerank.py` interface |
| Multi-lingual answers | Prompt + embedding model swap via env |
| Voice I/O | New channel adapter; same agents |
| Recruiter “leave contact” capture → email/webhook | New API + UI module |
| Analytics dashboard (top questions, JD themes) | Aggregates on `messages` / `jd_matches` |
| Multi-candidate / agency mode | Needs tenancy + RLS — explicit future fork |
| Knowledge-graph enrichment | Optional parallel index |
| A/B prompt versions | Feature flag + eval harness |
| Cached FAQ for ultra-common questions | Redis semantic cache in front of graph |

**Design rule for Tier C:** new capabilities = new modules + interfaces, not forks of provider/RAG core.

---

## 8. Chat agent (Phase 4) — behavior contract

```
retrieve_context → compose_prompt → generate_response (stream) → verify_groundedness
```

- **System prompt:** role = candidate’s AI representative; output format; failure modes; honesty rules (shown to you before freeze).
- **Memory:** recent window in Postgres + summary of older turns.
- **Groundedness:** secondary (cheap) model or heuristic claim-check against retrieved chunks.
  - **Recommended fallback on fail:** regenerate once with tighter “cite-only” constraint; if still fail → reply with partial answer + explicit disclaimer (better than silent fiction for recruiters).
- **Streaming:** async generator → SSE → Vercel AI SDK on frontend.

---

## 9. JD matching (Phase 5)

1. Upload PDF/DOCX/TXT (size/type limits).
2. Treat body as **untrusted**: delimiters, no instruction privilege.
3. Extract requirements (structured).
4. Embed + retrieve against profile chunks.
5. Structured output: `match_score`, `matched_skills[]`, `gaps[]`, `explanation`.
6. Adversarial test: JD containing “ignore previous instructions…” must not alter system behavior.

---

## 10. Frontend & design (Phase 7) — anti-generic mandate

**Do not ship:** unstyled shadcn defaults, purple-indigo AI gradient, Inter-on-white chatbot template, dashboard-of-cards hero, floating glassmorphism blobs.

**Do ship (sign-off before components):**

1. **Design system doc:** palette (CSS variables), type scale (expressive non-default fonts), spacing, motion tokens.
2. **One composition hero:** brand/name dominant, one pitch line, one CTA into chat, one real visual anchor (you / work / atmosphere — not abstract mesh).
3. **Chat as product surface:** typography-led transcript, streaming tokens, citation chips → expandable sources.
4. **JD report as distinct artifact:** score + skills/gaps layout — not a chat bubble dump.
5. Responsive + intentional dark mode.
6. Motion: 2–3 purposeful transitions (hero→chat, message appear, report reveal).

Design proposal is a **hard gate** before Phase 7 implementation.

---

## 11. Security, reliability, observability

| Concern | Approach |
|---|---|
| Admin auth | API key / bearer on `/admin/*` (Phase 6); public chat unauthenticated but rate-limited |
| Rate limits | Redis per-IP + per-session |
| Uploads | MIME allowlist, size cap, malware-safe parsing; JD/docs never concatenated as system instructions |
| Secrets | Server-only env; never in client bundle or logs |
| CORS | Explicit origin allowlist |
| Errors | Structured problem responses; no stack traces to clients |
| LLM outage | Provider fallback chain; user-visible soft error |
| Logging | structlog + request IDs |
| Tracing | Langfuse hooks ready; wire when keys present |
| Cost | LiteLLM usage on every completion; persist per message |
| Evals | Golden Q&A set; fail CI on groundedness/regression when enabled |

---

## 12. Tech stack (locked unless you request a change)

| Layer | Choice |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy async, Alembic, Pydantic v2, LangGraph, LiteLLM |
| DB | PostgreSQL 16 + pgvector |
| Cache | Redis (Upstash-compatible) |
| Frontend | Next.js 15 App Router, TS, Tailwind, Vercel AI SDK |
| Tests | pytest · Vitest/Playwright |
| Local | docker-compose (db + redis); backend/frontend on host |
| Deploy | Vercel · Render/Railway · Neon/Supabase · Upstash |
| CI | Deferred (no GitHub for now); add Actions in Phase 10 when you enable it |

---

## 13. Phased delivery plan

Each phase: **propose → your go-ahead → implement → manual test notes**. No skipping ahead.

| Phase | Deliverable | Exit criteria |
|---|---|---|
| **0** ✅ | Monorepo, compose, FastAPI health, Next skeleton | Health 200, frontend loads |
| **1** ✅ | Provider interfaces, LiteLLM, fallback, env-swap tests | Tests prove model string swap; fallback unit tests |
| **2** | Schema, Alembic, ingestion pipeline | Re-ingest idempotent; chunk tests |
| **3** | Hybrid retrieval | Known corpus query quality tests |
| **4** | LangGraph chat + stream + groundedness + memory | Stream works; verify node real |
| **5** | JD subgraph + injection test | Structured report; adversarial pass |
| **6** | Full API hardening | Auth, limits, validation, logging |
| **7** | Design system sign-off → UI | Playwright critical flows |
| **8** | Security pass | Checklist signed |
| **9** | Observability + evals | Golden set runnable |
| **10** | Deploy + smoke | Live URL checklist |
| **11+** | Tier C features | Behind interfaces; no core rewrite |

### Suggested calendar (indicative, not commitment)

- Phases 1–3: foundation (providers → data → retrieval)
- Phases 4–6: intelligence + API
- Phases 7–8: product surface + security
- Phases 9–10: operate + ship

---

## 14. Phase 1 immediate scope (next implementation)

Already proposed; summary:

- `LLMProvider` / `EmbeddingProvider` protocols (async `complete` / `stream` / `embed`)
- LiteLLM adapters
- `FallbackLLMProvider` + factory-only wiring
- `get_llm_provider(settings)` / `get_embedding_provider(settings)` — no call-site fallback
- Tests: dual instantiation with different env/Settings asserts LiteLLM `model_name`; fallback behavior mocked

**Does not include:** chat UI, RAG, or real API keys in tests.

---

## 15. Risks & tradeoffs (explicit)

| Risk | Mitigation |
|---|---|
| Small corpus → retrieval noise | Section chunking + hybrid search; add rerank only if evals fail |
| Mid-stream provider failover | Not supported; failover only pre-first-token |
| Groundedness false positives | Tune verifier; prefer disclaimer over silent drop |
| Design drift to generic AI UI | Hard Phase 7 design gate; reject purple-template aesthetics |
| LiteLLM breaking changes | Pin version; thin adapter isolates upgrades |
| Scope creep (Tier C early) | Park behind roadmap; protect provider/RAG interfaces |

---

## 16. What you approve next

Reply with:

1. **Plan accepted** (or edits: e.g. include reranker in Phase 3, Tier C contact-capture in v1, etc.)
2. **Proceed Phase 1** — implement provider layer per Section 14 / prior Phase 1 proposal

Optional later: drop `ai-portfolio-system-plan.md` into `docs/` if you have a prior architecture dump to merge.
