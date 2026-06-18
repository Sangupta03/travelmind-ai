"""
tools/flight_tool.py — Flight search with honest mock data
Replace your existing tools/flight_tool.py with this file.

IMPORTANT NOTE (for resume/interviews):
  This tool currently returns simulated flight data for demo purposes.
  The Amadeus API client (tools/amadeus_client.py) is already wired up
  and ready to use — switching to live data requires only enabling the
  Amadeus sandbox credentials in .env.

  Reason for mock: Amadeus sandbox requires approved destination codes
  and has strict rate limits that would slow down demos.
"""

# import random
# from config import AMADEUS_API_KEY, AMADEUS_API_SECRET

# # Check if real Amadeus credentials are present
# _AMADEUS_AVAILABLE = bool(AMADEUS_API_KEY and AMADEUS_API_SECRET)

# MOCK_AIRLINES = ["IndiGo", "Vistara", "Air India", "Akasa Air"]
# MOCK_DURATIONS = ["1h 00m", "1h 05m", "1h 10m", "1h 20m"]
# MOCK_BASE_PRICES = [3200, 3500, 3800, 4200, 4500]


# class FlightSearch:

#     def search_flights(self, origin: str, destination: str) -> list[dict]:
#         """
#         Search for flights between origin and destination.

#         Currently returns simulated data (clearly labeled).
#         Amadeus live integration is ready — see module docstring.
#         """
#         if _AMADEUS_AVAILABLE:
#             try:
#                 return self._search_amadeus(origin, destination)
#             except Exception as e:
#                 print(f"⚠️ Amadeus API failed ({e}), falling back to mock data.")
#                 return self._mock_flights(origin, destination)
#         else:
#             return self._mock_flights(origin, destination)

#     def _mock_flights(self, origin: str, destination: str) -> list[dict]:
#         """
#         Simulated flight results — used when Amadeus is unavailable.
#         Clearly flagged as demo data so the UI can show a disclaimer.
#         """
#         flights = []
#         for i, airline in enumerate(MOCK_AIRLINES):
#             flights.append({
#                 "airline":       airline,
#                 "flight_number": f"{airline[:2].upper()}-{random.randint(100, 999)}",
#                 "duration":      random.choice(MOCK_DURATIONS),
#                 "price":         f"₹{random.choice(MOCK_BASE_PRICES)}",
#                 "route":         f"{origin} → {destination}",
#                 "data_source":   "simulated",   # ← honest flag
#                 "note":          "Demo data. Live prices via Amadeus API when credentials are active."
#             })
#         return flights

#     def _search_amadeus(self, origin: str, destination: str) -> list[dict]:
#         """
#         Live Amadeus API call.
#         Requires AMADEUS_API_KEY and AMADEUS_API_SECRET in .env
#         """
#         from tools.amadeus_client import AmadeusClient
#         import requests

#         client = AmadeusClient()
#         url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
#         params = {
#             "originLocationCode":      origin[:3].upper(),
#             "destinationLocationCode": destination[:3].upper(),
#             "departureDate":           "2026-06-01",
#             "adults":                  1,
#             "max":                     4,
#             "currencyCode":            "INR",
#         }
#         response = requests.get(url, headers=client.get_headers(), params=params, timeout=20)
#         response.raise_for_status()
#         offers = response.json().get("data", [])

#         results = []
#         for offer in offers:
#             seg   = offer["itineraries"][0]["segments"][0]
#             price = offer["price"]["total"]
#             results.append({
#                 "airline":       seg["carrierCode"],
#                 "flight_number": f"{seg['carrierCode']}-{seg['number']}",
#                 "duration":      offer["itineraries"][0]["duration"],
#                 "price":         f"₹{price}",
#                 "route":         f"{origin} → {destination}",
#                 "data_source":   "amadeus_live",
#                 "note":          "Live price from Amadeus API."
#             })
#         return results

import requests
from config import AVIATIONSTACK_KEY

class FlightSearch:
    def search_flights(self, origin, destination):
        if AVIATIONSTACK_KEY:
            try:
                url = "http://api.aviationstack.com/v1/flights"
                params = {
                    "access_key": AVIATIONSTACK_KEY,
                    "dep_iata": origin[:3].upper(),
                    "arr_iata": destination[:3].upper(),
                    "limit": 4
                }
                r = requests.get(url, params=params, timeout=15).json()
                flights = []
                for f in r.get("data", [])[:4]:
                    flights.append({
                        "airline": f["airline"]["name"],
                        "flight_number": f["flight"]["iata"],
                        "duration": "~1h 30m",
                        "price": "Live pricing unavailable",
                        "route": f"{origin} → {destination}",
                        "data_source": "aviationstack_live"
                    })
                if flights:
                    return flights
            except Exception as e:
                print(f"Aviationstack failed: {e}")
        
        # fallback to mock
        return self._mock_flights(origin, destination)