"""Approximate IP geolocation using the public ip-api.com endpoint."""
from __future__ import annotations

import httpx

from app.core.config import settings


def locate_ip(ip_address: str | None = None, http_client: httpx.Client | None = None) -> dict:
    client = http_client or httpx.Client(timeout=8.0)
    owns_client = http_client is None
    try:
        response = client.get(settings.IP_GEOLOCATION_URL, params={"fields": "status,city,regionName,zip,lat,lon,query"} if ip_address in (None, "", "127.0.0.1", "::1") else {"ip": ip_address, "fields": "status,city,regionName,zip,lat,lon,query"})
        response.raise_for_status()
        data = response.json()
        if data.get("status") != "success":
            raise ValueError(data.get("message", "Could not determine location"))
        return {"city": data.get("city"), "province": data.get("regionName"), "postal_code": data.get("zip"), "latitude": data.get("lat"), "longitude": data.get("lon"), "ip": data.get("query")}
    finally:
        if owns_client:
            client.close()