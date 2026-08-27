"""Development demo data. Never used as production credentials."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.models.application import Application, ApplicationStatus, InterviewStatus
from app.models.candidate import Candidate, CandidateStatus
from app.models.candidate_preference import CandidatePreference
from app.models.job import Job, JobStatus
from app.models.user import User, UserRole
from app.services.matching import generate_matches_for_candidate
from app.services.notification_service import create_notification

SUPER_ADMIN_NAME = "Talha Inayat"
SUPER_ADMIN_EMAIL = "talhainayat302@gmail.com"
SUPER_ADMIN_PASSWORD = "DemoAdmin123!"
DEMO_ADMIN_EMAIL = "admin@demo.local"
DEMO_CANDIDATE_EMAIL = "candidate@demo.local"
DEMO_CANDIDATE_PASSWORD = "DemoCand123!"


def seed_if_needed(db: Session) -> None:
    if not settings.SEED_DEMO_DATA:
        return
    admin = db.query(User).filter(User.email == SUPER_ADMIN_EMAIL).first()
    legacy_admin = db.query(User).filter(User.email == DEMO_ADMIN_EMAIL).first()
    if not admin and legacy_admin:
        admin = legacy_admin
        admin.email = SUPER_ADMIN_EMAIL
    if not admin:
        admin = User(email=SUPER_ADMIN_EMAIL, hashed_password=hash_password(SUPER_ADMIN_PASSWORD))
        db.add(admin)
    admin.name = SUPER_ADMIN_NAME
    admin.email = SUPER_ADMIN_EMAIL
    admin.hashed_password = hash_password(SUPER_ADMIN_PASSWORD)
    admin.role = UserRole.ADMIN
    admin.is_active = True

    if db.query(User).filter(User.email == DEMO_CANDIDATE_EMAIL).first():
        db.commit()
        return

    candidate_user = User(
        email=DEMO_CANDIDATE_EMAIL,
        hashed_password=hash_password(DEMO_CANDIDATE_PASSWORD),
        role=UserRole.CANDIDATE,
    )
    db.add_all([admin, candidate_user])
    db.flush()

    candidate = Candidate(
        user_id=candidate_user.id,
        name="Alex Rivera",
        email=DEMO_CANDIDATE_EMAIL,
        phone="416-555-0142",
        location="Toronto",
        city="Toronto",
        province="ON",
        postal_code="M5V 2T6",
        preferred_city="Toronto",
        preferred_shift="day",
        job_type="warehouse",
        skills=["warehouse", "forklift", "inventory", "packing"],
        years_experience=3,
        experience="3 years in fulfillment and warehouse operations.",
        education="High school diploma",
        availability="Immediately",
        has_vehicle=True,
        status=CandidateStatus.ACTIVE,
    )
    db.add(candidate)
    db.flush()
    db.add(
        CandidatePreference(
            candidate_id=candidate.id,
            location="Toronto",
            radius_km=30,
            shift="day",
            job_type="warehouse",
            minimum_pay=20,
            availability="Immediately",
            has_vehicle=True,
            years_experience=3,
        )
    )

    now = datetime.now(timezone.utc)
    jobs = [
        Job(
            title="Warehouse Associate",
            company="Northstar Logistics",
            description="Pick, pack, and ship orders in a modern fulfillment centre. Steel-toe boots required.",
            requirements="Ability to lift 40 lbs. Comfortable standing for a full shift.",
            location="Toronto",
            city="Toronto",
            province="ON",
            postal_code="M9W 1A1",
            shift="day",
            job_type="warehouse",
            skills=["warehouse", "packing", "inventory"],
            years_experience=1,
            openings=12,
            pay_min=21,
            pay_max=24,
            pay_period="hourly",
            source="manual_upload",
            external_job_id="demo-wh-001",
            status=JobStatus.OPEN,
            posted_at=now - timedelta(days=2),
            application_deadline=now + timedelta(days=21),
        ),
        Job(
            title="Night Shift Sorter",
            company="RapidSort Inc.",
            description="Sort parcels on an overnight shift at a high-volume hub.",
            requirements="Must be available overnight. Prior warehouse experience preferred.",
            location="Brampton",
            city="Brampton",
            province="ON",
            postal_code="L6T 5R5",
            shift="night",
            job_type="warehouse",
            skills=["sorting", "warehouse"],
            years_experience=0,
            openings=8,
            pay_min=22,
            pay_max=26,
            pay_period="hourly",
            source="manual_upload",
            external_job_id="demo-wh-002",
            status=JobStatus.OPEN,
            posted_at=now - timedelta(days=1),
        ),
        Job(
            title="Delivery Driver",
            company="CityLink Express",
            description="Local delivery routes across the GTA. Vehicle and valid license required.",
            location="Mississauga",
            city="Mississauga",
            province="ON",
            postal_code="L5B 1M5",
            shift="day",
            job_type="driver",
            skills=["driving", "navigation", "customer service"],
            years_experience=2,
            openings=4,
            pay_min=23,
            pay_max=28,
            pay_period="hourly",
            source="manual_upload",
            external_job_id="demo-dr-001",
            status=JobStatus.OPEN,
            posted_at=now - timedelta(days=4),
        ),
        Job(
            title="Inventory Clerk (Draft)",
            company="Northstar Logistics",
            description="Internal draft role — not yet published to candidates.",
            location="Toronto",
            city="Toronto",
            province="ON",
            shift="day",
            job_type="warehouse",
            source="manual_upload",
            external_job_id="demo-draft-001",
            status=JobStatus.DRAFT,
        ),
    ]
    db.add_all(jobs)
    db.flush()

    open_job = jobs[0]
    application = Application(
        candidate_id=candidate.id,
        job_id=open_job.id,
        status=ApplicationStatus.REVIEWING,
        applied_at=now - timedelta(days=1),
        notes="Excited to join the day shift team.",
        interview_status=InterviewStatus.SCHEDULED,
        interview_date=now + timedelta(days=5),
    )
    db.add(application)
    db.flush()

    create_notification(
        db,
        candidate=candidate,
        title="Application received",
        message="Your application for Warehouse Associate was submitted.",
        notification_type="application_submitted",
        job_id=open_job.id,
        application_id=application.id,
        commit=False,
    )
    create_notification(
        db,
        candidate=candidate,
        title="Status update",
        message="Your Warehouse Associate application is now under review.",
        notification_type="application_status",
        job_id=open_job.id,
        application_id=application.id,
        commit=False,
    )
    db.commit()
    generate_matches_for_candidate(db, candidate)
