from tools.maps_tool import MapsTool

class AttractionsTool:
    def __init__(self):
        self.maps = MapsTool()

    def get_attractions(self, city):
        loc = self.maps.geocode(city)
        if not loc:
            return []
        data = self.maps.nearby_places(loc, keyword="tourist attraction", radius=8000)
        results = data.get("results", [])[:8]
        return [r["name"] for r in results]
