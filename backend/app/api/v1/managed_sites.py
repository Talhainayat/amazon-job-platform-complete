from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin
from app.models.managed_site import ManagedSite
from app.models.user import User
from app.schemas.managed_site import ManagedSiteCreate, ManagedSiteOut

router = APIRouter(prefix="/api/admin/sites", tags=["admin-sites"])


@router.get("", response_model=list[ManagedSiteOut])
def list_sites(db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    return db.query(ManagedSite).order_by(ManagedSite.created_at.desc()).all()


@router.post("", response_model=ManagedSiteOut, status_code=201)
def create_site(payload: ManagedSiteCreate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    site = ManagedSite(**payload.model_dump())
    db.add(site)
    db.commit()
    db.refresh(site)
    return site


@router.patch("/{site_id}", response_model=ManagedSiteOut)
def update_site(site_id: int, payload: ManagedSiteCreate, db: Session = Depends(get_db), _admin: User = Depends(require_admin)):
    site = db.query(ManagedSite).filter(ManagedSite.id == site_id).first()
    if not site:
        raise HTTPException(status_code=404, detail="Managed site not found")
    for field, value in payload.model_dump().items():
        setattr(site, field, value)
    db.commit()
    db.refresh(site)
    return site