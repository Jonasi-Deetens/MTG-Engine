# axis3/engine/abilities/effects/unparsed.py

from dataclasses import dataclass
from typing import Optional, List, Any

from axis3.engine.abilities.effects.base import Axis3Effect


@dataclass
class UnparsedEffect(Axis3Effect):
    """
    Axis3 effect: Placeholder for effects that failed to parse.

    This effect does nothing when applied, but it records the original
    text or AST node so the engine, UI, or developer tools can surface
    the issue.

    Examples:
        UnparsedEffect(raw="Deal X damage to any target")
        UnparsedEffect(raw=node)
    """

    raw: Any
    zones: Optional[List[str]] = None

    # Unparsed effects do not participate in layers
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        # Emit a debug event so the UI/logging layer can show the issue
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "unparsed_effect",
                "source": source,
                "controller": controller,
                "raw": str(self.raw),
            })

        # Do nothing
        return True
