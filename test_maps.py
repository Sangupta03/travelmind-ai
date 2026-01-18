from tools.maps_tool import MapsTool

m = MapsTool()
print("Geocode Jaipur:", m.geocode("Jaipur"))
print("Distance Jaipur → Amber Fort:", m.distance_matrix("Jaipur", "Amber Fort Jaipur"))
