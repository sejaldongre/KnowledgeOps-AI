from app.core.exceptions import (
    AppException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
)


def test_app_exception():
    """Verify the base application exception."""

    exception = AppException(
        message="Something went wrong.",
        code="TEST_ERROR",
    )

    assert exception.message == "Something went wrong."
    assert exception.code == "TEST_ERROR"


def test_not_found_exception():
    """Verify the not-found exception."""

    exception = NotFoundException(
        message="Document not found.",
        code="DOCUMENT_NOT_FOUND",
    )

    assert exception.message == "Document not found."
    assert exception.code == "DOCUMENT_NOT_FOUND"


def test_unauthorized_exception():
    """Verify unauthorized exception."""

    exception = UnauthorizedException()

    assert exception.code == "UNAUTHORIZED"


def test_forbidden_exception():
    """Verify forbidden exception."""

    exception = ForbiddenException()

    assert exception.code == "FORBIDDEN"


def test_permission_already_exists_exception_code():
    """Verify duplicate permission uses the correct error code."""

    exception = AppException(
        message="This document permission already exists.",
        code="PERMISSION_ALREADY_EXISTS",
    )

    assert exception.code == "PERMISSION_ALREADY_EXISTS"
