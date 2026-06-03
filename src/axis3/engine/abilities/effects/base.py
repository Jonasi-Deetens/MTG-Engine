# axis3/engine/abilities/effects/base.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class Axis3Effect:
    """
    Base class for all Axis3 runtime effects.

    Axis3 effects are NOT Axis2 effect descriptors.
    They do not use effect_type, selector, or params.
    They are concrete runtime behaviors that modify the GameState
    by registering permissions, costs, replacement effects, or
    continuous effects.

    Every Axis3Effect must implement apply(game_state, source, controller).
    """

    # Effects default to the "resolution" layer unless overridden
    layering: str = "resolution"

    def apply(self, game_state: Any, source: str, controller: int) -> bool:
        """
        Apply this effect to the game state.

        This method is overridden by concrete effects such as:
          - FlashbackEffect
          - CreateDynamicTokenEffect
          - UnparsedEffect
          - KickerEffect (future)
          - EscapeEffect (future)
          - BuybackEffect (future)

        The return value indicates whether the effect successfully applied.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement apply()"
        )
