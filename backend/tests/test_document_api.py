from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import ForbiddenException
from app.main import app
from app.api.dependencies import (
    get_current_user,
    get_document_permission_service,
    get_document_service,
    get_document_upload_service,
    get_document_version_service,
    get_document_processing_service,
)
from app.models.document import DocumentStatus
from app.models.document_permission import PermissionLevel


DOCUMENT_ID = uuid4()
USER_ID = uuid4()


def create_fake_document():
    """Create a fake document for API tests."""

    now = datetime.now(timezone.utc)

    return SimpleNamespace(
        id=DOCUMENT_ID,
        title="Employee Handbook",
        description="Company HR policies",
        status=DocumentStatus.UPLOADED,
        owner_id=USER_ID,
        folder_id=None,
        created_at=now,
        updated_at=now,
    )


def create_fake_user():
    """Create a fake authenticated user."""

    return SimpleNamespace(
        id=USER_ID,
        email="employee@example.com",
        full_name="Test Employee",
        is_active=True,
    )


class FakeDocumentService:
    """Fake document service for API tests."""

    def __init__(self):
        self.document = create_fake_document()

    def create_document(
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
        """Create a fake document."""

        document = SimpleNamespace(
            id=uuid4(),
            title=title,
            description=description,
            status=DocumentStatus.UPLOADED,
            owner_id=owner_id,
            folder_id=folder_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        return document

    def get_document(self, document_id):
        if document_id == self.document.id:
            return self.document

        return None

    def get_documents_by_owner_and_status(
        self,
        owner_id,
        status,
    ):
        """Return documents matching owner and status."""

        if (
            owner_id == self.document.owner_id
            and status == self.document.status
        ):
            return [self.document]

        return []

    def update_document(
        self,
        document_id,
        title=None,
        description=None,
    ):
        if title is not None:
            self.document.title = title

        if description is not None:
            self.document.description = description

        return self.document

    def delete_document(self, document_id):
        if document_id == self.document.id:
            return True

        return False

    def set_current_version(
        self,
        document_id,
        version_id,
    ):
        """Set the current version for the fake document."""

        self.document.current_version_id = version_id

        return self.document

    def get_documents_by_owner(self, owner_id):
        """Return documents owned by the requested user."""

        if owner_id == self.document.owner_id:
            return [self.document]

        return []


class FakePermissionService:
    """Fake permission service for API authorization tests."""

    def __init__(self, allowed_permissions):
        self.allowed_permissions = allowed_permissions

    def require_permission(
        self,
        user_id,
        document_id,
        permission,
    ):
        if permission not in self.allowed_permissions:
            raise ForbiddenException(
                message=(
                    f"Document permission "
                    f"'{permission.value}' is required."
                )
            )


@pytest.fixture
def fake_user():
    return create_fake_user()


@pytest.fixture
def document_service():
    return FakeDocumentService()


def override_current_user(fake_user):
    def dependency():
        return fake_user

    return dependency


def override_document_service(document_service):
    def dependency():
        return document_service

    return dependency


def override_permission_service(permission_service):
    def dependency():
        return permission_service

    return dependency


def test_get_document_with_view_permission(
    fake_user,
    document_service,
):
    """Verify that VIEW permission allows GET."""

    permission_service = FakePermissionService(
        {PermissionLevel.VIEW}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{DOCUMENT_ID}"
        )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(DOCUMENT_ID)
        assert body["title"] == "Employee Handbook"

    finally:
        app.dependency_overrides.clear()


def test_get_document_without_view_permission_is_forbidden(
    fake_user,
    document_service,
):
    """Verify that missing VIEW permission returns 403."""

    permission_service = FakePermissionService(set())

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{DOCUMENT_ID}"
        )

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()


def test_update_document_with_edit_permission(
    fake_user,
    document_service,
):
    """Verify that EDIT permission allows PATCH."""

    permission_service = FakePermissionService(
        {PermissionLevel.EDIT}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    try:
        client = TestClient(app)

        response = client.patch(
            f"/documents/{DOCUMENT_ID}",
            json={
                "title": "Updated Handbook",
                "description": "Updated policies",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["title"] == "Updated Handbook"
        assert body["description"] == "Updated policies"

    finally:
        app.dependency_overrides.clear()


def test_update_document_without_edit_permission_is_forbidden(
    fake_user,
    document_service,
):
    """Verify that missing EDIT permission returns 403."""

    permission_service = FakePermissionService(
        {PermissionLevel.VIEW}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    try:
        client = TestClient(app)

        response = client.patch(
            f"/documents/{DOCUMENT_ID}",
            json={
                "title": "Unauthorized Update",
            },
        )

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()


def test_delete_document_with_delete_permission(
    fake_user,
    document_service,
):
    """Verify that DELETE permission allows deletion."""

    permission_service = FakePermissionService(
        {PermissionLevel.DELETE}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    try:
        client = TestClient(app)

        response = client.delete(
            f"/documents/{DOCUMENT_ID}"
        )

        assert response.status_code == 204

    finally:
        app.dependency_overrides.clear()


def test_delete_document_without_delete_permission_is_forbidden(
    fake_user,
    document_service,
):
    """Verify that missing DELETE permission returns 403."""

    permission_service = FakePermissionService(
        {PermissionLevel.VIEW}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    try:
        client = TestClient(app)

        response = client.delete(
            f"/documents/{DOCUMENT_ID}"
        )

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()


def test_get_unknown_document_returns_404(
    fake_user,
    document_service,
):
    """Verify that an unknown document returns 404."""

    permission_service = FakePermissionService(
        {PermissionLevel.VIEW}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    unknown_document_id = uuid4()

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{unknown_document_id}"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found."

    finally:
        app.dependency_overrides.clear()


def test_update_unknown_document_returns_404(
    fake_user,
    document_service,
):
    """Verify that updating an unknown document returns 404."""

    permission_service = FakePermissionService(
        {PermissionLevel.EDIT}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    unknown_document_id = uuid4()

    try:
        client = TestClient(app)

        response = client.patch(
            f"/documents/{unknown_document_id}",
            json={
                "title": "Updated Document",
            },
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()


def test_delete_unknown_document_returns_404(
    fake_user,
    document_service,
):
    """Verify that deleting an unknown document returns 404."""

    permission_service = FakePermissionService(
        {PermissionLevel.DELETE}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    unknown_document_id = uuid4()

    try:
        client = TestClient(app)

        response = client.delete(
            f"/documents/{unknown_document_id}"
        )

        assert response.status_code == 404

    finally:
        app.dependency_overrides.clear()


def test_create_document_with_authenticated_user(
    fake_user,
    document_service,
):
    """Verify that an authenticated user can create a document."""

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    try:
        client = TestClient(app)

        response = client.post(
            "/documents",
            json={
                "title": "New Employee Handbook",
                "filename": "employee_handbook.pdf",
                "file_type": "application/pdf",
                "file_size": 245760,
                "description": "Company HR policies",
                "folder_id": None,
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["title"] == "New Employee Handbook"
        assert body["description"] == "Company HR policies"
        assert body["status"] == "uploaded"

    finally:
        app.dependency_overrides.clear()


def test_create_document_sets_authenticated_user_as_owner(
    fake_user,
    document_service,
):
    """Verify that the authenticated user becomes the owner."""

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    try:
        client = TestClient(app)

        response = client.post(
            "/documents",
            json={
                "title": "Private Document",
                "filename": "private.pdf",
                "file_type": "application/pdf",
                "file_size": 1000,
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["owner_id"] == str(fake_user.id)

    finally:
        app.dependency_overrides.clear()


def test_create_document_ignores_client_owner_id(
    fake_user,
    document_service,
):
    """Verify that owner_id comes from the authenticated user."""

    another_user_id = uuid4()

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    try:
        client = TestClient(app)

        response = client.post(
            "/documents",
            json={
                "title": "Protected Document",
                "filename": "protected.pdf",
                "file_type": "application/pdf",
                "file_size": 5000,
                "owner_id": str(another_user_id),
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["owner_id"] == str(fake_user.id)
        assert body["owner_id"] != str(another_user_id)

    finally:
        app.dependency_overrides.clear()


def test_create_document_rejects_missing_file_metadata(
    fake_user,
    document_service,
):
    """Verify required file metadata is validated."""

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    try:
        client = TestClient(app)

        response = client.post(
            "/documents",
            json={
                "title": "Incomplete Document",
                "description": "Missing file metadata",
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()


def test_create_document_rejects_invalid_file_size(
    fake_user,
    document_service,
):
    """Verify that file size must be greater than zero."""

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    try:
        client = TestClient(app)

        response = client.post(
            "/documents",
            json={
                "title": "Invalid Document",
                "filename": "document.pdf",
                "file_type": "application/pdf",
                "file_size": 0,
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()


def test_list_documents_returns_owned_documents(
    fake_user,
    document_service,
):
    """Verify that a user receives their own documents."""

    document_service.document.owner_id = fake_user.id

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    try:
        client = TestClient(app)

        response = client.get("/documents")

        assert response.status_code == 200

        body = response.json()

        assert len(body) >= 1
        assert body[0]["owner_id"] == str(fake_user.id)

    finally:
        app.dependency_overrides.clear()


def test_list_documents_returns_empty_list_when_user_has_no_documents(
    fake_user,
):
    """Verify that users without documents receive an empty list."""

    class EmptyDocumentService:
        def get_documents_by_owner(self, owner_id):
            assert owner_id == fake_user.id
            return []

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(
        EmptyDocumentService()
    )

    try:
        client = TestClient(app)

        response = client.get("/documents")

        assert response.status_code == 200
        assert response.json() == []

    finally:
        app.dependency_overrides.clear()


def test_list_documents_uses_authenticated_user_id(
    fake_user,
):
    """Verify that listing uses the authenticated user's ID."""

    captured_owner_id = None

    class TrackingDocumentService:
        def get_documents_by_owner(self, owner_id):
            nonlocal captured_owner_id
            captured_owner_id = owner_id
            return []

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(
        TrackingDocumentService()
    )

    try:
        client = TestClient(app)

        response = client.get("/documents")

        assert response.status_code == 200
        assert captured_owner_id == fake_user.id

    finally:
        app.dependency_overrides.clear()


def test_list_documents_filters_by_status(
    fake_user,
    document_service,
):
    """Verify that documents can be filtered by status."""

    document_service.document.owner_id = fake_user.id
    document_service.document.status = DocumentStatus.UPLOADED

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    try:
        client = TestClient(app)

        response = client.get(
            "/documents?status=uploaded"
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 1
        assert body[0]["status"] == "uploaded"
        assert body[0]["owner_id"] == str(fake_user.id)

    finally:
        app.dependency_overrides.clear()


def test_list_documents_with_wrong_status_returns_empty(
    fake_user,
    document_service,
):
    """Verify that a non-matching status returns no documents."""

    document_service.document.owner_id = fake_user.id
    document_service.document.status = DocumentStatus.UPLOADED

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    try:
        client = TestClient(app)

        response = client.get(
            "/documents?status=failed"
        )

        assert response.status_code == 200
        assert response.json() == []

    finally:
        app.dependency_overrides.clear()


def test_list_documents_rejects_invalid_status(
    fake_user,
    document_service,
):
    """Verify that invalid document statuses are rejected."""

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    try:
        client = TestClient(app)

        response = client.get(
            "/documents?status=invalid_status"
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()


def test_get_document_returns_404_when_document_does_not_exist(
    fake_user,
):
    """Verify that a missing document returns 404."""

    class EmptyDocumentService:
        def get_document(self, document_id):
            return None

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(
        EmptyDocumentService()
    )

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{uuid4()}"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found."

    finally:
        app.dependency_overrides.clear()


def test_get_document_checks_view_permission_for_current_user(
    fake_user,
    document_service,
):
    """Verify that VIEW permission uses the current user and document."""

    captured = {}

    class TrackingPermissionService:
        def require_permission(
            self,
            user_id,
            document_id,
            permission,
        ):
            captured["user_id"] = user_id
            captured["document_id"] = document_id
            captured["permission"] = permission

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(
        TrackingPermissionService()
    )

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{DOCUMENT_ID}"
        )

        assert response.status_code == 200

        assert captured["user_id"] == fake_user.id
        assert captured["document_id"] == DOCUMENT_ID
        assert captured["permission"] == PermissionLevel.VIEW

    finally:
        app.dependency_overrides.clear()


def test_update_document_rejects_empty_title(
    fake_user,
    document_service,
):
    """Verify that an empty title is rejected."""

    permission_service = FakePermissionService(
        {PermissionLevel.EDIT}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    try:
        client = TestClient(app)

        response = client.patch(
            f"/documents/{DOCUMENT_ID}",
            json={
                "title": "",
            },
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()


def test_update_document_rejects_empty_update(
    fake_user,
    document_service,
):
    """Verify that an empty update payload is rejected."""

    permission_service = FakePermissionService(
        {PermissionLevel.EDIT}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    try:
        client = TestClient(app)

        response = client.patch(
            f"/documents/{DOCUMENT_ID}",
            json={},
        )

        assert response.status_code == 422

    finally:
        app.dependency_overrides.clear()


def test_update_document_description_only(
    fake_user,
    document_service,
):
    """Verify that description can be updated independently."""

    permission_service = FakePermissionService(
        {PermissionLevel.EDIT}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    try:
        client = TestClient(app)

        original_title = document_service.document.title

        response = client.patch(
            f"/documents/{DOCUMENT_ID}",
            json={
                "description": "Updated HR policies",
            },
        )

        assert response.status_code == 200

        body = response.json()

        assert body["description"] == "Updated HR policies"
        assert body["title"] == original_title

    finally:
        app.dependency_overrides.clear()


def test_delete_document_returns_404_when_document_does_not_exist(
    fake_user,
):
    """Verify that deleting a missing document returns 404."""

    class EmptyDocumentService:
        def get_document(self, document_id):
            return None

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(
        EmptyDocumentService()
    )

    try:
        client = TestClient(app)

        response = client.delete(
            f"/documents/{uuid4()}"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found."

    finally:
        app.dependency_overrides.clear()


def test_delete_document_checks_delete_permission(
    fake_user,
    document_service,
):
    """Verify that DELETE permission is checked correctly."""

    captured = {}

    class TrackingPermissionService:
        def require_permission(
            self,
            user_id,
            document_id,
            permission,
        ):
            captured["user_id"] = user_id
            captured["document_id"] = document_id
            captured["permission"] = permission

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(
        TrackingPermissionService()
    )

    try:
        client = TestClient(app)

        response = client.delete(
            f"/documents/{DOCUMENT_ID}"
        )

        assert response.status_code == 204

        assert captured["user_id"] == fake_user.id
        assert captured["document_id"] == DOCUMENT_ID
        assert captured["permission"] == PermissionLevel.DELETE

    finally:
        app.dependency_overrides.clear()


class FakeVersionService:
    """Fake document version service for API tests."""

    def __init__(self, versions=None):
        self.versions = versions or []
        self.requested_document_id = None

    def get_versions(self, document_id):
        self.requested_document_id = document_id
        return self.versions


def test_list_document_versions_with_view_permission(
    fake_user,
    document_service,
):
    """Verify that VIEW permission allows version listing."""

    versions = [
        SimpleNamespace(
            id=uuid4(),
            document_id=DOCUMENT_ID,
            version_number=1,
            storage_path="storage/version1.pdf",
            file_hash="hash1",
            created_by=USER_ID,
            created_at=datetime.now(timezone.utc),
        ),
        SimpleNamespace(
            id=uuid4(),
            document_id=DOCUMENT_ID,
            version_number=2,
            storage_path="storage/version2.pdf",
            file_hash="hash2",
            created_by=USER_ID,
            created_at=datetime.now(timezone.utc),
        ),
    ]

    version_service = FakeVersionService(versions)

    permission_service = FakePermissionService(
        {PermissionLevel.VIEW}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{DOCUMENT_ID}/versions"
        )

        assert response.status_code == 200

        body = response.json()

        assert len(body) == 2
        assert body[0]["version_number"] == 1
        assert body[1]["version_number"] == 2

    finally:
        app.dependency_overrides.clear()


def test_list_document_versions_without_view_permission_is_forbidden(
    fake_user,
    document_service,
):
    """Verify that missing VIEW permission returns 403."""

    version_service = FakeVersionService()

    permission_service = FakePermissionService(set())

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{DOCUMENT_ID}/versions"
        )

        assert response.status_code == 403

    finally:
        app.dependency_overrides.clear()


def test_list_document_versions_returns_404_for_missing_document(
    fake_user,
):
    """Verify that missing documents return 404."""

    class EmptyDocumentService:
        def get_document(self, document_id):
            return None

    permission_service = FakePermissionService(
        {PermissionLevel.VIEW}
    )

    version_service = FakeVersionService()

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(
        EmptyDocumentService()
    )

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{uuid4()}/versions"
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Document not found."

    finally:
        app.dependency_overrides.clear()


def test_list_document_versions_passes_correct_document_id(
    fake_user,
    document_service,
):
    """Verify that the correct document ID reaches the version service."""

    version_service = FakeVersionService()

    permission_service = FakePermissionService(
        {PermissionLevel.VIEW}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{DOCUMENT_ID}/versions"
        )

        assert response.status_code == 200
        assert (
            version_service.requested_document_id
            == DOCUMENT_ID
        )

    finally:
        app.dependency_overrides.clear()


def test_list_document_versions_passes_correct_document_id(
    fake_user,
    document_service,
):
    """Verify that the correct document ID reaches the version service."""

    version_service = FakeVersionService()

    permission_service = FakePermissionService(
        {PermissionLevel.VIEW}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(permission_service)

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.get(
            f"/documents/{DOCUMENT_ID}/versions"
        )

        assert response.status_code == 200
        assert (
            version_service.requested_document_id
            == DOCUMENT_ID
        )

    finally:
        app.dependency_overrides.clear()


class FakeUploadService:
    """Fake upload service for API tests."""

    def __init__(self):
        self.filename = None
        self.content = None

    def save_file(
        self,
        *,
        filename,
        content,
    ):
        self.filename = filename
        self.content = content

        return (
            "storage/test-file.pdf",
            "a" * 64,
        )


class FakeUploadVersionService:
    """Fake version service for upload API tests."""

    def __init__(self):
        self.document_id = None
        self.created_by = None
        self.storage_path = None
        self.file_hash = None
        self.version = None

    def create_version(
        self,
        *,
        document_id,
        storage_path,
        file_hash,
        created_by,
    ):
        self.document_id = document_id
        self.created_by = created_by
        self.storage_path = storage_path
        self.file_hash = file_hash

        self.version = SimpleNamespace(
            id=uuid4(),
            document_id=document_id,
            version_number=1,
            storage_path=storage_path,
            file_hash=file_hash,
            created_by=created_by,
            created_at=datetime.now(timezone.utc),
        )

        return self.version


class FakeDocumentProcessingService:
    """Fake document processing service for API tests."""

    def __init__(self):
        self.document_version_id = None
        self.document_id = None
        self.file_path = None
        self.called = False
        self.called_with = None

    def process(
        self,
        *,
        document_version_id,
        document_id,
        file_path,
    ):
        """Record document processing invocation."""

        self.called = True

        self.document_version_id = document_version_id
        self.document_id = document_id
        self.file_path = file_path

        self.called_with = {
            "document_version_id": document_version_id,
            "document_id": document_id,
            "file_path": file_path,
        }

        return []


def test_upload_document_version_with_edit_permission(
    fake_user,
    document_service,
):
    """Verify that EDIT permission allows file upload."""

    upload_service = FakeUploadService()
    version_service = FakeUploadVersionService()
    processing_service = FakeDocumentProcessingService()

    permission_service = FakePermissionService(
        {PermissionLevel.EDIT}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(
        permission_service
    )

    app.dependency_overrides[
        get_document_upload_service
    ] = lambda: upload_service

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.post(
            f"/documents/{DOCUMENT_ID}/upload",
            files={
                "file": (
                    "handbook.pdf",
                    b"Employee Handbook Content",
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 201

        body = response.json()

        assert body["document_id"] == str(DOCUMENT_ID)
        assert body["version_number"] == 1
        assert body["storage_path"] == "storage/test-file.pdf"
        assert body["file_hash"] == "a" * 64
        assert body["created_by"] == str(USER_ID)

        assert upload_service.filename == "handbook.pdf"
        assert upload_service.content == (
            b"Employee Handbook Content"
        )

        assert processing_service.called is True
        assert (
            processing_service.document_version_id
            == version_service.version.id
        )
        assert processing_service.file_path == (
            "storage/test-file.pdf"
        )

    finally:
        app.dependency_overrides.clear()


def test_upload_document_without_edit_permission_is_forbidden(
    fake_user,
    document_service,
):
    """Verify that missing EDIT permission returns 403."""

    upload_service = FakeUploadService()
    version_service = FakeUploadVersionService()
    processing_service = FakeDocumentProcessingService()

    permission_service = FakePermissionService(set())

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(
        permission_service
    )

    app.dependency_overrides[
        get_document_upload_service
    ] = lambda: upload_service

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.post(
            f"/documents/{DOCUMENT_ID}/upload",
            files={
                "file": (
                    "handbook.pdf",
                    b"Unauthorized content",
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 403

        assert upload_service.content is None
        assert version_service.document_id is None

    finally:
        app.dependency_overrides.clear()


def test_upload_document_returns_404_when_document_missing(
    fake_user,
):
    """Verify that uploading to a missing document returns 404."""

    class EmptyDocumentService:
        def get_document(self, document_id):
            return None

    upload_service = FakeUploadService()
    version_service = FakeUploadVersionService()
    processing_service = FakeDocumentProcessingService()

    permission_service = FakePermissionService(
        {PermissionLevel.EDIT}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(
        EmptyDocumentService()
    )

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(
        permission_service
    )

    app.dependency_overrides[
        get_document_upload_service
    ] = lambda: upload_service

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.post(
            f"/documents/{uuid4()}/upload",
            files={
                "file": (
                    "handbook.pdf",
                    b"Some content",
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == (
            "Document not found."
        )

        assert upload_service.content is None
        assert version_service.document_id is None

    finally:
        app.dependency_overrides.clear()


def test_upload_document_creates_version_with_correct_metadata(
    fake_user,
    document_service,
):
    """Verify that upload creates a version with correct metadata."""

    upload_service = FakeUploadService()
    version_service = FakeUploadVersionService()
    processing_service = FakeDocumentProcessingService()

    permission_service = FakePermissionService(
        {PermissionLevel.EDIT}
    )

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(document_service)

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(
        permission_service
    )

    app.dependency_overrides[
        get_document_upload_service
    ] = lambda: upload_service

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.post(
            f"/documents/{DOCUMENT_ID}/upload",
            files={
                "file": (
                    "updated-handbook.pdf",
                    b"Updated Handbook",
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 201

        assert (
            version_service.document_id
            == DOCUMENT_ID
        )

        assert (
            version_service.created_by
            == USER_ID
        )

        assert (
            version_service.storage_path
            == "storage/test-file.pdf"
        )

        assert (
            version_service.file_hash
            == "a" * 64
        )

        assert processing_service.called is True
        assert (
            processing_service.document_version_id
            == version_service.version.id
        )
        assert processing_service.file_path == (
            "storage/test-file.pdf"
        )

    finally:
        app.dependency_overrides.clear()


def test_upload_document_updates_current_version(
    fake_user,
    document_service,
):
    """Verify that upload updates the document current version."""

    upload_service = FakeUploadService()
    version_service = FakeUploadVersionService()
    processing_service = FakeDocumentProcessingService()

    permission_service = FakePermissionService(
        {PermissionLevel.EDIT}
    )

    current_version_id = uuid4()

    class TrackingDocumentService(FakeDocumentService):
        def __init__(self):
            super().__init__()
            self.current_version_id = None

        def set_current_version(
            self,
            document_id,
            version_id,
        ):
            assert document_id == DOCUMENT_ID

            self.current_version_id = version_id

    tracking_document_service = TrackingDocumentService()

    app.dependency_overrides[
        get_current_user
    ] = override_current_user(fake_user)

    app.dependency_overrides[
        get_document_service
    ] = override_document_service(
        tracking_document_service
    )

    app.dependency_overrides[
        get_document_permission_service
    ] = override_permission_service(
        permission_service
    )

    app.dependency_overrides[
        get_document_upload_service
    ] = lambda: upload_service

    app.dependency_overrides[
        get_document_version_service
    ] = lambda: version_service

    app.dependency_overrides[
        get_document_processing_service
    ] = lambda: processing_service

    try:
        client = TestClient(app)

        response = client.post(
            f"/documents/{DOCUMENT_ID}/upload",
            files={
                "file": (
                    "handbook.pdf",
                    b"Employee Handbook",
                    "application/pdf",
                )
            },
        )

        assert response.status_code == 201

        assert (
            tracking_document_service.current_version_id
            == version_service.version.id
        )

        assert processing_service.called is True
        assert (
            processing_service.document_version_id
            == version_service.version.id
        )

    finally:
        app.dependency_overrides.clear()
