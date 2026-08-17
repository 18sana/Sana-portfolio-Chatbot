"""Document ingestion pipeline: extract → chunk → embed → upsert."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import delete, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Document, DocumentChunk
from app.ingestion.chunking import chunk_text, content_sha256
from app.ingestion.extract import extract_text
from app.providers.base import EmbeddingProvider


@dataclass(frozen=True, slots=True)
class IngestResult:
    document_id: uuid.UUID
    created: bool
    chunk_count: int
    content_hash: str


async def ingest_document(
    session: AsyncSession,
    *,
    profile_id: uuid.UUID,
    title: str,
    source_type: str,
    data: bytes,
    filename: str | None,
    content_type: str | None,
    embedding_provider: EmbeddingProvider,
    reingest: bool = True,
) -> IngestResult:
    raw_text = extract_text(data, filename=filename, content_type=content_type)
    doc_hash = content_sha256(raw_text)

    existing = await session.scalar(
        select(Document).where(
            Document.profile_id == profile_id,
            Document.content_hash == doc_hash,
        )
    )
    if existing is not None and not reingest:
        count = len(existing.chunks) if existing.chunks is not None else 0
        return IngestResult(
            document_id=existing.id,
            created=False,
            chunk_count=count,
            content_hash=doc_hash,
        )

    if existing is not None:
        # Idempotent refresh: replace chunks for same hash/content
        await session.execute(
            delete(DocumentChunk).where(DocumentChunk.document_id == existing.id)
        )
        document = existing
        document.title = title
        document.source_type = source_type
        document.filename = filename
        document.content_type = content_type
        document.raw_text = raw_text
        created = False
    else:
        document = Document(
            profile_id=profile_id,
            title=title,
            source_type=source_type,
            filename=filename,
            content_type=content_type,
            content_hash=doc_hash,
            raw_text=raw_text,
            metadata_json={},
        )
        session.add(document)
        await session.flush()
        created = True

    pieces = chunk_text(raw_text)
    if not pieces:
        raise ValueError("No chunks produced from document")

    vectors = (
        await embedding_provider.embed([p.content for p in pieces])
    ).vectors
    if len(vectors) != len(pieces):
        raise RuntimeError("Embedding provider returned unexpected vector count")

    for piece, vector in zip(pieces, vectors, strict=True):
        chunk = DocumentChunk(
            document_id=document.id,
            chunk_index=piece.chunk_index,
            section_title=piece.section_title,
            content=piece.content,
            content_hash=piece.content_hash,
            token_count=piece.token_count,
            embedding=vector,
            metadata_json={"source_type": source_type, "title": title},
        )
        session.add(chunk)
        await session.flush()
        await session.execute(
            text(
                "UPDATE document_chunks "
                "SET tsv = to_tsvector('english', coalesce(section_title,'') || ' ' || content) "
                "WHERE id = :id"
            ),
            {"id": str(chunk.id)},
        )

    await session.flush()
    return IngestResult(
        document_id=document.id,
        created=created,
        chunk_count=len(pieces),
        content_hash=doc_hash,
    )
