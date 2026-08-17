# Phase 8 — Security hardening checklist

## Auth
- [x] `/admin/*` requires `X-Admin-Api-Key`
- [x] Missing server `ADMIN_API_KEY` → 503 (fail closed)
- [x] Public chat/JD are unauthenticated but rate-limited

## Uploads / injection
- [x] File type allowlist (pdf/docx/txt/md)
- [x] Size limit via `MAX_UPLOAD_BYTES`
- [x] JD text delimiter-wrapped + injection detection
- [x] Extracted JD fields scrubbed for instruction-like strings

## Rate limits
- [x] Per-IP and per-session for chat
- [x] Per-IP for JD
- [x] Redis primary, in-memory fallback
- [x] Unit test proves enforcement

## Secrets
- [x] API keys only in server env
- [x] Frontend only exposes `NEXT_PUBLIC_*`
- [x] Error handlers do not return stack traces

## CORS
- [x] Explicit `CORS_ORIGINS` allowlist (default localhost:3000)

## Manual verification
1. Call `/admin/profile` without header → 401
2. Burst `/chat` beyond limit → 429
3. Upload JD containing "ignore previous instructions" → `injection_attempt_detected: true`, no system leak
