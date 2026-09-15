import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base_class import Base


class JobStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"
    EXPIRED = "expired"


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("source", "external_job_id", name="uq_job_source_external_id"),
        Index("ix_jobs_location", "location"),
        Index("ix_jobs_status", "status"),
        Index("ix_jobs_city", "city"),
        Index("ix_jobs_job_type", "job_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    requirements: Mapped[str] = mapped_column(Text, nullable=True)

    location: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(255), nullable=True)
    province: Mapped[str] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    shift: Mapped[str] = mapped_column(String(50), nullable=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=True)
    skills: Mapped[list] = mapped_column(JSON, default=lambda: [])
    years_experience: Mapped[int] = mapped_column(Integer, nullable=True)
    openings: Mapped[int] = mapped_column(Integer, default=1)
    pay_min: Mapped[float] = mapped_column(Float, nullable=True)
    pay_max: Mapped[float] = mapped_column(Float, nullable=True)
    pay_period: Mapped[str] = mapped_column(String(30), nullable=True)
    pay_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="CAD")
    application_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    source: Mapped[str] = mapped_column(String(100), nullable=False)
    external_job_id: Mapped[str] = mapped_column(String(255), nullable=False)
    job_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    external_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    is_official_link: Mapped[bool] = mapped_column(nullable=False, default=True)

    posted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.OPEN, nullable=False)

    # Custom job fields
    is_custom: Mapped[bool] = mapped_column(nullable=False, default=False)
    application_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    badge_status: Mapped[str] = mapped_column(String(50), nullable=True, default="live")  # "live" or "urgent"
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    matches: Mapped[list["Match"]] = relationship("Match", back_populates="job", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="job", cascade="all, delete-orphan"
    )
