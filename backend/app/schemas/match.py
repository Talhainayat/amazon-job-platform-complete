from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    job_id: int
    match_score: float
    matched_criteria: dict
    unmatched_criteria: dict
    explanation: list[str] = []
    distance_km: float | None = None
    distance_known: bool = False
    status: str
    matched_at: datetime
    job_title: str | None = None
    company: str | None = None
    location: str | None = None
