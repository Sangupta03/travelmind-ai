# from tools.flight_tool import FlightSearch

# fs = FlightSearch()

# # Delhi → Jaipur
# flights = fs.search_flights("DEL", "LKO")

# print("\nReal Flights (Delhi → Jaipur):")
# for f in flights:
#     print(f)

# from tools.flight_tool import FlightSearch

# fs = FlightSearch()

# print("\nTesting Delhi → Jaipur")
# flights = fs.search_flights("DEL", "JAI")

# print("\nParsed Flights:")
# for f in flights:
#     print(f)


from tools.flight_tool import FlightSearch

fs = FlightSearch()

print("\nDelhi → Jaipur Flights:")
for f in fs.search_flights("DEL", "JAI"):
    print(f)

