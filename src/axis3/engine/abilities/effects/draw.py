# axis3/engine/abilities/effects/draw_card.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class DrawCardEffect(ContinuousEffect):
    """
    Axis3 effect: Controller draws N cards.

    Examples:
        DrawCardEffect(amount=1)
        DrawCardEffect(amount=3)
    """

    amount: int
    zones: Optional[List[str]] = None

    # Drawing cards is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        player = game_state.players[controller]
        drawn_cards = []

        for _ in range(self.amount):
            if not player.library:
                # TODO: handle draw-from-empty-library (lose game)
                break

            card = player.library.pop(0)
            player.hand.append(card)
            drawn_cards.append(getattr(card, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "cards_drawn",
                "source": source,
                "controller": controller,
                "amount": self.amount,
                "drawn_ids": drawn_cards,
            })

        return True
