"""
Tests for core/embeddings.py. Mocks the Gemini client so these run
without a real API key or network access.
"""
import core.embeddings as embeddings


def test_trip_summary_text_combines_destination_and_input():
    text = embeddings.trip_summary_text("Chennai", "Budget trip focused on temples")
    assert text == "Trip to Chennai: Budget trip focused on temples"


def test_trip_summary_text_handles_missing_input():
    text = embeddings.trip_summary_text("Chennai", "")
    assert text == "Trip to Chennai:"


class _FakeEmbedding:
    def __init__(self, values):
        self.values = values


class _FakeResponse:
    def __init__(self, values):
        self.embeddings = [_FakeEmbedding(values)]


def test_embed_text_returns_vector(monkeypatch):
    monkeypatch.setattr(
        embeddings.client.models, "embed_content",
        lambda **kwargs: _FakeResponse([0.1, 0.2, 0.3]),
    )

    result = embeddings.embed_text("A budget trip to Chennai.")

    assert result == [0.1, 0.2, 0.3]


def test_empty_text_returns_none_without_calling_api(monkeypatch):
    called = {"n": 0}
    monkeypatch.setattr(
        embeddings.client.models, "embed_content",
        lambda **kwargs: called.update(n=called["n"] + 1) or _FakeResponse([1.0]),
    )

    assert embeddings.embed_text("") is None
    assert embeddings.embed_text("   ") is None
    assert embeddings.embed_text(None) is None
    assert called["n"] == 0


def test_retries_on_quota_error_then_succeeds(monkeypatch):
    monkeypatch.setattr(embeddings.time, "sleep", lambda seconds: None)
    calls = {"n": 0}

    def fake_embed(**kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise Exception("RESOURCE_EXHAUSTED: quota hit")
        return _FakeResponse([0.5, 0.5])

    monkeypatch.setattr(embeddings.client.models, "embed_content", fake_embed)

    result = embeddings.embed_text("some trip summary", retries=2)

    assert result == [0.5, 0.5]
    assert calls["n"] == 2


def test_returns_none_after_exhausting_retries(monkeypatch):
    monkeypatch.setattr(embeddings.time, "sleep", lambda seconds: None)
    monkeypatch.setattr(
        embeddings.client.models, "embed_content",
        lambda **kwargs: (_ for _ in ()).throw(Exception("RESOURCE_EXHAUSTED")),
    )

    result = embeddings.embed_text("some trip summary", retries=2)

    assert result is None


def test_non_quota_error_is_raised_immediately(monkeypatch):
    def fake_embed(**kwargs):
        raise ValueError("something else broke")

    monkeypatch.setattr(embeddings.client.models, "embed_content", fake_embed)

    try:
        embeddings.embed_text("some trip summary")
        assert False, "expected ValueError to propagate"
    except ValueError:
        pass
