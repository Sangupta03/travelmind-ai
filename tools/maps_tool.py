import requests
from config import GOOGLE_MAPS_KEY

class MapsTool:
    def geocode(self, place):
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": place, "key": GOOGLE_MAPS_KEY}
        r = requests.get(url, params=params, timeout=20).json()
        if not r.get("results"):
            return None
        loc = r["results"][0]["geometry"]["location"]
        return f"{loc['lat']},{loc['lng']}"

    def distance_matrix(self, origin, destination, mode="driving"):
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode,
            "key": GOOGLE_MAPS_KEY
        }
        return requests.get(url, params=params, timeout=20).json()

    def directions(self, origin, destination, mode="driving"):
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            "origin": origin,
            "destination": destination,
            "mode": mode,
            "key": GOOGLE_MAPS_KEY
        }
        return requests.get(url, params=params, timeout=20).json()

    def nearby_places(self, location, keyword="tourist attraction", radius=5000):
        # location: "lat,lng"
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": location,
            "radius": radius,
            "keyword": keyword,
            "key": GOOGLE_MAPS_KEY
        }
        return requests.get(url, params=params, timeout=20).json()
