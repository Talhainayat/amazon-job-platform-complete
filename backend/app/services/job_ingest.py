"""Fetch permitted job feeds, persist new jobs, then run matching + manager alerts."""
from __future__ import annotations

import logging

from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.db.session import SessionLocal
from app.job_sources.base import AVAILABLE_SOURCES, RawJob
from app.models.job import Job, JobStatus
from app.models.match import Match
from app.services.geo import resolve_point
from app.services.matching import generate_matches_for_job
from app.services.notification_service import send_manager_match_alert

logger = logging.getLogger(__name__)


def resolve_source_name(source_name: str | None = None) -> str:
    if settings.JOB_FEED_URL:
        return "http_json"
    return source_name or settings.JOB_FEED_SOURCE or "sample_feed"


def raw_job_to_model(raw: RawJob) -> Job:
    city = raw.city or raw.location
    point = resolve_point(city=city, location=raw.location)
    return Job(
        title=raw.title,
        company=raw.company,
        description=raw.description,
        location=raw.location,
        city=city,
        province=raw.province,
        postal_code=raw.postal_code,
        latitude=point.latitude if point else None,
        longitude=point.longitude if point else None,
        shift=raw.shift,
        job_type=raw.job_type,
        skills=raw.skills or [],
        years_experience=raw.years_experience,
        openings=raw.openings or 1,
        pay_min=raw.pay_min,
        pay_max=raw.pay_max,
        pay_period=raw.pay_period,
        source=raw.source,
        external_job_id=raw.external_job_id,
        job_url=raw.job_url,
        posted_at=raw.posted_at,
        status=JobStatus.OPEN,
    )


def import_jobs(db: Session, source_name: str | None = None) -> tuple[list[Job], int]:
    name = resolve_source_name(source_name)
    source_cls = AVAILABLE_SOURCES.get(name)
    if not source_cls:
        raise ValueError(f"Unknown job source: {name}")
    source = source_cls()
    imported: list[Job] = []
    skipped = 0
    for raw in source.fetch_jobs():
        exists = (
            db.query(Job)
            .filter(Job.source == raw.source, Job.external_job_id == raw.external_job_id)
            .first()
        )
        if exists:
            skipped += 1
            continue
        job = raw_job_to_model(raw)
        db.add(job)
        imported.append(job)
    db.flush()
    return imported, skipped


def alert_high_matches_for_jobs(db: Session, jobs: list[Job]) -> int:
    if not jobs:
        return 0
    job_ids = [job.id for job in jobs if job.id]
    if not job_ids:
        return 0
    matches = (
        db.query(Match)
        .options(joinedload(Match.candidate), joinedload(Match.job))
        .filter(Match.job_id.in_(job_ids), Match.match_score >= settings.HIGH_MATCH_THRESHOLD)
        .all()
    )
    alerted = 0
    for match in matches:
        if send_manager_match_alert(db, match, commit=False):
            alerted += 1
    db.commit()
    return alerted


def ingest_and_match(db: Session, source_name: str | None = None) -> dict:
    imported, skipped = import_jobs(db, source_name)
    db.commit()
    match_count = 0
    for job in imported:
        matches = generate_matches_for_job(db, job, commit=True)
        match_count += len(matches)
    alerted = alert_high_matches_for_jobs(db, imported)
    return {
        "source": resolve_source_name(source_name),
        "imported": len(imported),
        "skipped_duplicates": skipped,
        "matches_generated": match_count,
        "manager_alerts": alerted,
    }


def run_job_monitor_cycle(source_name: str | None = None) -> dict:
    db = SessionLocal()
    try:
        return ingest_and_match(db, source_name)
    except Exception:
        db.rollback()
        logger.exception("Job monitor cycle failed")
        raise
    finally:
        db.close()
