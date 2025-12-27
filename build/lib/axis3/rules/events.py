# src/axis3/rules/events.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Any


@dataclass
class Event:
    type: str
    payload: Dict[str, Any]


class EventBus:
    """
    Simple synchronous publish/subscribe event system.
    """

    def __init__(self):
        self.listeners: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Event], None]):
        self.listeners.setdefault(event_type, []).append(callback)

    def publish(self, event: Event):
        for callback in self.listeners.get(event.type, []):
            callback(event)
