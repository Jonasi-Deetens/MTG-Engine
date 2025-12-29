import requests
from typing import Dict, Any, List, Optional


class ScryfallClient:
    BASE = "https://api.scryfall.com"
    TIMEOUT = 10

    def _get(self, url: str, params: Optional[dict] = None) -> Dict[str, Any]:
        """Internal GET wrapper with timeout + error handling."""
        try:
            resp = requests.get(url, params=params, timeout=self.TIMEOUT)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Scryfall request failed: {e}")

    # ---------------------------------------------------------
    # Fetch a single card by Scryfall ID
    # ---------------------------------------------------------
    def fetch_card(self, card_id: str) -> Dict[str, Any]:
        url = f"{self.BASE}/cards/{card_id}"
        return self._get(url)

    # ---------------------------------------------------------
    # Search Scryfall (handles pagination)
    # ---------------------------------------------------------
    def search(self, query: str) -> List[Dict[str, Any]]:
        url = f"{self.BASE}/cards/search"
        results = []
        data = self._get(url, params={"q": query})

        results.extend(data.get("data", []))

        # Handle pagination
        while data.get("has_more"):
            data = self._get(data["next_page"])
            results.extend(data.get("data", []))

        return results

    # ---------------------------------------------------------
    # Fetch a deck from a URL (Moxfield, Archidekt, raw JSON)
    # ---------------------------------------------------------
    def fetch_deck(self, deck_url: str) -> Dict[str, Any]:
        """
        Supports:
        - Raw JSON deck URLs
        - Moxfield API
        - Archidekt API
        - Scryfall bulk lists
        """
        # Moxfield deck
        if "moxfield.com" in deck_url:
            deck_id = deck_url.rstrip("/").split("/")[-1]
            return self._get(f"https://api.moxfield.com/v2/decks/all/{deck_id}")

        # Archidekt deck
        if "archidekt.com" in deck_url:
            deck_id = deck_url.rstrip("/").split("/")[-1]
            return self._get(f"https://archidekt.com/api/decks/{deck_id}/")

        # Raw JSON deck
        return self._get(deck_url)
