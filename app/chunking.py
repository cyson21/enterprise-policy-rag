"""문서 본문을 검색 품질에 맞는 고정 길이 텍스트 조각으로 나누는 모듈."""

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
    # 긴 문단은 단어 단위로 추가 분해해 청크 길이 상한을 넘지 않도록 한다.
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
