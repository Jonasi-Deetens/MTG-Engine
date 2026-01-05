# axis3/engine/abilities/effects/search.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class SearchLibraryEffect(ContinuousEffect):
    """
    Axis3 effect: Search a player's library for cards matching a subject.

    This effect only *finds* the cards and emits an event. The actual
    selection, revealing, and moving of cards is handled by the choice/UI layer.

    Examples:
        SearchEffect(subject="creature_card", amount=1)
        SearchEffect(subject="basic_land_card", amount=2)
        SearchEffect(subject="any_card", amount=1)
    """

    subject: str
    amount: int = 1
    target_player: Optional[str] = None   # None = controller searches their own library
    zones: Optional[List[str]] = None

    # Searching is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        # Determine which player's library to search
        if self.target_player:
            resolver = game_state.subject_resolver
            players = resolver.resolve(self.target_player, source, controller)
            if not players:
                return True
            player = players[0]
        else:
            player = game_state.players[controller]

        library = player.library

        # Resolve which cards *could* be chosen
        resolver = game_state.subject_resolver
        valid_cards = resolver.filter_cards(self.subject, library, source, controller)

        # Limit to the allowed amount
        found_cards = valid_cards[: self.amount]
        found_ids = [getattr(c, "id", None) for c in found_cards]

        # Emit UI event so the choice system can prompt the player
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "search_library",
                "source": source,
                "controller": controller,
                "target_player": player.id,
                "subject": self.subject,
                "amount": self.amount,
                "found_ids": found_ids,
            })

        # Return the found cards so the caller can handle choices
        return found_cards
