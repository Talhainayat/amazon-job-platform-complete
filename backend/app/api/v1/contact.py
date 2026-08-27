from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.contact_inquiry import ContactInquiry
from app.schemas.contact import ContactInquiryCreate, ContactInquiryOut

router = APIRouter(prefix="/api/contact", tags=["contact"])


@router.post("/inquiries", response_model=ContactInquiryOut, status_code=status.HTTP_201_CREATED)
def create_contact_inquiry(payload: ContactInquiryCreate, db: Session = Depends(get_db)):
    inquiry = ContactInquiry(**payload.model_dump())
    db.add(inquiry)
    db.commit()
    db.refresh(inquiry)
    return inquiry