def _register_candidate(client, email="cand1@example.com"):
    resp = client.post(
        "/api/auth/register",
        json={"email": email, "password": "secret123", "name": "Cand One", "location": "Toronto"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_list_candidates(client, admin_headers):
    _register_candidate(client, "list1@example.com")
    resp = client.get("/api/candidates", headers=admin_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


def test_candidate_cannot_list_all(client):
    headers = _register_candidate(client, "nolistaccess@example.com")
    resp = client.get("/api/candidates", headers=headers)
    assert resp.status_code == 403


def test_candidate_can_view_and_update_own_profile(client):
    headers = _register_candidate(client, "self1@example.com")
    me = client.get("/api/auth/me", headers=headers)
    # find candidate id via admin listing lookup by email (simplest for test)
    admin_login = client.post("/api/auth/login", json={"email": "admin@test.com", "password": "admin123"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    listing = client.get("/api/candidates", headers=admin_headers).json()
    candidate_id = next(c["id"] for c in listing if c["email"] == "self1@example.com")

    resp = client.get(f"/api/candidates/{candidate_id}", headers=headers)
    assert resp.status_code == 200

    update = client.patch(
        f"/api/candidates/{candidate_id}", headers=headers, json={"location": "Mississauga"}
    )
    assert update.status_code == 200
    assert update.json()["location"] == "Mississauga"


def test_candidate_preferences_upsert(client, admin_headers):
    headers = _register_candidate(client, "prefs1@example.com")
    listing = client.get("/api/candidates", headers=admin_headers).json()
    candidate_id = next(c["id"] for c in listing if c["email"] == "prefs1@example.com")

    resp = client.put(
        f"/api/candidates/{candidate_id}/preferences",
        headers=headers,
        json={"location": "Toronto", "radius_km": 15, "shift": "day", "job_type": "warehouse"},
    )
    assert resp.status_code == 200
    assert resp.json()["shift"] == "day"
