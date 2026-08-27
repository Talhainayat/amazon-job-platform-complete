from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class RegisterCandidateRequest(BaseModel):
    email: EmailStr
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
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class MeResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    candidate_id: int | None = None
    name: str | None = None
    is_active: bool = True
