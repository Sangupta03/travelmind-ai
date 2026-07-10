"""
tools/flight_tool.py — Flight search

Price strategy:
  - If a departure_date is given and Amadeus credentials are configured,
    use Amadeus Flight Offers Search for real, priced offers (price search
    requires a date, so this path is unavailable without one).
  - Otherwise fall back to AviationStack for schedule data (no pricing).
  - If both are unavailable/fail, fall back to simulated data, clearly
    flagged via "data_source".
"""

import logging
import random
import requests
from config import AVIATIONSTACK_KEY, AMADEUS_API_KEY, AMADEUS_API_SECRET

logger = logging.getLogger(__name__)

MOCK_AIRLINES = ["IndiGo", "Vistara", "Air India", "Akasa Air"]
MOCK_DURATIONS = ["1h 00m", "1h 05m", "1h 10m", "1h 20m"]
MOCK_BASE_PRICES = [3200, 3500, 3800, 4200, 4500]

_AMADEUS_AVAILABLE = bool(AMADEUS_API_KEY and AMADEUS_API_SECRET)


class FlightSearch:

    def search_flights(self, origin: str, destination: str, departure_date: str = None) -> list[dict]:
        from tools.airport_lookup import resolve_iata

        origin_code = resolve_iata(origin)
        dest_code   = resolve_iata(destination)
        route_label = f"{origin} → {destination}"

        if departure_date and _AMADEUS_AVAILABLE:
            try:
                flights = self._search_amadeus(origin_code, dest_code, departure_date, route_label)
                if flights:
                    return flights
            except Exception as e:
                logger.warning("Amadeus search failed (%s), falling back.", e)

        if AVIATIONSTACK_KEY:
            try:
                flights = self._search_aviationstack(origin_code, dest_code, route_label)
                if flights:
                    return flights
            except Exception as e:
                logger.warning("Aviationstack failed: %s", e)

        return self._mock_flights(route_label)

    def _search_amadeus(self, origin_code: str, dest_code: str, departure_date: str, route_label: str) -> list[dict]:
        from tools.amadeus_client import AmadeusClient

        client = AmadeusClient()
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        params = {
            "originLocationCode":      origin_code,
            "destinationLocationCode": dest_code,
            "departureDate":           departure_date,
            "adults":                  1,
            "max":                     4,
            "currencyCode":            "INR",
        }
        response = requests.get(url, headers=client.get_headers(), params=params, timeout=20)
        response.raise_for_status()
        offers = response.json().get("data", [])

        results = []
        for offer in offers:
            seg   = offer["itineraries"][0]["segments"][0]
            price = float(offer["price"]["total"])
            results.append({
                "airline":       seg["carrierCode"],
                "flight_number": f"{seg['carrierCode']}-{seg['number']}",
                "duration":      offer["itineraries"][0]["duration"],
                "price":         f"₹{price:,.0f}",
                "price_value":   price,
                "route":         route_label,
                "data_source":   "amadeus_live",
                "note":          "Live price from Amadeus API."
            })
        return results

    def _search_aviationstack(self, origin_code: str, dest_code: str, route_label: str) -> list[dict]:
        url = "http://api.aviationstack.com/v1/flights"
        params = {
            "access_key": AVIATIONSTACK_KEY,
            "dep_iata":   origin_code,
            "arr_iata":   dest_code,
            "limit":      4
        }
        r = requests.get(url, params=params, timeout=15).json()
        flights = []
        for f in r.get("data", [])[:4]:
            flights.append({
                "airline":       f["airline"]["name"],
                "flight_number": f["flight"]["iata"],
                "duration":      "~1h 30m",
                "price":         "Live pricing unavailable",
                "price_value":   None,
                "route":         route_label,
                "data_source":   "aviationstack_live",
                "note":          "Schedule data only — AviationStack does not provide pricing."
            })
        return flights

    def _mock_flights(self, route_label: str) -> list[dict]:
        flights = []
        for airline in MOCK_AIRLINES:
            price = random.choice(MOCK_BASE_PRICES)
            flights.append({
                "airline":       airline,
                "flight_number": f"{airline[:2].upper()}-{random.randint(100, 999)}",
                "duration":      random.choice(MOCK_DURATIONS),
                "price":         f"₹{price}",
                "price_value":   price,
                "route":         route_label,
                "data_source":   "simulated",
                "note":          "Demo data. Provide a departure date for live Amadeus pricing."
            })
        return flights
