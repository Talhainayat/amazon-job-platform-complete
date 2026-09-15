"""Bundled sample job feed for local HITL demos (no third-party login)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.job_sources.base import JobSource, RawJob

SAMPLE_PATH = Path(__file__).with_name("sample_jobs.json")


class SampleFeedSource(JobSource):
    name = "sample_feed"

    def fetch_jobs(self) -> list[RawJob]:
        if not SAMPLE_PATH.exists():
            return []
        payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
        rows = payload.get("jobs", payload) if isinstance(payload, dict) else payload
        jobs: list[RawJob] = []
        now = datetime.now(timezone.utc)
        for row in rows or []:
            jobs.append(
                RawJob(
                    external_job_id=str(row["external_job_id"]),
                    title=row["title"],
                    company=row.get("company"),
                    description=row.get("description"),
                    location=row.get("location"),
                    city=row.get("city") or row.get("location"),
                    province=row.get("province"),
                    postal_code=row.get("postal_code"),
                    shift=row.get("shift"),
                    job_type=row.get("job_type"),
                    skills=row.get("skills") or [],
                    years_experience=row.get("years_experience"),
                    openings=int(row.get("openings") or 1),
                    pay_min=row.get("pay_min"),
                    pay_max=row.get("pay_max"),
                    pay_period=row.get("pay_period"),
                    job_url=row.get("job_url"),
                    external_url=row.get("external_url") or row.get("job_url"),
                    is_official_link=row.get("is_official_link", True),
                    posted_at=now,
                    source=self.name,
                )
            )
        return jobs
