from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Represent a chunk of document text."""

    text: str
    chunk_index: int


class DocumentChunkingService:
    """Split cleaned document text into overlapping chunks."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero."
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative."
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(
        self,
        text: str,
    ) -> list[DocumentChunk]:
        """Split text into overlapping chunks."""

        if not text:
            return []

        chunks: list[DocumentChunk] = []

        start = 0
        chunk_index = 0

        step = self.chunk_size - self.chunk_overlap

        while start < len(text):
            end = start + self.chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    DocumentChunk(
                        text=chunk_text,
                        chunk_index=chunk_index,
                    )
                )

                chunk_index += 1

            start += step

        return chunks
