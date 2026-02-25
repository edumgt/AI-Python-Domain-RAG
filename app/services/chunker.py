from app.core.config import settings


class TextChunker:
    def __init__(self, chunk_size: int | None = None, chunk_overlap: int | None = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap

    def split_text(self, text: str) -> list[str]:
        text = text.strip()
        if not text:
            return []

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks: list[str] = []

        current = ""
        for para in paragraphs:
            candidate = f"{current}\n\n{para}".strip() if current else para

            if len(candidate) <= self.chunk_size:
                current = candidate
                continue

            if current:
                chunks.append(current)

            if len(para) <= self.chunk_size:
                current = para
            else:
                chunks.extend(self._split_long_paragraph(para))
                current = ""

        if current:
            chunks.append(current)

        return self._apply_overlap(chunks)

    def _split_long_paragraph(self, para: str) -> list[str]:
        result = []
        start = 0
        while start < len(para):
            end = start + self.chunk_size
            result.append(para[start:end].strip())
            start = end
        return [x for x in result if x]

    def _apply_overlap(self, chunks: list[str]) -> list[str]:
        if not chunks or self.chunk_overlap <= 0:
            return chunks

        overlapped: list[str] = []

        for idx, chunk in enumerate(chunks):
            if idx == 0:
                overlapped.append(chunk)
                continue

            prev = chunks[idx - 1]
            prefix = prev[-self.chunk_overlap:] if len(prev) > self.chunk_overlap else prev
            merged = f"{prefix}\n{chunk}".strip()
            overlapped.append(merged)

        return overlapped
