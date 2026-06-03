# axis3/engine/abilities/effects/reveal.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class RevealEffect(ContinuousEffect):
    """
    Axis3 effect: Reveal one or more cards to all players.

    Examples:
        RevealEffect(subject="this_card")
        RevealEffect(subject="cards_in_your_hand")
        RevealEffect(subject="top_card_of_your_library")
    """

    subject: str
    zones: Optional[List[str]] = None

    # Revealing is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        cards = resolver.resolve(self.subject, source, controller)

        revealed_ids = []

        for card in cards:
            # Mark card as revealed for UI purposes
            setattr(card, "revealed", True)
            revealed_ids.append(getattr(card, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "cards_revealed",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "objects": revealed_ids,
            })

        return True
