"""Text extraction from uploaded documents."""

from __future__ import annotations

import io
from pathlib import Path


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
    "text/markdown",
}


class ExtractionError(ValueError):
    pass


def extract_text(
    data: bytes,
    *,
    filename: str | None = None,
    content_type: str | None = None,
) -> str:
    ext = Path(filename or "").suffix.lower()
    if ext and ext not in ALLOWED_EXTENSIONS:
        raise ExtractionError(f"Unsupported file type: {ext}")
    if content_type and content_type.split(";")[0].strip() not in ALLOWED_CONTENT_TYPES:
        # Allow mismatch when extension is authoritative
        if ext not in ALLOWED_EXTENSIONS:
            raise ExtractionError(f"Unsupported content type: {content_type}")

    if ext == ".pdf" or (content_type or "").startswith("application/pdf"):
        return _extract_pdf(data)
    if ext == ".docx" or "wordprocessingml" in (content_type or ""):
        return _extract_docx(data)
    return _extract_text(data)


def _extract_pdf(data: bytes) -> str:
    import fitz  # pymupdf

    doc = fitz.open(stream=data, filetype="pdf")
    try:
        parts = [page.get_text("text") for page in doc]
    finally:
        doc.close()
    text = "\n".join(parts).strip()
    if not text:
        raise ExtractionError("PDF contained no extractable text")
    return text


def _extract_docx(data: bytes) -> str:
    from docx import Document

    document = Document(io.BytesIO(data))
    parts = [p.text.strip() for p in document.paragraphs if p.text and p.text.strip()]
    text = "\n".join(parts).strip()
    if not text:
        raise ExtractionError("DOCX contained no extractable text")
    return text


def _extract_text(data: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text = data.decode(encoding).strip()
            if text:
                return text
        except UnicodeDecodeError:
            continue
    raise ExtractionError("Could not decode text file")
