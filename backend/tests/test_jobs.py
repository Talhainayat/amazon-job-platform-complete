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
