# src/axis3/abilities/static.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Set

from axis3.state.objects import RuntimeObjectId
from axis3.state.game_state import GameState


@dataclass
class RuntimeContinuousEffect:
    """
    Runtime form of a continuous effect (from Axis2).
    """

    source_id: Optional[RuntimeObjectId]

    # Which layer this effect lives in (6, 7, etc.)
    layer: int

    # If it's a P/T effect, we also specify sublayer:
    # 7a, 7b, 7c, 7d etc. We'll start with '7b', '7c' as strings.
    sublayer: Optional[str]

    # Predicate: does this effect apply to this object?
    applies_to: Callable[[GameState, RuntimeObjectId], bool]

    # Effect functions; only some will be used per effect
    modify_power: Optional[Callable[[GameState, RuntimeObjectId, int], int]] = None
    modify_toughness: Optional[Callable[[GameState, RuntimeObjectId, int], int]] = None
    grant_abilities: Optional[Callable[[GameState, RuntimeObjectId, Set[str]], None]] = None
    remove_abilities: Optional[Callable[[GameState, RuntimeObjectId, Set[str]], None]] = None
