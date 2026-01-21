from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from .ability_graph import AbilityGraphRuntimeAdapter
from .events import Event
from .triggers.trigger_registry import TriggerRegistry, RegisteredTrigger
from .triggers.trigger_handler import TriggerHandler
from .state import GameObject, GameState, ResolveContext
from .stack import StackItem


# Backward compatibility alias
@dataclass
class RegisteredAbility:
    """Backward compatibility alias for RegisteredTrigger."""
    source_id: str
    controller_id: int
    trigger: str
    graph: Dict
    trigger_data: Optional[Dict]


class AbilityRegistry:
    """Registry and handler for triggered abilities.

    This class now delegates to TriggerRegistry and TriggerHandler
    while maintaining backward compatibility with existing code.
    """

    def __init__(self, game_state: GameState) -> None:
        self.game_state = game_state
        self.adapter = AbilityGraphRuntimeAdapter(game_state)

        # Create the new modular components
        self._trigger_registry = TriggerRegistry(self.adapter)
        self._trigger_handler = TriggerHandler(self._trigger_registry, game_state)

        # Initialize
        self._register_from_objects()
        self._subscribe()

    @property
    def registered(self) -> List[RegisteredAbility]:
        """Backward compatibility: return registered triggers as RegisteredAbility."""
        return [
            RegisteredAbility(
                source_id=entry.source_id,
                controller_id=entry.controller_id,
                trigger=entry.trigger,
                graph=entry.graph,
                trigger_data=entry.trigger_data,
            )
            for entry in self._trigger_registry.registered
        ]

    @property
    def trigger_registry(self) -> TriggerRegistry:
        """Get the underlying TriggerRegistry."""
        return self._trigger_registry

    @property
    def trigger_handler(self) -> TriggerHandler:
        """Get the underlying TriggerHandler."""
        return self._trigger_handler

    def _register_from_objects(self) -> None:
        """Register triggered abilities from all game objects."""
        self._trigger_registry.register_from_objects(self.game_state.objects)

    def _register_object(self, obj: GameObject) -> None:
        """Register triggered abilities from a single object."""
        self._trigger_registry.register_object(obj)

    def _unregister_object(self, obj_id: str) -> None:
        """Unregister all triggered abilities from an object."""
        self._trigger_registry.unregister_object(obj_id)

    def _subscribe(self) -> None:
        """Subscribe to events for all registered trigger types."""
        triggers = self._trigger_registry.registered_triggers
        special_triggers = {"enters_battlefield", "leaves_battlefield"}

        for trigger in triggers - special_triggers:
            self.game_state.event_bus.subscribe(trigger, self._handle_event)

        if "enters_battlefield" in triggers:
            self.game_state.event_bus.subscribe("enters_battlefield", self._handle_enters)
        if "leaves_battlefield" in triggers:
            self.game_state.event_bus.subscribe("leaves_battlefield", self._handle_leaves)

    def _handle_enters(self, event: Event) -> None:
        """Handle enters_battlefield event - register new object and process triggers."""
        obj_id = event.payload.get("object_id")
        if not obj_id:
            return
        obj = self.game_state.objects.get(obj_id)
        if obj:
            self._register_object(obj)
        self._handle_event(event)

    def _handle_leaves(self, event: Event) -> None:
        """Handle leaves_battlefield event - process triggers and unregister object."""
        self._handle_event(event)
        obj_id = event.payload.get("object_id")
        if obj_id:
            self._unregister_object(obj_id)

    def _handle_event(self, event: Event) -> None:
        """Handle an event by delegating to TriggerHandler."""
        self._trigger_handler.handle_event(event)


