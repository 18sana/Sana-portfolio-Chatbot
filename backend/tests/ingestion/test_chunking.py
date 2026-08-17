from app.ingestion.chunking import chunk_text, content_sha256


SAMPLE = """
SUMMARY
Backend engineer specializing in RAG systems and FastAPI.

EXPERIENCE
Built a multi-tenant RAG platform with PostgreSQL and pgvector.
Led latency work that cut p95 from 2.1s to 780ms.

PROJECTS
Portfolio Chatbot
Used LangGraph for grounded conversational retrieval.
"""


def test_chunk_text_splits_by_section() -> None:
    chunks = chunk_text(SAMPLE, target_tokens=80, max_tokens=120)
    assert len(chunks) >= 2
    titles = {c.section_title for c in chunks if c.section_title}
    assert "EXPERIENCE" in titles or "Experience" in {t.title() for t in titles if t}
    assert all(c.content_hash == content_sha256(c.content) for c in chunks)
    assert all(c.chunk_index == i for i, c in enumerate(chunks))


def test_chunk_text_empty() -> None:
    assert chunk_text("   ") == []


def test_reingest_hash_stable() -> None:
    a = content_sha256("hello world")
    b = content_sha256("hello world")
    assert a == b
    assert a != content_sha256("hello world!")
