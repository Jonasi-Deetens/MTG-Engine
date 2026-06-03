# axis3/engine/abilities/effects/pump.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class PumpEffect(ContinuousEffect):
    """
    Axis3 effect: Modify power/toughness of one or more creatures.

    Examples:
        PumpEffect(subject="target_creature", power=3, toughness=3)
        PumpEffect(subject="creatures_you_control", power=1, toughness=0)
        PumpEffect(subject="this", power=2, toughness=2)
    """

    subject: str
    power: int = 0
    toughness: int = 0
    zones: Optional[List[str]] = None

    # Power/toughness modifications are Layer 7c
    layering: str = "layer_7c"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        objects = resolver.resolve(self.subject, source, controller)

        affected_ids = []

        for obj in objects:
            # Ensure the object has temporary PT modifiers
            if not hasattr(obj, "temp_power"):
                obj.temp_power = 0
            if not hasattr(obj, "temp_toughness"):
                obj.temp_toughness = 0

            obj.temp_power += self.power
            obj.temp_toughness += self.toughness

            affected_ids.append(getattr(obj, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "creature_pumped",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "power": self.power,
                "toughness": self.toughness,
                "objects": affected_ids,
            })

        return True
