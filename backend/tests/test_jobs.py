def test_admin_can_create_job(client, admin_headers):
    resp = client.post(
        "/api/jobs",
        headers=admin_headers,
        json={
            "title": "Warehouse Associate",
            "location": "Toronto",
            "shift": "day",
            "job_type": "warehouse",
            "source": "manual_upload",
            "external_job_id": "job-001",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Warehouse Associate"


def test_duplicate_job_rejected(client, admin_headers):
    payload = {
        "title": "Sorter",
        "location": "Brampton",
        "source": "manual_upload",
        "external_job_id": "job-dup-001",
    }
    first = client.post("/api/jobs", headers=admin_headers, json=payload)
    assert first.status_code == 201
    second = client.post("/api/jobs", headers=admin_headers, json=payload)
    assert second.status_code == 409


def test_non_admin_cannot_create_job(client):
    reg = client.post(
        "/api/auth/register",
        json={"email": "notadmin@example.com", "password": "secret123", "name": "Not Admin"},
    )
    headers = {"Authorization": f"Bearer {reg.json()['access_token']}"}
    resp = client.post(
        "/api/jobs",
        headers=headers,
        json={"title": "X", "source": "manual_upload", "external_job_id": "job-x"},
    )
    assert resp.status_code == 403


def test_list_jobs_public(client, admin_headers):
    client.post(
        "/api/jobs",
        headers=admin_headers,
        json={"title": "Picker", "location": "Etobicoke", "source": "manual_upload", "external_job_id": "job-002"},
    )
    resp = client.get("/api/jobs")
    assert resp.status_code == 200
    body = resp.json()
    assert "items" in body
    assert len(body["items"]) >= 1


def test_external_apply_tracks_intent_before_redirect(client, admin_headers):
    created = client.post(
        "/api/jobs",
        headers=admin_headers,
        json={
            "title": "Amazon Fulfillment Associate",
            "company": "Amazon",
            "source": "amazon_official",
            "external_job_id": "amazon-track-001",
            "external_url": "https://hiring.amazon.ca/",
            "is_official_link": True,
        },
    )
    assert created.status_code == 201
    registered = client.post(
        "/api/auth/register",
        json={"email": "official@candidate.local", "password": "secret123", "name": "Official Candidate"},
    )
    headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}
    response = client.get(
        f"/api/jobs/{created.json()['id']}/apply-external",
        headers=headers,
        follow_redirects=False,
    )
    assert response.status_code == 307
    assert response.headers["location"] == "https://hiring.amazon.ca/"
