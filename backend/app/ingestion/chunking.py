"""Section-aware semantic chunking (not naive fixed-token sliding windows)."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


HEADING_RE = re.compile(
    r"^(?:"
    r"#{1,6}\s+.+"  # markdown headings
    r"|[A-Z][A-Z0-9 /&-]{2,80}$"  # ALL CAPS section labels
    r"|(?:Experience|Education|Projects|Skills|Summary|Achievements|"
    r"Work History|Technical Skills|Certifications|Publications)"
    r"(?:\s*[:\-])?"
    r")$",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True, slots=True)
class TextChunk:
    content: str
    section_title: str | None
    chunk_index: int
    content_hash: str
    token_count: int


def estimate_tokens(text: str) -> int:
    # Cheap approx (~4 chars/token). Avoid hard tiktoken dependency in chunker tests.
    return max(1, len(text) // 4)


def content_sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def chunk_text(
    text: str,
    *,
    target_tokens: int = 500,
    max_tokens: int = 800,
    overlap_tokens: int = 60,
) -> list[TextChunk]:
    """Split text by section headings, then pack into token-bounded chunks."""
    cleaned = text.replace("\r\n", "\n").strip()
    if not cleaned:
        return []

    sections = _split_sections(cleaned)
    chunks: list[TextChunk] = []
    index = 0

    for section_title, body in sections:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        if not paragraphs:
            continue
        buffer = ""
        for para in paragraphs:
            candidate = f"{buffer}\n\n{para}".strip() if buffer else para
            if estimate_tokens(candidate) <= target_tokens:
                buffer = candidate
                continue
            if buffer:
                for piece in _pack(buffer, max_tokens=max_tokens, overlap_tokens=overlap_tokens):
                    chunks.append(_make_chunk(piece, section_title, index))
                    index += 1
                # overlap tail into next buffer
                overlap = _tail_tokens(buffer, overlap_tokens)
                buffer = f"{overlap}\n\n{para}".strip() if overlap else para
                if estimate_tokens(buffer) > max_tokens:
                    for piece in _pack(buffer, max_tokens=max_tokens, overlap_tokens=0):
                        chunks.append(_make_chunk(piece, section_title, index))
                        index += 1
                    buffer = ""
            else:
                for piece in _pack(para, max_tokens=max_tokens, overlap_tokens=overlap_tokens):
                    chunks.append(_make_chunk(piece, section_title, index))
                    index += 1
        if buffer:
            for piece in _pack(buffer, max_tokens=max_tokens, overlap_tokens=0):
                chunks.append(_make_chunk(piece, section_title, index))
                index += 1

    return chunks


def _make_chunk(content: str, section_title: str | None, index: int) -> TextChunk:
    return TextChunk(
        content=content,
        section_title=section_title,
        chunk_index=index,
        content_hash=content_sha256(content),
        token_count=estimate_tokens(content),
    )


def _split_sections(text: str) -> list[tuple[str | None, str]]:
    matches = list(HEADING_RE.finditer(text))
    if not matches:
        return [(None, text)]

    sections: list[tuple[str | None, str]] = []
    if matches[0].start() > 0:
        preamble = text[: matches[0].start()].strip()
        if preamble:
            sections.append((None, preamble))

    for i, match in enumerate(matches):
        title = match.group(0).strip().lstrip("#").strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        sections.append((title, body or title))
    return sections


def _pack(text: str, *, max_tokens: int, overlap_tokens: int) -> list[str]:
    if estimate_tokens(text) <= max_tokens:
        return [text]
    words = text.split()
    pieces: list[str] = []
    current: list[str] = []
    for word in words:
        current.append(word)
        if estimate_tokens(" ".join(current)) >= max_tokens:
            pieces.append(" ".join(current))
            if overlap_tokens > 0:
                overlap = _tail_tokens(" ".join(current), overlap_tokens)
                current = overlap.split() if overlap else []
            else:
                current = []
    if current:
        pieces.append(" ".join(current))
    return pieces


def _tail_tokens(text: str, token_budget: int) -> str:
    if token_budget <= 0:
        return ""
    words = text.split()
    # ~1 word ≈ 1 token for budget approximation
    return " ".join(words[-token_budget:])
