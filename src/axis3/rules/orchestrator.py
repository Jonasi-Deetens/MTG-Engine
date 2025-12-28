# axis3/rules/orchestrator.py

from axis3.rules.events.bus import EventBus
from axis3.rules.events.event import Event
from axis3.rules.replacement.apply import apply_replacements
from axis3.rules.sba.rules import run_sbas
from axis3.rules.triggers.registry import check_triggers
from axis3.rules.stack.resolver import resolve_top_of_stack, push_to_stack, StackItem
from axis3.rules.atomic.dispatch import apply_atomic_event

class GameOrchestrator:
    """
    Central game engine orchestrator.
    Handles event flow, triggers, stack, and SBAs.
    """
    def __init__(self, game_state):
        self.game_state = game_state
        self.event_bus = EventBus()
        self.game_state.event_bus = self.event_bus

        # Subscribe orchestrator to all events
        self.event_bus.subscribe(self._handle_event)

    def _handle_event(self, event: Event):
        """
        Handles every event published to the event bus.
        1. Apply replacement effects
        2. Run triggers
        3. Execute atomic rule if not skipped
        4. Run SBAs
        """
        # 1️⃣ Apply replacements
        event = apply_replacements(self.game_state, event)

        # Skip event if a replacement effect canceled it
        if event.payload.get("skip", False):
            return

        # 2️⃣ Check triggers
        check_triggers(self.game_state, event)

        # 3️⃣ Execute atomic rules
        apply_atomic_event(self.game_state, event)

        # 4️⃣ Run SBAs after atomic changes
        run_sbas(self.game_state)

    # -----------------------
    # Stack helper functions
    # -----------------------

    def push_to_stack(self, stack_item: StackItem):
        push_to_stack(self.game_state, stack_item)

    def resolve_top_of_stack(self):
        resolve_top_of_stack(self.game_state)

    def resolve_full_stack(self):
        while self.game_state.stack and not self.game_state.stack.is_empty():
            resolve_top_of_stack(self.game_state)

    # -----------------------
    # Event helper
    # -----------------------

    def publish_event(self, event: Event):
        self.event_bus.publish(event)
