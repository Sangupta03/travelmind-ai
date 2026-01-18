import requests
from config import SERPAPI_KEY

class HotelSearch:
    def search_hotels(self, city):
        url = "https://serpapi.com/search.json"

        params = {
            "engine": "google_hotels",
            "q": f"hotels in {city}",
            "check_in_date": "2026-02-01",
            "check_out_date": "2026-02-04",
            "adults": 2,
            "currency": "INR",
            "api_key": SERPAPI_KEY
        }

        response = requests.get(url, params=params, timeout=20)
        data = response.json()

        hotels = []
        for h in data.get("properties", [])[:5]:
            hotels.append({
                "name": h["name"],
                "rating": h.get("rating"),
                "price": h.get("rate_per_night", {}).get("lowest")
            })

        return hotels
