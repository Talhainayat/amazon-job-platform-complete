import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base_class import Base


class CandidateStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    PLACED = "placed"
    INACTIVE = "inactive"


class Candidate(Base):
    __tablename__ = "candidates"
    __table_args__ = (
        Index("ix_candidates_location", "location"),
        Index("ix_candidates_city", "city"),
        Index("ix_candidates_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=True)

    location: Mapped[str] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(255), nullable=True)
    province: Mapped[str] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)

    preferred_city: Mapped[str] = mapped_column(String(255), nullable=True)
    preferred_shift: Mapped[str] = mapped_column(String(50), nullable=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=True)

    skills: Mapped[list] = mapped_column(JSON, default=lambda: [])
    years_experience: Mapped[int] = mapped_column(Integer, nullable=True)
    experience: Mapped[str] = mapped_column(Text, nullable=True)
    education: Mapped[str] = mapped_column(Text, nullable=True)
    availability: Mapped[str] = mapped_column(String(100), nullable=True)
    has_vehicle: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    resume_path: Mapped[str] = mapped_column(String(1024), nullable=True)
    resume_filename: Mapped[str] = mapped_column(String(255), nullable=True)

    amazon_portal_link: Mapped[str] = mapped_column(String(1024), nullable=True)
    work_eligibility: Mapped[str] = mapped_column(String(255), nullable=True)
    alert_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    interview_scheduled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    status: Mapped[CandidateStatus] = mapped_column(
        Enum(CandidateStatus), default=CandidateStatus.ACTIVE, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )

    user: Mapped["User"] = relationship("User", back_populates="candidate")
    preferences: Mapped["CandidatePreference"] = relationship(
        "CandidatePreference", back_populates="candidate", uselist=False, cascade="all, delete-orphan"
    )
    matches: Mapped[list["Match"]] = relationship("Match", back_populates="candidate", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(
        "Application", back_populates="candidate", cascade="all, delete-orphan"
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="candidate", cascade="all, delete-orphan"
    )
