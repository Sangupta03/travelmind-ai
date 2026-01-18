from core.llm import call_llm
from tools.hotel_tool import HotelSearch

class ComfortAgent:
    def __init__(self):
        self.hotel_client = HotelSearch()

    def create_plan(self, destination, days, constraints):
        hotels = self.hotel_client.search_hotels(destination)

        prompt = f"""
        You are a Comfort Travel Agent.

        Real Hotels:
        {hotels}

        Destination: {destination}
        Days: {days}
        Constraints: {constraints}

        Create a comfortable low-walking plan.
        """

        return call_llm(prompt)

