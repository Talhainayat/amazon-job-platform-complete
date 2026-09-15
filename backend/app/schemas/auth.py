import re

from pydantic import BaseModel, Field, field_validator

from app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole


def _normalize_email(value: str) -> str:
    normalized = value.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized):
        raise ValueError("Invalid email address")
    return normalized


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)


class RegisterCandidateRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=72)
    name: str = Field(min_length=2, max_length=255)
    phone: str | None = None
    location: str | None = None
    postal_code: str | None = None
    preferred_shift: str | None = None
    work_eligibility: str | None = None
    amazon_portal_link: str | None = None

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_email(value)


class MeResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    candidate_id: int | None = None
    name: str | None = None
    is_active: bool = True
