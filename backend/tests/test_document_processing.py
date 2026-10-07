from types import SimpleNamespace
from uuid import uuid4


class FakeExtractionService:
    """Fake extraction service for processing tests."""

    def __init__(self, text: str):
        self.text = text
        self.called_with = None

    def extract(self, file_path: str) -> str:
        self.called_with = file_path
        return self.text


class FakeCleaningService:
    """Fake cleaning service for processing tests."""

    def __init__(self):
        self.called_with = None

    def clean(self, text: str) -> str:
        self.called_with = text
        return text.strip()


class FakeChunkingService:
    """Fake chunking service for processing tests."""

    def __init__(self, chunks):
        self.chunks = chunks
        self.called_with = None

    def chunk(self, text: str):
        self.called_with = text
        return self.chunks


class FakeChunkRepository:
    """Fake repository for processing tests."""

    def __init__(self):
        self.document_version_id = None
        self.chunks = None

    def create_many(
        self,
        *,
        document_version_id,
        chunks,
    ):
        self.document_version_id = document_version_id
        self.chunks = chunks

        return [
            SimpleNamespace(
                id=uuid4(),
                chunk_index=chunk_index,
                text=text,
            )
            for chunk_index, text in chunks
        ]


class FakeVectorStore:
    """Fake vector store for processing tests."""

    def __init__(self):
        self.added_chunks = []

    def add(
        self,
        *,
        chunk_id,
        document_id,
        document_version_id,
        chunk_index,
        text,
    ):
        self.added_chunks.append(
            {
                "chunk_id": chunk_id,
                "document_id": document_id,
                "document_version_id": document_version_id,
                "chunk_index": chunk_index,
                "text": text,
            }
        )


def test_processing_extracts_cleans_chunks_and_persists():
    """Verify the complete processing pipeline."""

    from app.services.document_processing import (
        DocumentProcessingService,
    )

    document_id = uuid4()
    version_id = uuid4()

    extraction = FakeExtractionService(
        "  First chunk text  "
    )

    cleaning = FakeCleaningService()

    chunking = FakeChunkingService(
        [
            SimpleNamespace(
                chunk_index=0,
                text="First chunk text",
            )
        ]
    )

    repository = FakeChunkRepository()
    vector_store = FakeVectorStore()

    service = DocumentProcessingService(
        chunk_repository=repository,
        extraction_service=extraction,
        cleaning_service=cleaning,
        chunking_service=chunking,
        vector_store=vector_store,
    )

    result = service.process(
        document_id=document_id,
        document_version_id=version_id,
        file_path="storage/test.pdf",
    )

    assert extraction.called_with == "storage/test.pdf"

    assert cleaning.called_with == (
        "  First chunk text  "
    )

    assert chunking.called_with == "First chunk text"

    assert repository.document_version_id == version_id

    assert repository.chunks == [
        (0, "First chunk text")
    ]

    assert len(result) == 1
    assert result[0].chunk_index == 0
    assert result[0].text == "First chunk text"

    assert len(vector_store.added_chunks) == 1

    vector_chunk = vector_store.added_chunks[0]

    assert vector_chunk["document_id"] == str(document_id)

    assert (
        vector_chunk["document_version_id"]
        == str(version_id)
    )

    assert vector_chunk["chunk_index"] == 0

    assert vector_chunk["text"] == "First chunk text"


def test_processing_returns_empty_list_for_empty_text():
    """Verify empty extracted text produces no chunks."""

    from app.services.document_processing import (
        DocumentProcessingService,
    )

    extraction = FakeExtractionService("")

    cleaning = FakeCleaningService()

    chunking = FakeChunkingService([])

    repository = FakeChunkRepository()
    vector_store = FakeVectorStore()

    service = DocumentProcessingService(
        chunk_repository=repository,
        extraction_service=extraction,
        cleaning_service=cleaning,
        chunking_service=chunking,
        vector_store=vector_store,
    )

    result = service.process(
        document_id=uuid4(),
        document_version_id=uuid4(),
        file_path="storage/empty.pdf",
    )

    assert result == []

    assert repository.chunks is None

    assert vector_store.added_chunks == []


def test_processing_preserves_chunk_indexes():
    """Verify chunk indexes are passed to the repository."""

    from app.services.document_processing import (
        DocumentProcessingService,
    )

    chunking = FakeChunkingService(
        [
            SimpleNamespace(
                chunk_index=0,
                text="First",
            ),
            SimpleNamespace(
                chunk_index=1,
                text="Second",
            ),
            SimpleNamespace(
                chunk_index=2,
                text="Third",
            ),
        ]
    )

    repository = FakeChunkRepository()
    vector_store = FakeVectorStore()

    document_id = uuid4()
    version_id = uuid4()

    service = DocumentProcessingService(
        chunk_repository=repository,
        extraction_service=FakeExtractionService(
            "First Second Third"
        ),
        cleaning_service=FakeCleaningService(),
        chunking_service=chunking,
        vector_store=vector_store,
    )

    service.process(
        document_id=document_id,
        document_version_id=version_id,
        file_path="storage/test.pdf",
    )

    assert repository.chunks == [
        (0, "First"),
        (1, "Second"),
        (2, "Third"),
    ]

    assert [
        chunk["chunk_index"]
        for chunk in vector_store.added_chunks
    ] == [0, 1, 2]


def test_processing_uses_correct_document_version():
    """Verify chunks are associated with the correct version."""

    from app.services.document_processing import (
        DocumentProcessingService,
    )

    document_id = uuid4()
    version_id = uuid4()

    chunking = FakeChunkingService(
        [
            SimpleNamespace(
                chunk_index=0,
                text="Test",
            )
        ]
    )

    repository = FakeChunkRepository()
    vector_store = FakeVectorStore()

    service = DocumentProcessingService(
        chunk_repository=repository,
        extraction_service=FakeExtractionService(
            "Test"
        ),
        cleaning_service=FakeCleaningService(),
        chunking_service=chunking,
        vector_store=vector_store,
    )

    service.process(
        document_id=document_id,
        document_version_id=version_id,
        file_path="storage/test.pdf",
    )

    assert repository.document_version_id == version_id

    assert len(vector_store.added_chunks) == 1

    assert (
        vector_store.added_chunks[0][
            "document_version_id"
        ]
        == str(version_id)
    )
