# axis3/engine/abilities/effects/bounce.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class BounceEffect(ContinuousEffect):
    """
    Axis3 effect: Return one or more permanents to their owner's hand.
    """

    subject: str
    zones: Optional[List[str]] = None

    # Bounce is a one-shot effect, not layered
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        objects = resolver.resolve(self.subject, source, controller)

        bounced_ids = []

        for obj in list(objects):
            owner = getattr(obj, "owner", None)
            if owner is None:
                continue

            # Remove from battlefield
            if obj in game_state.battlefield:
                game_state.battlefield.remove(obj)

            # Add to owner's hand
            if owner not in game_state.hands:
                game_state.hands[owner] = []

            game_state.hands[owner].append(obj)

            # Track for UI logging
            bounced_ids.append(getattr(obj, "id", None))

        # Optional event emission for UI
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "permanent_bounced",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "objects": bounced_ids,
            })

        return True
