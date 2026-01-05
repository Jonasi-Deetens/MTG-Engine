# axis3/engine/abilities/effects/damage.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class DealDamageEffect(ContinuousEffect):
    """
    Axis3 effect: Deal damage to one or more objects or players.

    Examples:
        DealDamageEffect(amount=3, subject="target_creature")
        DealDamageEffect(amount=2, subject="opponent")
        DealDamageEffect(amount=1, subject="all_creatures")
    """

    amount: int
    subject: str
    zones: Optional[List[str]] = None

    # Damage is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver
        targets = resolver.resolve(self.subject, source, controller)

        damaged_ids = []

        for target in targets:
            # Damage to permanents
            if hasattr(target, "damage"):
                target.damage += self.amount

            # Damage to players
            elif hasattr(target, "life"):
                target.life -= self.amount

            damaged_ids.append(getattr(target, "id", None))

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "damage_dealt",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "amount": self.amount,
                "targets": damaged_ids,
            })

        return True
