"""
Tests for DailyTimeEngine.build_daily_plan().

Like transport_engine, this depends on live Google Maps calls through
MapsOptimizer -> MapsTool, so we monkeypatch compute_pairwise_time to
return fixed travel times instead of hitting the network.
"""
from core.daily_time_engine import DailyTimeEngine


def test_places_are_split_evenly_across_days(monkeypatch):
    engine = DailyTimeEngine(max_hours_per_day=8)
    monkeypatch.setattr(
        engine.maps, "compute_pairwise_time",
        lambda a, b, mode="driving": {"distance": "1 km", "duration": "10 mins", "duration_value": 600},
    )

    places = ["A", "B", "C", "D"]
    plan = engine.build_daily_plan(start_point="Hotel", places=places, num_days=2, visit_minutes=60)

    assert len(plan) == 2
    assert len(plan[0]) == 2
    assert len(plan[1]) == 2


def test_extra_places_go_to_earlier_days(monkeypatch):
    engine = DailyTimeEngine()
    monkeypatch.setattr(
        engine.maps, "compute_pairwise_time",
        lambda a, b, mode="driving": {"distance": "1 km", "duration": "10 mins", "duration_value": 600},
    )

    places = ["A", "B", "C", "D", "E"]
    plan = engine.build_daily_plan(start_point="Hotel", places=places, num_days=2, visit_minutes=60)

    assert len(plan[0]) == 3
    assert len(plan[1]) == 2


def test_places_with_no_travel_data_are_skipped(monkeypatch):
    engine = DailyTimeEngine()
    monkeypatch.setattr(engine.maps, "compute_pairwise_time", lambda a, b, mode="driving": None)

    plan = engine.build_daily_plan(start_point="Hotel", places=["A", "B"], num_days=1)

    assert plan == [[]]


def test_num_days_is_never_less_than_one():
    engine = DailyTimeEngine()
    plan = engine.build_daily_plan(start_point="Hotel", places=[], num_days=0)
    assert len(plan) == 1
