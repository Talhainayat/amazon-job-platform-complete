from app.models.candidate import Candidate
from app.models.candidate_preference import CandidatePreference
from app.models.job import Job
from app.services.matching import score_candidate_job


def test_score_full_and_partial_without_db():
    candidate = Candidate(
        user_id=1,
        name="Pat",
        email="pat@example.com",
        location="Toronto",
        city="Toronto",
        job_type="warehouse",
        preferred_shift="day",
        skills=["warehouse", "packing"],
        years_experience=2,
    )
    candidate.preferences = CandidatePreference(
        candidate_id=1,
        location="Toronto",
        radius_km=25,
        shift="day",
        job_type="warehouse",
        minimum_pay=18,
        years_experience=2,
    )
    full = Job(
        title="Warehouse",
        location="Toronto",
        city="Toronto",
        shift="day",
        job_type="warehouse",
        source="manual_upload",
        external_job_id="u1",
        skills=["warehouse"],
        years_experience=1,
        pay_min=20,
        pay_max=24,
    )
    result = score_candidate_job(candidate, full)
    assert result.score == 100
    assert any("Shift matches" in item for item in result.explanation)

    night = Job(
        title="Night",
        location="Toronto",
        city="Toronto",
        shift="night",
        job_type="warehouse",
        source="manual_upload",
        external_job_id="u2",
    )
    partial = score_candidate_job(candidate, night)
    assert partial.score == 85.0
    assert "Shift does not match" in partial.explanation
