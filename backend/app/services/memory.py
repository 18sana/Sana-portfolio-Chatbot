"""Conversation memory helpers."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Conversation, Message
from app.providers.types import ChatMessage


async def get_or_create_conversation(session: AsyncSession, session_id: str) -> Conversation:
    result = await session.scalar(
        select(Conversation)
        .where(Conversation.session_id == session_id)
        .options(selectinload(Conversation.messages))
    )
    if result:
        return result
    convo = Conversation(session_id=session_id)
    session.add(convo)
    await session.flush()
    return convo


def windowed_history(messages: list[Message], *, window: int = 4) -> list[ChatMessage]:
    recent = messages[-window:]
    return [{"role": m.role, "content": m.content} for m in recent if m.role in {"user", "assistant"}]


async def append_message(
    session: AsyncSession,
    conversation: Conversation,
    *,
    role: str,
    content: str,
    citations: list | None = None,
    model: str | None = None,
    token_usage: dict | None = None,
    grounded: bool | None = None,
) -> Message:
    msg = Message(
        conversation_id=conversation.id,
        role=role,
        content=content,
        citations=citations or [],
        model=model,
        token_usage=token_usage,
        grounded=grounded,
    )
    session.add(msg)
    await session.flush()
    return msg
