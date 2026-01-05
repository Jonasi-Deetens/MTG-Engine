# axis3/abilities/triggered.py

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType

class RuntimeTriggeredAbility:
    """
    Runtime representation of a triggered ability.
    """
    def __init__(self, source_id: int, controller: int, axis2_trigger):
        self.source_id = source_id
        self.controller = controller
        self.axis2_trigger = axis2_trigger  # Axis2 trigger definition

    def resolve(self, game_state):
        """
        Resolve the triggered ability by publishing its effect events.
        The EventBus handles replacement, atomic rules, triggers, and SBAs.
        """
        effect = self.axis2_trigger.effect

        # The Axis2 trigger should already define structured effect actions.
        # Example: effect = [("DRAW", {"player_id": controller, "amount": 1})]

        for action_type, payload in effect:
            game_state.event_bus.publish(Event(
                type=action_type,
                payload=payload
            ))
