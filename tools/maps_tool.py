import requests
from config import GOOGLE_MAPS_KEY

class MapsTool:
    def geocode(self, place):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": place, "key": GOOGLE_MAPS_KEY}
        try:
            r = requests.get(url, params=params, timeout=15).json()
        except requests.exceptions.RequestException as e:
            print(f"Geocode request failed for '{place}': {e}")
            return None
        if not r.get("results"):
            return None
        loc = r["results"][0]["geometry"]["location"]
        return f"{loc['lat']},{loc['lng']}"

    def distance_matrix(self, origin, destination, mode="driving"):
        return self.distance_matrix_batch(origin, [destination], mode=mode)

    def distance_matrix_batch(self, origin, destinations, mode="driving"):
        """destinations: list of place strings — resolved in a single API call."""
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": "|".join(destinations),
            "mode": mode,
            "key": GOOGLE_MAPS_KEY
        }
        try:
            return requests.get(url, params=params, timeout=15).json()
        except requests.exceptions.RequestException as e:
            print(f"Distance Matrix request failed ({origin} -> {destinations}): {e}")
            return {}

    def directions(self, origin, destination, mode="driving"):
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": GOOGLE_MAPS_KEY
        }
        try:
            return requests.get(url, params=params, timeout=15).json()
        except requests.exceptions.RequestException as e:
            print(f"Directions request failed ({origin} -> {destination}): {e}")
            return {}

    def nearby_places(self, location, keyword="tourist attraction", radius=5000):
        # location: "lat,lng"
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": location,
            "radius": radius,
            "keyword": keyword,
            "key": GOOGLE_MAPS_KEY
        }
        try:
            return requests.get(url, params=params, timeout=15).json()
        except requests.exceptions.RequestException as e:
            print(f"Nearby places request failed for '{location}': {e}")
            return {}
