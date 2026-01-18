from tools.maps_tool import MapsTool

class MapsOptimizer:
    def __init__(self):
        self.maps = MapsTool()

    def compute_pairwise_time(self, a, b, mode="driving"):
        dm = self.maps.distance_matrix(a, b, mode=mode)
        rows = dm.get("rows", [])
        if not rows:
            return None
        elem = rows[0]["elements"][0]
        if elem.get("status") != "OK":
            return None
        return {
            "distance": elem["distance"]["text"],
            "duration": elem["duration"]["text"],
            "duration_value": elem["duration"]["value"]  # seconds
        }

    def order_by_nearest(self, start, places):
        # greedy nearest-neighbor ordering by driving time
        ordered = []
        current = start
        remaining = places[:]

        while remaining:
            best = None
            best_time = None
            for p in remaining:
                info = self.compute_pairwise_time(current, p, mode="driving")
                if not info:
                    continue
                if best_time is None or info["duration_value"] < best_time:
                    best_time = info["duration_value"]
                    best = p
            if not best:
                break
            ordered.append(best)
            remaining.remove(best)
            current = best

        return ordered
