# axis3/engine/abilities/effects/exile.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class ExileEffect(ContinuousEffect):
    """
    Axis3 effect: Exile one or more permanents.

    Examples:
        ExileEffect(subject="target_creature")
        ExileEffect(subject="creature_opponent_controls")
        ExileEffect(subject="all_artifacts")
    """

    subject: str
    zones: Optional[List[str]] = None

    # Exile is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        targets = resolver.resolve(self.subject, source, controller)

        exiled_ids = []

        for obj in list(targets):
            # Tokens cease to exist when exiled
            if getattr(obj, "is_token", False):
                if obj in game_state.battlefield:
                    game_state.battlefield.remove(obj)
                exiled_ids.append(getattr(obj, "id", None))
                continue

            # Non-token permanents go to the exile zone
            owner = getattr(obj, "owner", None)
            if owner is None:
                continue

            if obj in game_state.battlefield:
                game_state.battlefield.remove(obj)

            if owner not in game_state.exile:
                game_state.exile[owner] = []

            game_state.exile[owner].append(obj)
            exiled_ids.append(getattr(obj, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "permanent_exiled",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "objects": exiled_ids,
            })

        return True
