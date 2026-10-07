from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import UserRegister
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.core.exceptions import (
    AppException,
    UnauthorizedException,
)


class AuthService:
    """Service responsible for authentication-related operations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = UserRepository(db)

    def register_user(self, data: UserRegister) -> User:
        """Register a new user."""

        existing_user = self.repository.get_by_email(
            data.email
        )

        if existing_user is not None:
            raise AppException(
                message="A user with this email already exists.",
                code="EMAIL_ALREADY_EXISTS",
            )

        user = User(
            email=data.email,
            full_name=data.full_name,
            password_hash=hash_password(data.password),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def login_user(
        self,
        email: str,
        password: str,
    ) -> str:
        """Authenticate a user and return a JWT access token."""

        user = self.repository.get_by_email(email)

        if user is None:
            raise UnauthorizedException(
                message="Invalid email or password.",
            )

        if not user.is_active:
            raise UnauthorizedException(
                message="User account is inactive.",
            )

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise UnauthorizedException(
                message="Invalid email or password.",
            )

        return create_access_token(
            subject=str(user.id),
        )
