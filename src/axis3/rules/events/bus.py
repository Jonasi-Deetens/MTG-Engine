# axis3/rules/events/bus.py

from axis3.rules.events.event import Event
from axis3.rules.events.queue import EventQueue
from axis3.rules.replacement.apply import apply_replacements
from axis3.rules.triggers.types import TriggerRegistry
from axis3.rules.sba.checker import run_sbas
from axis3.rules.atomic.dispatch import apply_atomic_event


class EventBus:
    def __init__(self, game_state: "GameState"):
        self.game_state = game_state
        self.queue = EventQueue()
        self.triggers = TriggerRegistry()

    def publish(self, event: Event):
        """
        Public entry point.
        """
        self.queue.push(event)
        self._drain()

    def _drain(self):
        while not self.queue.is_empty():
            event = self.queue.pop()

            # 1️⃣ Replacement effects
            event = apply_replacements(self.game_state, event)
            if event is None:
                continue  # event was replaced away

            # 2️⃣ Apply atomic rule
            apply_atomic_event(self.game_state, event)

            # 3️⃣ Observe triggers
            self.triggers.notify(event)

            # 4️⃣ State-based actions
            run_sbas(self.game_state)

    # Add this so tests and other code can subscribe to triggers
    def subscribe(self, event_type: str, callback):
        self.triggers.register(event_type, callback)