"""Pydantic request/response schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str = Field(default="default", min_length=1, max_length=128)

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message must not be empty")
        return cleaned


class Citation(BaseModel):
    chunk_id: str
    document_id: str
    section_title: str | None = None
    source_title: str | None = None
    snippet: str
    score: float | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    grounded: bool | None = None
    citations: list[Citation] = []
    model: str | None = None


class ProfileCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    headline: str | None = None
    summary: str | None = None
    email: str | None = None
    location: str | None = None
    links: dict[str, Any] = Field(default_factory=dict)
    skills: list[str] = Field(default_factory=list)


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    headline: str | None = None
    summary: str | None = None
    email: str | None = None
    location: str | None = None
    links: dict[str, Any] | None = None
    skills: list[str] | None = None


class ProfileOut(BaseModel):
    id: UUID
    full_name: str
    headline: str | None
    summary: str | None
    email: str | None
    location: str | None
    links: dict[str, Any]
    skills: list[Any]

    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    id: UUID
    title: str
    source_type: str
    filename: str | None
    content_hash: str
    chunk_count: int | None = None

    model_config = {"from_attributes": True}


class JDMatchResponse(BaseModel):
    match_score: float
    matched_skills: list[str]
    gaps: list[str]
    explanation: str
    injection_attempt_detected: bool = False
    id: str | None = None
    requirements: dict[str, Any] | None = None


class AdminMessageOut(BaseModel):
    id: UUID
    role: str
    content: str
    grounded: bool | None = None
    model: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminConversationSummary(BaseModel):
    id: UUID
    session_id: str
    message_count: int
    preview: str | None = None
    client_ip: str | None = None
    created_at: datetime
    updated_at: datetime


class AdminConversationDetail(BaseModel):
    id: UUID
    session_id: str
    client_ip: str | None = None
    user_agent: str | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[AdminMessageOut]
