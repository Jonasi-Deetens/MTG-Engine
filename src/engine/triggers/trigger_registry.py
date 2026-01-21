"""Trigger registration for triggered abilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from ..state import GameObject
    from ..ability_graph import AbilityGraphRuntimeAdapter

logger = logging.getLogger(__name__)


@dataclass
class RegisteredTrigger:
    """A registered triggered ability."""

    source_id: str
    controller_id: int
    trigger: str
    graph: Dict[str, Any]
    trigger_data: Optional[Dict[str, Any]]


class TriggerRegistry:
    """Registry for triggered abilities.

    Responsible for:
    - Registering triggered abilities from game objects
    - Unregistering abilities when objects leave the battlefield
    - Tracking which trigger types are registered
    - Providing registered triggers for event matching
    """

    def __init__(self, adapter: "AbilityGraphRuntimeAdapter") -> None:
        self._adapter = adapter
        self._registered: List[RegisteredTrigger] = []
        self._registered_triggers: Set[str] = set()

    @property
    def registered(self) -> List[RegisteredTrigger]:
        """Get all registered triggers."""
        return self._registered

    @property
    def registered_triggers(self) -> Set[str]:
        """Get all unique trigger types that are registered."""
        return self._registered_triggers

    def register_from_objects(self, objects: Dict[str, "GameObject"]) -> None:
        """Register triggered abilities from all game objects."""
        for obj in objects.values():
            self.register_object(obj)

    def register_object(self, obj: "GameObject") -> None:
        """Register triggered abilities from a single object."""
        for graph in obj.ability_graphs:
            runtime = self._adapter.build_runtime(graph)
            if not runtime.trigger:
                continue

            # Check for duplicates
            if self._is_duplicate(obj.id, runtime.trigger, graph):
                continue

            trigger = RegisteredTrigger(
                source_id=obj.id,
                controller_id=obj.controller_id,
                trigger=runtime.trigger,
                graph=graph,
                trigger_data=runtime.trigger_data,
            )
            self._registered.append(trigger)
            self._registered_triggers.add(runtime.trigger)
            logger.debug(f"Registered trigger: {obj.id} -> {runtime.trigger}")

    def unregister_object(self, obj_id: str) -> None:
        """Unregister all triggered abilities from an object."""
        self._registered = [
            entry for entry in self._registered if entry.source_id != obj_id
        ]
        # Rebuild registered triggers set
        self._registered_triggers = {entry.trigger for entry in self._registered}
        logger.debug(f"Unregistered triggers for: {obj_id}")

    def get_by_trigger(self, trigger_type: str) -> List[RegisteredTrigger]:
        """Get all registered triggers of a specific type."""
        return [entry for entry in self._registered if entry.trigger == trigger_type]

    def get_by_source(self, source_id: str) -> List[RegisteredTrigger]:
        """Get all registered triggers from a specific source object."""
        return [entry for entry in self._registered if entry.source_id == source_id]

    def has_trigger_type(self, trigger_type: str) -> bool:
        """Check if any triggers of a specific type are registered."""
        return trigger_type in self._registered_triggers

    def clear(self) -> None:
        """Clear all registered triggers."""
        self._registered.clear()
        self._registered_triggers.clear()

    def _is_duplicate(self, source_id: str, trigger: str, graph: Dict[str, Any]) -> bool:
        """Check if this trigger is already registered (avoid duplicates)."""
        for entry in self._registered:
            if entry.source_id != source_id:
                continue
            if entry.trigger != trigger:
                continue
            # Use identity check for graph (same object in memory)
            if entry.graph is graph:
                return True
        return False
