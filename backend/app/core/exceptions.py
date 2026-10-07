class AppException(Exception):
    """Base exception for application-level errors."""

    def __init__(
        self,
        message: str,
        code: str = "APPLICATION_ERROR",
    ) -> None:
        self.message = message
        self.code = code

        super().__init__(message)


class NotFoundException(AppException):
    """Raised when a requested resource does not exist."""

    def __init__(
        self,
        message: str = "Resource not found.",
        code: str = "RESOURCE_NOT_FOUND",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
        )


class UnauthorizedException(AppException):
    """Raised when authentication is required or invalid."""

    def __init__(
        self,
        message: str = "Authentication required.",
        code: str = "UNAUTHORIZED",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
        )


class ForbiddenException(AppException):
    """Raised when the user lacks permission."""

    def __init__(
        self,
        message: str = "You do not have permission to perform this action.",
        code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(
            message=message,
            code=code,
        )
