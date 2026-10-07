from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.repositories.base import BaseRepository


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    """Repository for document chunk operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(DocumentChunk, db)

    def get_by_document_version(
        self,
        document_version_id: UUID,
    ) -> list[DocumentChunk]:
        """Return all chunks belonging to a document version."""

        statement = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_version_id
                == document_version_id
            )
            .order_by(
                DocumentChunk.chunk_index.asc()
            )
        )

        return list(
            self.db.scalars(statement).all()
        )

    def create(
        self,
        *,
        document_version_id: UUID,
        chunk_index: int,
        text: str,
    ) -> DocumentChunk:
        """Create a document chunk."""

        chunk = DocumentChunk(
            document_version_id=document_version_id,
            chunk_index=chunk_index,
            text=text,
        )

        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)

        return chunk

    def create_many(
        self,
        *,
        document_version_id: UUID,
        chunks: list[tuple[int, str]],
    ) -> list[DocumentChunk]:
        """Create multiple chunks for a document version."""

        records = [
            DocumentChunk(
                document_version_id=document_version_id,
                chunk_index=chunk_index,
                text=text,
            )
            for chunk_index, text in chunks
        ]

        self.db.add_all(records)
        self.db.commit()

        for record in records:
            self.db.refresh(record)

        return records
