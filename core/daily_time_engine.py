from core.maps_optimizer import MapsOptimizer

class DailyTimeEngine:
    def __init__(self, max_hours_per_day=8):
        self.max_seconds = max_hours_per_day * 3600
        self.maps = MapsOptimizer()

    def build_daily_plan(self, start_point, places, num_days=1, visit_minutes=60):
        """
        start_point: hotel or city center
        places: list of attraction names
        num_days: how many days the trip should be split across
        visit_minutes: avg visit time per place
        """

        num_days = max(1, num_days)
        VISIT_TIME = visit_minutes * 60

        # Distribute places evenly across the requested number of days
        n = len(places)
        base, extra = divmod(n, num_days)
        sizes = [base + 1 if i < extra else base for i in range(num_days)]

        days = []
        idx = 0
        for size in sizes:
            chunk = places[idx: idx + size]
            idx += size

            current_day = []
            current_time = 0
            current_location = start_point

            for place in chunk:
                travel_info = self.maps.compute_pairwise_time(current_location, place)
                if not travel_info:
                    continue

                travel_time = travel_info["duration_value"]
                current_time += travel_time + VISIT_TIME

                current_day.append({
                    "place": place,
                    "travel_time": travel_info["duration"],
                    "distance": travel_info["distance"],
                    "visit_time": f"{visit_minutes} mins"
                })
                current_location = place

            days.append(current_day)

        return days
