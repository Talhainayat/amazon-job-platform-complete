def test_register_candidate(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "jane@example.com",
            "password": "secret123",
            "name": "Jane Doe",
            "phone": "555-0100",
            "location": "Toronto",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["role"] == "candidate"
    assert "access_token" in body


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"email": "login1@example.com", "password": "secret123", "name": "Login One"},
    )
    resp = client.post("/api/auth/login", json={"email": "login1@example.com", "password": "secret123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "login2@example.com", "password": "secret123", "name": "Login Two"},
    )
    resp = client.post("/api/auth/login", json={"email": "login2@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_me_requires_auth(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401


def test_me_with_token(client):
    client.post(
        "/api/auth/register",
        json={"email": "login3@example.com", "password": "secret123", "name": "Login Three"},
    )
    login = client.post("/api/auth/login", json={"email": "login3@example.com", "password": "secret123"})
    token = login.json()["access_token"]
    resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "login3@example.com"


def test_duplicate_registration_rejected(client):
    client.post(
        "/api/auth/register",
        json={"email": "dupe@example.com", "password": "secret123", "name": "Dupe One"},
    )
    resp = client.post(
        "/api/auth/register",
        json={"email": "dupe@example.com", "password": "secret123", "name": "Dupe Two"},
    )
    assert resp.status_code == 400
