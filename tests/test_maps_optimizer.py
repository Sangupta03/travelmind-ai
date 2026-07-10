"""
Tests for MapsOptimizer.order_by_nearest().

Mocks MapsTool.distance_matrix_batch so the nearest-neighbor ordering
logic can be tested without a real Google Maps API key or network call.
"""
from core.maps_optimizer import MapsOptimizer


def _batch_response(durations_by_place):
    """durations_by_place: dict mapping place -> duration in seconds (None = unreachable)."""
    elements = []
    for duration in durations_by_place.values():
        if duration is None:
            elements.append({"status": "ZERO_RESULTS"})
        else:
            elements.append({"status": "OK", "duration": {"value": duration}})
    return {"rows": [{"elements": elements}]}


def test_orders_places_by_nearest_first(monkeypatch):
    optimizer = MapsOptimizer()

    # First call from "Hotel": C is closest, then A, then B.
    call_count = {"n": 0}

    def fake_batch(current, remaining, mode="driving"):
        call_count["n"] += 1
        distances = {"A": 600, "B": 900, "C": 300}
        return _batch_response({p: distances[p] for p in remaining})

    monkeypatch.setattr(optimizer.maps, "distance_matrix_batch", fake_batch)

    result = optimizer.order_by_nearest("Hotel", ["A", "B", "C"])

    assert result[0] == "C"
    assert call_count["n"] == 3


def test_unreachable_places_are_excluded(monkeypatch):
    optimizer = MapsOptimizer()
    monkeypatch.setattr(
        optimizer.maps, "distance_matrix_batch",
        lambda current, remaining, mode="driving": _batch_response({p: None for p in remaining}),
    )

    result = optimizer.order_by_nearest("Hotel", ["A", "B"])

    assert result == []


def test_empty_places_list_returns_empty():
    optimizer = MapsOptimizer()
    assert optimizer.order_by_nearest("Hotel", []) == []
