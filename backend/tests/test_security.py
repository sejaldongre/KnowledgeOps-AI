from app.core.security import hash_password, verify_password
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedException
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hashing():
    """Verify that passwords are hashed and can be verified."""

    password = "StrongPassword123!"

    hashed_password = hash_password(password)

    assert hashed_password != password
    assert hashed_password != ""

    assert verify_password(
        password,
        hashed_password,
    )


def test_wrong_password_fails():
    """Verify that an incorrect password is rejected."""

    password = "StrongPassword123!"

    hashed_password = hash_password(password)

    assert not verify_password(
        "WrongPassword123!",
        hashed_password,
    )


def test_same_password_produces_different_hashes():
    """Verify that password hashing uses a salt."""

    password = "StrongPassword123!"

    hash_one = hash_password(password)
    hash_two = hash_password(password)

    assert hash_one != hash_two

    assert verify_password(password, hash_one)
    assert verify_password(password, hash_two)


def test_access_token_round_trip():
    """Verify that a valid JWT can be created and decoded."""

    user_id = "3600d94c-aac8-4e8c-86d2-c9f9c6f4c72d"

    token = create_access_token(user_id)

    assert decode_access_token(token) == user_id


def test_invalid_access_token_is_rejected():
    """Verify that a malformed JWT is rejected."""

    with pytest.raises(UnauthorizedException):
        decode_access_token("this-is-not-a-valid-jwt")


def test_tampered_access_token_is_rejected():
    """Verify that a modified JWT signature is rejected."""

    user_id = "3600d94c-aac8-4e8c-86d2-c9f9c6f4c72d"

    token = create_access_token(user_id)

    parts = token.split(".")

    assert len(parts) == 3

    signature = parts[2]

    # Change a significant character in the signature.
    tampered_signature = (
        ("a" if signature[0] != "a" else "b")
        + signature[1:]
    )

    tampered_token = ".".join(
        [
            parts[0],
            parts[1],
            tampered_signature,
        ]
    )

    with pytest.raises(UnauthorizedException):
        decode_access_token(tampered_token)


def test_expired_access_token_is_rejected():
    """Verify that an expired JWT is rejected."""

    settings = get_settings()

    expired_time = datetime.now(timezone.utc) - timedelta(
        minutes=5
    )

    payload = {
        "sub": "3600d94c-aac8-4e8c-86d2-c9f9c6f4c72d",
        "exp": expired_time,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(UnauthorizedException):
        decode_access_token(token)


def test_access_token_without_subject_is_rejected():
    """Verify that a JWT without sub is rejected."""

    settings = get_settings()

    payload = {
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=5),
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(UnauthorizedException):
        decode_access_token(token)
