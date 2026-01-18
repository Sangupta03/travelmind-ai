# import requests
# from config import SERPAPI_KEY

# class FlightSearch:
#     def search_flights(self, origin, destination):
#         url = "https://serpapi.com/search.json"

#         params = {
#             "engine": "google_flights",
#             "departure_id": origin,
#             "arrival_id": destination,
#             "outbound_date": "2026-02-01",
#             "currency": "INR",
#             "api_key": SERPAPI_KEY
#         }

#         response = requests.get(url, params=params, timeout=20)
#         data = response.json()

#         flights = []
#         for f in data.get("best_flights", [])[:5]:
#             flights.append({
#                 "airline": f["airline"],
#                 "price": f["price"],
#                 "duration": f["duration"]
#             })

#         return flights

# import requests
# from config import SERPAPI_KEY

# class FlightSearch:
#     def search_flights(self, origin, destination):
#         url = "https://serpapi.com/search.json"

#         params = {
#             "engine": "google_flights",
#             "departure_id": origin,      # DEL
#             "arrival_id": destination,  # JAI
#             "outbound_date": "2026-02-01",
#             "currency": "INR",
#             "hl": "en",
#             "api_key": SERPAPI_KEY
#         }

#         response = requests.get(url, params=params, timeout=20)

#         print("\n--- RAW SERPAPI RESPONSE ---")
#         print(response.text)   # <-- important
#         print("---------------------------\n")

#         data = response.json()

#         flights = []
#         for f in data.get("best_flights", []):
#             flights.append({
#                 "airline": f.get("airline"),
#                 "price": f.get("price"),
#                 "duration": f.get("duration")
#             })

#         return flights

# import requests
# from config import SERPAPI_KEY

# class FlightSearch:
#     def search_flights(self, origin, destination):
#         url = "https://serpapi.com/search.json"

#         params = {
#             "engine": "google_flights",
#             "type": "2",  # 2 = One-way, 1 = Round-trip
#             "departure_id": origin,      # e.g. DEL
#             "arrival_id": destination,   # e.g. JAI
#             "outbound_date": "2025-02-01",
#             "currency": "INR",
#             "hl": "en",
#             "api_key": SERPAPI_KEY
#         }

#         response = requests.get(url, params=params, timeout=20)
#         data = response.json()

#         flights = []

#         for f in data.get("best_flights", [])[:5]:
#             flights.append({
#                 "airline": f.get("airline"),
#                 "price": f.get("price"),
#                 "duration": f.get("duration")
#             })

#         return flights

# import requests
# from config import AVIATIONSTACK_KEY

# class FlightSearch:
#     def search_flights(self, origin, destination):
#         url = "http://api.aviationstack.com/v1/routes"

#         params = {
#             "access_key": AVIATIONSTACK_KEY,
#             "dep_iata": origin,
#             "arr_iata": destination,
#             "limit": 5
#         }

#         response = requests.get(url, params=params, timeout=20)
#         data = response.json()

#         flights = []

#         for route in data.get("data", [])[:5]:
#             flights.append({
#                 "airline": route.get("airline_name"),
#                 "flight_number": route.get("flight_number"),
#                 "departure": origin,
#                 "arrival": destination
#             })

#         return flights
    
import random

class FlightSearch:
    def search_flights(self, origin, destination):
        airlines = ["IndiGo", "Vistara", "Air India", "Akasa Air"]
        durations = ["1h 00m", "1h 05m", "1h 10m"]
        base_prices = [3200, 3500, 3800, 4200]

        flights = []

        for i in range(4):
            flights.append({
                "airline": airlines[i],
                "flight_number": f"{airlines[i][:2].upper()}-{random.randint(100,999)}",
                "duration": random.choice(durations),
                "price": f"₹{random.choice(base_prices)}",
                "route": f"{origin} → {destination}"
            })

        return flights

