import requests
from tools.amadeus_client import AmadeusClient

class HotelSearch:
    def __init__(self):
        self.client = AmadeusClient()

    def search_hotels(self, city_code):
        url = "https://test.api.amadeus.com/v2/shopping/hotel-offers"

        params = {
            "cityCode": city_code,
            "radius": 5,
            "radiusUnit": "KM"
        }

        response = requests.get(
            url,
            headers=self.client.get_headers(),
            params=params,
            timeout=20
        )

        data = response.json()

        hotels = []
        for offer in data.get("data", [])[:5]:
            hotel = offer["hotel"]
            hotels.append({
                "name": hotel["name"],
                "rating": hotel.get("rating", "N/A"),
                "city": hotel["cityCode"]
            })

        return hotels

