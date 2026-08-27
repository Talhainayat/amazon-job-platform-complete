from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class ManagedSite(Base):
    __tablename__ = "managed_sites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=True)
    portal_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    feed_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    available_slots: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))