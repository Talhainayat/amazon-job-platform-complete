"""
Notification service.

In-app notifications are always persisted. Email/SMS/WhatsApp/push are
optional channels and never required for the product to work.

WhatsApp/SMS uses Twilio when credentials are present, otherwise posts
to ALERT_WEBHOOK_URL. Manager alerts never store employer passwords.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import httpx
import smtplib
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.match import Match
from app.models.notification import Notification, NotificationChannel, NotificationStatus
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


def _send_email(to_email: str, subject: str, body: str) -> bool:
    if not settings.EMAIL_ENABLED:
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email
        msg.set_content(body)
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception:
        logger.exception("Email send failed")
        return False


def _normalize_e164(phone: str | None) -> str:
    raw = (phone or "").strip()
    if not raw:
        return ""
    if raw.startswith("+"):
        digits = "+" + "".join(ch for ch in raw[1:] if ch.isdigit())
        return digits
    digits = "".join(ch for ch in raw if ch.isdigit())
    return f"+{digits}" if digits else ""


def _whatsapp_address(number: str) -> str:
    normalized = _normalize_e164(number.replace("whatsapp:", ""))
    return f"whatsapp:{normalized}" if normalized else ""


def _twilio_configured() -> bool:
    return bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN)


def send_twilio_message(*, to_phone: str, body: str, whatsapp: bool = True) -> bool:
    if not _twilio_configured():
        return False
    to_value = _whatsapp_address(to_phone) if whatsapp else _normalize_e164(to_phone)
    from_raw = settings.TWILIO_WHATSAPP_NUMBER if whatsapp else (settings.TWILIO_SMS_NUMBER or settings.TWILIO_WHATSAPP_NUMBER)
    from_value = _whatsapp_address(from_raw) if whatsapp else _normalize_e164(from_raw)
    if not to_value or not from_value:
        logger.warning("Twilio skipped: missing from/to numbers")
        return False
    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(
                url,
                data={"From": from_value, "To": to_value, "Body": body},
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
            )
        if response.status_code >= 400:
            logger.warning("Twilio error %s: %s", response.status_code, response.text[:300])
            return False
        return True
    except Exception:
        logger.exception("Twilio request failed")
        return False


def send_webhook_alert(payload: dict) -> bool:
    url = (settings.ALERT_WEBHOOK_URL or "").strip()
    if not url:
        return False
    try:
        with httpx.Client(timeout=15.0) as client:
            response = client.post(url, json=payload)
        return response.status_code < 400
    except Exception:
        logger.exception("Alert webhook failed")
        return False


def dispatch_manager_channel(body: str, payload: dict) -> bool:
    """WhatsApp first, then SMS, then HTTP webhook."""
    to_phone = settings.ADMIN_ALERT_PHONE_NUMBER or "+923332158308"
    sent = False
    if _twilio_configured():
        if settings.TWILIO_WHATSAPP_NUMBER:
            sent = send_twilio_message(to_phone=to_phone, body=body, whatsapp=True)
        if not sent:
            sent = send_twilio_message(to_phone=to_phone, body=body, whatsapp=False)
    if not sent:
        sent = send_webhook_alert(payload)
    return sent


def create_notification(
    db: Session,
    *,
    message: str,
    title: str | None = None,
    notification_type: str = "general",
    user_id: int | None = None,
    candidate=None,
    job_id: int | None = None,
    application_id: int | None = None,
    channel: NotificationChannel = NotificationChannel.IN_APP,
    commit: bool = True,
    status: NotificationStatus | None = None,
) -> Notification:
    candidate_id = candidate.id if candidate is not None else None
    resolved_user_id = user_id
    if resolved_user_id is None and candidate is not None:
        resolved_user_id = candidate.user_id

    notification = Notification(
        user_id=resolved_user_id,
        candidate_id=candidate_id,
        job_id=job_id,
        application_id=application_id,
        title=title or "Update",
        notification_type=notification_type,
        channel=channel,
        message=message,
        status=status or (
            NotificationStatus.SENT if channel == NotificationChannel.IN_APP else NotificationStatus.PENDING
        ),
        is_read=False,
        sent_at=datetime.now(timezone.utc) if channel == NotificationChannel.IN_APP else None,
    )
    db.add(notification)
    db.flush()

    if channel == NotificationChannel.EMAIL and candidate is not None:
        sent = _send_email(candidate.email, title or "Job Platform Notification", message)
        notification.status = NotificationStatus.SENT if sent else NotificationStatus.PENDING
        if sent:
            notification.sent_at = datetime.now(timezone.utc)

    if commit:
        db.commit()
        db.refresh(notification)
    return notification


def notify_candidate(
    db: Session,
    candidate,
    message: str,
    channel: NotificationChannel = NotificationChannel.IN_APP,
    job_id: int | None = None,
    title: str | None = None,
    notification_type: str = "general",
) -> Notification:
    return create_notification(
        db,
        message=message,
        title=title,
        notification_type=notification_type,
        candidate=candidate,
        job_id=job_id,
        channel=channel,
    )


def notify_admins_in_app(
    db: Session,
    *,
    title: str,
    message: str,
    notification_type: str,
    job_id: int | None = None,
    candidate=None,
) -> None:
    admins = db.query(User).filter(User.role == UserRole.ADMIN, User.is_active.is_(True)).all()
    for admin in admins:
        create_notification(
            db,
            message=message,
            title=title,
            notification_type=notification_type,
            user_id=admin.id,
            candidate=candidate,
            job_id=job_id,
            commit=False,
        )


def build_manager_alert_message(
    *,
    candidate_name: str,
    location: str,
    shift: str,
    match_score: float,
    portal_link: str,
    job_title: str | None = None,
) -> str:
    job_line = f"\nJob: {job_title}" if job_title else ""
    return (
        "URGENT: High-match Amazon slot found\n"
        f"Candidate: {candidate_name}\n"
        f"Target location: {location}\n"
        f"Shift: {shift}\n"
        f"Match score: {int(round(match_score))}%{job_line}\n"
        f"Open candidate portal: {portal_link}\n"
        "Claim this slot manually now."
    )


def send_manager_match_alert(db: Session, match: Match, commit: bool = True) -> bool:
    """Alert the manager when a candidate matches a job above the threshold."""
    if match.manager_alerted_at:
        return False
    if match.match_score < settings.HIGH_MATCH_THRESHOLD:
        return False

    candidate = match.candidate
    job = match.job
    if candidate is None or job is None:
        return False

    location = (
        candidate.preferred_city
        or candidate.city
        or candidate.location
        or job.city
        or job.location
        or "Not set"
    )
    shift = job.shift or candidate.preferred_shift or "Not set"
    portal = (candidate.amazon_portal_link or job.job_url or "").strip() or "No portal link on file"
    body = build_manager_alert_message(
        candidate_name=candidate.name,
        location=location,
        shift=shift,
        match_score=match.match_score,
        portal_link=portal,
        job_title=job.title,
    )
    payload = {
        "type": "high_match_alert",
        "to": settings.ADMIN_ALERT_PHONE_NUMBER,
        "candidate_id": candidate.id,
        "candidate_name": candidate.name,
        "location": location,
        "shift": shift,
        "match_score": match.match_score,
        "job_id": job.id,
        "job_title": job.title,
        "portal_link": portal,
        "message": body,
    }
    sent = dispatch_manager_channel(body, payload)
    if sent:
        match.manager_alerted_at = datetime.now(timezone.utc)
        candidate.alert_sent = True
    channel = NotificationChannel.WHATSAPP if settings.TWILIO_WHATSAPP_NUMBER else NotificationChannel.SMS
    create_notification(
        db,
        message=body,
        title="URGENT: high-match slot",
        notification_type="manager_high_match",
        candidate=candidate,
        job_id=job.id,
        channel=channel if sent else NotificationChannel.IN_APP,
        status=NotificationStatus.SENT if sent else NotificationStatus.PENDING,
        commit=False,
    )
    notify_admins_in_app(
        db,
        title="Speed-apply: high match",
        message=body,
        notification_type="manager_high_match",
        job_id=job.id,
        candidate=candidate,
    )
    if commit:
        db.commit()
    return sent
