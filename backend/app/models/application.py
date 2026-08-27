import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Index, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class ApplicationStatus(str, enum.Enum):
    SAVED = "saved"
    APPLIED = "applied"
    REVIEWING = "reviewing"
    UNDER_REVIEW = "under_review"
    SHORTLISTED = "shortlisted"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class InterviewStatus(str, enum.Enum):
    NOT_SCHEDULED = "not_scheduled"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", name="uq_application_candidate_job"),
        Index("ix_applications_status", "status"),
        Index("ix_applications_job_id", "job_id"),
        Index("ix_applications_candidate_id", "candidate_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus), default=ApplicationStatus.APPLIED, nullable=False
    )
    applied_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    interview_status: Mapped[InterviewStatus] = mapped_column(
        Enum(InterviewStatus), default=InterviewStatus.NOT_SCHEDULED, nullable=False
    )
    interview_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="applications")
    job: Mapped["Job"] = relationship("Job", back_populates="applications")
