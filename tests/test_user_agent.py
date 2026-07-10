"""
Tests for UserAgent.extract_constraints(). Mocks call_llm_json so these
run without a real API key, and checks that similar_past_trips is
correctly folded into the prompt sent to the LLM.
"""
from unittest.mock import patch

from agents.user_agent import UserAgent

_FAKE_CONSTRAINTS = {
    "budget": "low",
    "walking_preference": "flexible",
    "food_preference": "unspecified",
    "pace": "flexible",
    "travel_with_elderly": False,
    "interests": [],
}


def test_no_similar_trips_shows_none_in_prompt():
    agent = UserAgent()
    with patch("agents.user_agent.call_llm_json", return_value=_FAKE_CONSTRAINTS) as mock_call:
        agent.extract_constraints("Budget trip to Goa")
        prompt = mock_call.call_args[0][0]
        assert "None" in prompt


def test_similar_trips_are_included_in_prompt():
    agent = UserAgent()
    similar = [
        {"destination": "Chennai", "constraints": {"budget": "strict budget", "interests": ["temples"]}},
        {"destination": "Varanasi", "constraints": {"budget": "low", "interests": ["temples"]}},
    ]
    with patch("agents.user_agent.call_llm_json", return_value=_FAKE_CONSTRAINTS) as mock_call:
        agent.extract_constraints("Another temple-focused trip", similar_past_trips=similar)
        prompt = mock_call.call_args[0][0]
        assert "Chennai" in prompt
        assert "Varanasi" in prompt
        assert "strict budget" in prompt


def test_returns_fallback_when_llm_call_fails():
    agent = UserAgent()
    with patch("agents.user_agent.call_llm_json", return_value=None):
        result = agent.extract_constraints("Some trip")
        assert result["budget"] == "unspecified"
        assert result["interests"] == []
