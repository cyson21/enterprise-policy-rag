from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    text: str


def chunk_text(content: str, max_chars: int = 700) -> list[TextChunk]:
    """Split Markdown/TXT content into deterministic paragraph chunks."""
    if max_chars < 1:
        raise ValueError("max_chars must be positive")

    normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        raise ValueError("content is empty")

    paragraphs = [part.strip() for part in normalized.split("\n\n") if part.strip()]
    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        paragraph = " ".join(paragraph.split())
        if len(paragraph) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(_split_long_paragraph(paragraph, max_chars))
            continue

        if not current:
            current = paragraph
        elif len(current) + 2 + len(paragraph) <= max_chars:
            current = f"{current}\n\n{paragraph}"
        else:
            chunks.append(current)
            current = paragraph

    if current:
        chunks.append(current)

    return [TextChunk(index=index, text=text) for index, text in enumerate(chunks)]


def _split_long_paragraph(paragraph: str, max_chars: int) -> list[str]:
    words = paragraph.split()
    chunks: list[str] = []
    current = ""

    for word in words:
        if len(word) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(word[start : start + max_chars] for start in range(0, len(word), max_chars))
            continue

        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_chars:
            current = f"{current} {word}"
        else:
            chunks.append(current)
            current = word

    if current:
        chunks.append(current)

    return chunks
