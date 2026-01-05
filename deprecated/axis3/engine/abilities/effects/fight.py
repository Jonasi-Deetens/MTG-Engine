# axis3/engine/abilities/effects/fight.py

from dataclasses import dataclass
from typing import Optional, List

from axis3.effects.base import ContinuousEffect


@dataclass
class FightEffect(ContinuousEffect):
    """
    Axis3 effect: Two creatures fight (each deals damage equal to its power to the other).

    Examples:
        FightEffect(subject="target_creature", opponent_subject="creature_opponent_controls")
        FightEffect(subject="this", opponent_subject="target_creature")
    """

    subject: str
    opponent_subject: str
    zones: Optional[List[str]] = None

    # Fight is a one-shot effect
    layering: str = "resolution"

    def apply(self, game_state, source, controller):
        resolver = game_state.subject_resolver

        # Resolve both sides
        fighters = resolver.resolve(self.subject, source, controller)
        opponents = resolver.resolve(self.opponent_subject, source, controller)

        if not fighters or not opponents:
            return True  # Nothing to fight

        # Fight is always 1 vs 1 in MTG rules
        a = fighters[0]
        b = opponents[0]

        # Ensure both are creatures with power/toughness
        if not hasattr(a, "power") or not hasattr(b, "power"):
            return True

        # Damage assignment
        a_damage = getattr(b, "power", 0)
        b_damage = getattr(a, "power", 0)

        # Apply damage
        if hasattr(a, "damage"):
            a.damage += a_damage
        if hasattr(b, "damage"):
            b.damage += b_damage

        # Optional UI event
        if hasattr(game_state, "event_bus"):
            game_state.event_bus.publish({
                "type": "creatures_fought",
                "source": source,
                "controller": controller,
                "subject": self.subject,
                "opponent_subject": self.opponent_subject,
                "fighter_id": getattr(a, "id", None),
                "opponent_id": getattr(b, "id", None),
                "damage_to_fighter": a_damage,
                "damage_to_opponent": b_damage,
            })

        return True
