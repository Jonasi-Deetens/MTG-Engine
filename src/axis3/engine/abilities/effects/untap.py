# axis3/engine/abilities/effects/untap.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class UntapEffect(ContinuousEffect):
    """
    Axis3 effect: Untap one or more permanents.

    Examples:
        UntapEffect(subject="target_creature")
        UntapEffect(subject="creatures_you_control")
        UntapEffect(subject="this")
    """

    subject: str
    zones: Optional[List[str]] = None

    # Untapping is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        objects = resolver.resolve(self.subject, source, controller)

        untapped_ids = []

        for obj in objects:
            # Only permanents on the battlefield can be untapped
            if obj not in game_state.battlefield:
                continue

            # Ensure the permanent has a tapped flag
            if not hasattr(obj, "tapped"):
                obj.tapped = False

            # Untap it
            obj.tapped = False
            untapped_ids.append(getattr(obj, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "permanent_untapped",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "objects": untapped_ids,
            })

        return True
