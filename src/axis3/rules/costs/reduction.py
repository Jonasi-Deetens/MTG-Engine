# axis3/rules/costs/reduction.py

from axis3.rules.costs.mana import ManaCost

class CostReduction:
    """
    Represents a static or temporary cost reduction.
    Example: "Spells you cast cost {1} less"
    """
    def __init__(self, description: str, amount: int = 0, condition=None):
        """
        - description: textual description
        - amount: generic mana reduction
        - condition: function(game_state, player_id, spell) -> bool
        """
        self.description = description
        self.amount = amount
        self.condition = condition or (lambda gs, pid, spell: True)

    def apply(self, game_state, player_id, spell_cost: ManaCost):
        if self.condition(game_state, player_id, spell_cost):
            spell_cost.colorless = max(0, spell_cost.colorless - self.amount)
        return spell_cost
