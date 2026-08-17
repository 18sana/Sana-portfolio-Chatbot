# AI Portfolio Chatbot — Backend

Python 3.12 FastAPI service.

- **Phase 0:** config + `/health`
- **Phase 1:** provider-agnostic LLM/embedding layer (LiteLLM + fallback)

## Setup

```bash
cd backend
cp .env.example .env
uv sync --extra dev
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health: `GET http://localhost:8000/health`

## Provider swap (Phase 1)

Change only env vars — no code changes:

```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
OPENAI_API_KEY=...

# or
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-5
ANTHROPIC_API_KEY=...
```

Optional fallback:

```bash
LLM_FALLBACK_PROVIDER=anthropic
LLM_FALLBACK_MODEL=claude-sonnet-4-5
```

```python
from app.providers import get_llm_provider, get_embedding_provider
from app.core.config import Settings

llm = get_llm_provider(Settings(_env_file=None, llm_provider="anthropic", llm_model="claude-sonnet-4-5"))
print(llm.model_name)  # anthropic/claude-sonnet-4-5
```

## Tests

```bash
uv run pytest
```
