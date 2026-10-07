from uuid import UUID

from app.repositories.document_chunk import DocumentChunkRepository
from app.services.document_chunking import DocumentChunkingService
from app.services.document_extraction import DocumentExtractionService
from app.services.document_text_cleaning import (
    DocumentTextCleaningService,
)
from app.services.vector_store import ChromaVectorStore


class DocumentProcessingService:
    """Process a document version into searchable text chunks."""

    def __init__(
        self,
        chunk_repository: DocumentChunkRepository,
        extraction_service: DocumentExtractionService | None = None,
        cleaning_service: DocumentTextCleaningService | None = None,
        chunking_service: DocumentChunkingService | None = None,
        vector_store: ChromaVectorStore | None = None,
    ) -> None:
        self.chunk_repository = chunk_repository

        self.extraction_service = (
            extraction_service
            if extraction_service is not None
            else DocumentExtractionService()
        )

        self.cleaning_service = (
            cleaning_service
            if cleaning_service is not None
            else DocumentTextCleaningService()
        )

        self.chunking_service = (
            chunking_service
            if chunking_service is not None
            else DocumentChunkingService()
        )

        self.vector_store = (
            vector_store
            if vector_store is not None
            else ChromaVectorStore()
        )

    def process(
        self,
        *,
        document_version_id: UUID,
        document_id: UUID,
        file_path: str,
    ):
        """
        Extract, clean, chunk, persist, and vectorize
        a document version.
        """

        extracted_text = self.extraction_service.extract(
            file_path
        )

        cleaned_text = self.cleaning_service.clean(
            extracted_text
        )

        chunks = self.chunking_service.chunk(
            cleaned_text
        )

        chunk_data = [
            (chunk.chunk_index, chunk.text)
            for chunk in chunks
        ]

        if not chunk_data:
            return []

        persisted_chunks = self.chunk_repository.create_many(
            document_version_id=document_version_id,
            chunks=chunk_data,
        )

        for chunk in persisted_chunks:
            self.vector_store.add(
                chunk_id=str(chunk.id),
                document_id=str(document_id),
                document_version_id=str(
                    document_version_id
                ),
                chunk_index=chunk.chunk_index,
                text=chunk.text,
            )

        return persisted_chunks
