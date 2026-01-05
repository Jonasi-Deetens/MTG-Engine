# axis3/engine/abilities/effects/gain_life.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class GainLifeEffect(ContinuousEffect):
    """
    Axis3 effect: Controller gains N life.

    Examples:
        GainLifeEffect(amount=3)
        GainLifeEffect(amount=5)
    """

    amount: int
    zones: Optional[List[str]] = None

    # Life gain is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        player = game_state.players[controller]

        # Apply life gain
        player.life += self.amount

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "life_gained",
                "source": source,
                "controller": controller,
                "amount": self.amount,
                "new_life_total": player.life,
            })

        return True
