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
        # Greedy nearest-neighbor ordering by driving time.
        # Each iteration resolves distances to ALL remaining places in a
        # single batched API call, instead of one call per pair (which was
        # O(n^2) requests and prone to timing out for longer trips).
        ordered = []
        current = start
        remaining = places[:]

        while remaining:
            dm = self.maps.distance_matrix_batch(current, remaining, mode="driving")
            rows = dm.get("rows", [])
            elements = rows[0]["elements"] if rows else []

            best = None
            best_time = None
            for place, elem in zip(remaining, elements):
                if elem.get("status") != "OK":
                    continue
                duration = elem["duration"]["value"]
                if best_time is None or duration < best_time:
                    best_time = duration
                    best = place

            if not best:
                break
            ordered.append(best)
            remaining.remove(best)
            current = best

        return ordered
