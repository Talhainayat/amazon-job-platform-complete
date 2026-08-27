from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_admin
from app.models.candidate import Candidate
from app.models.notification import Notification, NotificationChannel
from app.models.user import User, UserRole
from app.schemas.notification import NotificationListResponse, NotificationOut
from app.services.notification_service import notify_candidate

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def _authorize(candidate: Candidate, current_user: User):
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.CANDIDATE and candidate.user_id == current_user.id:
        return
    raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/me", response_model=NotificationListResponse)
def my_notifications(
    unread_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if current_user.role == UserRole.CANDIDATE:
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if candidate:
            query = db.query(Notification).filter(
                (Notification.user_id == current_user.id) | (Notification.candidate_id == candidate.id)
            )
    if unread_only:
        query = query.filter(Notification.is_read.is_(False))
    rows = query.order_by(Notification.created_at.desc()).limit(100).all()
    unread = sum(1 for row in rows if not row.is_read)
    # unread should be counted from full set
    unread_query = db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read.is_(False))
    unread = unread_query.count()
    return NotificationListResponse(items=rows, unread_count=unread, total=len(rows))


@router.get("/unread-count")
def unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .count()
    )
    return {"unread_count": count}


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id not in (None, current_user.id) and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    if current_user.role == UserRole.CANDIDATE:
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if notification.candidate_id and candidate and notification.candidate_id != candidate.id:
            if notification.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@router.post("/read-all", status_code=204)
def mark_all_read(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read.is_(False)).update(
        {"is_read": True}
    )
    db.commit()
    return None


@router.get("/candidates/{candidate_id}", response_model=list[NotificationOut])
def list_notifications(
    candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    _authorize(candidate, current_user)
    return (
        db.query(Notification)
        .filter(Notification.candidate_id == candidate_id)
        .order_by(Notification.created_at.desc())
        .all()
    )


@router.post("/candidates/{candidate_id}/send", response_model=NotificationOut)
def send_notification(
    candidate_id: int,
    message: str,
    channel: NotificationChannel = NotificationChannel.IN_APP,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return notify_candidate(
        db,
        candidate,
        message,
        channel,
        title="Admin update",
        notification_type="admin_update",
    )
