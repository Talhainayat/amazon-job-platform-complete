from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_  # pyright: ignore[reportMissingImports]
from sqlalchemy.orm import Session, joinedload  # pyright: ignore[reportMissingImports]

from app.api.deps import get_current_user_optional, get_db, require_admin
from app.models.application import Application
from app.models.audit_log import AuditLog
from app.models.candidate import Candidate
from app.models.job import Job, JobStatus
from app.models.match import Match
from app.models.user import User, UserRole
from app.schemas.job import JobCreate, JobListResponse, JobOut, JobUpdate
from app.services.geo import haversine_km, resolve_point
from app.services.matching import generate_matches_for_candidate, score_candidate_job
from app.services.notification_service import create_notification

router = APIRouter(prefix="/api/jobs", tags=["jobs"])

ALLOWED_TRANSITIONS = {
    JobStatus.DRAFT: {JobStatus.OPEN, JobStatus.ARCHIVED},
    JobStatus.OPEN: {JobStatus.CLOSED, JobStatus.ARCHIVED, JobStatus.EXPIRED},
    JobStatus.CLOSED: {JobStatus.OPEN, JobStatus.ARCHIVED},
    JobStatus.EXPIRED: {JobStatus.OPEN, JobStatus.ARCHIVED, JobStatus.CLOSED},
    JobStatus.ARCHIVED: {JobStatus.DRAFT, JobStatus.OPEN},
}


def _job_or_404(db: Session, job_id: int) -> Job:
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def _set_status(db: Session, job: Job, new_status: JobStatus, user: User):
    if job.status == new_status:
        return job
    allowed = ALLOWED_TRANSITIONS.get(job.status, set())
    if new_status not in allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change job from {job.status.value} to {new_status.value}",
        )
    previous = job.status
    job.status = new_status
    db.add(
        AuditLog(
            user_id=user.id,
            action=f"job_status:{previous.value}->{new_status.value}",
            entity_type="job",
            entity_id=job.id,
        )
    )
    if new_status == JobStatus.CLOSED:
        applicants = (
            db.query(Candidate)
            .join(Application, Application.candidate_id == Candidate.id)
            .filter(Application.job_id == job.id)
            .all()
        )
        for candidate in applicants:
            create_notification(
                db,
                candidate=candidate,
                title="Job closed",
                message=f"{job.title} is no longer accepting applications.",
                notification_type="job_closed",
                job_id=job.id,
                commit=False,
            )
    return job


def _enrich_job(db: Session, job: Job, user: User | None) -> dict:
    data = JobOut.model_validate(job).model_dump()
    if not user or user.role != UserRole.CANDIDATE:
        return data
    candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()
    if not candidate:
        return data
    result = score_candidate_job(candidate, job)
    data["match_score"] = result.score
    data["match_explanation"] = result.explanation
    data["distance_km"] = result.distance_km
    data["distance_known"] = result.distance_known
    application = (
        db.query(Application)
        .filter(Application.candidate_id == candidate.id, Application.job_id == job.id)
        .first()
    )
    data["already_applied"] = application is not None and application.status.value != "withdrawn"
    data["application_status"] = application.status.value if application else None
    return data


