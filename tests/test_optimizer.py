from core.optimizer import TimeOptimizer, WalkingOptimizer, DistanceOptimizer


def test_time_optimizer_caps_places_at_three_per_day():
    optimizer = TimeOptimizer(days=2)
    places = ["A", "B", "C", "D", "E", "F", "G"]
    result = optimizer.allocate_time(places)
    assert result == ["A", "B", "C", "D", "E", "F"]


def test_time_optimizer_keeps_all_places_when_under_the_cap():
    optimizer = TimeOptimizer(days=3)
    places = ["A", "B"]
    assert optimizer.allocate_time(places) == ["A", "B"]


def test_walking_optimizer_limits_places_for_low_preference():
    optimizer = WalkingOptimizer()
    places = ["A", "B", "C", "D", "E", "F"]
    assert optimizer.filter_places(places, "low") == ["A", "B", "C", "D", "E"]


def test_walking_optimizer_keeps_all_places_for_normal_preference():
    optimizer = WalkingOptimizer()
    places = ["A", "B", "C", "D", "E", "F"]
    assert optimizer.filter_places(places, "normal") == places


def test_distance_optimizer_sorts_places_alphabetically():
    optimizer = DistanceOptimizer()
    places = ["Zoo", "Aquarium", "Museum"]
    assert optimizer.cluster_places(places) == ["Aquarium", "Museum", "Zoo"]
