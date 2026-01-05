# axis3/engine/abilities/effects/return_from_graveyard.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class ReturnFromGYEffect(ContinuousEffect):
    """
    Axis3 effect: Return one or more cards from a graveyard to the battlefield.

    Examples:
        ReturnFromGraveyardEffect(subject="target_creature_in_your_graveyard")
        ReturnFromGraveyardEffect(subject="creature_card_in_opponent_graveyard")
        ReturnFromGraveyardEffect(subject="this_card")
    """

    subject: str
    zones: Optional[List[str]] = None

    # Returning from graveyard is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver

        # Resolve cards in graveyards
        cards = resolver.resolve(self.subject, source, controller)

        returned_ids = []

        for card in list(cards):
            owner = getattr(card, "owner", None)
            if owner is None:
                continue

            # Ensure graveyard exists
            graveyard = game_state.graveyards.get(owner, [])

            # Remove from graveyard if present
            if card in graveyard:
                graveyard.remove(card)

            # Put onto battlefield under controller's control
            card.controller = controller
            game_state.battlefield.append(card)

            returned_ids.append(getattr(card, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "returned_from_graveyard",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "objects": returned_ids,
            })

        return True
