def test_candidate_and_admin_journey(client, admin_headers):
    register = client.post(
        "/api/auth/register",
        json={
            "email": "journey@example.com",
            "password": "secret123",
            "name": "Jordan Lee",
            "location": "Toronto",
        },
    )
    assert register.status_code == 201
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    me = client.get("/api/auth/me", headers=headers).json()
    cid = me["candidate_id"]
    assert cid

    profile = client.patch(
        f"/api/candidates/{cid}",
        headers=headers,
        json={
            "phone": "4165550100",
            "city": "Toronto",
            "province": "ON",
            "postal_code": "M5V 1A1",
            "job_type": "warehouse",
            "preferred_shift": "day",
            "skills": ["warehouse", "packing"],
            "years_experience": 2,
        },
    )
    assert profile.status_code == 200
    assert profile.json()["profile_completion"] > 0

    prefs = client.put(
        f"/api/candidates/{cid}/preferences",
        headers=headers,
        json={"location": "Toronto", "radius_km": 30, "shift": "day", "job_type": "warehouse", "minimum_pay": 18},
    )
    assert prefs.status_code == 200

    job = client.post(
        "/api/jobs",
        headers=admin_headers,
        json={
            "title": "Journey Warehouse",
            "company": "Acme",
            "location": "Toronto",
            "city": "Toronto",
            "shift": "day",
            "job_type": "warehouse",
            "skills": ["warehouse"],
            "pay_min": 20,
            "source": "manual_upload",
            "external_job_id": "journey-job-1",
            "status": "open",
        },
    )
    assert job.status_code == 201
    job_id = job.json()["id"]

    matches = client.post(f"/api/matches/candidates/{cid}/recalculate", headers=headers).json()
    assert matches
    assert matches[0]["match_score"] >= 70
    assert matches[0]["explanation"]

    detail = client.get(f"/api/jobs/{job_id}", headers=headers).json()
    assert detail["match_score"] is not None
    assert detail["already_applied"] is False

    applied = client.post("/api/applications", headers=headers, json={"job_id": job_id})
    assert applied.status_code == 201

    notes = client.get("/api/notifications/me", headers=headers).json()
    assert notes["total"] >= 1

    listed = client.get(f"/api/applications/candidates/{cid}", headers=headers).json()
    assert listed[0]["status"] == "applied"

    updated = client.patch(
        f"/api/applications/{applied.json()['id']}",
        headers=admin_headers,
        json={"status": "interview"},
    )
    assert updated.status_code == 200

    summary = client.get("/api/admin/summary", headers=admin_headers).json()
    assert summary["total_jobs"] >= 1
    assert summary["total_applications"] >= 1

    closed = client.post(f"/api/jobs/{job_id}/close", headers=admin_headers)
    assert closed.status_code == 200
    assert closed.json()["status"] == "closed"
