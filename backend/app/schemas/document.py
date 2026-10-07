from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.document import DocumentStatus


class DocumentCreate(BaseModel):
    """Request schema for creating a document."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    filename: str = Field(
        ...,
        min_length=1,
        max_length=500,
    )

    file_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    file_size: int = Field(
        ...,
        gt=0,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    folder_id: UUID | None = None


class DocumentResponse(BaseModel):
    """Response schema for returning document information."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None
    status: DocumentStatus
    owner_id: UUID
    folder_id: UUID | None
    created_at: datetime
    updated_at: datetime


class DocumentVersionResponse(BaseModel):
    """Response schema for a document version."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    version_number: int
    storage_path: str
    file_hash: str
    created_by: UUID
    created_at: datetime


class DocumentUpdate(BaseModel):
    """Request schema for updating document metadata."""

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
    )

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        """Require at least one field to be updated."""

        if self.title is None and self.description is None:
            raise ValueError(
                "At least one field must be provided for update."
            )

        return self
