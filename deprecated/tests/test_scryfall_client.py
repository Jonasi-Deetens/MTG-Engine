import pytest
from scryfall.client import ScryfallClient

def test_scryfall_search_returns_list(monkeypatch):
    """Test that search() returns a list of cards."""

    # Fake Scryfall response
    fake_response = {
        "data": [{"id": "1"}, {"id": "2"}],
        "has_more": False
    }

    def fake_get(url, params=None, timeout=10):
        class FakeResp:
            def raise_for_status(self): pass
            def json(self): return fake_response
        return FakeResp()

    monkeypatch.setattr("requests.get", fake_get)

    client = ScryfallClient()
    results = client.search("elf")

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["id"] == "1"
