"""LangGraph chat agent: retrieve → compose → generate → verify."""

from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass, field
from typing import Any, TypedDict
from uuid import UUID

from langgraph.graph import END, StateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompts import GROUNDEDNESS_CHECK_PROMPT, PORTFOLIO_SYSTEM_PROMPT
from app.providers.base import EmbeddingProvider, LLMProvider
from app.providers.types import ChatMessage, CompletionChunk
from app.retrieval.hybrid import RetrievedChunk, hybrid_search


class ChatState(TypedDict, total=False):
    query: str
    session_id: str
    history: list[ChatMessage]
    summary: str | None
    retrieved: list[dict[str, Any]]
    messages: list[ChatMessage]
    answer: str
    model: str
    usage: dict[str, int] | None
    grounded: bool
    unsupported_claims: list[str]
    disclaimer: str | None
    citations: list[dict[str, Any]]


@dataclass
class ChatAgent:
    llm: LLMProvider
    embeddings: EmbeddingProvider
    session: AsyncSession
    top_k: int = 8
    verify_with_llm: bool = True

    async def retrieve_context(self, state: ChatState) -> ChatState:
        hits = await hybrid_search(
            self.session,
            query=state["query"],
            embedding_provider=self.embeddings,
            top_k=self.top_k,
        )
        retrieved = [_chunk_to_dict(h) for h in hits]
        citations = [
            {
                "chunk_id": str(h.chunk_id),
                "document_id": str(h.document_id),
                "section_title": h.section_title,
                "source_title": h.source_title,
                "snippet": h.content[:280],
                "score": h.score,
            }
            for h in hits
        ]
        return {**state, "retrieved": retrieved, "citations": citations}

    async def compose_prompt(self, state: ChatState) -> ChatState:
        context_block = _format_context(state.get("retrieved") or [])
        system = PORTFOLIO_SYSTEM_PROMPT + "\n\n## CONTEXT\n" + context_block
        if state.get("summary"):
            system += "\n\n## PRIOR CONVERSATION SUMMARY\n" + state["summary"]

        messages: list[ChatMessage] = [{"role": "system", "content": system}]
        for turn in state.get("history") or []:
            messages.append(turn)
        messages.append({"role": "user", "content": state["query"]})
        return {**state, "messages": messages}

    async def generate_response(self, state: ChatState) -> ChatState:
        result = await self.llm.complete(state["messages"], temperature=0.2)
        return {
            **state,
            "answer": result.content,
            "model": result.model,
            "usage": result.usage,
        }

    async def verify_groundedness(self, state: ChatState) -> ChatState:
        context_block = _format_context(state.get("retrieved") or [])
        answer = state.get("answer") or ""

        grounded = True
        unsupported: list[str] = []
        disclaimer = None

        if self.verify_with_llm and answer.strip():
            check_messages: list[ChatMessage] = [
                {
                    "role": "system",
                    "content": "You are a strict factual verifier. Output JSON only.",
                },
                {
                    "role": "user",
                    "content": GROUNDEDNESS_CHECK_PROMPT.format(
                        context=context_block,
                        answer=answer,
                    ),
                },
            ]
            try:
                check = await self.llm.complete(check_messages, temperature=0)
                parsed = _parse_json_object(check.content)
                grounded = bool(parsed.get("grounded", True))
                unsupported = list(parsed.get("unsupported_claims") or [])
            except Exception:
                # Graceful degradation: heuristic overlap check
                grounded, unsupported = _heuristic_groundedness(answer, context_block)

        if not grounded:
            # One regeneration with tighter constraint
            tight: list[ChatMessage] = list(state["messages"])
            tight.append({"role": "assistant", "content": answer})
            tight.append(
                {
                    "role": "user",
                    "content": (
                        "Your previous answer may contain unsupported claims: "
                        f"{unsupported}. Rewrite using ONLY CONTEXT. "
                        "If unknown, say so explicitly."
                    ),
                }
            )
            retry = await self.llm.complete(tight, temperature=0)
            answer = retry.content
            # Re-check lightly
            grounded2, unsupported2 = _heuristic_groundedness(answer, context_block)
            if not grounded2:
                disclaimer = (
                    "Some details could not be fully verified against the candidate's "
                    "documents; treat uncertain points cautiously."
                )
                answer = answer.rstrip() + "\n\n—" + "\n" + disclaimer
                unsupported = unsupported2
                grounded = False
            else:
                grounded = True
                unsupported = []
                disclaimer = None

        return {
            **state,
            "answer": answer,
            "grounded": grounded,
            "unsupported_claims": unsupported,
            "disclaimer": disclaimer,
        }

    def build_graph(self):
        graph = StateGraph(ChatState)
        graph.add_node("retrieve_context", self.retrieve_context)
        graph.add_node("compose_prompt", self.compose_prompt)
        graph.add_node("generate_response", self.generate_response)
        graph.add_node("verify_groundedness", self.verify_groundedness)
        graph.set_entry_point("retrieve_context")
        graph.add_edge("retrieve_context", "compose_prompt")
        graph.add_edge("compose_prompt", "generate_response")
        graph.add_edge("generate_response", "verify_groundedness")
        graph.add_edge("verify_groundedness", END)
        return graph.compile()

    async def run(
        self,
        *,
        query: str,
        history: Sequence[ChatMessage] | None = None,
        summary: str | None = None,
        session_id: str = "default",
    ) -> ChatState:
        app = self.build_graph()
        return await app.ainvoke(
            {
                "query": query,
                "session_id": session_id,
                "history": list(history or []),
                "summary": summary,
            }
        )

    async def stream_answer(
        self,
        *,
        query: str,
        history: Sequence[ChatMessage] | None = None,
        summary: str | None = None,
        session_id: str = "default",
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream tokens after retrieval/compose; run verify after stream completes."""
        state: ChatState = {
            "query": query,
            "session_id": session_id,
            "history": list(history or []),
            "summary": summary,
        }
        state = await self.retrieve_context(state)
        yield {"event": "citations", "data": state.get("citations") or []}
        state = await self.compose_prompt(state)

        parts: list[str] = []
        async for chunk in self.llm.stream(state["messages"], temperature=0.2):
            if chunk.content:
                parts.append(chunk.content)
                yield {"event": "token", "data": chunk.content}

        state["answer"] = "".join(parts)
        state["model"] = self.llm.model_name
        state = await self.verify_groundedness(state)
        yield {
            "event": "final",
            "data": {
                "answer": state.get("answer"),
                "grounded": state.get("grounded"),
                "citations": state.get("citations") or [],
                "model": state.get("model"),
                "unsupported_claims": state.get("unsupported_claims") or [],
            },
        }


def _chunk_to_dict(chunk: RetrievedChunk) -> dict[str, Any]:
    return {
        "chunk_id": str(chunk.chunk_id),
        "document_id": str(chunk.document_id),
        "content": chunk.content,
        "section_title": chunk.section_title,
        "source_title": chunk.source_title,
        "source_type": chunk.source_type,
        "score": chunk.score,
    }


def _format_context(retrieved: list[dict[str, Any]]) -> str:
    if not retrieved:
        return "(No retrieved context.)"
    blocks = []
    for i, item in enumerate(retrieved, start=1):
        title = item.get("section_title") or item.get("source_title") or "Excerpt"
        blocks.append(f"[{i}] {title}\n{item.get('content', '')}")
    return "\n\n".join(blocks)


def _parse_json_object(raw: str) -> dict[str, Any]:
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _heuristic_groundedness(answer: str, context: str) -> tuple[bool, list[str]]:
    if not answer.strip():
        return True, []
    # Very rough: if answer asserts years/companies not present as substrings, flag.
    ctx_l = context.lower()
    claims = re.findall(
        r"\b(?:\d+\+?\s+years?|worked at [A-Z][\w&\s.-]{2,40}|led [^.!?]{5,60})\b",
        answer,
        flags=re.IGNORECASE,
    )
    unsupported = [c for c in claims if c.lower() not in ctx_l]
    return (len(unsupported) == 0), unsupported
