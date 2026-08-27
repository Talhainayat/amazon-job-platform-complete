from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db, require_admin
from app.models.application import Application, ApplicationStatus, InterviewStatus
from app.models.audit_log import AuditLog
from app.models.candidate import Candidate
from app.models.job import Job, JobStatus
from app.models.match import Match
from app.models.user import User, UserRole
from app.schemas.application import ApplicationCreate, ApplicationListResponse, ApplicationOut, ApplicationUpdate
from app.services.notification_service import create_notification

router = APIRouter(prefix="/api/applications", tags=["applications"])

CANDIDATE_ALLOWED_STATUSES = {ApplicationStatus.APPLIED, ApplicationStatus.WITHDRAWN, ApplicationStatus.SAVED}
ADMIN_ONLY_STATUSES = {
    ApplicationStatus.REVIEWING,
    ApplicationStatus.UNDER_REVIEW,
    ApplicationStatus.SHORTLISTED,
    ApplicationStatus.INTERVIEW,
    ApplicationStatus.OFFER,
    ApplicationStatus.HIRED,
    ApplicationStatus.REJECTED,
}


def _authorize(candidate: Candidate, current_user: User):
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.CANDIDATE and candidate.user_id == current_user.id:
        return
    raise HTTPException(status_code=403, detail="Not authorized")


def _serialize(application: Application, match_score: float | None = None) -> dict:
    data = ApplicationOut.model_validate(application).model_dump()
    if application.job:
        data["job"] = {
            "id": application.job.id,
            "title": application.job.title,
            "company": application.job.company,
            "location": application.job.location,
            "status": application.job.status.value,
        }
    if application.candidate:
        data["candidate"] = {
            "id": application.candidate.id,
            "name": application.candidate.name,
            "email": application.candidate.email,
            "phone": application.candidate.phone,
            "location": application.candidate.location,
        }
    data["match_score"] = match_score
    return data


@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(
    payload: ApplicationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    candidate_id = payload.candidate_id
    if current_user.role == UserRole.CANDIDATE:
        mine = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not mine:
            raise HTTPException(status_code=404, detail="Candidate profile not found")
        if candidate_id and candidate_id != mine.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        candidate = mine
    else:
        if not candidate_id:
            raise HTTPException(status_code=400, detail="candidate_id is required")
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        _authorize(candidate, current_user)

    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.OPEN:
        raise HTTPException(status_code=400, detail="This job is not open for applications")

    existing = (
        db.query(Application)
        .filter(Application.candidate_id == candidate.id, Application.job_id == job.id)
        .first()
    )
    if existing and existing.status != ApplicationStatus.WITHDRAWN:
        raise HTTPException(status_code=409, detail="You have already applied to this job")

    now = datetime.now(timezone.utc)
    if existing:
        existing.status = ApplicationStatus.APPLIED
        existing.notes = payload.notes or existing.notes
        existing.applied_at = now
        application = existing
    else:
        application = Application(
            candidate_id=candidate.id,
            job_id=job.id,
            notes=payload.notes,
            status=ApplicationStatus.APPLIED,
            applied_at=now,
        )
        db.add(application)
        db.flush()

    create_notification(
        db,
        candidate=candidate,
        title="Application submitted",
        message=f"You applied to {job.title}.",
        notification_type="application_submitted",
        job_id=job.id,
        application_id=application.id,
        commit=False,
    )
    db.add(AuditLog(user_id=current_user.id, action="apply", entity_type="application", entity_id=application.id))
    db.commit()
    db.refresh(application)
    application = (
        db.query(Application)
        .options(joinedload(Application.job), joinedload(Application.candidate))
        .filter(Application.id == application.id)
        .first()
    )
    return _serialize(application)


@router.get("", response_model=ApplicationListResponse)
def list_applications(
    status_filter: ApplicationStatus | None = None,
    q: str | None = None,
    job_id: int | None = None,
    candidate_id: int | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    query = db.query(Application).options(joinedload(Application.job), joinedload(Application.candidate))
    if status_filter:
        query = query.filter(Application.status == status_filter)
    if job_id:
        query = query.filter(Application.job_id == job_id)
    if candidate_id:
        query = query.filter(Application.candidate_id == candidate_id)
    if q:
        like = f"%{q.strip()}%"
        query = query.join(Candidate).join(Job).filter(
            (Candidate.name.ilike(like)) | (Candidate.email.ilike(like)) | (Job.title.ilike(like))
        )
    total = query.count()
    rows = (
        query.order_by(Application.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return ApplicationListResponse(
        items=[_serialize(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/candidates/{candidate_id}", response_model=list[ApplicationOut])
def list_applications_for_candidate(
    candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    _authorize(candidate, current_user)
    rows = (
        db.query(Application)
        .options(joinedload(Application.job), joinedload(Application.candidate))
        .filter(Application.candidate_id == candidate_id)
        .order_by(Application.created_at.desc())
        .all()
    )
    scores = {
        m.job_id: m.match_score
        for m in db.query(Match).filter(Match.candidate_id == candidate_id).all()
    }
    return [_serialize(row, scores.get(row.job_id)) for row in rows]


@router.patch("/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int,
    payload: ApplicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = (
        db.query(Application)
        .options(joinedload(Application.job), joinedload(Application.candidate))
        .filter(Application.id == application_id)
        .first()
    )
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    _authorize(application.candidate, current_user)

    data = payload.model_dump(exclude_unset=True)
    new_status = data.get("status")
    if new_status is not None:
        if current_user.role != UserRole.ADMIN and new_status not in CANDIDATE_ALLOWED_STATUSES:
            raise HTTPException(status_code=403, detail="You cannot set that application status")
        if new_status == ApplicationStatus.APPLIED and not application.applied_at:
            application.applied_at = datetime.now(timezone.utc)

    if current_user.role != UserRole.ADMIN:
        data.pop("interview_status", None)
        data.pop("interview_date", None)

    previous = application.status
    for field, value in data.items():
        setattr(application, field, value)

    if new_status and new_status != previous:
        create_notification(
            db,
            candidate=application.candidate,
            title="Application status updated",
            message=f"Your application for {application.job.title if application.job else 'a job'} is now {new_status.value}.",
            notification_type="application_status",
            job_id=application.job_id,
            application_id=application.id,
            commit=False,
        )
        if new_status == ApplicationStatus.INTERVIEW or application.interview_status == InterviewStatus.SCHEDULED:
            create_notification(
                db,
                candidate=application.candidate,
                title="Interview scheduled",
                message="An interview has been scheduled. Check your applications for details.",
                notification_type="interview_scheduled",
                job_id=application.job_id,
                application_id=application.id,
                commit=False,
            )

    db.commit()
    db.refresh(application)
    return _serialize(application)
