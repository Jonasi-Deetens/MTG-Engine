# src/axis3/rules/triggers/registry.py

from typing import Callable, Dict, List
from axis3.rules.events import Event

class TriggerRegistry:
    """
    A registry to track which objects are subscribed to which event types.
    Allows the EventBus to notify triggers when events occur.
    """

    def __init__(self):
        # event_type -> list of callbacks
        self._registry: Dict[str, List[Callable[[Event], None]]] = {}

    def register(self, event_type: str, callback: Callable[[Event], None]):
        """Subscribe a callback to a specific event type."""
        if event_type not in self._registry:
            self._registry[event_type] = []
        self._registry[event_type].append(callback)

    def unregister(self, event_type: str, callback: Callable[[Event], None]):
        """Remove a callback from a specific event type."""
        if event_type in self._registry and callback in self._registry[event_type]:
            self._registry[event_type].remove(callback)
            if not self._registry[event_type]:
                del self._registry[event_type]

    def notify(self, event: Event):
        """Notify all registered triggers of this event."""
        callbacks = self._registry.get(event.type, [])
        for cb in callbacks:
            cb(event)
