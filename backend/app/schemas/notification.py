from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationChannel, NotificationStatus


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    candidate_id: int | None
    job_id: int | None
    application_id: int | None = None
    title: str | None
    notification_type: str | None = "general"
    channel: NotificationChannel
    status: NotificationStatus
    message: str | None
    is_read: bool = False
    sent_at: datetime | None
    created_at: datetime


class NotificationListResponse(BaseModel):
    items: list[NotificationOut]
    unread_count: int
    total: int
