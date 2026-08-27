"""
Geographic matching helpers.

Uses known city coordinates when available. If a precise distance cannot
be calculated, the caller must treat distance as unknown — never invent km.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

CITY_COORDS: dict[str, tuple[float, float]] = {
    "toronto": (43.6532, -79.3832),
    "mississauga": (43.5890, -79.6441),
    "brampton": (43.7315, -79.7624),
    "vaughan": (43.8563, -79.5085),
    "markham": (43.8561, -79.3370),
    "richmond hill": (43.8828, -79.4403),
    "oakville": (43.4675, -79.6877),
    "burlington": (43.3255, -79.7990),
    "milton": (43.5183, -79.8774),
    "hamilton": (43.2557, -79.8711),
    "etobicoke": (43.6205, -79.5132),
    "scarborough": (43.7764, -79.2318),
    "north york": (43.7615, -79.4111),
    "ajax": (43.8509, -79.0204),
    "pickering": (43.8384, -79.0868),
    "newmarket": (44.0592, -79.4613),
    "ottawa": (45.4215, -75.6972),
    "vancouver": (49.2827, -123.1207),
    "calgary": (51.0447, -114.0719),
    "edmonton": (53.5461, -113.4938),
    "montreal": (45.5019, -73.5673),
    "winnipeg": (49.8951, -97.1384),
    "london": (42.9849, -81.2453),
    "kitchener": (43.4516, -80.4925),
    "waterloo": (43.4643, -80.5204),
    "windsor": (42.3149, -83.0364),
    "kingston": (44.2312, -76.4860),
    "halifax": (44.6488, -63.5752),
}


@dataclass
class GeoPoint:
    latitude: float
    longitude: float
    label: str
    source: str  # "coords" | "city_lookup"


def _normalize(value: str | None) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def normalize_postal(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def lookup_city_coords(city: str | None, location: str | None = None) -> tuple[float, float] | None:
    for raw in (city, location):
        key = _normalize(raw)
        if not key:
            continue
        if key in CITY_COORDS:
            return CITY_COORDS[key]
        for name, coords in CITY_COORDS.items():
            if name in key or key in name:
                return coords
    return None


def resolve_point(
    *,
    latitude: float | None = None,
    longitude: float | None = None,
    city: str | None = None,
    location: str | None = None,
) -> GeoPoint | None:
    if latitude is not None and longitude is not None:
        return GeoPoint(latitude, longitude, location or city or "coordinates", "coords")
    coords = lookup_city_coords(city, location)
    if coords:
        return GeoPoint(coords[0], coords[1], city or location or "city", "city_lookup")
    return None


def postal_prefix_match(a: str | None, b: str | None) -> bool:
    pa, pb = normalize_postal(a), normalize_postal(b)
    if len(pa) < 3 or len(pb) < 3:
        return False
    return pa[:3] == pb[:3]


def city_name_match(*values: str | None) -> bool:
    tokens = [_normalize(v) for v in values if _normalize(v)]
    if len(tokens) < 2:
        return False
    left, right = tokens[0], tokens[1]
    if left == right:
        return True
    return left in right or right in left
