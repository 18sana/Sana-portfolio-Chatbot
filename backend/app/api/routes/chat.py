"""Chat SSE endpoint."""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.agents.chat import ChatAgent
from app.api.schemas import ChatRequest
from app.core.config import get_settings
from app.core.rate_limit import check_rate_limit
from app.db.models import Conversation
from app.db.session import get_db_session
from app.providers import get_embedding_provider, get_llm_provider
from app.services.memory import append_message, get_or_create_conversation, windowed_history

router = APIRouter(tags=["chat"])


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
):
    settings = get_settings()
    client_ip = request.client.host if request.client else "unknown"
    ip_limit = await check_rate_limit(
        f"ip:{client_ip}",
        limit=settings.rate_limit_ip_per_minute,
        window_seconds=60,
    )
    if not ip_limit.allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded (IP)")

    session_limit = await check_rate_limit(
        f"session:{payload.session_id}",
        limit=settings.rate_limit_session_per_minute,
        window_seconds=60,
    )
    if not session_limit.allowed:
        raise HTTPException(status_code=429, detail="Rate limit exceeded (session)")

    conversation = await get_or_create_conversation(session, payload.session_id)
    # reload messages
    conversation = await session.scalar(
        select(Conversation)
        .where(Conversation.id == conversation.id)
        .options(selectinload(Conversation.messages))
    )
    assert conversation is not None

    meta = dict(conversation.metadata_json or {})
    meta["client_ip"] = client_ip
    ua = request.headers.get("user-agent")
    if ua:
        meta["user_agent"] = ua[:512]
    conversation.metadata_json = meta

    history = windowed_history(list(conversation.messages or []))

    await append_message(session, conversation, role="user", content=payload.message)

    agent = ChatAgent(
        llm=get_llm_provider(settings),
        embeddings=get_embedding_provider(settings),
        session=session,
        top_k=settings.retrieval_top_k,
        verify_with_llm=settings.verify_groundedness_llm,
        chat_max_tokens=settings.chat_max_tokens,
    )

    async def event_stream():
        final_answer = ""
        grounded = None
        citations = []
        model = None
        try:
            # Open the SSE pipe immediately (helps proxies flush).
            yield ": ok\n\n"
            async for event in agent.stream_answer(
                query=payload.message,
                history=history,
                summary=conversation.summary,
                session_id=payload.session_id,
            ):
                name = event["event"]
                data = event["data"]
                if name == "final":
                    final_answer = data.get("answer") or ""
                    grounded = data.get("grounded")
                    citations = data.get("citations") or []
                    model = data.get("model")
                yield f"event: {name}\ndata: {json.dumps(data)}\n\n"

            await append_message(
                session,
                conversation,
                role="assistant",
                content=final_answer,
                citations=citations,
                model=model,
                grounded=grounded,
            )
            await session.commit()
            yield "event: done\ndata: {}\n\n"
        except Exception as exc:
            await session.rollback()
            err = {"error": "chat_failed", "message": str(exc)}
            yield f"event: error\ndata: {json.dumps(err)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
