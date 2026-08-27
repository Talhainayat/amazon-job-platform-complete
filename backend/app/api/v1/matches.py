from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_db
from app.models.candidate import Candidate
from app.models.match import Match
from app.models.user import User, UserRole
from app.schemas.match import MatchOut
from app.services.matching import generate_matches_for_candidate

router = APIRouter(prefix="/api/matches", tags=["matches"])


def _authorize(candidate: Candidate, current_user: User):
    if current_user.role == UserRole.ADMIN:
        return
    if current_user.role == UserRole.CANDIDATE and candidate.user_id == current_user.id:
        return
    raise HTTPException(status_code=403, detail="Not authorized")


def _serialize(match: Match) -> dict:
    data = MatchOut.model_validate(match).model_dump()
    if match.job:
        data["job_title"] = match.job.title
        data["company"] = match.job.company
        data["location"] = match.job.location
    data["explanation"] = match.explanation or []
    return data


@router.post("/candidates/{candidate_id}/recalculate", response_model=list[MatchOut])
def recalculate_matches(
    candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    candidate = (
        db.query(Candidate).options(joinedload(Candidate.preferences)).filter(Candidate.id == candidate_id).first()
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    _authorize(candidate, current_user)
    matches = generate_matches_for_candidate(db, candidate)
    ids = [m.id for m in matches]
    loaded = (
        db.query(Match)
        .options(joinedload(Match.job))
        .filter(Match.id.in_(ids))
        .all()
        if ids
        else []
    )
    loaded.sort(key=lambda m: m.match_score, reverse=True)
    return [_serialize(m) for m in loaded]


@router.get("/candidates/{candidate_id}", response_model=list[MatchOut])
def list_matches_for_candidate(
    candidate_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    _authorize(candidate, current_user)
    rows = (
        db.query(Match)
        .options(joinedload(Match.job))
        .filter(Match.candidate_id == candidate_id)
        .order_by(Match.match_score.desc())
        .all()
    )
    return [_serialize(m) for m in rows]
