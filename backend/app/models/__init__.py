"""
Import all models here so Alembic's autogenerate and Base.metadata
can discover every table.
"""
from app.models.user import User, UserRole  # noqa
from app.models.candidate import Candidate, CandidateStatus  # noqa
from app.models.candidate_preference import CandidatePreference  # noqa
from app.models.job import Job, JobStatus  # noqa
from app.models.match import Match  # noqa
from app.models.application import Application, ApplicationStatus, InterviewStatus  # noqa
from app.models.notification import Notification, NotificationChannel, NotificationStatus  # noqa
from app.models.audit_log import AuditLog  # noqa
from app.models.contact_inquiry import ContactInquiry  # noqa
from app.models.managed_site import ManagedSite  # noqa
