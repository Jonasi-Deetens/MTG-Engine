from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    type: str
    payload: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: str, handler: Callable[[Event], None]) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def publish(self, event: Event) -> None:
        for handler in self._handlers.get(event.type, []):
            handler(event)
