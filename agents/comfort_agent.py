from core.llm import call_llm
from tools.hotel_tool import search_hotels

class ComfortAgent:
    def create_plan(self, destination, days, constraints):
        hotels = search_hotels(destination, constraints)

        prompt = f"""
        You are a Comfort Travel Agent.

        Available Hotels:
        {hotels}

        Destination: {destination}
        Days: {days}
        Constraints: {constraints}

        Create a comfortable, low-walking travel plan.
        """

        return call_llm(prompt)
