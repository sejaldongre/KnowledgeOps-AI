from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

from app.models.document import DocumentStatus
from app.services.document import DocumentService


def create_fake_document():
    """Create a fake document for service tests."""

    now = datetime.now(timezone.utc)

    return SimpleNamespace(
        id=uuid4(),
        title="Employee Handbook",
        filename="employee_handbook.pdf",
        file_type="application/pdf",
        file_size=1000,
        description="Company HR policies",
        status=DocumentStatus.UPLOADED,
        owner_id=uuid4(),
        folder_id=None,
        current_version_id=None,
        created_at=now,
        updated_at=now,
    )


class FakeRepository:
    """Fake repository for DocumentService tests."""

    def __init__(self):
        self.document = create_fake_document()

    def get_by_id(self, document_id):
        if document_id == self.document.id:
            return self.document

        return None

    def get_by_owner(self, owner_id):
        if owner_id == self.document.owner_id:
            return [self.document]

        return []

    def get_by_owner_and_status(self, owner_id, status):
        if (
            owner_id == self.document.owner_id
            and status == self.document.status
        ):
            return [self.document]

        return []

    def create(
        self,
        *,
        title,
        filename,
        file_type,
        file_size,
        owner_id,
        description=None,
        folder_id=None,
    ):
        self.document = SimpleNamespace(
            id=uuid4(),
            title=title,
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            description=description,
            status=DocumentStatus.UPLOADED,
            owner_id=owner_id,
            folder_id=folder_id,
            current_version_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return self.document

    def set_current_version(
        self,
        document_id,
        version_id,
    ):
        """Set the current version of the fake document."""

        if document_id != self.document.id:
            return None

        self.document.current_version_id = version_id

        return self.document


class FakeDatabase:
    """Fake database session for service tests."""

    def __init__(self):
        self.committed = False
        self.refreshed = False
        self.deleted = False

    def commit(self):
        self.committed = True

    def refresh(self, document):
        self.refreshed = True

    def delete(self, document):
        self.deleted = True


def create_service():
    """Create a DocumentService with fake dependencies."""

    service = DocumentService.__new__(DocumentService)

    service.repository = FakeRepository()
    service.db = FakeDatabase()

    return service


def test_document_service_can_be_created():
    """Verify that the document service initializes correctly."""

    service = create_service()

    assert service.repository is not None
    assert service.db is not None


def test_get_document_returns_document():
    """Verify that a document can be retrieved by ID."""

    service = create_service()

    document = service.repository.document

    result = service.get_document(document.id)

    assert result == document


def test_get_document_returns_none_for_missing_document():
    """Verify that a missing document returns None."""

    service = create_service()

    result = service.get_document(uuid4())

    assert result is None


def test_get_documents_by_owner():
    """Verify that documents can be retrieved by owner."""

    service = create_service()

    owner_id = service.repository.document.owner_id

    result = service.get_documents_by_owner(owner_id)

    assert len(result) == 1
    assert result[0].owner_id == owner_id


def test_get_documents_by_owner_and_status():
    """Verify owner and status filtering."""

    service = create_service()

    document = service.repository.document

    result = service.get_documents_by_owner_and_status(
        owner_id=document.owner_id,
        status=document.status,
    )

    assert len(result) == 1
    assert result[0] == document


def test_create_document():
    """Verify that a document can be created."""

    service = create_service()

    owner_id = uuid4()

    document = service.create_document(
        title="New Document",
        filename="new_document.pdf",
        file_type="application/pdf",
        file_size=5000,
        owner_id=owner_id,
        description="Test document",
        folder_id=None,
    )

    assert document.title == "New Document"
    assert document.filename == "new_document.pdf"
    assert document.file_type == "application/pdf"
    assert document.file_size == 5000
    assert document.owner_id == owner_id
    assert document.description == "Test document"


def test_update_document():
    """Verify that document metadata can be updated."""

    service = create_service()

    document = service.repository.document

    result = service.update_document(
        document_id=document.id,
        title="Updated Handbook",
        description="Updated policies",
    )

    assert result is document
    assert result.title == "Updated Handbook"
    assert result.description == "Updated policies"

    assert service.db.committed is True
    assert service.db.refreshed is True


def test_update_missing_document_returns_none():
    """Verify that updating a missing document returns None."""

    service = create_service()

    result = service.update_document(
        document_id=uuid4(),
        title="Updated",
    )

    assert result is None


def test_delete_document():
    """Verify that a document can be deleted."""

    service = create_service()

    document = service.repository.document

    result = service.delete_document(document.id)

    assert result is True
    assert service.db.deleted is True
    assert service.db.committed is True


def test_delete_missing_document_returns_false():
    """Verify that deleting a missing document returns False."""

    service = create_service()

    result = service.delete_document(uuid4())

    assert result is False


def test_document_service_can_set_current_version():
    """Verify that the document service updates current version."""

    service = create_service()

    document = service.repository.document
    version_id = uuid4()

    result = service.set_current_version(
        document_id=document.id,
        version_id=version_id,
    )

    assert result is document
    assert result.current_version_id == version_id
