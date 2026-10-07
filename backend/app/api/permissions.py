from fastapi import APIRouter, Depends, status


from app.api.dependencies import require_role

from app.models.document_permission import DocumentPermission
from app.models.user import User
from app.schemas.rbac import (
    DocumentPermissionCreate,
    DocumentPermissionResponse,
)
from app.api.dependencies import (
    get_document_permission_service,
    require_role,
)
from app.services.document_permission import (
    DocumentPermissionService,
)

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.post(
    "",
    response_model=DocumentPermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_permission(
    data: DocumentPermissionCreate,
    current_user: User = Depends(
        require_role("admin")
    ),
    service: DocumentPermissionService = Depends(
        get_document_permission_service
    ),
) -> DocumentPermissionResponse:
    """Grant a document permission to a user or role."""

    permission = service.create_permission(
        document_id=data.document_id,
        user_id=data.user_id,
        role_id=data.role_id,
        permission=data.permission,
    )

    return DocumentPermissionResponse.model_validate(
        permission
    )
