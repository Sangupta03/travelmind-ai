from tools.maps_tool import MapsTool

class AttractionsTool:
    def __init__(self):
        self.maps = MapsTool()

    def get_attractions(self, city, limit=8, interests=None):
        loc = self.maps.geocode(city)
        if not loc:
            return []

        interests = [i.strip() for i in (interests or []) if i and i.strip()]
        seen = set()
        ordered = []

        # Search per interest first, so what the traveler actually asked
        # for (e.g. "temples", "art cafes") is prioritized over generic
        # "tourist attraction" results.
        if interests:
            per_interest_limit = max(2, limit // len(interests))
            for interest in interests:
                data = self.maps.nearby_places(loc, keyword=interest, radius=8000)
                for r in data.get("results", [])[:per_interest_limit]:
                    name = r["name"]
                    if name not in seen:
                        seen.add(name)
                        ordered.append(name)
                if len(ordered) >= limit:
                    break

        # Fill any remaining slots with generic tourist attractions.
        if len(ordered) < limit:
            data = self.maps.nearby_places(loc, keyword="tourist attraction", radius=8000)
            for r in data.get("results", []):
                name = r["name"]
                if name not in seen:
                    seen.add(name)
                    ordered.append(name)
                if len(ordered) >= limit:
                    break

        return ordered[:limit]
