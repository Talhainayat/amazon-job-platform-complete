from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.candidate import CandidateStatus


def _normalize_skills(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    location: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    preferred_city: str | None = None
    preferred_shift: str | None = None
    job_type: str | None = None
    skills: list[str] | None = None
    years_experience: int | None = Field(default=None, ge=0, le=60)
    experience: str | None = None
    education: str | None = None
    availability: str | None = None
    has_vehicle: bool | None = None
    amazon_portal_link: str | None = None
    work_eligibility: str | None = None

    @field_validator("skills", mode="before")
    @classmethod
    def parse_skills(cls, value):
        return _normalize_skills(value)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None):
        if value is None or value == "":
            return value
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) < 7:
            raise ValueError("Enter a valid phone number")
        return value


class CandidateCreate(CandidateBase):
    password: str = Field(min_length=8, max_length=72)


class CandidateUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    location: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    preferred_city: str | None = None
    preferred_shift: str | None = None
    job_type: str | None = None
    skills: list[str] | None = None
    years_experience: int | None = Field(default=None, ge=0, le=60)
    experience: str | None = None
    education: str | None = None
    availability: str | None = None
    has_vehicle: bool | None = None
    amazon_portal_link: str | None = None
    work_eligibility: str | None = None
    alert_sent: bool | None = None
    applied: bool | None = None
    interview_scheduled: bool | None = None
    status: CandidateStatus | None = None

    @field_validator("skills", mode="before")
    @classmethod
    def parse_skills(cls, value):
        return _normalize_skills(value)


class CandidateOut(CandidateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: CandidateStatus
    resume_filename: str | None = None
    has_resume: bool = False
    profile_completion: int = 0
    amazon_portal_link: str | None = None
    work_eligibility: str | None = None
    alert_sent: bool = False
    applied: bool = False
    interview_scheduled: bool = False
    created_at: datetime
    updated_at: datetime


class CandidatePreferenceBase(BaseModel):
    location: str | None = None
    radius_km: float = Field(default=25.0, ge=1, le=500)
    shift: str | None = None
    job_type: str | None = None
    minimum_pay: float | None = Field(default=None, ge=0)
    maximum_pay: float | None = Field(default=None, ge=0)
    availability: str | None = None
    has_vehicle: bool | None = None
    years_experience: int | None = Field(default=None, ge=0, le=60)


class CandidatePreferenceUpdate(CandidatePreferenceBase):
    pass


class CandidatePreferenceOut(CandidatePreferenceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int


class AdminCandidateCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    phone: str | None = None
    email: EmailStr | None = None
    preferred_city: str | None = None
    postal_code: str | None = None
    preferred_shift: str | None = None
    work_eligibility: str | None = None
    amazon_portal_link: str | None = None
    job_type: str | None = None
    location: str | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None):
        if value is None or value == "":
            return value
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) < 7:
            raise ValueError("Enter a valid phone number")
        return value


class CandidateWorkflowUpdate(BaseModel):
    alert_sent: bool | None = None
    applied: bool | None = None
    interview_scheduled: bool | None = None
    amazon_portal_link: str | None = None
    work_eligibility: str | None = None
    status: CandidateStatus | None = None


class CandidateListResponse(BaseModel):
    items: list[CandidateOut]
    total: int
    page: int
    page_size: int
