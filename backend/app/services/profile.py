from app.models.candidate import Candidate
from app.models.candidate_preference import CandidatePreference


PROFILE_FIELDS = [
    "name",
    "email",
    "phone",
    "location",
    "city",
    "province",
    "postal_code",
    "skills",
    "experience",
    "education",
    "job_type",
    "preferred_shift",
    "availability",
    "years_experience",
    "resume_path",
]


def profile_completion(candidate: Candidate) -> int:
    filled = 0
    total = len(PROFILE_FIELDS) + 3
    for field in PROFILE_FIELDS:
        value = getattr(candidate, field, None)
        if isinstance(value, list):
            if value:
                filled += 1
        elif value not in (None, "", False):
            filled += 1
        elif field == "years_experience" and value == 0:
            filled += 1

    prefs: CandidatePreference | None = candidate.preferences
    if prefs:
        if prefs.radius_km:
            filled += 1
        if prefs.minimum_pay is not None:
            filled += 1
        if prefs.shift or prefs.job_type:
            filled += 1
    return min(100, round(100 * filled / total))


def serialize_candidate(candidate: Candidate) -> dict:
    return {
        "id": candidate.id,
        "name": candidate.name,
        "email": candidate.email,
        "phone": candidate.phone,
        "location": candidate.location,
        "city": candidate.city,
        "province": candidate.province,
        "postal_code": candidate.postal_code,
        "preferred_city": candidate.preferred_city,
        "preferred_shift": candidate.preferred_shift,
        "job_type": candidate.job_type,
        "skills": candidate.skills or [],
        "years_experience": candidate.years_experience,
        "experience": candidate.experience,
        "education": candidate.education,
        "availability": candidate.availability,
        "has_vehicle": candidate.has_vehicle,
        "status": candidate.status,
        "resume_filename": candidate.resume_filename,
        "has_resume": bool(candidate.resume_path),
        "profile_completion": profile_completion(candidate),
        "amazon_portal_link": candidate.amazon_portal_link,
        "work_eligibility": candidate.work_eligibility,
        "alert_sent": bool(candidate.alert_sent),
        "applied": bool(candidate.applied),
        "interview_scheduled": bool(candidate.interview_scheduled),
        "created_at": candidate.created_at,
        "updated_at": candidate.updated_at,
    }
