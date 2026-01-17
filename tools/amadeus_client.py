import requests
from config import AMADEUS_API_KEY, AMADEUS_API_SECRET

class AmadeusClient:
    def __init__(self):
        self.token = self.get_token()

    def get_token(self):
        url = "https://test.api.amadeus.com/v1/security/oauth2/token"

        data = {
            "grant_type": "client_credentials",
            "client_id": AMADEUS_API_KEY,
            "client_secret": AMADEUS_API_SECRET
        }

        response = requests.post(url, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }
