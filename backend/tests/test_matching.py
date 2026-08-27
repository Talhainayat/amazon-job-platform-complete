def _make_candidate_with_prefs(client, admin_headers, email, location, shift, job_type):
    reg = client.post(
        "/api/auth/register",
        json={"email": email, "password": "secret123", "name": "Match Cand", "location": location},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    listing = client.get("/api/candidates", headers=admin_headers).json()
    candidate_id = next(c["id"] for c in listing if c["email"] == email)
    client.put(
        f"/api/candidates/{candidate_id}/preferences",
        headers=headers,
        json={"location": location, "radius_km": 10, "shift": shift, "job_type": job_type},
    )
    return candidate_id, headers


def test_matching_scores_full_match_100(client, admin_headers):
    candidate_id, headers = _make_candidate_with_prefs(
        client, admin_headers, "matcher1@example.com", "Toronto", "day", "warehouse"
    )
    client.post(
        "/api/jobs",
        headers=admin_headers,
        json={
            "title": "Warehouse Day",
            "location": "Toronto",
            "shift": "day",
            "job_type": "warehouse",
            "source": "manual_upload",
            "external_job_id": "match-job-001",
        },
    )
    resp = client.post(f"/api/matches/candidates/{candidate_id}/recalculate", headers=headers)
    assert resp.status_code == 200
    matches = resp.json()
    assert len(matches) >= 1
    best = max(matches, key=lambda m: m["match_score"])
    assert best["match_score"] == 100.0
    assert set(best["matched_criteria"].keys()) >= {"location", "job_type", "shift"}


def test_matching_scores_partial_match(client, admin_headers):
    candidate_id, headers = _make_candidate_with_prefs(
        client, admin_headers, "matcher2@example.com", "Toronto", "night", "warehouse"
    )
    client.post(
        "/api/jobs",
        headers=admin_headers,
        json={
            "title": "Warehouse Day Only",
            "location": "Toronto",
            "shift": "day",
            "job_type": "warehouse",
            "source": "manual_upload",
            "external_job_id": "match-job-002",
        },
    )
    resp = client.post(f"/api/matches/candidates/{candidate_id}/recalculate", headers=headers)
    matches = resp.json()
    job = next(m for m in matches if m.get("unmatched_criteria", {}).get("shift") == "day")
    # location(35) + skills(20 n/a) + job_type(15) + shift(0) + experience(8 n/a) + pay(7 n/a) = 85
    assert job["match_score"] == 85.0


def test_matching_forbidden_for_other_candidate(client, admin_headers):
    candidate_id, _ = _make_candidate_with_prefs(
        client, admin_headers, "matcher3@example.com", "Toronto", "day", "warehouse"
    )
    other_reg = client.post(
        "/api/auth/register",
        json={"email": "othercand@example.com", "password": "secret123", "name": "Other"},
    )
    other_headers = {"Authorization": f"Bearer {other_reg.json()['access_token']}"}
    resp = client.get(f"/api/matches/candidates/{candidate_id}", headers=other_headers)
    assert resp.status_code == 403