@router.get("", response_model=JobListResponse)
def list_jobs(
    q: str | None = None,
    location: str | None = None,
    job_type: str | None = None,
    shift: str | None = None,
    status_filter: JobStatus | None = None,
    min_pay: float | None = None,
    max_pay: float | None = None,
    skills: str | None = None,
    experience: int | None = None,
    sort: str = "newest",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    radius_km: float | None = None,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    query = db.query(Job)
    is_admin = current_user is not None and current_user.role == UserRole.ADMIN
    
    # Filter for candidates: only OPEN jobs that are active
    if not is_admin:
        query = query.filter(
            (Job.status == JobStatus.OPEN) &
            ((Job.is_custom == False) | ((Job.is_custom == True) & (Job.is_active == True)))
        )
    elif status_filter:
        query = query.filter(Job.status == status_filter)
    
    if status_filter and is_admin:
        query = query.filter(Job.status == status_filter)
    elif status_filter:
        query = query.filter(Job.status == status_filter)

    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Job.title.ilike(like),
                Job.company.ilike(like),
                Job.description.ilike(like),
                Job.location.ilike(like),
            )
        )
    if location:
        like = f"%{location.strip()}%"
        query = query.filter(
            or_(Job.location.ilike(like), Job.city.ilike(like), Job.postal_code.ilike(like), Job.province.ilike(like))
        )
    if job_type:
        query = query.filter(Job.job_type.ilike(f"%{job_type.strip()}%"))
    if shift:
        query = query.filter(Job.shift.ilike(f"%{shift.strip()}%"))
    if min_pay is not None:
        query = query.filter(or_(Job.pay_max >= min_pay, Job.pay_min >= min_pay, Job.pay_min.is_(None)))
    if max_pay is not None:
        query = query.filter(or_(Job.pay_min <= max_pay, Job.pay_min.is_(None)))
    if experience is not None:
        query = query.filter(or_(Job.years_experience <= experience, Job.years_experience.is_(None)))

    if sort == "oldest":
        query = query.order_by(Job.created_at.asc())
    elif sort == "pay":
        query = query.order_by(Job.pay_max.desc().nullslast(), Job.pay_min.desc().nullslast())
    elif sort == "title":
        query = query.order_by(Job.title.asc())
    else:
        query = query.order_by(Job.created_at.desc())

    rows = query.all()
    if skills:
        needed = [s.strip().lower() for s in skills.split(",") if s.strip()]
        rows = [
            job
            for job in rows
            if job.skills and any(skill in [str(item).lower() for item in job.skills] for skill in needed)
        ]

    origin = None
    radius = radius_km
    if current_user and current_user.role == UserRole.CANDIDATE:
        candidate = db.query(Candidate).options(joinedload(Candidate.preferences)).filter(
            Candidate.user_id == current_user.id
        ).first()
        if candidate:
            origin = resolve_point(
                latitude=candidate.latitude,
                longitude=candidate.longitude,
                city=candidate.city or candidate.preferred_city,
                location=candidate.location,
            )
            if radius is None and candidate.preferences:
                radius = candidate.preferences.radius_km

    if origin and radius:
        filtered = []
        for job in rows:
            point = resolve_point(
                latitude=job.latitude, longitude=job.longitude, city=job.city, location=job.location
            )
            if not point:
                continue
            if haversine_km(origin.latitude, origin.longitude, point.latitude, point.longitude) <= radius:
                filtered.append(job)
        rows = filtered

    total = len(rows)
    start = (page - 1) * page_size
    page_rows = rows[start : start + page_size]
    items = [_enrich_job(db, job, current_user) for job in page_rows]
    if sort == "match":
        items.sort(key=lambda item: item.get("match_score") or 0, reverse=True)
    return JobListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    job = _job_or_404(db, job_id)
    if job.status in {JobStatus.DRAFT, JobStatus.ARCHIVED}:
        if not current_user or current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=404, detail="Job not found")
    return _enrich_job(db, job, current_user)


