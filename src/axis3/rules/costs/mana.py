# axis3/rules/costs/mana.py

from __future__ import annotations
import re

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType


class ManaCost:
    """
    Represents a generic mana cost (colorless + colored).
    Example: {2}{G}{G} -> {colorless:2, 'G':2}
    """
    def __init__(self, colorless: int = 0, colored: dict = None):
        self.colorless = colorless
        self.colored = colored or {}

    def total(self):
        return self.colorless + sum(self.colored.values())

    def can_pay(self, player) -> bool:
        """
        Check if the player's mana pool can pay this cost.
        """
        # Check colored mana
        for color, amount in self.colored.items():
            if player.mana_pool.get(color, 0) < amount:
                return False

        # Check generic mana after colored is accounted for
        remaining_pool = sum(player.mana_pool.values()) - sum(self.colored.values())
        return remaining_pool >= self.colorless

    def pay(self, game_state, player):
        """
        Deduct mana from player's pool using the event bus.
        """
        if not self.can_pay(player):
            raise ValueError("Player cannot pay mana cost")

        # 1️⃣ Pay colored mana
        for color, amount in self.colored.items():
            player.mana_pool[color] -= amount

            game_state.event_bus.publish(Event(
                type=EventType.MANA_SPENT,
                payload={
                    "player_id": player.id,
                    "color": color,
                    "amount": amount,
                    "cause": "mana_cost"
                }
            ))

        # 2️⃣ Pay generic mana (deterministic order)
        generic_needed = self.colorless
        if generic_needed > 0:
            for color in sorted(player.mana_pool.keys()):
                available = player.mana_pool[color]
                if available <= 0:
                    continue

                take = min(available, generic_needed)
                if take > 0:
                    player.mana_pool[color] -= take
                    generic_needed -= take

                    game_state.event_bus.publish(Event(
                        type=EventType.MANA_SPENT,
                        payload={
                            "player_id": player.id,
                            "color": color,
                            "amount": take,
                            "cause": "mana_cost"
                        }
                    ))

                if generic_needed <= 0:
                    break

MANA_SYMBOL = re.compile(r"\{([^}]+)\}")


def parse_mana_cost(raw_cost: str) -> ManaCost:
    """
    Axis3 mana cost parser.
    Converts "{1}{G}{G}" → ManaCost(colorless=1, colored={"G": 2})
    """
    if not raw_cost:
        return ManaCost()

    symbols = MANA_SYMBOL.findall(raw_cost)

    colorless = 0
    colored = {}

    for sym in symbols:
        # Numeric cost
        if sym.isdigit():
            colorless += int(sym)
        # Colored cost
        else:
            colored[sym] = colored.get(sym, 0) + 1

    return ManaCost(colorless=colorless, colored=colored)
