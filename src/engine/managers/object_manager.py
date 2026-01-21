"""Object lifecycle management for game objects."""

from __future__ import annotations

import itertools
import logging
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set

from ..core.types import ZONE_BATTLEFIELD

if TYPE_CHECKING:
    from ..state import GameObject

logger = logging.getLogger(__name__)

# Global ID counter for generating unique object IDs
_id_counter = itertools.count(1)


def next_object_id() -> str:
    """Generate the next unique object ID."""
    return f"obj_{next(_id_counter)}"


def reset_id_counter(start: int = 1) -> None:
    """Reset the ID counter (useful for testing)."""
    global _id_counter
    _id_counter = itertools.count(start)


class ObjectManager:
    """Manages game object lifecycle.

    Responsible for:
    - Adding objects to the game
    - Removing objects from the game
    - Object lookup
    - Token creation
    - Base property initialization
    """

    def __init__(
        self,
        objects: Dict[str, "GameObject"],
        get_turn_number: Callable[[], int],
    ) -> None:
        self._objects = objects
        self._get_turn_number = get_turn_number

    def add(self, obj: "GameObject") -> None:
        """Add an object to the game, initializing base properties."""
        self._objects[obj.id] = obj

        # Set entered turn for battlefield objects
        if obj.zone == ZONE_BATTLEFIELD and obj.entered_turn is None:
            obj.entered_turn = self._get_turn_number()

        # Initialize base properties if not set
        self._initialize_base_properties(obj)

    def remove(self, obj_id: str) -> Optional["GameObject"]:
        """Remove an object from the game and return it."""
        return self._objects.pop(obj_id, None)

    def get(self, obj_id: str) -> Optional["GameObject"]:
        """Get an object by ID."""
        return self._objects.get(obj_id)

    def get_all(self) -> Dict[str, "GameObject"]:
        """Get all objects."""
        return self._objects

    def exists(self, obj_id: str) -> bool:
        """Check if an object exists."""
        return obj_id in self._objects

    def get_by_ids(self, obj_ids: List[str]) -> List["GameObject"]:
        """Get multiple objects by IDs, filtering out non-existent ones."""
        return [self._objects[oid] for oid in obj_ids if oid in self._objects]

    def get_controlled_by(self, controller_id: int) -> List["GameObject"]:
        """Get all objects controlled by a player."""
        return [obj for obj in self._objects.values() if obj.controller_id == controller_id]

    def get_owned_by(self, owner_id: int) -> List["GameObject"]:
        """Get all objects owned by a player."""
        return [obj for obj in self._objects.values() if obj.owner_id == owner_id]

    def clear_battlefield_state(self, obj: "GameObject") -> None:
        """Clear battlefield-specific state from an object."""
        obj.damage = 0
        obj.tapped = False
        obj.is_attacking = False
        obj.is_blocking = False
        obj.attached_to = None
        obj.counters = {}
        obj.temporary_effects = []
        obj.protections = set()

    def apply_enter_copy(self, obj: "GameObject", source: "GameObject") -> None:
        """Apply copy effect from source to object (for clone effects)."""
        obj.base_name = source.name
        obj.base_mana_cost = source.mana_cost
        obj.base_mana_value = source.mana_value
        obj.base_type_line = source.type_line
        obj.base_oracle_text = source.oracle_text
        obj.base_types = list(source.types)
        obj.base_colors = list(source.colors)
        obj.base_power = source.power
        obj.base_toughness = source.toughness
        obj.base_keywords = set(source.keywords)
        obj.base_ability_graphs = list(source.ability_graphs)
        obj.base_etb_choices = dict(getattr(source, "etb_choices", {}) or {})
        obj.etb_choices = dict(obj.base_etb_choices)

        # Apply base values to current values
        obj.name = obj.base_name or obj.name
        obj.mana_cost = obj.base_mana_cost
        obj.mana_value = obj.base_mana_value
        obj.type_line = obj.base_type_line
        obj.oracle_text = obj.base_oracle_text
        obj.types = list(obj.base_types)
        obj.colors = list(obj.base_colors)
        obj.power = obj.base_power
        obj.toughness = obj.base_toughness
        obj.keywords = set(obj.base_keywords)
        obj.ability_graphs = list(obj.base_ability_graphs)

    def apply_enter_choices(self, obj: "GameObject", choices: Dict[str, Any]) -> None:
        """Apply ETB choices to an object."""
        if not choices:
            return
        obj.etb_choices.update(choices)
        obj.base_etb_choices.update(choices)

    def _initialize_base_properties(self, obj: "GameObject") -> None:
        """Initialize base properties if not already set."""
        if obj.base_controller_id is None:
            obj.base_controller_id = obj.controller_id
        if obj.base_name is None:
            obj.base_name = obj.name
        if obj.base_mana_cost is None:
            obj.base_mana_cost = obj.mana_cost
        if obj.base_mana_value is None:
            obj.base_mana_value = obj.mana_value
        if obj.base_type_line is None:
            obj.base_type_line = obj.type_line
        if obj.base_oracle_text is None:
            obj.base_oracle_text = obj.oracle_text
        if not obj.base_ability_graphs and obj.ability_graphs:
            obj.base_ability_graphs = list(obj.ability_graphs)
        if not obj.base_etb_choices and obj.etb_choices:
            obj.base_etb_choices = dict(obj.etb_choices)
