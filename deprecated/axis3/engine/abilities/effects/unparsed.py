# axis3/engine/abilities/effects/unparsed.py

from dataclasses import dataclass, field
from typing import Optional, List, Any

from axis3.engine.abilities.effects.base import Axis3Effect


@dataclass
class UnparsedEffect(Axis3Effect):
    """
    Axis3 effect: Placeholder for effects that failed to parse.
    """

    raw: Any = None
    zones: Optional[List[str]] = None

    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "unparsed_effect",
                "source": source,
                "controller": controller,
                "raw": str(self.raw),
            })
        return True
