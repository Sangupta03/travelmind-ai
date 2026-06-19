import requests
from datetime import datetime, timedelta
from config import SERPAPI_KEY

class HotelSearch:
    def search_hotels(self, city, check_in_date=None, nights=3):
        url = "https://serpapi.com/search.json"

        if check_in_date:
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        else:
            # No date given — default to a near-future date so SerpAPI
            # returns real availability instead of nothing for a past date.
            check_in = datetime.now() + timedelta(days=14)
        check_out = check_in + timedelta(days=max(nights, 1))

        params = {
            "engine": "google_hotels",
            "q": f"hotels in {city}",
            "check_in_date": check_in.strftime("%Y-%m-%d"),
            "check_out_date": check_out.strftime("%Y-%m-%d"),
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
