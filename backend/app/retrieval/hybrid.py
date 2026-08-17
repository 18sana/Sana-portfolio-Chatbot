"""Hybrid retrieval: pgvector cosine + Postgres full-text, RRF fusion."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.base import EmbeddingProvider


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    content: str
    section_title: str | None
    score: float
    source_title: str | None = None
    source_type: str | None = None


async def hybrid_search(
    session: AsyncSession,
    *,
    query: str,
    embedding_provider: EmbeddingProvider,
    top_k: int = 8,
    vector_weight: float = 0.6,
    text_weight: float = 0.4,
    candidate_pool: int = 20,
) -> list[RetrievedChunk]:
    """Retrieve chunks with Reciprocal Rank Fusion over vector + FTS rankings."""
    if not query.strip():
        return []

    emb = await embedding_provider.embed([query])
    if not emb.vectors:
        return []
    query_vec = emb.vectors[0]
    # asyncpg wants string form for vector cast
    vec_literal = "[" + ",".join(str(float(x)) for x in query_vec) + "]"

    pool = max(top_k, candidate_pool)
    sql = text(
        """
        WITH vector_hits AS (
            SELECT
                c.id,
                c.document_id,
                c.content,
                c.section_title,
                d.title AS source_title,
                d.source_type,
                1 - (c.embedding <=> CAST(:query_vec AS vector)) AS vector_score,
                ROW_NUMBER() OVER (ORDER BY c.embedding <=> CAST(:query_vec AS vector)) AS vector_rank
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.embedding IS NOT NULL
            ORDER BY c.embedding <=> CAST(:query_vec AS vector)
            LIMIT :pool
        ),
        text_hits AS (
            SELECT
                c.id,
                c.document_id,
                c.content,
                c.section_title,
                d.title AS source_title,
                d.source_type,
                ts_rank_cd(c.tsv, plainto_tsquery('english', :query)) AS text_score,
                ROW_NUMBER() OVER (
                    ORDER BY ts_rank_cd(c.tsv, plainto_tsquery('english', :query)) DESC
                ) AS text_rank
            FROM document_chunks c
            JOIN documents d ON d.id = c.document_id
            WHERE c.tsv @@ plainto_tsquery('english', :query)
            ORDER BY text_score DESC
            LIMIT :pool
        ),
        fused AS (
            SELECT
                COALESCE(v.id, t.id) AS id,
                COALESCE(v.document_id, t.document_id) AS document_id,
                COALESCE(v.content, t.content) AS content,
                COALESCE(v.section_title, t.section_title) AS section_title,
                COALESCE(v.source_title, t.source_title) AS source_title,
                COALESCE(v.source_type, t.source_type) AS source_type,
                COALESCE(1.0 / (60 + v.vector_rank), 0) * :vector_weight
                  + COALESCE(1.0 / (60 + t.text_rank), 0) * :text_weight AS rrf_score
            FROM vector_hits v
            FULL OUTER JOIN text_hits t ON v.id = t.id
        )
        SELECT * FROM fused
        ORDER BY rrf_score DESC
        LIMIT :top_k
        """
    )
    result = await session.execute(
        sql,
        {
            "query_vec": vec_literal,
            "query": query,
            "pool": pool,
            "top_k": top_k,
            "vector_weight": vector_weight,
            "text_weight": text_weight,
        },
    )
    rows = result.mappings().all()
    return [
        RetrievedChunk(
            chunk_id=row["id"],
            document_id=row["document_id"],
            content=row["content"],
            section_title=row["section_title"],
            score=float(row["rrf_score"] or 0.0),
            source_title=row["source_title"],
            source_type=row["source_type"],
        )
        for row in rows
    ]
