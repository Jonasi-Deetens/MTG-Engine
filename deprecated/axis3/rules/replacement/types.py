# axis3/rules/replacement/types.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

# For type hints only
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from axis3.rules.events.event import Event
    from axis3.state.game_state import GameState
    from axis3.state.objects import RuntimeObject


@dataclass
class ReplacementEffect:
    """
    A runtime replacement effect.
    Supports both modern (game_state-aware) and legacy (event-only) signatures.
    """
    source_id: Optional[int]  # None for global effects
    applies_to: str           # e.g. "zone_change", "draw", "damage"

    # Modern signatures:
    #   condition(game_state, event, rt_obj) -> bool
    #   apply(game_state, event, rt_obj) -> Event
    #
    # Legacy signatures (still supported):
    #   condition(event) -> bool
    #   apply(event) -> Event
    condition: Callable[..., bool]
    apply: Callable[..., Event]
