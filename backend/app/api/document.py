from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.api.dependencies import (
    get_current_user,
    get_document_permission_service,
    get_document_processing_service,
    get_document_service,
    get_document_upload_service,
    get_document_version_service,
)
from app.models.document import DocumentStatus
from app.models.document_permission import PermissionLevel
from app.models.user import User
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    DocumentVersionResponse,
)
from app.services.document import DocumentService
from app.services.document_permission import DocumentPermissionService
from app.services.document_processing import DocumentProcessingService
from app.services.document_upload import DocumentUploadService
from app.services.document_version import DocumentVersionService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "",
    response_model=DocumentResponse,
    status_code=201,
)
def create_document(
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(
        get_document_service
    ),
) -> DocumentResponse:
    """Create a new document."""

    document = document_service.create_document(
        title=payload.title,
        filename=payload.filename,
        file_type=payload.file_type,
        file_size=payload.file_size,
        owner_id=current_user.id,
        description=payload.description,
        folder_id=payload.folder_id,
    )

    return DocumentResponse.model_validate(document)


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents(
    status: DocumentStatus | None = None,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(
        get_document_service
    ),
) -> list[DocumentResponse]:
    """Return documents owned by the current user."""

    if status is not None:
        documents = (
            document_service.get_documents_by_owner_and_status(
                owner_id=current_user.id,
                status=status,
            )
        )
    else:
        documents = document_service.get_documents_by_owner(
            owner_id=current_user.id
        )

    return [
        DocumentResponse.model_validate(document)
        for document in documents
    ]


@router.post(
    "/{document_id}/upload",
    response_model=DocumentVersionResponse,
    status_code=201,
)
def upload_document_version(
    document_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(
        get_document_service
    ),
    permission_service: DocumentPermissionService = Depends(
        get_document_permission_service
    ),
    upload_service: DocumentUploadService = Depends(
        get_document_upload_service
    ),
    version_service: DocumentVersionService = Depends(
        get_document_version_service
    ),
    processing_service: DocumentProcessingService = Depends(
        get_document_processing_service
    ),
) -> DocumentVersionResponse:
    """Upload and process a new document version."""

    document = document_service.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    permission_service.require_permission(
        user_id=current_user.id,
        document_id=document.id,
        permission=PermissionLevel.EDIT,
    )

    try:
        # 1. Mark document as processing.
        document_service.set_status(
            document_id=document.id,
            status=DocumentStatus.PROCESSING,
        )

        # 2. Read uploaded file.
        content = file.file.read()

        if not content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        # 3. Save file to local storage.
        storage_path, file_hash = upload_service.save_file(
            filename=file.filename or "uploaded_file",
            content=content,
        )

        # 4. Create document version.
        version = version_service.create_version(
            document_id=document.id,
            storage_path=storage_path,
            file_hash=file_hash,
            created_by=current_user.id,
        )

        # 5. Extract, clean, chunk and index document.
        processing_service.process(
            document_version_id=version.id,
            document_id=document.id,
            file_path=storage_path,
        )

        # 6. Set this version as the current version.
        document_service.set_current_version(
            document_id=document.id,
            version_id=version.id,
        )

        # 7. Mark document as successfully indexed.
        document_service.set_status(
            document_id=document.id,
            status=DocumentStatus.INDEXED,
        )

        return DocumentVersionResponse.model_validate(
            version
        )

    except HTTPException:
        document_service.set_status(
            document_id=document.id,
            status=DocumentStatus.FAILED,
        )
        raise

    except Exception:
        document_service.set_status(
            document_id=document.id,
            status=DocumentStatus.FAILED,
        )
        raise


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(
        get_document_service
    ),
    permission_service: DocumentPermissionService = Depends(
        get_document_permission_service
    ),
) -> DocumentResponse:
    """Get a document."""

    document = document_service.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    permission_service.require_permission(
        user_id=current_user.id,
        document_id=document.id,
        permission=PermissionLevel.VIEW,
    )

    return DocumentResponse.model_validate(document)


@router.get(
    "/{document_id}/versions",
    response_model=list[DocumentVersionResponse],
)
def get_document_versions(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(
        get_document_service
    ),
    permission_service: DocumentPermissionService = Depends(
        get_document_permission_service
    ),
    version_service: DocumentVersionService = Depends(
        get_document_version_service
    ),
) -> list[DocumentVersionResponse]:
    """Get all versions of a document."""

    document = document_service.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    permission_service.require_permission(
        user_id=current_user.id,
        document_id=document.id,
        permission=PermissionLevel.VIEW,
    )

    versions = version_service.get_versions(
        document_id
    )

    return [
        DocumentVersionResponse.model_validate(version)
        for version in versions
    ]


@router.patch(
    "/{document_id}",
    response_model=DocumentResponse,
)
def update_document(
    document_id: UUID,
    payload: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(
        get_document_service
    ),
    permission_service: DocumentPermissionService = Depends(
        get_document_permission_service
    ),
) -> DocumentResponse:
    """Update document metadata."""

    document = document_service.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    permission_service.require_permission(
        user_id=current_user.id,
        document_id=document.id,
        permission=PermissionLevel.EDIT,
    )

    updated_document = document_service.update_document(
        document_id=document.id,
        title=payload.title,
        description=payload.description,
    )

    if updated_document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return DocumentResponse.model_validate(
        updated_document
    )


@router.delete(
    "/{document_id}",
    status_code=204,
)
def delete_document(
    document_id: UUID,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends(
        get_document_service
    ),
    permission_service: DocumentPermissionService = Depends(
        get_document_permission_service
    ),
) -> None:
    """Delete a document."""

    document = document_service.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    permission_service.require_permission(
        user_id=current_user.id,
        document_id=document.id,
        permission=PermissionLevel.DELETE,
    )

    deleted = document_service.delete_document(
        document_id=document.id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )
