from sqlalchemy.orm import Session

from app.repositories.document_chunk import DocumentChunkRepository
from app.services.vector_store import ChromaVectorStore


class VectorIndexRebuildService:
    """Rebuild the Chroma vector index from PostgreSQL document chunks."""

    def __init__(
        self,
        db: Session,
        vector_store: ChromaVectorStore | None = None,
    ) -> None:
        self.chunk_repository = DocumentChunkRepository(db)
        self.vector_store = (
            vector_store
            if vector_store is not None
            else ChromaVectorStore()
        )

    def rebuild(self) -> int:
        """Rebuild Chroma using chunks from current document versions."""

        chunks = self.chunk_repository.get_current_chunks()

        if not chunks:
            return 0

        self.vector_store.clear()

        for chunk in chunks:
            document_id = str(
                chunk.document_version.document_id
            )

            self.vector_store.add(
                chunk_id=str(chunk.id),
                document_id=document_id,
                document_version_id=str(
                    chunk.document_version_id
                ),
                chunk_index=chunk.chunk_index,
                text=chunk.text,
            )

        return len(chunks)
