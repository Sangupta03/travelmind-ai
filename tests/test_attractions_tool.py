"""
Tests for AttractionsTool.get_attractions().

Mocks MapsTool.geocode/nearby_places so these run without a real Google
Maps API key or network access.
"""
from tools.attractions_tool import AttractionsTool


def _places_response(names):
    return {"results": [{"name": n} for n in names]}


def test_no_interests_uses_generic_tourist_attraction_search(monkeypatch):
    tool = AttractionsTool()
    monkeypatch.setattr(tool.maps, "geocode", lambda city: "13.0,80.2")

    calls = []

    def fake_nearby(location, keyword="tourist attraction", radius=5000):
        calls.append(keyword)
        return _places_response(["Marina Beach", "Fort Museum"])

    monkeypatch.setattr(tool.maps, "nearby_places", fake_nearby)

    result = tool.get_attractions("Chennai", limit=5)

    assert calls == ["tourist attraction"]
    assert result == ["Marina Beach", "Fort Museum"]


def test_interests_are_searched_and_prioritized(monkeypatch):
    tool = AttractionsTool()
    monkeypatch.setattr(tool.maps, "geocode", lambda city: "13.0,80.2")

    calls = []

    def fake_nearby(location, keyword="tourist attraction", radius=5000):
        calls.append(keyword)
        if keyword == "temples":
            return _places_response(["Kapaleeshwarar Temple"])
        if keyword == "art cafes":
            return _places_response(["Cafe Amethyst"])
        return _places_response(["Marina Beach", "Fort Museum"])

    monkeypatch.setattr(tool.maps, "nearby_places", fake_nearby)

    result = tool.get_attractions("Chennai", limit=4, interests=["temples", "art cafes"])

    assert "temples" in calls
    assert "art cafes" in calls
    assert result[0] == "Kapaleeshwarar Temple"
    assert result[1] == "Cafe Amethyst"
    # remaining slots filled with generic results
    assert "Marina Beach" in result


def test_duplicate_places_across_interests_are_not_repeated(monkeypatch):
    tool = AttractionsTool()
    monkeypatch.setattr(tool.maps, "geocode", lambda city: "13.0,80.2")
    monkeypatch.setattr(
        tool.maps, "nearby_places",
        lambda location, keyword="tourist attraction", radius=5000: _places_response(["Shared Place"]),
    )

    result = tool.get_attractions("Chennai", limit=5, interests=["temples", "churches"])

    assert result.count("Shared Place") == 1


def test_empty_interests_list_behaves_like_no_interests(monkeypatch):
    tool = AttractionsTool()
    monkeypatch.setattr(tool.maps, "geocode", lambda city: "13.0,80.2")
    calls = []

    def fake_nearby(location, keyword="tourist attraction", radius=5000):
        calls.append(keyword)
        return _places_response(["Marina Beach"])

    monkeypatch.setattr(tool.maps, "nearby_places", fake_nearby)

    result = tool.get_attractions("Chennai", limit=5, interests=[])

    assert calls == ["tourist attraction"]
    assert result == ["Marina Beach"]


def test_no_location_returns_empty_list(monkeypatch):
    tool = AttractionsTool()
    monkeypatch.setattr(tool.maps, "geocode", lambda city: None)

    assert tool.get_attractions("Nowhere", limit=5, interests=["temples"]) == []
