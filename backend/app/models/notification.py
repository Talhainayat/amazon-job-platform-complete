import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class NotificationChannel(str, enum.Enum):
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PUSH = "push"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_candidate_id", "candidate_id"),
        Index("ix_notifications_user_id", "user_id"),
        Index("ix_notifications_is_read", "is_read"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id", ondelete="CASCADE"), nullable=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="SET NULL"), nullable=True)

    title: Mapped[str] = mapped_column(String(255), nullable=True)
    notification_type: Mapped[str] = mapped_column(String(80), default="general")
    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel), default=NotificationChannel.IN_APP, nullable=False
    )
    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus), default=NotificationStatus.SENT, nullable=False
    )
    message: Mapped[str] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    candidate: Mapped["Candidate"] = relationship("Candidate", back_populates="notifications")
