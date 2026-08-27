"""
Celery application setup for background processing.

Requires Redis to actually run workers (not available in the build/
sandbox environment this project was scaffolded in -- install and run
Redis locally, then start a worker with:

    celery -A app.workers.celery_app worker --loglevel=info

This module is safe to import even when Redis is not running; only
task *execution* requires a live broker.
"""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "job_platform",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "import-jobs-every-minute": {
            "task": "workers.import_jobs",
            "schedule": 60.0,
        }
    },
)
