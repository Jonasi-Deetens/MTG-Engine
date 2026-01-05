# axis3/engine/abilities/effects/tap.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class TapEffect(ContinuousEffect):
    """
    Axis3 effect: Tap one or more permanents.

    Examples:
        TapEffect(subject="target_creature")
        TapEffect(subject="creatures_opponent_controls")
        TapEffect(subject="this")
    """

    subject: str
    zones: Optional[List[str]] = None

    # Tapping is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        objects = resolver.resolve(self.subject, source, controller)

        tapped_ids = []

        for obj in objects:
            # Only permanents on the battlefield can be tapped
            if obj not in game_state.battlefield:
                continue

            # Ensure the permanent has a tapped flag
            if not hasattr(obj, "tapped"):
                obj.tapped = False

            # Tap it
            obj.tapped = True
            tapped_ids.append(getattr(obj, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "permanent_tapped",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "objects": tapped_ids,
            })

        return True
