from core.llm import call_llm
from tools.flight_tool import FlightSearch
from tools.hotel_tool import HotelSearch

class BudgetAgent:
    def __init__(self):
        self.flight_client = FlightSearch()
        self.hotel_client = HotelSearch()

    def create_plan(self, destination, days, constraints, departure_date=None, origin="Delhi", selected_hotel=None):
        flights = self.flight_client.search_flights(origin, destination, departure_date)

        if selected_hotel:
            hotels = [selected_hotel]
        else:
            hotels = self.hotel_client.search_hotels(destination, departure_date, days)
            selected_hotel = hotels[0] if hotels else {"name": "City Center Hotel"}

        prompt = f"""
        You are a Budget Travel Agent.

        Real Flights:
        {flights}

        Real Hotels:
        {hotels}

        Selected Hotel:
        {selected_hotel}

        Destination: {destination}
        Days: {days}
        Constraints: {constraints}

        Create a low-cost travel plan using real data.
        """

        plan = call_llm(prompt)

        return {
            "plan": plan,
            "hotel": selected_hotel,
            "flights": flights
        }


