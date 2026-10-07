from pydantic import BaseModel, ConfigDict, EmailStr, Field
from uuid import UUID


class UserRegister(BaseModel):
    """Request schema for user registration."""

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )


class UserResponse(BaseModel):
    """Safe user representation returned by the API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool


class TokenResponse(BaseModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    """Login request data."""

    email: EmailStr
    password: str
