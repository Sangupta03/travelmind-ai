from core.preferences import format_preferences


def test_hides_unspecified_and_default_falsy_values():
    result = format_preferences({
        "budget": "unspecified",
        "food_preference": "unspecified",
        "travel_with_elderly": False,
        "interests": [],
    })
    assert result == {}


def test_boolean_true_displays_as_yes():
    result = format_preferences({"travel_with_elderly": True})
    assert result == {"Travel With Elderly": "Yes"}


def test_interests_list_renders_as_titled_comma_separated_text():
    result = format_preferences({"interests": ["temples", "art cafes"]})
    assert result == {"Interests": "Temples, Art Cafes"}


def test_free_text_values_are_title_cased():
    result = format_preferences({"budget": "strict budget", "pace": "flexible"})
    assert result == {"Budget": "Strict Budget", "Pace": "Flexible"}


def test_keys_are_converted_to_readable_labels():
    result = format_preferences({"walking_preference": "low"})
    assert "Walking Preference" in result


def test_raw_fallback_key_is_hidden():
    result = format_preferences({"raw": "some unparsed llm text", "budget": "low"})
    assert "Raw" not in result
    assert result == {"Budget": "Low"}


def test_non_dict_input_returns_empty():
    assert format_preferences(None) == {}
    assert format_preferences("not a dict") == {}


def test_full_realistic_example():
    result = format_preferences({
        "budget": "strict budget",
        "walking_preference": "flexible",
        "food_preference": "unspecified",
        "pace": "flexible",
        "travel_with_elderly": True,
        "interests": ["temples", "art cafes"],
    })
    assert result == {
        "Budget": "Strict Budget",
        "Walking Preference": "Flexible",
        "Pace": "Flexible",
        "Travel With Elderly": "Yes",
        "Interests": "Temples, Art Cafes",
    }
