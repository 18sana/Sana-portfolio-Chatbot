"""Admin profile + document endpoints (auth-gated)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.schemas import (
    AdminConversationDetail,
    AdminConversationSummary,
    AdminMessageOut,
    DocumentOut,
    ProfileCreate,
    ProfileOut,
    ProfileUpdate,
)
from app.core.config import get_settings
from app.core.security import require_admin
from app.db.models import CandidateProfile, Conversation, Document
from app.db.session import get_db_session
from app.ingestion.extract import ExtractionError
from app.ingestion.pipeline import ingest_document
from app.providers import get_embedding_provider

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.post("/profile", response_model=ProfileOut)
async def create_profile(
    payload: ProfileCreate,
    session: AsyncSession = Depends(get_db_session),
):
    profile = CandidateProfile(**payload.model_dump())
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.get("/profile/{profile_id}", response_model=ProfileOut)
async def get_profile(profile_id: UUID, session: AsyncSession = Depends(get_db_session)):
    profile = await session.get(CandidateProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.patch("/profile/{profile_id}", response_model=ProfileOut)
async def update_profile(
    profile_id: UUID,
    payload: ProfileUpdate,
    session: AsyncSession = Depends(get_db_session),
):
    profile = await session.get(CandidateProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    await session.commit()
    await session.refresh(profile)
    return profile


@router.post("/documents", response_model=DocumentOut)
async def upload_document(
    profile_id: UUID = Form(...),
    title: str = Form(...),
    source_type: str = Form(default="other"),
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_db_session),
):
    settings = get_settings()
    profile = await session.get(CandidateProfile, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    data = await file.read()
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")

    try:
        result = await ingest_document(
            session,
            profile_id=profile_id,
            title=title,
            source_type=source_type,
            data=data,
            filename=file.filename,
            content_type=file.content_type,
            embedding_provider=get_embedding_provider(settings),
        )
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {exc}") from exc

    await session.commit()
    doc = await session.get(Document, result.document_id)
    assert doc is not None
    return DocumentOut(
        id=doc.id,
        title=doc.title,
        source_type=doc.source_type,
        filename=doc.filename,
        content_hash=doc.content_hash,
        chunk_count=result.chunk_count,
    )


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents(
    profile_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    rows = (
        await session.scalars(
            select(Document)
            .where(Document.profile_id == profile_id)
            .options(selectinload(Document.chunks))
        )
    ).all()
    return [
        DocumentOut(
            id=d.id,
            title=d.title,
            source_type=d.source_type,
            filename=d.filename,
            content_hash=d.content_hash,
            chunk_count=len(d.chunks or []),
        )
        for d in rows
    ]


@router.get("/conversations", response_model=list[AdminConversationSummary])
async def list_conversations(
    limit: int = 50,
    session: AsyncSession = Depends(get_db_session),
):
    limit = max(1, min(limit, 200))
    rows = (
        await session.scalars(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )
    ).all()
    out: list[AdminConversationSummary] = []
    for convo in rows:
        messages = list(convo.messages or [])
        preview = None
        for msg in reversed(messages):
            if msg.role == "user" and msg.content.strip():
                preview = msg.content.strip()[:180]
                break
        meta = convo.metadata_json or {}
        out.append(
            AdminConversationSummary(
                id=convo.id,
                session_id=convo.session_id,
                message_count=len(messages),
                preview=preview,
                client_ip=meta.get("client_ip"),
                created_at=convo.created_at,
                updated_at=convo.updated_at,
            )
        )
    return out


@router.get("/conversations/{conversation_id}", response_model=AdminConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    session: AsyncSession = Depends(get_db_session),
):
    convo = await session.scalar(
        select(Conversation)
        .where(Conversation.id == conversation_id)
        .options(selectinload(Conversation.messages))
    )
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")
    meta = convo.metadata_json or {}
    return AdminConversationDetail(
        id=convo.id,
        session_id=convo.session_id,
        client_ip=meta.get("client_ip"),
        user_agent=meta.get("user_agent"),
        created_at=convo.created_at,
        updated_at=convo.updated_at,
        messages=[
            AdminMessageOut(
                id=m.id,
                role=m.role,
                content=m.content,
                grounded=m.grounded,
                model=m.model,
                created_at=m.created_at,
            )
            for m in (convo.messages or [])
        ],
    )
