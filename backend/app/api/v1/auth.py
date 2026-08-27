from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.audit_log import AuditLog
from app.models.candidate import Candidate
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, MeResponse, RegisterCandidateRequest, Token

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_candidate(payload: RegisterCandidateRequest, db: Session = Depends(get_db)):
    email = str(payload.email).strip().lower()
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=email, hashed_password=hash_password(payload.password), role=UserRole.CANDIDATE)
    db.add(user)
    db.flush()

    candidate = Candidate(
        user_id=user.id,
        name=payload.name.strip(),
        email=email,
        phone=payload.phone,
        location=payload.location,
        city=payload.location,
        postal_code=payload.postal_code,
        preferred_shift=payload.preferred_shift,
        work_eligibility=payload.work_eligibility,
        amazon_portal_link=payload.amazon_portal_link,
    )
    db.add(candidate)
    db.add(AuditLog(user_id=user.id, action="register", entity_type="user", entity_id=user.id))
    db.commit()

    token = create_access_token(subject=user.email, role=user.role.value)
    return Token(access_token=token, role=user.role)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    db.add(AuditLog(user_id=user.id, action="login", entity_type="user", entity_id=user.id))
    db.commit()

    token = create_access_token(subject=user.email, role=user.role.value)
    return Token(access_token=token, role=user.role)


@router.post("/logout", status_code=204)
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.add(AuditLog(user_id=current_user.id, action="logout", entity_type="user", entity_id=current_user.id))
    db.commit()
    return None


@router.get("/me", response_model=MeResponse)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    candidate_id = None
    name = current_user.name
    if current_user.role == UserRole.CANDIDATE:
        candidate = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if candidate:
            candidate_id = candidate.id
            name = candidate.name
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        candidate_id=candidate_id,
        name=name,
        is_active=current_user.is_active,
    )
