"""Frankfurter exchange-rate integration with a small in-process cache."""
from __future__ import annotations

from time import monotonic

import httpx

from app.core.config import settings

_cache: dict[str, tuple[float, dict[str, float]]] = {}
_CACHE_SECONDS = 900


def get_rates(base: str = "USD", http_client: httpx.Client | None = None) -> dict[str, float]:
    base = base.upper()
    cached = _cache.get(base)
    if cached and monotonic() - cached[0] < _CACHE_SECONDS:
        return cached[1]
    client = http_client or httpx.Client(timeout=10.0)
    owns_client = http_client is None
    try:
        response = client.get(settings.FRANKFURTER_URL, params={"from": base})
        response.raise_for_status()
        payload = response.json()
        rates = {base: 1.0, **{key: float(value) for key, value in payload.get("rates", {}).items()}}
        _cache[base] = (monotonic(), rates)
        return rates
    finally:
        if owns_client:
            client.close()


def convert_amount(amount: float | None, source: str, target: str, rates: dict[str, float] | None = None) -> float | None:
    if amount is None or source.upper() == target.upper():
        return amount
    rates = rates or get_rates(source)
    return amount * rates[target.upper()]