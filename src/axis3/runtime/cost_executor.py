from __future__ import annotations

from typing import Any, List

from axis2 import schema as a2


class CostExecutor:
    """Pay Axis2 costs for activated abilities and spells."""

    def __init__(self, game_state: Any):
        self.game_state = game_state

    def can_pay(self, costs: List[Any], source_id: str, controller: int) -> bool:
        for cost in costs or []:
            if not self._can_pay_one(cost, source_id, controller):
                return False
        return True

    def pay(self, costs: List[Any], source_id: str, controller: int) -> bool:
        if not self.can_pay(costs, source_id, controller):
            return False
        for cost in costs or []:
            if not self._pay_one(cost, source_id, controller):
                return False
        return True

    def _can_pay_one(self, cost: Any, source_id: str, controller: int) -> bool:
        if isinstance(cost, a2.TapCost):
            obj = self.game_state.get_object(source_id)
            return obj is not None and not obj.tapped
        if isinstance(cost, a2.ManaCost):
            return self._can_pay_mana(cost, controller)
        if isinstance(cost, a2.SacrificeCost):
            return True
        if isinstance(cost, a2.DiscardCost):
            player = self.game_state.players[controller]
            return len(player.hand) >= cost.amount
        if isinstance(cost, a2.LoyaltyCost):
            obj = self.game_state.get_object(source_id)
            if not obj or not obj.counters:
                return False
            return obj.counters.get("loyalty", 0) >= abs(cost.amount)
        return True

    def _pay_one(self, cost: Any, source_id: str, controller: int) -> bool:
        if isinstance(cost, a2.TapCost):
            obj = self.game_state.get_object(source_id)
            if not obj or obj.tapped:
                return False
            obj.tapped = True
            return True
        if isinstance(cost, a2.ManaCost):
            return self._pay_mana(cost, controller)
        if isinstance(cost, a2.SacrificeCost):
            obj = self.game_state.get_object(source_id)
            if obj:
                self.game_state.move_card(source_id, "GRAVEYARD", controller=controller)
            return True
        if isinstance(cost, a2.DiscardCost):
            player = self.game_state.players[controller]
            for _ in range(cost.amount):
                if not player.hand:
                    return False
                cid = player.hand.pop()
                self.game_state.zone_list(controller, "GRAVEYARD").append(cid)
                o = self.game_state.get_object(cid)
                if o:
                    from axis3.state.zones import ZoneType
                    o.zone = ZoneType.GRAVEYARD
            return True
        if isinstance(cost, a2.LoyaltyCost):
            obj = self.game_state.get_object(source_id)
            if obj:
                obj.counters["loyalty"] = obj.counters.get("loyalty", 0) + cost.amount
            return True
        return True

    def _can_pay_mana(self, cost: a2.ManaCost, controller: int) -> bool:
        pool = self.game_state.players[controller].mana_pool
        needed = self._parse_mana_symbols(cost.symbols)
        for color, n in needed.items():
            if pool.get(color, 0) < n:
                return False
        return True

    def _pay_mana(self, cost: a2.ManaCost, controller: int) -> bool:
        if not self._can_pay_mana(cost, controller):
            return False
        pool = self.game_state.players[controller].mana_pool
        needed = self._parse_mana_symbols(cost.symbols)
        for color, n in needed.items():
            pool[color] = pool.get(color, 0) - n
        return True

    def _parse_mana_symbols(self, symbols: List[str]) -> dict:
        counts = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "C": 0}
        for sym in symbols:
            s = sym.strip("{}").upper()
            if s in counts:
                counts[s] += 1
            elif s.isdigit():
                counts["C"] += int(s)
            elif s in ("X", "Y", "Z"):
                x = getattr(self.game_state, "chosen_x", 0) or 0
                counts["C"] += x
        return counts
