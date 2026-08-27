from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base_class import Base


class Match(Base):
    __tablename__ = "matches"
    __table_args__ = (
        UniqueConstraint("candidate_id", "job_id", name="uq_match_candidate_job"),
        Index("ix_matches_score", "match_score"),
        Index("ix_matches_candidate_id", "candidate_id"),
        Index("ix_matches_job_id", "job_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)

    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    matched_criteria: Mapped[dict] = mapped_column(JSON, default=lambda: {})
    unmatched_criteria: Mapped[dict] = mapped_column(JSON, default=lambda: {})
    explanation: Mapped[list] = mapped_column(JSON, default=lambda: [])
    distance_km: Mapped[float] = mapped_column(Float, nullable=True)
    distance_known: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="new")
    manager_alerted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    matched_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="matches")
    job: Mapped["Job"] = relationship("Job", back_populates="matches")
