def test_duplicate_application_rejected(client, admin_headers):
    reg = client.post(
        "/api/auth/register", json={"email": "dupapp@example.com", "password": "secret123", "name": "Dup App"}
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    listing = client.get("/api/candidates", headers=admin_headers).json()
    candidate_id = next(c["id"] for c in listing if c["email"] == "dupapp@example.com")
    job = client.post(
        "/api/jobs",
        headers=admin_headers,
        json={"title": "Packer", "source": "manual_upload", "external_job_id": "dup-app-job"},
    ).json()
    first = client.post(
        "/api/applications", headers=headers, json={"candidate_id": candidate_id, "job_id": job["id"]}
    )
    second = client.post(
        "/api/applications", headers=headers, json={"candidate_id": candidate_id, "job_id": job["id"]}
    )
    assert first.status_code == 201
    assert second.status_code == 409


def test_candidate_cannot_hire_themselves(client, admin_headers):
    reg = client.post(
        "/api/auth/register", json={"email": "nohire@example.com", "password": "secret123", "name": "No Hire"}
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    listing = client.get("/api/candidates", headers=admin_headers).json()
    candidate_id = next(c["id"] for c in listing if c["email"] == "nohire@example.com")
    job = client.post(
        "/api/jobs",
        headers=admin_headers,
        json={"title": "Clerk", "source": "manual_upload", "external_job_id": "no-hire-job"},
    ).json()
    created = client.post(
        "/api/applications", headers=headers, json={"candidate_id": candidate_id, "job_id": job["id"]}
    ).json()
    resp = client.patch(f"/api/applications/{created['id']}", headers=headers, json={"status": "hired"})
    assert resp.status_code == 403


def test_admin_can_update_application_status(client, admin_headers):
    reg = client.post(
        "/api/auth/register", json={"email": "hireme@example.com", "password": "secret123", "name": "Hire Me"}
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    listing = client.get("/api/candidates", headers=admin_headers).json()
    candidate_id = next(c["id"] for c in listing if c["email"] == "hireme@example.com")
    job = client.post(
        "/api/jobs",
        headers=admin_headers,
        json={"title": "Lead", "source": "manual_upload", "external_job_id": "hire-job"},
    ).json()
    created = client.post(
        "/api/applications", headers=headers, json={"candidate_id": candidate_id, "job_id": job["id"]}
    ).json()
    resp = client.patch(
        f"/api/applications/{created['id']}", headers=admin_headers, json={"status": "interview"}
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "interview"


def test_job_search_and_publish(client, admin_headers):
    draft = client.post(
        "/api/jobs",
        headers=admin_headers,
        json={
            "title": "Draft Role",
            "source": "manual_upload",
            "external_job_id": "draft-role-1",
            "status": "draft",
        },
    )
    assert draft.status_code == 201
    job_id = draft.json()["id"]
    public = client.get("/api/jobs")
    ids = [item["id"] for item in public.json()["items"]]
    assert job_id not in ids
    published = client.post(f"/api/jobs/{job_id}/publish", headers=admin_headers)
    assert published.status_code == 200
    assert published.json()["status"] == "open"
