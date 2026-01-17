from tools.flight_tool import FlightSearch

fs = FlightSearch()
flights = fs.search_flights("DEL", "JAI")  # Delhi → Jaipur
print(flights)
