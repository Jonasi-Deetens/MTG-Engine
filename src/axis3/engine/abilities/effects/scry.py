# axis3/engine/abilities/effects/scry.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class ScryEffect(ContinuousEffect):
    """
    Axis3 effect: Scry N (look at the top N cards of your library, then put any number
    on the bottom and the rest back on top in any order).

    This effect only reveals the cards to the controller and emits an event.
    The actual reordering is handled by the UI / choice system.
    """

    amount: int
    zones: Optional[List[str]] = None

    # Scry is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        player = game_state.players[controller]
        library = player.library

        # Look at the top N cards
        top_cards = library[: self.amount]
        revealed_ids = []

        for card in top_cards:
            # Mark as revealed only to the controller
            setattr(card, "revealed_to", controller)
            revealed_ids.append(getattr(card, "id", None))

        # Emit UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "scry",
                "source": source,
                "controller": controller,
                "amount": self.amount,
                "card_ids": revealed_ids,
            })

        return True
