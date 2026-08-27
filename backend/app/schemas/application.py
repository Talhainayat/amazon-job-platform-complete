from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.application import ApplicationStatus, InterviewStatus


class ApplicationCreate(BaseModel):
    candidate_id: int | None = None
    job_id: int
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus | None = None
    notes: str | None = None
    interview_status: InterviewStatus | None = None
    interview_date: datetime | None = None


class ApplicationJobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str | None = None
    location: str | None = None
    status: str


class ApplicationCandidateSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: str | None = None
    location: str | None = None


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    applied_at: datetime | None
    notes: str | None
    interview_status: InterviewStatus
    interview_date: datetime | None
    created_at: datetime
    updated_at: datetime
    job: ApplicationJobSummary | None = None
    candidate: ApplicationCandidateSummary | None = None
    match_score: float | None = None


class ApplicationListResponse(BaseModel):
    items: list[ApplicationOut]
    total: int
    page: int
    page_size: int
