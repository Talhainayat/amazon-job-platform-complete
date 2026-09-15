"""Small, permitted Amazon job feed helpers for demos and local development."""
from __future__ import annotations

from datetime import datetime, timezone

from app.job_sources.base import RawJob
import httpx

from app.core.config import settings


AMAZON_JOBS_URL = "https://www.amazon.jobs/en/search"
AMAZON_FULFILLMENT_URL = "https://hiring.amazon.ca/"
AMAZON_DSP_URL = "https://logistics.amazon.com/marketing"


def fetch_live_jobs(http_client: httpx.Client | None = None) -> list[RawJob]:
    """Fetch public Arbeitnow listings without authentication or scraping."""
    client = http_client or httpx.Client(timeout=20.0, follow_redirects=True)
    owns_client = http_client is None
    try:
        response = client.get(settings.LIVE_JOB_FEED_URL)
        response.raise_for_status()
        rows = response.json().get("data", [])
        jobs = []
        for row in rows:
            url = row.get("url")
            title = row.get("title")
            if not title or not url:
                continue
            location = row.get("location") or "Remote"
            jobs.append(RawJob(
                external_job_id=f"arbeitnow-{row.get('slug') or row.get('id') or url}",
                title=title,
                company=row.get("company_name") or "Unknown company",
                description=row.get("description"),
                location=location,
                city=location,
                job_type="technology",
                skills=row.get("tags") or [],
                external_url=url,
                job_url=url,
                pay_currency="USD",
                source="arbeitnow",
                is_official_link=False,
            ))
        return jobs
    finally:
        if owns_client:
            client.close()


def fetch_amazon_jobs() -> list[RawJob]:
    """Return curated official-link records when no official API is configured."""
    now = datetime.now(timezone.utc)
    return [
        RawJob(
            external_job_id="amazon-fulfillment-associate-demo",
            title="Amazon Fulfillment Associate",
            company="Amazon",
            description="Pick, pack, and ship customer orders in an Amazon fulfillment centre.",
            location="Toronto, ON",
            city="Toronto",
            province="ON",
            job_type="warehouse",
            skills=["warehouse", "packing", "inventory"],
            pay_min=21.50,
            pay_max=24.50,
            pay_period="hourly",
            external_url=AMAZON_FULFILLMENT_URL,
            is_official_link=True,
            posted_at=now,
            source="amazon_official",
        ),
        RawJob(
            external_job_id="amazon-delivery-associate-demo",
            title="Amazon Delivery Associate",
            company="Amazon DSP",
            description="Deliver packages on local routes through an independent Amazon Delivery Service Partner.",
            location="Mississauga, ON",
            city="Mississauga",
            province="ON",
            job_type="driver",
            skills=["driving", "navigation", "customer service"],
            pay_min=23.00,
            pay_max=28.00,
            pay_period="hourly",
            external_url=AMAZON_DSP_URL,
            is_official_link=True,
            posted_at=now,
            source="amazon_official",
        ),
    ]