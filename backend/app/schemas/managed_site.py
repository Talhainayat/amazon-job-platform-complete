from pydantic import BaseModel, ConfigDict, Field


class ManagedSiteCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    postal_code: str | None = None
    portal_url: str | None = None
    feed_enabled: bool = True
    available_slots: int = Field(default=0, ge=0)


class ManagedSiteOut(ManagedSiteCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int