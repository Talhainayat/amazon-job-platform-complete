"""Permitted HTTP JSON job feed. Does not log into employer portals."""
from __future__ import annotations

from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.job_sources.base import JobSource, RawJob


def _as_list(payload) -> list:
    if payload is None:
        return []
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        for key in ("jobs", "items", "data", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
    return []


class HttpJsonFeedSource(JobSource):
    name = "http_json"

    def __init__(self, url: str | None = None):
        self.url = (url or settings.JOB_FEED_URL or "").strip()

    def fetch_jobs(self) -> list[RawJob]:
        if not self.url:
            return []
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(self.url)
            response.raise_for_status()
            rows = _as_list(response.json())

        jobs: list[RawJob] = []
        now = datetime.now(timezone.utc)
        for row in rows:
            external_id = row.get("external_job_id") or row.get("id") or row.get("job_id")
            title = row.get("title") or row.get("job_title")
            if not external_id or not title:
                continue
            jobs.append(
                RawJob(
                    external_job_id=str(external_id),
                    title=str(title),
                    company=row.get("company"),
                    description=row.get("description"),
                    location=row.get("location"),
                    city=row.get("city") or row.get("location"),
                    province=row.get("province") or row.get("state"),
                    postal_code=row.get("postal_code") or row.get("zip"),
                    shift=row.get("shift"),
                    job_type=row.get("job_type") or row.get("type"),
                    skills=row.get("skills") or [],
                    years_experience=row.get("years_experience"),
                    openings=int(row.get("openings") or 1),
                    pay_min=row.get("pay_min") or row.get("pay"),
                    pay_max=row.get("pay_max"),
                    pay_period=row.get("pay_period"),
                    job_url=row.get("job_url") or row.get("url"),
                    external_url=row.get("external_url") or row.get("job_url") or row.get("url"),
                    is_official_link=row.get("is_official_link", True),
                    posted_at=now,
                    source=self.name,
                )
            )
        return jobs
