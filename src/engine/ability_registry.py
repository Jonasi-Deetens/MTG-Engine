from __future__ import annotations

from typing import List, Optional
from .events import Event
from .triggers.trigger_registry import RegisteredTrigger
from .triggers.trigger_handler import TriggerHandler
from .state import GameObject, GameState
from .effects import register_active_effects_from_object, unregister_active_effects_for_source


class AbilityRegistry:
    """Registry and handler for triggered effects."""

    def __init__(self, game_state: GameState) -> None:
        self.game_state = game_state
        self._trigger_handler = TriggerHandler(game_state)
        self._subscribed_triggers: set[str] = set()

        # Initialize
        self._register_from_objects()
        self._subscribe()

    @property
    def registered(self) -> List[RegisteredTrigger]:
        """Legacy triggers are no longer registered."""
        return []

    @property
    def trigger_registry(self):
        """Legacy trigger registry is deprecated."""
        return None

    @property
    def trigger_handler(self) -> TriggerHandler:
        """Get the underlying TriggerHandler."""
        return self._trigger_handler

    def _register_from_objects(self) -> None:
        """Register triggered effects from all game objects."""
        for obj in self.game_state.objects.values():
            register_active_effects_from_object(self.game_state, obj)
        self._subscribe_to_active_triggers()

    def _register_object(self, obj: GameObject) -> None:
        """Register triggered effects from a single object."""
        register_active_effects_from_object(self.game_state, obj)
        self._subscribe_to_active_triggers()

    def _unregister_object(self, obj_id: str) -> None:
        """Unregister all triggered effects from an object."""
        unregister_active_effects_for_source(self.game_state, obj_id)

    def _subscribe(self) -> None:
        """Subscribe to events for all registered trigger types."""
        # Always subscribe to enters/leaves_battlefield regardless of current triggers.
        self.game_state.event_bus.subscribe("enters_battlefield", self._handle_enters)
        self.game_state.event_bus.subscribe("leaves_battlefield", self._handle_leaves)
        self._subscribe_to_active_triggers()

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

    def _entry_key(self, entry) -> str:
        """Legacy trigger entries are no longer supported."""
        return ""

    def _subscribe_to_active_triggers(self) -> None:
        for trigger in self.game_state.active_effect_registry.get_trigger_event_types():
            if trigger in self._subscribed_triggers:
                continue
            self.game_state.event_bus.subscribe(trigger, self._handle_event)
            self._subscribed_triggers.add(trigger)


