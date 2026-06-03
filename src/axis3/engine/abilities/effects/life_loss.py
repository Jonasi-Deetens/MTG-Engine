# axis3/engine/abilities/effects/life_loss.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class LoseLifeEffect(ContinuousEffect):
    """
    Axis3 effect: Controller loses N life.

    Examples:
        LifeLossEffect(amount=3)
        LifeLossEffect(amount=1)
    """

    amount: int
    zones: Optional[List[str]] = None

    # Life loss is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        player = game_state.players[controller]

        # Apply life loss
        player.life -= self.amount

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "life_lost",
                "source": source,
                "controller": controller,
                "amount": self.amount,
                "new_life_total": player.life,
            })

        return True
