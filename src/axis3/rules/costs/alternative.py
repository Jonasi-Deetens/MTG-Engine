# axis3/rules/costs/alternative.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

from axis3.rules.events.event import Event
from axis3.rules.events.types import EventType
from axis3.state.zones import ZoneType as Zone


@dataclass
class AlternativeCost:
    """
    Represents an alternative cost for a spell or ability.
    """
    description: str
    pay_func: Callable[[GameState, int, bool], bool]

    def can_pay(self, game_state, player_id) -> bool:
        """
        Check if the alternative cost can be paid.
        """
        return self.pay_func(game_state, player_id, check_only=True)

    def pay(self, game_state, player_id):
        """
        Execute the alternative cost.
        """
        ok = self.pay_func(game_state, player_id, check_only=False)
        if not ok:
            raise RuntimeError(f"Failed to pay alternative cost: {self.description}")


def discard_card_cost(game_state, player_id, check_only=False) -> bool:
    """
    Discard a card as an alternative cost.
    """
    ps = game_state.players[player_id]

    if not ps.hand:
        return False

    if not check_only:
        discarded = ps.hand[-1]  # or choose via UI later

        game_state.event_bus.publish(Event(
            type=EventType.ZONE_CHANGE,
            payload={
                "obj_id": discarded,
                "from_zone": Zone.HAND,
                "to_zone": Zone.GRAVEYARD,
                "controller": player_id,
                "cause": "alternative_cost_discard",
            }
        ))

    return True


discard_cost = AlternativeCost(
    description="Discard a card instead of paying mana",
    pay_func=discard_card_cost
)
