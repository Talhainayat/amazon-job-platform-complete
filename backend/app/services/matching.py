"""
Rule-based candidate/job matching engine.

Default weights (must sum to 100):
  location 35, skills 20, job_type 15, shift 15, experience 8, pay 7

If a job does not specify a criterion, that criterion is treated as
satisfied so candidates are not penalized for missing job metadata.
Distance is only reported when coordinates (or a city lookup) exist.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.candidate import Candidate, CandidateStatus
from app.models.job import Job, JobStatus
from app.models.match import Match
from app.services.geo import city_name_match, haversine_km, postal_prefix_match, resolve_point

JOB_TYPE_ALIASES = {
    "warehouse": {"warehouse", "fulfillment", "distribution", "logistics"},
    "fulfillment": {"warehouse", "fulfillment", "distribution"},
    "driver": {"driver", "delivery", "courier"},
    "delivery": {"driver", "delivery", "courier"},
    "full-time": {"full-time", "full time", "fulltime", "permanent"},
    "part-time": {"part-time", "part time", "parttime"},
    "contract": {"contract", "temporary", "temp"},
}

SHIFT_ALIASES = {
    "day": {"day", "days", "daytime", "morning"},
    "night": {"night", "nights", "overnight", "graveyard"},
    "evening": {"evening", "afternoons", "afternoon", "swing"},
    "rotating": {"rotating", "rotation", "flexible"},
}


@dataclass
class MatchResult:
    score: float
    matched_criteria: dict = field(default_factory=dict)
    unmatched_criteria: dict = field(default_factory=dict)
    explanation: list[str] = field(default_factory=list)
    distance_km: float | None = None
    distance_known: bool = False


def _normalize(value: str | None) -> str:
    return (value or "").strip().lower()


def _as_skill_list(value) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [p.strip().lower() for p in value.replace(";", ",").split(",") if p.strip()]
    return [str(item).strip().lower() for item in value if str(item).strip()]


def _aliased_match(left: str, right: str, aliases: dict[str, set[str]]) -> bool:
    if not left or not right:
        return False
    if left == right:
        return True
    left_group = aliases.get(left, {left})
    right_group = aliases.get(right, {right})
    for key, group in aliases.items():
        if left in group:
            left_group = group
        if right in group:
            right_group = group
    return not left_group.isdisjoint(right_group)


def _location_component(candidate: Candidate, job: Job, weight: float) -> tuple[float, str, dict, dict, float | None, bool]:
    prefs = candidate.preferences
    radius = (prefs.radius_km if prefs and prefs.radius_km else None) or 25.0
    cand_location = (prefs.location if prefs and prefs.location else None) or candidate.location
    cand_city = candidate.preferred_city or candidate.city or cand_location
    job_city = job.city or job.location

    cand_point = resolve_point(
        latitude=candidate.latitude,
        longitude=candidate.longitude,
        city=cand_city,
        location=cand_location,
    )
    job_point = resolve_point(
        latitude=job.latitude,
        longitude=job.longitude,
        city=job_city,
        location=job.location,
    )

    matched: dict = {}
    unmatched: dict = {}

    if cand_point and job_point:
        distance = round(haversine_km(cand_point.latitude, cand_point.longitude, job_point.latitude, job_point.longitude), 1)
        if distance <= radius:
            factor = max(0.0, 1.0 - (distance / (radius * 1.25)))
            score = round(weight * factor, 2)
            matched["location"] = job.location or job.city
            matched["distance_km"] = distance
            why = f"About {distance} km away, within your {int(radius)} km radius"
            return score, why, matched, unmatched, distance, True
        unmatched["location"] = job.location or job.city
        unmatched["distance_km"] = distance
        return 0.0, f"About {distance} km away, outside your {int(radius)} km radius", matched, unmatched, distance, True

    if city_name_match(cand_city, job_city) or city_name_match(cand_location, job.location):
        matched["location"] = job.location or job.city
        return weight, "Location matches", matched, unmatched, None, False

    if postal_prefix_match(candidate.postal_code, job.postal_code):
        matched["location"] = job.postal_code
        return round(weight * 0.8, 2), "Postal code area matches", matched, unmatched, None, False

    if not cand_location and not cand_city:
        unmatched["location"] = job.location or job.city
        return 0.0, "Add a location to improve matching", matched, unmatched, None, False

    unmatched["location"] = job.location or job.city
    return 0.0, "Location does not match", matched, unmatched, None, False


def score_candidate_job(candidate: Candidate, job: Job) -> MatchResult:
    matched: dict = {}
    unmatched: dict = {}
    reasons: list[str] = []
    total = 0.0

    prefs = candidate.preferences
    loc_score, loc_why, loc_m, loc_u, distance_km, distance_known = _location_component(
        candidate, job, float(settings.MATCH_WEIGHT_LOCATION)
    )
    total += loc_score
    matched.update(loc_m)
    unmatched.update(loc_u)
    reasons.append(loc_why)

    job_skills = _as_skill_list(job.skills)
    cand_skills = _as_skill_list(candidate.skills)
    if not job_skills:
        total += settings.MATCH_WEIGHT_SKILLS
        matched["skills"] = "not specified on job"
        reasons.append("No specific skills required")
    else:
        overlap = [s for s in job_skills if s in cand_skills]
        ratio = len(overlap) / len(job_skills)
        total += round(settings.MATCH_WEIGHT_SKILLS * ratio, 2)
        if overlap:
            matched["skills"] = overlap
            reasons.append(f"{len(overlap)}/{len(job_skills)} required skills match")
        if len(overlap) < len(job_skills):
            missing = [s for s in job_skills if s not in cand_skills]
            unmatched["skills"] = missing
            if not overlap:
                reasons.append("Required skills do not match")

    cand_job_type = _normalize(prefs.job_type if prefs and prefs.job_type else candidate.job_type)
    job_type = _normalize(job.job_type)
    if not job_type:
        total += settings.MATCH_WEIGHT_JOB_TYPE
        matched["job_type"] = "not specified"
        reasons.append("Job type not specified")
    elif _aliased_match(cand_job_type, job_type, JOB_TYPE_ALIASES):
        total += settings.MATCH_WEIGHT_JOB_TYPE
        matched["job_type"] = job.job_type
        reasons.append("Job type matches")
    else:
        unmatched["job_type"] = job.job_type
        reasons.append("Job type does not match")

    cand_shift = _normalize(prefs.shift if prefs and prefs.shift else candidate.preferred_shift)
    job_shift = _normalize(job.shift)
    if not job_shift:
        total += settings.MATCH_WEIGHT_SHIFT
        matched["shift"] = "not specified"
        reasons.append("Shift not specified")
    elif _aliased_match(cand_shift, job_shift, SHIFT_ALIASES):
        total += settings.MATCH_WEIGHT_SHIFT
        matched["shift"] = job.shift
        reasons.append("Shift matches")
    else:
        unmatched["shift"] = job.shift
        reasons.append("Shift does not match")

    cand_years = (
        prefs.years_experience if prefs and prefs.years_experience is not None else candidate.years_experience
    )
    if job.years_experience is None:
        total += settings.MATCH_WEIGHT_EXPERIENCE
        matched["experience"] = "not specified"
        reasons.append("No experience requirement")
    elif cand_years is not None and cand_years >= job.years_experience:
        total += settings.MATCH_WEIGHT_EXPERIENCE
        matched["experience"] = cand_years
        reasons.append("Experience requirement satisfied")
    elif cand_years is not None and job.years_experience > 0:
        ratio = min(1.0, cand_years / job.years_experience)
        total += round(settings.MATCH_WEIGHT_EXPERIENCE * ratio, 2)
        unmatched["experience"] = f"{cand_years} vs {job.years_experience} years"
        reasons.append("Partial experience match")
    else:
        unmatched["experience"] = job.years_experience
        reasons.append("Experience requirement not met")

    min_pay = prefs.minimum_pay if prefs else None
    job_pay = job.pay_max if job.pay_max is not None else job.pay_min
    if job_pay is None or min_pay is None:
        total += settings.MATCH_WEIGHT_PAY
        matched["pay"] = "not specified"
        reasons.append("Pay preference not compared")
    elif job_pay >= min_pay:
        total += settings.MATCH_WEIGHT_PAY
        matched["pay"] = job_pay
        reasons.append("Pay meets your preference")
    else:
        unmatched["pay"] = job_pay
        reasons.append("Pay is below your preference")

    return MatchResult(
        score=min(100.0, round(total, 2)),
        matched_criteria=matched,
        unmatched_criteria=unmatched,
        explanation=reasons,
        distance_km=distance_km,
        distance_known=distance_known,
    )


def _upsert_match(db: Session, candidate: Candidate, job: Job, result: MatchResult) -> Match:
    existing = db.query(Match).filter(Match.candidate_id == candidate.id, Match.job_id == job.id).first()
    if existing:
        existing.match_score = result.score
        existing.matched_criteria = result.matched_criteria
        existing.unmatched_criteria = result.unmatched_criteria
        existing.explanation = result.explanation
        existing.distance_km = result.distance_km
        existing.distance_known = result.distance_known
        return existing
    match = Match(
        candidate_id=candidate.id,
        job_id=job.id,
        match_score=result.score,
        matched_criteria=result.matched_criteria,
        unmatched_criteria=result.unmatched_criteria,
        explanation=result.explanation,
        distance_km=result.distance_km,
        distance_known=result.distance_known,
    )
    db.add(match)
    return match


def generate_matches_for_candidate(
    db: Session, candidate: Candidate, min_score: float = 0.0, commit: bool = True
) -> list[Match]:
    open_jobs = db.query(Job).filter(Job.status == JobStatus.OPEN).all()
    results: list[Match] = []

    for job in open_jobs:
        result = score_candidate_job(candidate, job)
        if result.score < min_score:
            continue
        results.append(_upsert_match(db, candidate, job, result))

    db.flush()
    if commit:
        db.commit()
        for item in results:
            db.refresh(item)
    return sorted(results, key=lambda m: m.match_score, reverse=True)


def generate_matches_for_job(db: Session, job: Job, min_score: float = 0.0, commit: bool = True) -> list[Match]:
    if job.status != JobStatus.OPEN:
        return []
    candidates = (
        db.query(Candidate)
        .filter(Candidate.status == CandidateStatus.ACTIVE)
        .all()
    )
    results: list[Match] = []
    for candidate in candidates:
        result = score_candidate_job(candidate, job)
        if result.score < min_score:
            continue
        results.append(_upsert_match(db, candidate, job, result))
    db.flush()
    if commit:
        db.commit()
        for item in results:
            db.refresh(item)
    return sorted(results, key=lambda m: m.match_score, reverse=True)
