from tools.hotel_tool import HotelSearch

hs = HotelSearch()
hotels = hs.search_hotels("PAR")   # Paris
print(hotels)
