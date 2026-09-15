from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.job import JobStatus


def _normalize_skills(value: Any) -> list[str] | None:
    if value is None:
        return None
    if isinstance(value, str):
        return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


class JobBase(BaseModel):
    title: str
    company: str | None = None
    description: str | None = None
    requirements: str | None = None
    location: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    shift: str | None = None
    job_type: str | None = None
    skills: list[str] | None = None
    years_experience: int | None = Field(default=None, ge=0, le=40)
    openings: int | None = Field(default=1, ge=1, le=500)
    pay_min: float | None = Field(default=None, ge=0)
    pay_max: float | None = Field(default=None, ge=0)
    pay_period: str | None = None
    pay_currency: str = "CAD"
    application_deadline: datetime | None = None
    source: str = "manual_upload"
    external_job_id: str | None = None
    job_url: str | None = None
    external_url: str | None = None
    is_official_link: bool = True
    posted_at: datetime | None = None
    is_custom: bool = False
    application_url: str | None = None
    badge_status: str | None = "live"
    is_active: bool = True

    @field_validator("skills", mode="before")
    @classmethod
    def parse_skills(cls, value):
        return _normalize_skills(value)

    @model_validator(mode="after")
    def pay_range_ok(self):
        if self.pay_min is not None and self.pay_max is not None and self.pay_max < self.pay_min:
            raise ValueError("pay_max must be greater than or equal to pay_min")
        return self


class JobCreate(JobBase):
    status: JobStatus | None = JobStatus.OPEN

    @field_validator("external_job_id", mode="before")
    @classmethod
    def default_external_id(cls, value):
        return value or f"manual-{uuid4()}"


class JobUpdate(BaseModel):
    title: str | None = None
    company: str | None = None
    description: str | None = None
    requirements: str | None = None
    location: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    shift: str | None = None
    job_type: str | None = None
    skills: list[str] | None = None
    years_experience: int | None = Field(default=None, ge=0, le=40)
    openings: int | None = Field(default=None, ge=1, le=500)
    pay_min: float | None = Field(default=None, ge=0)
    pay_max: float | None = Field(default=None, ge=0)
    pay_period: str | None = None
    pay_currency: str | None = None
    application_deadline: datetime | None = None
    job_url: str | None = None
    external_url: str | None = None
    is_official_link: bool | None = None
    status: JobStatus | None = None
    application_url: str | None = None
    badge_status: str | None = None
    is_active: bool | None = None

    @field_validator("skills", mode="before")
    @classmethod
    def parse_skills(cls, value):
        return _normalize_skills(value)


class JobOut(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: JobStatus
    latitude: float | None = None
    longitude: float | None = None
    created_at: datetime
    updated_at: datetime
    match_score: float | None = None
    match_explanation: list[str] | None = None
    distance_km: float | None = None
    distance_known: bool | None = None
    already_applied: bool | None = None
    application_status: str | None = None


class JobListResponse(BaseModel):
    items: list[JobOut]
    total: int
    page: int
    page_size: int
