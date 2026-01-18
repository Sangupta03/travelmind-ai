from core.walking_estimator import WalkingEstimator
from core.maps_optimizer import MapsOptimizer

class TransportEngine:
    def __init__(self, walk_max_meters=800, walk_max_minutes=12):
        self.walk_max_meters = walk_max_meters
        self.walk_max_seconds = walk_max_minutes * 60
        self.walker = WalkingEstimator()
        self.maps = MapsOptimizer()

    def decide(self, origin, destination):
        walk = self.walker.walking_time(origin, destination)
        if walk:
            meters = walk["distance"]
            seconds = walk["duration_value"]

            # meters may come as "0.5 km" or "400 m" via text; rely on seconds threshold
            if seconds <= self.walk_max_seconds:
                return {
                    "mode": "WALK",
                    "distance": walk["distance"],
                    "time": walk["duration"],
                    "reason": "Short distance — walking is comfortable."
                }

        drive = self.maps.compute_pairwise_time(origin, destination, mode="driving")
        if drive:
            return {
                "mode": "CAB",
                "distance": drive["distance"],
                "time": drive["duration"],
                "reason": "Distance is long — cab recommended for comfort."
            }

        return {
            "mode": "UNKNOWN",
            "distance": None,
            "time": None,
            "reason": "Route data unavailable."
        }
