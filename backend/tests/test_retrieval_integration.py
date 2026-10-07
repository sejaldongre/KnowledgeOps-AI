from uuid import uuid4

from sqlalchemy.orm import Session

from app.infrastructure.database import engine
from app.models.document import Document, DocumentVersion
from app.models.document_chunk import DocumentChunk
from app.models.document_permission import (
    DocumentPermission,
    PermissionLevel,
)
from app.models.user import User
from app.services.document_permission import (
    DocumentPermissionService,
)
from app.services.retrieval import RetrievalService
from app.services.vector_store import ChromaVectorStore


def create_test_user(db: Session, name: str) -> User:
    """Create a valid database user."""

    user = User(
        id=uuid4(),
        email=f"{uuid4()}@example.com",
        password_hash="integration-test-password",
        full_name=name,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_test_document(
    db: Session,
    owner: User,
    title: str,
) -> tuple[Document, DocumentVersion, DocumentChunk]:
    """Create a document, version, and chunk."""

    document = Document(
        id=uuid4(),
        title=title,
        filename=f"{title.lower().replace(' ', '-')}.txt",
        file_type="text/plain",
        file_size=100,
        owner_id=owner.id,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    version = DocumentVersion(
        id=uuid4(),
        document_id=document.id,
        version_number=1,
        storage_path=f"storage/{document.id}.txt",
        file_hash="b" * 64,
        created_by=owner.id,
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    chunk = DocumentChunk(
        id=uuid4(),
        document_version_id=version.id,
        chunk_index=0,
        text="The employee annual leave policy allows twenty paid vacation days.",
    )

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return document, version, chunk


def test_real_retrieval_respects_document_permissions(
    tmp_path,
):
    """
    Verify the complete retrieval flow using real PostgreSQL
    and real ChromaDB.
    """

    with Session(engine) as db:
        owner = create_test_user(
            db,
            "Integration Owner",
        )

        viewer = create_test_user(
            db,
            "Integration Viewer",
        )

        allowed_document, allowed_version, allowed_chunk = (
            create_test_document(
                db,
                owner,
                "Allowed Leave Policy",
            )
        )

        denied_document, denied_version, denied_chunk = (
            create_test_document(
                db,
                owner,
                "Private Leave Policy",
            )
        )

        permission = DocumentPermission(
            id=uuid4(),
            document_id=allowed_document.id,
            user_id=viewer.id,
            permission=PermissionLevel.VIEW,
        )

        db.add(permission)
        db.commit()

        vector_store = ChromaVectorStore(
            path=str(tmp_path / "chroma"),
            collection_name="retrieval_integration",
        )

        vector_store.add(
            chunk_id=str(allowed_chunk.id),
            document_id=str(allowed_document.id),
            document_version_id=str(
                allowed_version.id
            ),
            chunk_index=allowed_chunk.chunk_index,
            text=allowed_chunk.text,
        )

        vector_store.add(
            chunk_id=str(denied_chunk.id),
            document_id=str(denied_document.id),
            document_version_id=str(
                denied_version.id
            ),
            chunk_index=denied_chunk.chunk_index,
            text=denied_chunk.text,
        )

        permission_service = DocumentPermissionService(
            db
        )

        retrieval_service = RetrievalService(
            vector_store=vector_store,
            permission_service=permission_service,
        )

        results = retrieval_service.search(
            query="employee annual leave policy",
            user_id=viewer.id,
            limit=5,
        )

        result_document_ids = {
            result.document_id
            for result in results
        }

        result_chunk_ids = {
            result.chunk_id
            for result in results
        }

        assert allowed_document.id in result_document_ids

        assert str(allowed_chunk.id) in result_chunk_ids

        assert denied_document.id not in result_document_ids

        assert str(denied_chunk.id) not in result_chunk_ids

        assert all(
            result.document_id == allowed_document.id
            for result in results
        )

        db.delete(allowed_document)
        db.delete(denied_document)
        db.delete(viewer)
        db.delete(owner)
        db.commit()
