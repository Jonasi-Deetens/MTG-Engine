# axis3/engine/abilities/effects/put_counters.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class PutCountersEffect(ContinuousEffect):
    """
    Axis3 effect: Put counters on one or more permanents.

    Examples:
        PutCountersEffect(subject="target_creature", counter_type="+1/+1", amount=1)
        PutCountersEffect(subject="creatures_you_control", counter_type="-1/-1", amount=2)
        PutCountersEffect(subject="this", counter_type="loyalty", amount=3)
    """

    subject: str
    counter_type: str
    amount: int = 1
    zones: Optional[List[str]] = None

    # Counters modify P/T in Layer 7d, but placing counters is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        objects = resolver.resolve(self.subject, source, controller)

        affected_ids = []

        for obj in objects:
            # Ensure the object has a counter dictionary
            if not hasattr(obj, "counters"):
                obj.counters = {}

            obj.counters[self.counter_type] = obj.counters.get(self.counter_type, 0) + self.amount
            affected_ids.append(getattr(obj, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "counters_added",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "counter_type": self.counter_type,
                "amount": self.amount,
                "objects": affected_ids,
            })

        return True
