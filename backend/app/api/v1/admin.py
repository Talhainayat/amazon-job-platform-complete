from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, require_admin
from app.models.application import Application, ApplicationStatus, InterviewStatus
from app.models.candidate import Candidate, CandidateStatus
from app.models.job import Job, JobStatus
from app.models.match import Match
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    total_candidates = db.query(func.count(Candidate.id)).scalar() or 0
    active_candidates = (
        db.query(func.count(Candidate.id)).filter(Candidate.status == CandidateStatus.ACTIVE).scalar() or 0
    )
    total_jobs = db.query(func.count(Job.id)).scalar() or 0
    open_jobs = db.query(func.count(Job.id)).filter(Job.status == JobStatus.OPEN).scalar() or 0
    closed_jobs = db.query(func.count(Job.id)).filter(Job.status == JobStatus.CLOSED).scalar() or 0
    total_matches = db.query(func.count(Match.id)).scalar() or 0
    total_applications = db.query(func.count(Application.id)).scalar() or 0
    pending_applications = (
        db.query(func.count(Application.id))
        .filter(Application.status.in_([ApplicationStatus.APPLIED, ApplicationStatus.REVIEWING, ApplicationStatus.UNDER_REVIEW]))
        .scalar()
        or 0
    )
    interviews = (
        db.query(func.count(Application.id))
        .filter(
            (Application.status == ApplicationStatus.INTERVIEW)
            | (Application.interview_status == InterviewStatus.SCHEDULED)
        )
        .scalar()
        or 0
    )
    hires = db.query(func.count(Application.id)).filter(Application.status == ApplicationStatus.HIRED).scalar() or 0
    avg_match = db.query(func.avg(Match.match_score)).scalar()
    total_notifications = db.query(func.count(Notification.id)).scalar() or 0

    recent_applications = (
        db.query(Application)
        .options(joinedload(Application.candidate), joinedload(Application.job))
        .order_by(Application.created_at.desc())
        .limit(8)
        .all()
    )
    recent_jobs = db.query(Job).order_by(Job.created_at.desc()).limit(5).all()

    return {
        "total_candidates": total_candidates,
        "active_candidates": active_candidates,
        "total_jobs": total_jobs,
        "open_jobs": open_jobs,
        "closed_jobs": closed_jobs,
        "total_matches": total_matches,
        "total_applications": total_applications,
        "pending_applications": pending_applications,
        "interviews": interviews,
        "hires": hires,
        "average_match_score": round(float(avg_match), 1) if avg_match is not None else 0,
        "total_notifications": total_notifications,
        "recent_activity": [
            {
                "type": "application",
                "id": app.id,
                "label": f"{app.candidate.name if app.candidate else 'Candidate'} applied to {app.job.title if app.job else 'a job'}",
                "status": app.status.value,
                "created_at": app.created_at,
            }
            for app in recent_applications
        ],
        "recent_jobs": [
            {"id": job.id, "title": job.title, "status": job.status.value, "location": job.location}
            for job in recent_jobs
        ],
    }
