class TimeOptimizer:
    def __init__(self, days):
        self.days = days

    def allocate_time(self, places):
        hours_per_day = 8
        max_places = self.days * 3  # 3 places per day max

        return places[:max_places]
    
class WalkingOptimizer:
    def filter_places(self, places, walking_pref):
        if walking_pref == "low":
            return places[:5]  # fewer places
        return places
    
class DistanceOptimizer:
    def cluster_places(self, places):
        # simple clustering (city-center first)
        return sorted(places)

