from types import SimpleNamespace
from uuid import uuid4

from app.services.document_version import DocumentVersionService


class FakeRepository:
    """Fake repository for document version tests."""

    def __init__(self):
        self.versions = []

    def get_by_document(self, document_id):
        return [
            version
            for version in self.versions
            if version.document_id == document_id
        ]

    def get_latest_version(self, document_id):
        versions = self.get_by_document(document_id)

        if not versions:
            return None

        return max(
            versions,
            key=lambda version: version.version_number,
        )

    def create(
        self,
        *,
        document_id,
        version_number,
        storage_path,
        file_hash,
        created_by,
    ):
        version = SimpleNamespace(
            id=uuid4(),
            document_id=document_id,
            version_number=version_number,
            storage_path=storage_path,
            file_hash=file_hash,
            created_by=created_by,
        )

        self.versions.append(version)

        return version


def create_service():
    """Create a service with a fake repository."""

    service = DocumentVersionService.__new__(
        DocumentVersionService
    )

    service.repository = FakeRepository()

    return service


def test_get_versions_returns_document_versions():
    """Verify that all document versions are returned."""

    service = create_service()

    document_id = uuid4()
    user_id = uuid4()

    service.repository.create(
        document_id=document_id,
        version_number=1,
        storage_path="storage/version1.pdf",
        file_hash="hash1",
        created_by=user_id,
    )

    service.repository.create(
        document_id=document_id,
        version_number=2,
        storage_path="storage/version2.pdf",
        file_hash="hash2",
        created_by=user_id,
    )

    versions = service.get_versions(document_id)

    assert len(versions) == 2
    assert versions[0].version_number == 1
    assert versions[1].version_number == 2


def test_get_latest_version_returns_latest():
    """Verify that the latest version is returned."""

    service = create_service()

    document_id = uuid4()
    user_id = uuid4()

    service.repository.create(
        document_id=document_id,
        version_number=1,
        storage_path="storage/version1.pdf",
        file_hash="hash1",
        created_by=user_id,
    )

    service.repository.create(
        document_id=document_id,
        version_number=2,
        storage_path="storage/version2.pdf",
        file_hash="hash2",
        created_by=user_id,
    )

    latest = service.get_latest_version(document_id)

    assert latest is not None
    assert latest.version_number == 2
    assert latest.file_hash == "hash2"


def test_get_latest_version_returns_none_when_missing():
    """Verify that missing versions return None."""

    service = create_service()

    result = service.get_latest_version(uuid4())

    assert result is None


def test_create_first_version():
    """Verify that the first version starts at version 1."""

    service = create_service()

    document_id = uuid4()
    user_id = uuid4()

    version = service.create_version(
        document_id=document_id,
        storage_path="storage/document.pdf",
        file_hash="abc123",
        created_by=user_id,
    )

    assert version.version_number == 1
    assert version.document_id == document_id
    assert version.storage_path == "storage/document.pdf"
    assert version.file_hash == "abc123"
    assert version.created_by == user_id


def test_create_next_version():
    """Verify that version numbers increment."""

    service = create_service()

    document_id = uuid4()
    user_id = uuid4()

    first = service.create_version(
        document_id=document_id,
        storage_path="storage/version1.pdf",
        file_hash="hash1",
        created_by=user_id,
    )

    second = service.create_version(
        document_id=document_id,
        storage_path="storage/version2.pdf",
        file_hash="hash2",
        created_by=user_id,
    )

    assert first.version_number == 1
    assert second.version_number == 2
