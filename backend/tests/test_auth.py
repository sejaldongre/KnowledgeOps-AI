from app.core.security import create_access_token
import pytest
from pydantic import ValidationError

from app.schemas.auth import UserRegister


def test_valid_registration_data():
    """Verify valid registration data."""

    data = UserRegister(
        email="employee@example.com",
        password="StrongPassword123!",
        full_name="Test Employee",
    )

    assert data.email == "employee@example.com"
    assert data.full_name == "Test Employee"


def test_short_password_is_rejected():
    """Verify password length validation."""

    with pytest.raises(ValidationError):
        UserRegister(
            email="employee@example.com",
            password="short",
            full_name="Test Employee",
        )


def test_invalid_email_is_rejected():
    """Verify email validation."""

    with pytest.raises(ValidationError):
        UserRegister(
            email="not-an-email",
            password="StrongPassword123!",
            full_name="Test Employee",
        )


def test_create_access_token():
    """Verify that a JWT can be created."""

    token = create_access_token(
        subject="test-user-id",
    )

    assert isinstance(token, str)
    assert len(token) > 20
