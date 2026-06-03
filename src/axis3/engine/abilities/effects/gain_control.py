# axis3/engine/abilities/effects/gain_control.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class GainControlEffect(ContinuousEffect):
    """
    Axis3 effect: Controller gains control of one or more permanents.

    Examples:
        GainControlEffect(subject="target_creature")
        GainControlEffect(subject="artifact_opponent_controls")
        GainControlEffect(subject="this")
    """

    subject: str
    zones: Optional[List[str]] = None

    # Control change is a one-shot effect (not layered unless continuous)
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        targets = resolver.resolve(self.subject, source, controller)

        changed_ids = []

        for obj in list(targets):
            # Only permanents can change control
            if obj not in game_state.battlefield:
                continue

            # Update controller
            old_controller = getattr(obj, "controller", None)
            obj.controller = controller

            changed_ids.append(getattr(obj, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "control_changed",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "objects": changed_ids,
            })

        return True
