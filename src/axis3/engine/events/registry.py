# src/axis3/engine/events/registry.py

from typing import Callable, Dict, List
from axis3.rules.events import Event

class EventCallbackRegistry:
    """
    Registry for rule-level event handlers.
    """

    def __init__(self, game_state):
        self.game_state = game_state
        self._registry: Dict[str, List[Callable[[object, Event], None]]] = {}

    def register(self, event_type: str, callback: Callable[[object, Event], None]):
        if event_type not in self._registry:
            self._registry[event_type] = []
        self._registry[event_type].append(callback)

    def unregister(self, event_type: str, callback):
        if event_type in self._registry and callback in self._registry[event_type]:
            self._registry[event_type].remove(callback)
            if not self._registry[event_type]:
                del self._registry[event_type]

    def notify(self, event: Event):
        callbacks = self._registry.get(event.type, [])
        for cb in callbacks:
            cb(self.game_state, event)
