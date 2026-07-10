"""
tools/airport_lookup.py — Resolves a city or airport name to its real IATA code.

Uses Amadeus's Airport & City Search API (the same credentials already
used for flight pricing). Falls back to a 3-letter guess if the lookup
fails or Amadeus isn't configured, so callers never have to handle errors.
"""

import logging

import requests

logger = logging.getLogger(__name__)

_CACHE = {}

# Amadeus's location database only recognizes official city names —
# map common alternate/colonial names so users can type what they know.
_CITY_ALIASES = {
    "bangalore":    "Bengaluru",
    "bombay":       "Mumbai",
    "calcutta":     "Kolkata",
    "madras":       "Chennai",
    "cochin":       "Kochi",
    "trivandrum":   "Thiruvananthapuram",
    "pondicherry":  "Puducherry",
    "mysore":       "Mysuru",
    "vizag":        "Visakhapatnam",
    "gurgaon":      "Gurugram",
}


def resolve_iata(place: str) -> str:
    if not place:
        return ""

    key = place.strip().lower()
    if key in _CACHE:
        return _CACHE[key]

    # Already looks like an IATA code (e.g. "DEL", "BOM") — use as-is.
    if len(place.strip()) == 3 and place.strip().isalpha():
        code = place.strip().upper()
        _CACHE[key] = code
        return code

    fallback = place.strip()[:3].upper()
    search_term = _CITY_ALIASES.get(key, place.strip())

    try:
        from tools.amadeus_client import AmadeusClient

        client = AmadeusClient()
        url = "https://test.api.amadeus.com/v1/reference-data/locations"
        params = {
            "subType":      "CITY,AIRPORT",
            "keyword":      search_term,
            "page[limit]":  1,
        }
        r = requests.get(url, headers=client.get_headers(), params=params, timeout=10)
        r.raise_for_status()
        results = r.json().get("data", [])
        if results and results[0].get("iataCode"):
            code = results[0]["iataCode"].upper()
            _CACHE[key] = code
            return code
    except Exception as e:
        logger.warning("Airport lookup failed for '%s': %s", place, e)

    _CACHE[key] = fallback
    return fallback
