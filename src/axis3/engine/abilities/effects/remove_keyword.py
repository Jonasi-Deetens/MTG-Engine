# axis3/engine/abilities/effects/remove_keyword.py

from dataclasses import dataclass
from typing import List, Optional

from axis3.effects.base import ContinuousEffect


@dataclass
class RemoveKeywordEffect(ContinuousEffect):
    """
    Axis3 effect: Remove one or more keyword abilities from a subject.

    Examples:
        RemoveKeywordEffect(subject="this", keywords=["flying"])
        RemoveKeywordEffect(subject="creatures_you_control", keywords=["trample", "vigilance"])
    """

    subject: str
    keywords: List[str]

    # Layer 6: Ability adding/removing
    layering: str = "layer_6"

    # Applies only on battlefield unless overridden
    zones: Optional[List[str]] = None

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        objects = resolver.resolve(self.subject, source, controller)

        affected_ids = []

        for obj in objects:
            if not hasattr(obj, "keywords"):
                continue

            for kw in self.keywords:
                if kw in obj.keywords:
                    obj.keywords.remove(kw)

            affected_ids.append(getattr(obj, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "keyword_removed",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "keywords": list(self.keywords),
                "objects": affected_ids,
            })

        return True
