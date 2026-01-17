import requests
from tools.amadeus_client import AmadeusClient

class FlightSearch:
    def __init__(self):
        self.client = AmadeusClient()

    def search_flights(self, origin, destination):
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"

        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "adults": 1,
            "max": 5
        }

        response = requests.get(
            url,
            headers=self.client.get_headers(),
            params=params,
            timeout=20
        )

        data = response.json()

        flights = []
        for offer in data.get("data", []):
            flights.append({
                "price": offer["price"]["total"],
                "airline": offer["validatingAirlineCodes"][0]
            })

        return flights
