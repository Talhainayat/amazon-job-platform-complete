"""
Background tasks. Each task opens its own DB session since Celery workers
run in separate processes.
"""
from app.services.job_ingest import run_job_monitor_cycle
from app.db.session import SessionLocal
from app.models.candidate import Candidate, CandidateStatus
from app.services.matching import generate_matches_for_candidate
from app.workers.celery_app import celery_app


@celery_app.task(name="workers.import_jobs")
def import_jobs_task(source_name: str | None = None) -> dict:
    """Fetch jobs from a registered JobSource, skip duplicates, then match + alert."""
    return run_job_monitor_cycle(source_name)


@celery_app.task(name="workers.recalculate_all_matches")
def recalculate_all_matches_task() -> dict:
    """Recalculate matches for every active candidate against all open jobs."""
    db = SessionLocal()
    try:
        candidates = db.query(Candidate).filter(Candidate.status == CandidateStatus.ACTIVE).all()
        total_matches = 0
        for candidate in candidates:
            matches = generate_matches_for_candidate(db, candidate)
            total_matches += len(matches)
        return {"candidates_processed": len(candidates), "matches_generated": total_matches}
    finally:
        db.close()


@celery_app.task(name="workers.send_pending_notifications")
def send_pending_notifications_task() -> dict:
    return {"status": "delegated_to_ingest_alerts"}
