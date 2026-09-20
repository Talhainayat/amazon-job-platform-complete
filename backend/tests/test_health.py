def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "healthy"}


def test_docs_available(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


def test_http_errors_use_consistent_json_shape(client):
    not_found = client.get("/does-not-exist")
    assert not_found.status_code == 404
    assert isinstance(not_found.json()["detail"], str)

    invalid_payload = client.post("/api/auth/login", json={"email": "invalid"})
    assert invalid_payload.status_code == 422
    assert "detail" in invalid_payload.json()
