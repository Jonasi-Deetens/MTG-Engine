# axis3/engine/abilities/effects/add_keyword.py

from dataclasses import dataclass
from typing import List, Optional

from axis3.effects.base import ContinuousEffect


@dataclass
class AddKeywordEffect(ContinuousEffect):
    subject: str
    keywords: List[str]

    layering: str = "layer_6"
    zones: Optional[List[str]] = None

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        objects = resolver.resolve(self.subject, source, controller)

        for obj in objects:
            if not hasattr(obj, "keywords"):
                obj.keywords = set()

            for kw in self.keywords:
                obj.keywords.add(kw)

        # Optional event emission
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "keyword_added",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "keywords": list(self.keywords),
                "objects": [getattr(obj, "id", None) for obj in objects],
            })

        return True
