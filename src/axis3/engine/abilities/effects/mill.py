# axis3/engine/abilities/effects/mill.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class MillEffect(ContinuousEffect):
    """
    Axis3 effect: Target player mills N cards (puts the top N cards of their library into their graveyard).

    Examples:
        MillEffect(amount=3)  # controller mills 3
        MillEffect(amount=5, subject="opponent")
        MillEffect(amount=2, subject="target_player")
    """

    amount: int
    subject: Optional[str] = None   # None = controller mills
    zones: Optional[List[str]] = None

    # Milling is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        # Determine which player mills
        if self.subject:
            resolver = game_state.subject_resolver
            players = resolver.resolve(self.subject, source, controller)
            if not players:
                return True
            player = players[0]
        else:
            player = game_state.players[controller]

        milled_ids = []
        graveyard = game_state.graveyards[player.id]

        for _ in range(self.amount):
            if not player.library:
                # TODO: handle draw-from-empty-library loss if needed
                break

            card = player.library.pop(0)
            graveyard.append(card)
            milled_ids.append(getattr(card, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "cards_milled",
                "source": source,
                "controller": controller,
                "target_player": player.id,
                "amount": self.amount,
                "milled_ids": milled_ids,
            })

        return True
