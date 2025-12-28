# axis3/abilities/static.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Optional, Set, List

from axis3.state.objects import RuntimeObjectId

# For type hints only:
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from axis3.state.game_state import GameState

@dataclass
class RuntimeContinuousEffect:
    """
    Data-driven representation of a continuous effect.
    Handles P/T modification, abilities, etc.
    """
    source_id: Optional[RuntimeObjectId]  # Which object created this effect
    layer: int                             # Layer 1-7
    sublayer: Optional[str] = None         # e.g., '7b', '7c', etc.
    applies_to: Callable[[GameState, RuntimeObjectId], bool] = lambda gs, oid: True

    # Optional effect functions
    modify_power: Optional[Callable[[GameState, RuntimeObjectId, int], int]] = None
    modify_toughness: Optional[Callable[[GameState, RuntimeObjectId, int], int]] = None
    add_abilities: Optional[Callable[[GameState, RuntimeObjectId, Set[str]], None]] = None
    remove_abilities: Optional[Callable[[GameState, RuntimeObjectId, Set[str]], None]] = None

    # Optional additions/removals for types/colors/keywords
    add_types: Set[str] = field(default_factory=set)
    remove_types: Set[str] = field(default_factory=set)
    add_subtypes: Set[str] = field(default_factory=set)
    remove_subtypes: Set[str] = field(default_factory=set)
    add_supertypes: Set[str] = field(default_factory=set)
    remove_supertypes: Set[str] = field(default_factory=set)
    add_colors: Set[str] = field(default_factory=set)
    remove_colors: Set[str] = field(default_factory=set)
    add_keywords: Set[str] = field(default_factory=set)
    remove_keywords: Set[str] = field(default_factory=set)

@dataclass
class RuntimeStaticAbility:
    """
    Container for one or more RuntimeContinuousEffects.
    Attached to a permanent.
    """
    source_id: RuntimeObjectId
    effects: List[RuntimeContinuousEffect]

    def apply(self, game_state: GameState, obj_id: RuntimeObjectId, ec):
        """
        Apply all continuous effects to the evaluated characteristics (ec)
        of obj_id, respecting layer/sub-layer order.
        """
        for effect in self.effects:
            # Skip if effect does not apply
            if not effect.applies_to(game_state, obj_id):
                continue

            # Apply P/T modifications
            if effect.modify_power:
                ec.power = effect.modify_power(game_state, obj_id, ec.power)
            if effect.modify_toughness:
                ec.toughness = effect.modify_toughness(game_state, obj_id, ec.toughness)

            # Apply abilities
            if effect.grant_abilities:
                effect.grant_abilities(game_state, obj_id, ec.abilities)
            if effect.remove_abilities:
                effect.remove_abilities(game_state, obj_id, ec.abilities)
