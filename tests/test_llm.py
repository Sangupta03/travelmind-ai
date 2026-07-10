"""
Tests for core/llm.py's call_llm_json().

We mock the Gemini client so these tests don't need a real API key or
network access, and can run in CI.
"""
import core.llm as llm


class _FakeResponse:
    def __init__(self, text):
        self.text = text


def test_call_llm_json_parses_valid_json(monkeypatch):
    monkeypatch.setattr(
        llm.client.models, "generate_content",
        lambda **kwargs: _FakeResponse('{"budget": "low", "pace": "slow"}'),
    )

    result = llm.call_llm_json("some prompt", schema={"type": "object"})

    assert result == {"budget": "low", "pace": "slow"}


def test_call_llm_json_returns_none_on_invalid_json(monkeypatch):
    monkeypatch.setattr(
        llm.client.models, "generate_content",
        lambda **kwargs: _FakeResponse("not valid json"),
    )

    result = llm.call_llm_json("some prompt", schema={"type": "object"})

    assert result is None


def test_call_llm_json_retries_on_quota_error_then_succeeds(monkeypatch):
    monkeypatch.setattr(llm.time, "sleep", lambda seconds: None)

    calls = {"n": 0}

    def fake_generate(**kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise Exception("RESOURCE_EXHAUSTED: quota hit")
        return _FakeResponse('{"budget": "medium"}')

    monkeypatch.setattr(llm.client.models, "generate_content", fake_generate)

    result = llm.call_llm_json("some prompt", schema={"type": "object"}, retries=2)

    assert result == {"budget": "medium"}
    assert calls["n"] == 2
