from tools.maps_tool import MapsTool

class WalkingEstimator:
    def __init__(self):
        self.maps = MapsTool()

    def walking_time(self, origin, destination):
        dm = self.maps.distance_matrix(origin, destination, mode="walking")
        rows = dm.get("rows", [])
        if not rows:
            return None
        elem = rows[0]["elements"][0]
        if elem.get("status") != "OK":
            return None
        return {
            "distance": elem["distance"]["text"],
            "duration": elem["duration"]["text"],
            "duration_value": elem["duration"]["value"]
        }