@router.post("", response_model=JobOut, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    external_id = payload.external_job_id or f"manual-{uuid4()}"
    existing = db.query(Job).filter(Job.source == payload.source, Job.external_job_id == external_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Job already exists (duplicate source + external_job_id)")

    data = payload.model_dump()
    data["external_job_id"] = external_id
    data["skills"] = data.get("skills") or []
    data["status"] = data.get("status") or JobStatus.OPEN
    if not data.get("city") and data.get("location"):
        data["city"] = data["location"]
    point = resolve_point(city=data.get("city"), location=data.get("location"))
    if point:
        data["latitude"] = point.latitude
        data["longitude"] = point.longitude
    job = Job(**data)
    db.add(job)
    db.add(AuditLog(user_id=admin.id, action="job_create", entity_type="job", details=job.title))
    db.commit()
    db.refresh(job)

    if job.status == JobStatus.OPEN:
        candidates = db.query(Candidate).options(joinedload(Candidate.preferences)).all()
        for candidate in candidates:
            generate_matches_for_candidate(db, candidate)
            match = (
                db.query(Match)
                .filter(Match.candidate_id == candidate.id, Match.job_id == job.id)
                .first()
            )
            if match and match.match_score >= 70:
                create_notification(
                    db,
                    candidate=candidate,
                    title="New job match",
                    message=f"{job.title} looks like a {int(match.match_score)}% match.",
                    notification_type="new_job_match",
                    job_id=job.id,
                    commit=False,
                )
        db.commit()
        db.refresh(job)
    return job


@router.patch("/{job_id}", response_model=JobOut)
def update_job(
    job_id: int, payload: JobUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)
):
    job = _job_or_404(db, job_id)
    data = payload.model_dump(exclude_unset=True)
    new_status = data.pop("status", None)
    for field, value in data.items():
        setattr(job, field, value)
    point = resolve_point(latitude=job.latitude, longitude=job.longitude, city=job.city, location=job.location)
    if point and (job.latitude is None or job.longitude is None):
        job.latitude = point.latitude
        job.longitude = point.longitude
    if new_status is not None:
        _set_status(db, job, new_status, admin)
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/publish", response_model=JobOut)
def publish_job(job_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    job = _job_or_404(db, job_id)
    _set_status(db, job, JobStatus.OPEN, admin)
    db.commit()
    db.refresh(job)
    candidates = db.query(Candidate).options(joinedload(Candidate.preferences)).all()
    for candidate in candidates:
        generate_matches_for_candidate(db, candidate)
    db.refresh(job)
    return job


@router.post("/{job_id}/close", response_model=JobOut)
def close_job_action(job_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    job = _job_or_404(db, job_id)
    _set_status(db, job, JobStatus.CLOSED, admin)
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/reopen", response_model=JobOut)
def reopen_job(job_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    job = _job_or_404(db, job_id)
    _set_status(db, job, JobStatus.OPEN, admin)
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/archive", response_model=JobOut)
def archive_job(job_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    job = _job_or_404(db, job_id)
    _set_status(db, job, JobStatus.ARCHIVED, admin)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def close_job(job_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    job = _job_or_404(db, job_id)
    _set_status(db, job, JobStatus.CLOSED, admin)
    db.commit()
    return None


# ============= Custom Job Management Endpoints =============
@router.get("/custom/list/all", response_model=JobListResponse)
def list_custom_jobs(
    q: str | None = None,
    status_filter: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """List custom jobs for admin management."""
    query = db.query(Job).filter(Job.is_custom == True)
    
    if status_filter:
        try:
            status = JobStatus(status_filter)
            query = query.filter(Job.status == status)
        except ValueError:
            pass
    
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Job.title.ilike(like),
                Job.company.ilike(like),
            )
        )
    
    query = query.order_by(Job.created_at.desc())
    
    total = query.count()
    start = (page - 1) * page_size
    page_rows = query.offset(start).limit(page_size).all()
    
    items = [JobOut.model_validate(job).model_dump() for job in page_rows]
    return JobListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/custom/create", response_model=JobOut, status_code=201)
def create_custom_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Create a custom job with external application URL."""
    external_id = payload.external_job_id or f"custom-{uuid4()}"
    
    data = payload.model_dump()
    data["external_job_id"] = external_id
    data["source"] = "custom"
    data["is_custom"] = True
    data["skills"] = data.get("skills") or []
    data["status"] = data.get("status") or JobStatus.OPEN
    data["is_active"] = True
    
    # Set badge_status if not provided
    if "badge_status" not in data or not data["badge_status"]:
        data["badge_status"] = "live"
    
    # Resolve geolocation
    if not data.get("city") and data.get("location"):
        data["city"] = data["location"]
    
    point = resolve_point(city=data.get("city"), location=data.get("location"))
    if point:
        data["latitude"] = point.latitude
        data["longitude"] = point.longitude
    
    job = Job(**data)
    db.add(job)
    db.add(AuditLog(
        user_id=admin.id,
        action="custom_job_create",
        entity_type="job",
        entity_id=job.id,
        details=f"Created custom job: {job.title}"
    ))
    db.commit()
    db.refresh(job)
    
    # Generate matches for open custom jobs
    if job.status == JobStatus.OPEN:
        candidates = db.query(Candidate).options(joinedload(Candidate.preferences)).all()
        for candidate in candidates:
            generate_matches_for_candidate(db, candidate)
    
    db.commit()
    db.refresh(job)
    return job


@router.patch("/custom/{job_id}", response_model=JobOut)
def update_custom_job(
    job_id: int,
    payload: JobUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Update a custom job."""
    job = _job_or_404(db, job_id)
    
    if not job.is_custom:
        raise HTTPException(status_code=400, detail="This is not a custom job")
    
    data = payload.model_dump(exclude_unset=True)
    new_status = data.pop("status", None)
    
    for field, value in data.items():
        setattr(job, field, value)
    
    # Resolve geolocation if location changed
    point = resolve_point(latitude=job.latitude, longitude=job.longitude, city=job.city, location=job.location)
    if point and (job.latitude is None or job.longitude is None):
        job.latitude = point.latitude
        job.longitude = point.longitude
    
    if new_status is not None:
        _set_status(db, job, new_status, admin)
    
    db.add(AuditLog(
        user_id=admin.id,
        action="custom_job_update",
        entity_type="job",
        entity_id=job.id,
        details=f"Updated custom job: {job.title}"
    ))
    db.commit()
    db.refresh(job)
    return job


@router.delete("/custom/{job_id}", status_code=204)
def delete_custom_job(
    job_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Delete a custom job."""
    job = _job_or_404(db, job_id)
    
    if not job.is_custom:
        raise HTTPException(status_code=400, detail="This is not a custom job")
    
    db.add(AuditLog(
        user_id=admin.id,
        action="custom_job_delete",
        entity_type="job",
        entity_id=job.id,
        details=f"Deleted custom job: {job.title}"
    ))
    db.delete(job)
    db.commit()
    return None


@router.post("/custom/{job_id}/toggle", response_model=JobOut)
def toggle_custom_job_active(
    job_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """Toggle custom job active/inactive status."""
    job = _job_or_404(db, job_id)
    
    if not job.is_custom:
        raise HTTPException(status_code=400, detail="This is not a custom job")
    
    job.is_active = not job.is_active
    
    db.add(AuditLog(
        user_id=admin.id,
        action="custom_job_toggle",
        entity_type="job",
        entity_id=job.id,
        details=f"Toggle custom job {'active' if job.is_active else 'inactive'}: {job.title}"
    ))
    db.commit()
    db.refresh(job)
    return job
