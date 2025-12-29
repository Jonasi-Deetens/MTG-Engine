from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class AddManaEffect(ContinuousEffect):
    """
    Axis3 effect: Add mana to the controller's mana pool.

    Examples:
        AddManaEffect(color="G")
        AddManaEffect(color="U", amount=2)
    """

    color: str
    amount: int = 1
    zones: Optional[List[str]] = None

    # Mana abilities resolve immediately, not layered
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        """
        Runtime execution: add mana to the controller's mana pool.
        """

        player = game_state.players[controller]
        player.mana_pool[self.color] += self.amount

        # Optional event emission (Axis3-friendly)
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "mana_added",
                "source": source,
                "controller": controller,
                "color": self.color,
                "amount": self.amount,
            })

        return True
