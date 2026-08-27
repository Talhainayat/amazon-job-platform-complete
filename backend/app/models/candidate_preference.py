from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class CandidatePreference(Base):
    __tablename__ = "candidate_preferences"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(
        ForeignKey("candidates.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    location: Mapped[str] = mapped_column(String(255), nullable=True)
    radius_km: Mapped[float] = mapped_column(Float, default=25.0)
    shift: Mapped[str] = mapped_column(String(50), nullable=True)
    job_type: Mapped[str] = mapped_column(String(100), nullable=True)
    minimum_pay: Mapped[float] = mapped_column(Float, nullable=True)
    maximum_pay: Mapped[float] = mapped_column(Float, nullable=True)
    availability: Mapped[str] = mapped_column(String(100), nullable=True)
    has_vehicle: Mapped[bool] = mapped_column(Boolean, nullable=True)
    years_experience: Mapped[int] = mapped_column(Integer, nullable=True)

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="preferences")
