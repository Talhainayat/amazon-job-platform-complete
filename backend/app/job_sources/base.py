"""
Pluggable job source architecture.

A JobSource represents ONE legitimate, permitted way of obtaining job
listings (an official API, an RSS/JSON feed the employer publishes, a
manually-curated CSV, etc). Implementations must NOT scrape sites in a
way that violates their terms of service, bypass CAPTCHA/anti-bot
protections, or perform automated logins.

To add a new source: subclass JobSource, implement fetch_jobs(), and
register it in AVAILABLE_SOURCES below.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawJob:
    """Normalized job data returned by any JobSource, before DB insertion."""
    external_job_id: str
    title: str
    company: str | None = None
    description: str | None = None
    location: str | None = None
    city: str | None = None
    province: str | None = None
    postal_code: str | None = None
    shift: str | None = None
    job_type: str | None = None
    skills: list | None = None
    years_experience: int | None = None
    openings: int = 1
    pay_min: float | None = None
    pay_max: float | None = None
    pay_period: str | None = None
    job_url: str | None = None
    posted_at: datetime | None = None
    source: str = ""
    extra: dict = field(default_factory=dict)


class JobSource(ABC):
    """Base class every job source integration must implement."""

    name: str = "base"

    @abstractmethod
    def fetch_jobs(self) -> list[RawJob]:
        """
        Fetch current job postings from this source.

        Must only use permitted/official channels (public APIs, RSS/JSON
        feeds, manually uploaded files). Must never require storing a
        user's Amazon (or any employer) password or session cookies, and
        must never attempt to bypass CAPTCHA or anti-bot protections.
        """
        raise NotImplementedError


class ManualUploadSource(JobSource):
    """
    Example source: jobs added manually/via CSV import by an admin,
    rather than pulled from any external system. Always compliant since
    it involves no automated access to a third-party site.
    """
    name = "manual_upload"

    def __init__(self, raw_jobs: list[RawJob] | None = None):
        self._raw_jobs = raw_jobs or []

    def fetch_jobs(self) -> list[RawJob]:
        for job in self._raw_jobs:
            job.source = self.name
        return self._raw_jobs


# Register available sources here as they're implemented.
AVAILABLE_SOURCES: dict[str, type[JobSource]] = {
    ManualUploadSource.name: ManualUploadSource,
}


def _register_builtin_sources() -> None:
    from app.job_sources.http_feed import HttpJsonFeedSource
    from app.job_sources.sample_feed import SampleFeedSource

    AVAILABLE_SOURCES[SampleFeedSource.name] = SampleFeedSource
    AVAILABLE_SOURCES[HttpJsonFeedSource.name] = HttpJsonFeedSource


_register_builtin_sources()
