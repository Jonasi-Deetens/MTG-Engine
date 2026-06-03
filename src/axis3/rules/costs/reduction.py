# axis3/rules/costs/reduction.py

from __future__ import annotations
from dataclasses import dataclass
from axis3.engine.abilities.costs.mana import ManaCost


@dataclass
class CostReduction:
    """
    Represents a static or temporary cost reduction.
    Example: "Spells you cast cost {1} less"
    """
    description: str
    amount: int = 0
    condition: callable = lambda gs, pid, spell: True

    def apply(self, game_state, player_id, spell, original_cost: ManaCost) -> ManaCost:
        """
        Returns a NEW ManaCost with the reduction applied.
        Does not mutate the original cost.
        """
        # If the reduction does not apply, return the original cost unchanged
        if not self.condition(game_state, player_id, spell):
            return original_cost

        # Create a new cost object
        new_cost = ManaCost(
            colorless=original_cost.colorless,
            colored=dict(original_cost.colored)
        )

        # Apply generic reduction
        new_cost.colorless = max(0, new_cost.colorless - self.amount)

        return new_cost
