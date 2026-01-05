# axis3/engine/abilities/effects/destroy.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class DestroyEffect(ContinuousEffect):
    """
    Axis3 effect: Destroy one or more permanents.

    Examples:
        DestroyEffect(subject="target_creature")
        DestroyEffect(subject="creature_opponent_controls")
        DestroyEffect(subject="all_artifacts")
    """

    subject: str
    zones: Optional[List[str]] = None

    # Destroy is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        targets = resolver.resolve(self.subject, source, controller)

        destroyed_ids = []

        for obj in list(targets):
            # Tokens cease to exist when destroyed
            if getattr(obj, "is_token", False):
                if obj in game_state.battlefield:
                    game_state.battlefield.remove(obj)
                destroyed_ids.append(getattr(obj, "id", None))
                continue

            # Non-token permanents go to graveyard
            owner = getattr(obj, "owner", None)
            if owner is None:
                continue

            if obj in game_state.battlefield:
                game_state.battlefield.remove(obj)

            if owner not in game_state.graveyards:
                game_state.graveyards[owner] = []

            game_state.graveyards[owner].append(obj)
            destroyed_ids.append(getattr(obj, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "permanent_destroyed",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "objects": destroyed_ids,
            })

        return True
