"""In-process job monitor so HITL alerts work without Redis/Celery."""
from __future__ import annotations

import logging
import threading

from app.core.config import settings

logger = logging.getLogger(__name__)

_stop = threading.Event()
_thread: threading.Thread | None = None


def start_job_monitor() -> None:
    global _thread
    if not settings.JOB_MONITOR_ENABLED:
        logger.info("Job monitor disabled")
        return
    if _thread and _thread.is_alive():
        return
    _stop.clear()
    interval = max(15, int(settings.JOB_MONITOR_INTERVAL_SECONDS or 60))
    _thread = threading.Thread(target=_loop, args=(interval,), name="job-monitor", daemon=True)
    _thread.start()
    logger.info("Job monitor started (every %ss)", interval)


def stop_job_monitor() -> None:
    _stop.set()


def _loop(interval: int) -> None:
    from app.services.job_ingest import run_job_monitor_cycle

    while not _stop.is_set():
        try:
            result = run_job_monitor_cycle()
            logger.info("Job monitor cycle: %s", result)
        except Exception:
            logger.exception("Job monitor cycle error")
        _stop.wait(interval)
