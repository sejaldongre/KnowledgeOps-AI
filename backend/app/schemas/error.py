from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Structured API error information."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standard API error response."""

    error: ErrorDetail
