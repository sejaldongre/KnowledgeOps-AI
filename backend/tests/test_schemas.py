from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.models.document import DocumentStatus
from app.schemas.document import DocumentCreate, DocumentResponse


def test_document_create_schema():
    """Verify valid document creation data."""

    document = DocumentCreate(
        title="Employee Handbook",
        filename="employee_handbook.pdf",
        file_type="application/pdf",
        file_size=245760,
        description="Company HR policies",
    )

    assert document.title == "Employee Handbook"
    assert document.filename == "employee_handbook.pdf"
    assert document.file_type == "application/pdf"
    assert document.file_size == 245760
    assert document.description == "Company HR policies"
    assert document.folder_id is None


def test_document_response_schema():
    """Verify document response serialization."""

    document = DocumentResponse(
        id=uuid4(),
        title="Employee Handbook",
        description="Company HR policies",
        status=DocumentStatus.UPLOADED,
        owner_id=uuid4(),
        folder_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    assert isinstance(document.id, UUID)
    assert document.title == "Employee Handbook"
    assert document.description == "Company HR policies"
    assert document.status == DocumentStatus.UPLOADED
    assert isinstance(document.owner_id, UUID)
    assert document.folder_id is None
