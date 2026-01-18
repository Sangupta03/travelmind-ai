from core.llm import call_llm
from tools.flight_tool import FlightSearch
from tools.hotel_tool import HotelSearch

class BudgetAgent:
    def __init__(self):
        self.flight_client = FlightSearch()
        self.hotel_client = HotelSearch()

    def create_plan(self, destination, days, constraints):
        flights = self.flight_client.search_flights("DEL", destination[:3].upper())
        hotels = self.hotel_client.search_hotels(destination)

        prompt = f"""
        You are a Budget Travel Agent.

        Real Flights:
        {flights}

        Real Hotels:
        {hotels}

        Destination: {destination}
        Days: {days}
        Constraints: {constraints}

        Create a low-cost travel plan using real data.
        """

        return call_llm(prompt)

