from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactInquiryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    phone: str | None = None
    message: str = Field(min_length=10, max_length=5000)


class ContactInquiryOut(ContactInquiryCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int