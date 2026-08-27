from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from uuid import uuid4
from sqlalchemy import or_
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db, require_admin
from app.core.security import hash_password
from app.models.application import Application
from app.models.candidate import Candidate, CandidateStatus
from app.models.candidate_preference import CandidatePreference
from app.models.match import Match
from app.models.user import User, UserRole
from app.schemas.candidate import (
    AdminCandidateCreate,
    CandidateListResponse,
    CandidateOut,
    CandidatePreferenceOut,
    CandidatePreferenceUpdate,
    CandidateUpdate,
    CandidateWorkflowUpdate,
)
from app.services.profile import serialize_candidate
from app.services.uploads import save_resume

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


def _get_candidate_or_404(db: Session, candidate_id: int) -> Candidate:
    candidate = (
        db.query(Candidate)
        .options(joinedload(Candidate.preferences), joinedload(Candidate.user))
        .filter(Candidate.id == candidate_id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


def _authorize_candidate_access(candidate: Candidate, current_user: User):
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.CANDIDATE and candidate.user_id == current_user.id:
        return
    raise HTTPException(status_code=403, detail="Not authorized to access this candidate")


@router.get("", response_model=list[CandidateOut])
def list_candidates(
    status_filter: CandidateStatus | None = None,
    q: str | None = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    query = db.query(Candidate).options(joinedload(Candidate.preferences))
    if status_filter:
        query = query.filter(Candidate.status == status_filter)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(Candidate.name.ilike(like), Candidate.email.ilike(like), Candidate.location.ilike(like))
        )
    rows = query.order_by(Candidate.created_at.desc()).offset(skip).limit(limit).all()
    return [serialize_candidate(row) for row in rows]


@router.post("/admin-create", response_model=CandidateOut, status_code=status.HTTP_201_CREATED)
def create_candidate_for_admin(
    payload: AdminCandidateCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    email = str(payload.email).strip().lower() if payload.email else f"lead-{uuid4().hex[:12]}@talentpath.local"
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=email, hashed_password=hash_password(uuid4().hex), role=UserRole.CANDIDATE)
    db.add(user)
    db.flush()
    candidate = Candidate(
        user_id=user.id,
        name=payload.name.strip(),
        email=email,
        phone=payload.phone,
        preferred_city=payload.preferred_city,
        city=payload.preferred_city,
        postal_code=payload.postal_code,
        preferred_shift=payload.preferred_shift,
        work_eligibility=payload.work_eligibility,
        amazon_portal_link=payload.amazon_portal_link,
        job_type=payload.job_type,
        location=payload.location or payload.preferred_city,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return serialize_candidate(candidate)


@router.get("/search", response_model=CandidateListResponse)
def search_candidates(
    status_filter: CandidateStatus | None = None,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    query = db.query(Candidate).options(joinedload(Candidate.preferences))
    if status_filter:
        query = query.filter(Candidate.status == status_filter)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            or_(Candidate.name.ilike(like), Candidate.email.ilike(like), Candidate.location.ilike(like))
        )
    total = query.count()
    rows = query.order_by(Candidate.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return CandidateListResponse(
        items=[CandidateOut.model_validate(serialize_candidate(row)) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/me", response_model=CandidateOut)
def get_my_candidate(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.CANDIDATE:
        raise HTTPException(status_code=403, detail="Candidate access required")
    candidate = (
        db.query(Candidate)
        .options(joinedload(Candidate.preferences))
        .filter(Candidate.user_id == current_user.id)
        .first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return serialize_candidate(candidate)


@router.get("/{candidate_id}", response_model=CandidateOut)
def get_candidate(
    candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    candidate = _get_candidate_or_404(db, candidate_id)
    _authorize_candidate_access(candidate, current_user)
    return serialize_candidate(candidate)


@router.patch("/{candidate_id}", response_model=CandidateOut)
def update_candidate(
    candidate_id: int,
    payload: CandidateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = _get_candidate_or_404(db, candidate_id)
    _authorize_candidate_access(candidate, current_user)

    data = payload.model_dump(exclude_unset=True)
    if "status" in data and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can change candidate status")

    for field, value in data.items():
        setattr(candidate, field, value)
    db.commit()
    db.refresh(candidate)
    return serialize_candidate(candidate)


@router.delete("/{candidate_id}", status_code=204)
def deactivate_candidate(
    candidate_id: int, db: Session = Depends(get_db), _admin: User = Depends(require_admin)
):
    candidate = _get_candidate_or_404(db, candidate_id)
    candidate.status = CandidateStatus.INACTIVE
    if candidate.user:
        candidate.user.is_active = False
    db.commit()
    return None


@router.post("/{candidate_id}/resume", response_model=CandidateOut)
def upload_resume(
    candidate_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = _get_candidate_or_404(db, candidate_id)
    _authorize_candidate_access(candidate, current_user)
    stored_path, original_name = save_resume(file, candidate.id)
    candidate.resume_path = stored_path
    candidate.resume_filename = original_name
    db.commit()
    db.refresh(candidate)
    return serialize_candidate(candidate)


@router.get("/{candidate_id}/preferences", response_model=CandidatePreferenceOut)
def get_preferences(
    candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    candidate = _get_candidate_or_404(db, candidate_id)
    _authorize_candidate_access(candidate, current_user)
    if not candidate.preferences:
        raise HTTPException(status_code=404, detail="Preferences not set yet")
    return candidate.preferences


@router.put("/{candidate_id}/preferences", response_model=CandidatePreferenceOut)
def upsert_preferences(
    candidate_id: int,
    payload: CandidatePreferenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    candidate = _get_candidate_or_404(db, candidate_id)
    _authorize_candidate_access(candidate, current_user)

    prefs = candidate.preferences
    if not prefs:
        prefs = CandidatePreference(candidate_id=candidate.id)
        db.add(prefs)

    for field, value in payload.model_dump().items():
        setattr(prefs, field, value)
    db.commit()
    db.refresh(prefs)
    return prefs


@router.get("/{candidate_id}/overview")
def candidate_overview(
    candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    candidate = _get_candidate_or_404(db, candidate_id)
    _authorize_candidate_access(candidate, current_user)
    applications = db.query(Application).filter(Application.candidate_id == candidate_id).all()
    matches = (
        db.query(Match)
        .filter(Match.candidate_id == candidate_id)
        .order_by(Match.match_score.desc())
        .limit(10)
        .all()
    )
    return {
        "candidate": serialize_candidate(candidate),
        "preferences": candidate.preferences,
        "applications_count": len(applications),
        "top_matches": [
            {"job_id": m.job_id, "match_score": m.match_score, "explanation": m.explanation or []} for m in matches
        ],
    }
