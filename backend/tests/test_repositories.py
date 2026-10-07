from uuid import uuid4

from sqlalchemy.orm import Session

from app.infrastructure.database import engine
from app.models.document import Document, DocumentVersion
from app.models.document_chunk import DocumentChunk
from app.models.user import User
from app.repositories.document import DocumentRepository
from app.repositories.document_chunk import DocumentChunkRepository


def create_test_user(db: Session) -> User:
    """Create a real user for foreign-key dependent tests."""

    user = User(
        id=uuid4(),
        email=f"repository-test-{uuid4()}@example.com",
        password_hash="test-password-hash",
        full_name="Repository Test User",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_test_document_version(
    db: Session,
) -> tuple[Document, DocumentVersion, User]:
    """Create a valid user, document, and document version."""

    user = create_test_user(db)

    document = Document(
        id=uuid4(),
        title="Repository Test Document",
        filename="repository-test.pdf",
        file_type="application/pdf",
        file_size=100,
        owner_id=user.id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    version = DocumentVersion(
        id=uuid4(),
        document_id=document.id,
        version_number=1,
        storage_path="storage/test.pdf",
        file_hash="a" * 64,
        created_by=user.id,
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    return document, version, user


def test_document_repository_can_be_created():
    """Verify that the document repository initializes correctly."""

    with Session(engine) as db:
        repository = DocumentRepository(db)

        assert repository.model.__name__ == "Document"


def test_document_repository_can_set_current_version():
    """Verify that a document current version can be updated."""

    document = type(
        "FakeDocument",
        (),
        {
            "id": uuid4(),
            "current_version_id": None,
        },
    )()

    version_id = uuid4()

    repository = DocumentRepository.__new__(
        DocumentRepository
    )

    repository.db = type(
        "FakeDatabase",
        (),
        {
            "commit": lambda self: None,
            "refresh": lambda self, document: None,
        },
    )()

    repository.get_by_id = lambda document_id: (
        document
        if document_id == document.id
        else None
    )

    result = repository.set_current_version(
        document_id=document.id,
        version_id=version_id,
    )

    assert result is document
    assert result.current_version_id == version_id


def test_document_chunk_repository_can_be_created():
    """Verify that the document chunk repository initializes correctly."""

    with Session(engine) as db:
        repository = DocumentChunkRepository(db)

        assert repository.model.__name__ == "DocumentChunk"


def test_document_chunk_repository_get_by_document_version():
    """Verify that chunks can be retrieved for a document version."""

    with Session(engine) as db:
        document, version, user = create_test_document_version(db)

        chunk_1 = DocumentChunk(
            id=uuid4(),
            document_version_id=version.id,
            chunk_index=0,
            text="First chunk",
        )

        chunk_2 = DocumentChunk(
            id=uuid4(),
            document_version_id=version.id,
            chunk_index=1,
            text="Second chunk",
        )

        db.add_all([chunk_1, chunk_2])
        db.commit()

        repository = DocumentChunkRepository(db)

        result = repository.get_by_document_version(
            version.id
        )

        assert len(result) == 2
        assert result[0].chunk_index == 0
        assert result[0].text == "First chunk"
        assert result[1].chunk_index == 1
        assert result[1].text == "Second chunk"

        db.delete(document)
        db.delete(user)
        db.commit()


def test_document_chunk_repository_create():
    """Verify that a single document chunk can be created."""

    with Session(engine) as db:
        document, version, user = create_test_document_version(db)

        repository = DocumentChunkRepository(db)

        result = repository.create(
            document_version_id=version.id,
            chunk_index=0,
            text="This is a test chunk.",
        )

        assert result is not None
        assert result.document_version_id == version.id
        assert result.chunk_index == 0
        assert result.text == "This is a test chunk."

        db.delete(document)
        db.delete(user)
        db.commit()


def test_document_chunk_repository_create_many():
    """Verify that multiple document chunks can be created."""

    with Session(engine) as db:
        document, version, user = create_test_document_version(db)

        repository = DocumentChunkRepository(db)

        result = repository.create_many(
            document_version_id=version.id,
            chunks=[
                (0, "First chunk"),
                (1, "Second chunk"),
                (2, "Third chunk"),
            ],
        )

        assert len(result) == 3

        assert result[0].chunk_index == 0
        assert result[0].text == "First chunk"

        assert result[1].chunk_index == 1
        assert result[1].text == "Second chunk"

        assert result[2].chunk_index == 2
        assert result[2].text == "Third chunk"

        db.delete(document)
        db.delete(user)
        db.commit()


def test_document_chunk_repository_returns_chunks_in_index_order():
    """Verify that chunks are returned in ascending chunk order."""

    with Session(engine) as db:
        document, version, user = create_test_document_version(db)

        db.add_all(
            [
                DocumentChunk(
                    id=uuid4(),
                    document_version_id=version.id,
                    chunk_index=2,
                    text="Third chunk",
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_version_id=version.id,
                    chunk_index=0,
                    text="First chunk",
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_version_id=version.id,
                    chunk_index=1,
                    text="Second chunk",
                ),
            ]
        )

        db.commit()

        repository = DocumentChunkRepository(db)

        result = repository.get_by_document_version(
            version.id
        )

        assert [chunk.chunk_index for chunk in result] == [
            0,
            1,
            2,
        ]

        db.delete(document)
        db.delete(user)
        db.commit()
