"""
Tests for TransportEngine.decide().

TransportEngine normally calls out to the real Google Maps API through
MapsTool. We don't want tests to depend on network access or a real API
key, so we replace (monkeypatch) the underlying maps calls with fake
data that mimics the shape of a real Google Distance Matrix response.
"""
from core.transport_engine import TransportEngine


def _distance_matrix_response(distance_text, duration_text, duration_seconds, status="OK"):
    return {
        "rows": [
            {"elements": [{
                "status": status,
                "distance": {"text": distance_text},
                "duration": {"text": duration_text, "value": duration_seconds},
            }]}
        ]
    }


def test_short_distance_recommends_walking(monkeypatch):
    engine = TransportEngine(walk_max_meters=800, walk_max_minutes=12)
    monkeypatch.setattr(
        engine.walker.maps, "distance_matrix",
        lambda *a, **k: _distance_matrix_response("500 m", "6 mins", 360),
    )

    decision = engine.decide("Hotel", "Museum")

    assert decision["mode"] == "WALK"
    assert decision["distance"] == "500 m"


def test_long_distance_recommends_cab(monkeypatch):
    engine = TransportEngine(walk_max_meters=800, walk_max_minutes=12)
    monkeypatch.setattr(
        engine.walker.maps, "distance_matrix",
        lambda *a, **k: _distance_matrix_response("5 km", "40 mins", 2400),
    )
    monkeypatch.setattr(
        engine.maps.maps, "distance_matrix",
        lambda *a, **k: _distance_matrix_response("5 km", "15 mins", 900),
    )

    decision = engine.decide("Hotel", "Airport")

    assert decision["mode"] == "CAB"
    assert decision["distance"] == "5 km"


def test_unknown_when_no_route_data_available(monkeypatch):
    engine = TransportEngine()
    monkeypatch.setattr(engine.walker.maps, "distance_matrix", lambda *a, **k: {"rows": []})
    monkeypatch.setattr(engine.maps.maps, "distance_matrix", lambda *a, **k: {"rows": []})

    decision = engine.decide("Nowhere", "Nowhere Else")

    assert decision["mode"] == "UNKNOWN"
    assert decision["distance"] is None
