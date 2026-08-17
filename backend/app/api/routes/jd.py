"""JD match endpoint."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.jd import JDMatchAgent
from app.api.schemas import JDMatchResponse
from app.core.config import get_settings
from app.core.rate_limit import check_rate_limit
from app.db.session import get_db_session
from app.ingestion.extract import ExtractionError, extract_text
from app.providers import get_embedding_provider, get_llm_provider

router = APIRouter(tags=["jd"])


@router.post("/jd-match", response_model=JDMatchResponse)
async def jd_match(
    request: Request,
    file: UploadFile | None = File(default=None),
    jd_text: str | None = Form(default=None),
    profile_id: str | None = Form(default=None),
    session: AsyncSession = Depends(get_db_session),
):
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    limit = await check_rate_limit(
        f"jd:{client_ip}",
        limit=settings.rate_limit_jd_per_minute,
        window_seconds=60,
    )
    if not limit.allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    pasted = (jd_text or "").strip()
    filename = "pasted-jd.txt"
    text = pasted

    if file is not None and file.filename:
        data = await file.read()
        if len(data) > settings.max_upload_bytes:
            raise HTTPException(status_code=413, detail="File too large")
        try:
            text = extract_text(data, filename=file.filename, content_type=file.content_type)
        except ExtractionError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        filename = file.filename or filename
    elif not pasted:
        raise HTTPException(
            status_code=400,
            detail="Paste a job description or upload a file",
        )

    if len(text) < 40:
        raise HTTPException(status_code=400, detail="Job description is too short")
    if len(text) > 100_000:
        raise HTTPException(status_code=413, detail="Job description is too long")

    pid = UUID(profile_id) if profile_id else None
    agent = JDMatchAgent(
        llm=get_llm_provider(settings),
        embeddings=get_embedding_provider(settings),
        session=session,
    )
    result = await agent.run(jd_text=text, filename=filename, profile_id=pid)
    await session.commit()
    return JDMatchResponse(**result)
