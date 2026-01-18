from core.maps_optimizer import MapsOptimizer

class DailyTimeEngine:
    def __init__(self, max_hours_per_day=8):
        self.max_seconds = max_hours_per_day * 3600
        self.maps = MapsOptimizer()

    def build_daily_plan(self, start_point, places, visit_minutes=60):
        """
        start_point: hotel or city center
        places: list of attraction names
        visit_minutes: avg visit time per place
        """

        days = []
        current_day = []
        current_time = 0
        current_location = start_point

        VISIT_TIME = visit_minutes * 60

        for place in places:
            travel_info = self.maps.compute_pairwise_time(current_location, place)

            if not travel_info:
                continue

            travel_time = travel_info["duration_value"]
            total_needed = travel_time + VISIT_TIME

            # If adding this place exceeds day limit → new day
            if current_time + total_needed > self.max_seconds:
                days.append(current_day)
                current_day = []
                current_time = 0
                current_location = start_point

            current_day.append({
                "place": place,
                "travel_time": travel_info["duration"],
                "distance": travel_info["distance"],
                "visit_time": f"{visit_minutes} mins"
            })

            current_time += total_needed
            current_location = place

        if current_day:
            days.append(current_day)

        return days
