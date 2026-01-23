from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .core.types import EventType

logger = logging.getLogger(__name__)


@dataclass
class Event:
    """Represents a game event that can be published through the event bus."""

    type: str
    payload: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_type(cls, event_type: EventType, **payload: Any) -> Event:
        """Create an event from an EventType enum."""
        return cls(type=event_type.value, payload=payload)


EventHandler = Callable[[Event], None]


class EventBus:
    """Pub/sub event system for game events.

    Supports both immediate publishing and queued (deferred) event publishing.
    """

    def __init__(self) -> None:
        self._handlers: Dict[str, List[EventHandler]] = {}
        self._queue: deque[Event] = deque()
        self._processing_queue: bool = False

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe a handler to an event type."""
        self._handlers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Unsubscribe a handler from an event type."""
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)

    def unsubscribe_all(self, event_type: Optional[str] = None) -> None:
        """Unsubscribe all handlers for an event type, or all handlers if no type specified."""
        if event_type is None:
            self._handlers.clear()
        elif event_type in self._handlers:
            del self._handlers[event_type]

    def publish(self, event: Event) -> None:
        """Publish an event immediately, calling all subscribed handlers."""
        if event.type in ("enters_battlefield", "card_enters"):
            logger.debug(f"[graph] event_bus {event.type} payload={event.payload}")
            print(f"[graph] event_bus {event.type} payload={event.payload}", flush=True)
        for handler in self._handlers.get(event.type, []):
            handler(event)

    def queue(self, event: Event) -> None:
        """Queue an event for deferred publishing.

        Queued events are published when flush_queue() is called.
        This is useful for batching events or avoiding recursive event handling.
        """
        self._queue.append(event)

    def flush_queue(self) -> None:
        """Process all queued events in FIFO order.

        Events are published one at a time. New events queued during processing
        will be processed in the same flush cycle.
        """
        if self._processing_queue:
            # Prevent re-entrant queue processing
            return

        self._processing_queue = True
        try:
            while self._queue:
                event = self._queue.popleft()
                self.publish(event)
        finally:
            self._processing_queue = False

    def has_queued_events(self) -> bool:
        """Check if there are events waiting in the queue."""
        return len(self._queue) > 0

    def clear_queue(self) -> None:
        """Clear all queued events without publishing them."""
        self._queue.clear()

    def get_handlers(self, event_type: str) -> List[EventHandler]:
        """Get all handlers for an event type (for testing/debugging)."""
        return list(self._handlers.get(event_type, []))
