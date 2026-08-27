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
