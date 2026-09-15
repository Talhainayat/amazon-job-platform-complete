import httpx

from app.services.currency_service import convert_amount, get_rates
from app.services.geo_service import locate_ip
from app.services.job_fetcher import fetch_live_jobs


class MockClient:
    def __init__(self, payload):
        self.payload = payload

    def get(self, *args, **kwargs):
        return httpx.Response(200, json=self.payload, request=httpx.Request("GET", "https://example.test"))


def test_live_job_fetcher_normalizes_public_payload():
    jobs = fetch_live_jobs(MockClient({"data": [{"slug": "python-role", "title": "Python Developer", "company_name": "Example", "location": "Remote", "tags": ["python"], "url": "https://example.test/jobs/python"}]}))
    assert jobs[0].external_job_id == "arbeitnow-python-role"
    assert jobs[0].external_url == "https://example.test/jobs/python"
    assert jobs[0].skills == ["python"]


def test_currency_service_converts_using_mock_rates(monkeypatch):
    monkeypatch.setattr("app.services.currency_service.settings.FRANKFURTER_URL", "https://example.test/latest")
    rates = get_rates("USD", MockClient({"rates": {"CAD": 1.35}}))
    assert rates["CAD"] == 1.35
    assert convert_amount(10, "USD", "CAD", rates) == 13.5


def test_geo_service_normalizes_mock_ip_response():
    result = locate_ip("203.0.113.10", MockClient({"status": "success", "city": "Toronto", "regionName": "ON", "zip": "M5V", "lat": 43.65, "lon": -79.38, "query": "203.0.113.10"}))
    assert result["city"] == "Toronto"
    assert result["latitude"] == 43.65