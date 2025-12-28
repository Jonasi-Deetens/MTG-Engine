# axis3/rules/costs/mana.py

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType

class ManaCost:
    """
    Represents a generic mana cost (colorless + colored).
    Example: {2}{G}{G} -> {colorless:2, 'G':2}
    """
    def __init__(self, colorless: int = 0, colored: dict = None):
        self.colorless = colorless
        self.colored = colored or {}  # e.g., {'G':2, 'U':1}

    def total(self):
        return self.colorless + sum(self.colored.values())

    def can_pay(self, player):
        """
        Check if the player's mana pool can pay this cost.
        """
        # Check colored mana
        for color, amount in self.colored.items():
            if player.mana_pool.get(color, 0) < amount:
                return False

        # Check generic mana
        generic_available = sum(player.mana_pool.values())
        if generic_available < self.colorless + sum(self.colored.values()):
            return False

        return True

    def pay(self, player):
        """
        Deduct mana from player's pool.
        """
        if not self.can_pay(player):
            raise ValueError("Player cannot pay mana cost")

        # Pay colored first
        for color, amount in self.colored.items():
            player.mana_pool[color] -= amount

        # Pay generic (any color)
        generic_needed = self.colorless
        if generic_needed > 0:
            # Use any available mana
            for color, available in player.mana_pool.items():
                take = min(available, generic_needed)
                player.mana_pool[color] -= take
                generic_needed -= take
                if generic_needed <= 0:
                    break
