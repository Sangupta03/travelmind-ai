from core.llm import call_llm
from tools.flight_tool import search_flights
from tools.hotel_tool import search_hotels

class BudgetAgent:
    def create_plan(self, destination, days, constraints):
        flights = search_flights(destination, days, constraints)
        hotels = search_hotels(destination, constraints)

        prompt = f"""
        You are a Budget Travel Agent.

        Available Flights:
        {flights}

        Available Hotels:
        {hotels}

        Destination: {destination}
        Days: {days}
        Constraints: {constraints}

        Create a low-cost travel plan using the given data.
        """

        return call_llm(prompt)
