from typing import List
from axis1.schema import Axis1Card


class DeckImportService:
    def __init__(self, scryfall_client, mapper, repo):
        self.scryfall = scryfall_client
        self.mapper = mapper
        self.repo = repo

    def import_deck(self, deck_url: str) -> List[Axis1Card]:
        # For now, assume deck_url returns a JSON with an "entries" list,
        # each entry having a "card_id" or "scryfall_id".
        deck_json = self.scryfall.fetch_deck(deck_url)
        cards: List[Axis1Card] = []

        for entry in deck_json.get("entries", []):
            card_json = self.scryfall.fetch_card(entry["id"])
            axis1 = self.mapper.map(card_json)
            self.repo.save(axis1)
            cards.append(axis1)

        return cards
