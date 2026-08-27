def _register_and_get_id(client, admin_headers, email):
    reg = client.post(
        "/api/auth/register", json={"email": email, "password": "secret123", "name": "App Cand"}
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    listing = client.get("/api/candidates", headers=admin_headers).json()
    candidate_id = next(c["id"] for c in listing if c["email"] == email)
    return candidate_id, headers


def test_create_and_update_application(client, admin_headers):
    candidate_id, headers = _register_and_get_id(client, admin_headers, "appcand1@example.com")
    job_resp = client.post(
        "/api/jobs",
        headers=admin_headers,
        json={"title": "Picker", "source": "manual_upload", "external_job_id": "app-job-001"},
    )
    job_id = job_resp.json()["id"]

    create = client.post(
        "/api/applications",
        headers=headers,
        json={"candidate_id": candidate_id, "job_id": job_id, "notes": "Looks good"},
    )
    assert create.status_code == 201
    app_id = create.json()["id"]
    assert create.json()["status"] == "applied"
    assert create.json()["applied_at"] is not None

    update = client.patch(
        f"/api/applications/{app_id}", headers=headers, json={"status": "withdrawn"}
    )
    assert update.status_code == 200
    assert update.json()["status"] == "withdrawn"


def test_list_applications_for_candidate(client, admin_headers):
    candidate_id, headers = _register_and_get_id(client, admin_headers, "appcand2@example.com")
    job_resp = client.post(
        "/api/jobs",
        headers=admin_headers,
        json={"title": "Sorter", "source": "manual_upload", "external_job_id": "app-job-002"},
    )
    job_id = job_resp.json()["id"]
    client.post(
        "/api/applications", headers=headers, json={"candidate_id": candidate_id, "job_id": job_id}
    )
    resp = client.get(f"/api/applications/candidates/{candidate_id}", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
