from uuid import UUID
from app.services.document_version import DocumentVersionService
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.services.rbac import RBACService
from app.core.exceptions import (
    ForbiddenException,
    UnauthorizedException,
)
from app.repositories.conversation import (
    ConversationRepository,
)
from app.services.chat import ChatService
from app.repositories.conversation import (
    ConversationRepository,
)
from app.repositories.message import MessageRepository
from app.services.rag import RAGPromptBuilder
from app.repositories.message import MessageRepository
from app.services.chat import ChatService
from app.services.rag import RAGPromptBuilder
from app.services.retrieval import RetrievalService
from app.services.vector_store import ChromaVectorStore
from app.services.document_upload import DocumentUploadService
from app.core.security import decode_access_token
from app.core.config import get_settings
from app.infrastructure.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.document import DocumentService
from app.services.document_permission import (
    DocumentPermissionService,
)
from app.repositories.document_chunk import DocumentChunkRepository
from app.services.document_processing import DocumentProcessingService

bearer_scheme = HTTPBearer()


def get_document_service(
    db: Session = Depends(get_db),
) -> DocumentService:
    """Provide a DocumentService instance for an API request."""

    return DocumentService(db)


def get_auth_service(
    db: Session = Depends(get_db),
) -> AuthService:
    """Provide an AuthService instance."""

    return AuthService(db)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: Session = Depends(get_db),
) -> User:
    """Return the authenticated user from the JWT."""

    token = credentials.credentials

    user_id = decode_access_token(token)

    try:
        user_uuid = UUID(user_id)
    except ValueError as exc:
        raise UnauthorizedException(
            message="Invalid user identifier in access token.",
        ) from exc

    repository = UserRepository(db)

    user = repository.get_by_id(user_uuid)

    if user is None:
        raise UnauthorizedException(
            message="User not found.",
        )

    if not user.is_active:
        raise UnauthorizedException(
            message="User account is inactive.",
        )

    return user


def get_rbac_service(
    db: Session = Depends(get_db),
) -> RBACService:
    """Provide an RBACService instance."""

    return RBACService(db)


def require_role(required_role: str):
    """Require the authenticated user to have a specific role."""

    def role_checker(
        current_user: User = Depends(get_current_user),
        service: RBACService = Depends(get_rbac_service),
    ) -> User:
        """Check whether the current user has the required role."""

        roles = service.get_user_roles(current_user.id)

        has_role = any(
            role.name.lower() == required_role.lower()
            for role in roles
        )

        if not has_role:
            raise ForbiddenException(
                message=(
                    f"Role '{required_role}' is required "
                    "to perform this action."
                ),
            )

        return current_user

    return role_checker


def require_any_role(*required_roles: str):
    """Require the authenticated user to have at least one role."""

    def role_checker(
        current_user: User = Depends(get_current_user),
        service: RBACService = Depends(get_rbac_service),
    ) -> User:
        """Check whether the current user has any required role."""

        user_roles = service.get_user_roles(current_user.id)

        user_role_names = {
            role.name.lower()
            for role in user_roles
        }

        allowed_roles = {
            role.lower()
            for role in required_roles
        }

        if not user_role_names.intersection(allowed_roles):
            raise ForbiddenException(
                message=(
                    "You do not have any of the required roles."
                ),
            )

        return current_user

    return role_checker


def get_document_permission_service(
    db: Session = Depends(get_db),
) -> DocumentPermissionService:
    """Provide a DocumentPermissionService instance."""

    return DocumentPermissionService(db)


def get_document_version_service(
    db: Session = Depends(get_db),
) -> DocumentVersionService:
    """Provide a DocumentVersionService instance."""

    return DocumentVersionService(db)


def get_document_upload_service() -> DocumentUploadService:
    """Provide a DocumentUploadService instance."""

    return DocumentUploadService()


def get_document_processing_service(
    db: Session = Depends(get_db),
) -> DocumentProcessingService:
    """Provide a DocumentProcessingService instance."""

    chunk_repository = DocumentChunkRepository(db)

    return DocumentProcessingService(
        chunk_repository=chunk_repository,
    )


def get_retrieval_service(
    db: Session = Depends(get_db),
) -> RetrievalService:
    """Provide a RetrievalService instance."""

    permission_service = DocumentPermissionService(db)

    vector_store = ChromaVectorStore()

    return RetrievalService(
        vector_store=vector_store,
        permission_service=permission_service,
    )


def get_chat_service(
    db: Session = Depends(get_db),
) -> ChatService:
    """Provide a ChatService instance."""

    conversation_repository = (
        ConversationRepository(db)
    )

    message_repository = (
        MessageRepository(db)
    )

    retrieval_service = get_retrieval_service(db)

    prompt_builder = RAGPromptBuilder()

    settings = get_settings()

    return ChatService(
        conversation_repository=(
            conversation_repository
        ),
        message_repository=(
            message_repository
        ),
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        settings=settings,
    )


def get_chat_service(
    db: Session = Depends(get_db),
) -> ChatService:
    """Provide a ChatService instance."""

    conversation_repository = (
        ConversationRepository(db)
    )

    message_repository = (
        MessageRepository(db)
    )

    permission_service = (
        DocumentPermissionService(db)
    )

    vector_store = ChromaVectorStore()

    retrieval_service = RetrievalService(
        vector_store=vector_store,
        permission_service=permission_service,
    )

    prompt_builder = RAGPromptBuilder()

    settings = get_settings()

    return ChatService(
        conversation_repository=(
            conversation_repository
        ),
        message_repository=(
            message_repository
        ),
        retrieval_service=retrieval_service,
        prompt_builder=prompt_builder,
        settings=settings,
    )
