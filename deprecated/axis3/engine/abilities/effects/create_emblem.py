# axis3/engine/abilities/effects/create_emblem.py

from dataclasses import dataclass
from typing import Optional, List, Any

from axis3.effects.base import ContinuousEffect


@dataclass
class CreateEmblemEffect(ContinuousEffect):
    """
    Axis3 effect: Create an emblem for the controller with specified static effects.
    """

    name: str
    static_effects: List[Any]   # Typically StaticEffect objects
    zones: Optional[List[str]] = None

    # Emblems resolve immediately; their static effects are layered separately
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        """
        Runtime execution: create an emblem object and attach its static effects
        to the game state. Emblems live in the command zone.
        """

        emblem = {
            "name": self.name,
            "controller": controller,
            "static_effects": self.static_effects,
            "source": source,
            "is_emblem": True,
        }

        # Ensure command zone exists
        if not hasattr(game_state, "command_zone"):
            game_state.command_zone = []

        # Add emblem to command zone
        game_state.command_zone.append(emblem)

        # Register static effects globally
        for eff in self.static_effects:
            game_state.continuous_effects.append(eff)

        # Optional event emission for UI
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "emblem_created",
                "source": source,
                "controller": controller,
                "name": self.name,
                "static_effect_count": len(self.static_effects),
            })

        return True
