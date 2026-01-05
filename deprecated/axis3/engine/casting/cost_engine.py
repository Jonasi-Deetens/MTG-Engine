# axis3/engine/casting/cost_engine.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Dict

from axis3.engine.casting.context import CastContext
from axis3.state.registries import (
    AlternativeCostRegistry,
    CostReductionRegistry,
)


@dataclass
class CostEngine:
    """
    Handles all cost computation for casting spells.

    This engine is fully mechanic-agnostic:
      - Flashback registers an alternative cost + reduction rule
      - Escape registers an alternative cost + exile requirement
      - Kicker registers additional costs
      - Convoke registers cost reductions
      - Affinity registers cost reductions
      - Improvise registers cost reductions
      - Delve registers cost reductions

    The CostEngine simply interprets the registries.
    """

    alt_costs: AlternativeCostRegistry
    reductions: CostReductionRegistry

    # ============================================================
    # PUBLIC API
    # ============================================================

    def build_cost_options(self, ctx: CastContext, game_state: Any) -> List[Dict[str, Any]]:
        """
        Build a list of possible cost options for the player to choose from.
        Each option is a dict containing:
          - "tag": None or alternative cost tag
          - "cost": mana cost string
        """

        obj = game_state.get_object(ctx.source_id)
        if obj is None:
            ctx.set_illegal("Object not found")
            return []

        base_cost = obj.mana_cost  # e.g. "{4}{W}"

        options = [{"tag": None, "cost": base_cost}]

        # Add alternative costs (flashback, escape, overload, prototype…)
        for alt in self.alt_costs.get(ctx.source_id):
            options.append({"tag": alt.tag, "cost": alt.cost})

        return options

    def choose_cost(self, ctx: CastContext, game_state: Any, choice_tag: Optional[str]):
        """
        The player (or UI) chooses which cost to pay.
        choice_tag = None means base cost.
        """

        options = self.build_cost_options(ctx, game_state)

        for opt in options:
            if opt["tag"] == choice_tag:
                ctx.set_chosen_cost(opt["cost"])
                if choice_tag is not None:
                    ctx.mark_alt_cost_used(choice_tag)
                return

        ctx.set_illegal(f"Invalid cost choice: {choice_tag}")

    def apply_reductions(self, ctx: CastContext, game_state: Any):
        """
        Apply all cost reductions that apply to this cast.
        """

        if ctx.chosen_cost is None:
            ctx.set_illegal("No cost chosen")
            return

        # Convert mana cost string to a structured representation
        cost = self._parse_mana_cost(ctx.chosen_cost)

        for rule in self.reductions.get(ctx.source_id):
            if rule.applies_if(ctx):
                amount = rule.amount_fn(game_state, ctx.controller)
                ctx.add_reduction(rule.tag, amount)
                cost = self._reduce_cost(cost, amount)

        # Convert back to mana string
        ctx.set_chosen_cost(self._format_mana_cost(cost))

    def pay_cost(self, ctx: CastContext, game_state: Any) -> bool:
        """
        Pay the final mana cost from the player's mana pool.
        Additional costs (sacrifice, discard, exile) are handled elsewhere.
        """

        if ctx.chosen_cost is None:
            ctx.set_illegal("No cost chosen")
            return False

        cost = self._parse_mana_cost(ctx.chosen_cost)
        player = game_state.players[ctx.controller]

        # Check if player has enough mana
        for symbol, amount in cost.items():
            if player.mana_pool.get(symbol, 0) < amount:
                ctx.set_illegal("Not enough mana")
                return False

        # Deduct mana
        for symbol, amount in cost.items():
            player.mana_pool[symbol] -= amount

        return True

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    def _parse_mana_cost(self, cost_str: str) -> Dict[str, int]:
        """
        Convert a mana string like "{4}{W}{W}" into a dict:
          {"generic": 4, "W": 2}
        """

        import re
        parts = re.findall(r"\{([^}]+)\}", cost_str)
        cost = {"generic": 0}

        for p in parts:
            if p.isdigit():
                cost["generic"] += int(p)
            else:
                cost[p] = cost.get(p, 0) + 1

        return cost

    def _reduce_cost(self, cost: Dict[str, int], amount: int) -> Dict[str, int]:
        """
        Reduce generic mana first.
        """

        if amount <= 0:
            return cost

        # Reduce generic mana
        if cost["generic"] >= amount:
            cost["generic"] -= amount
            return cost

        # If reduction exceeds generic, reduce colored mana (rare but possible)
        remaining = amount - cost["generic"]
        cost["generic"] = 0

        for symbol in list(cost.keys()):
            if symbol == "generic":
                continue
            if remaining <= 0:
                break
            if cost[symbol] > 0:
                cost[symbol] -= 1
                remaining -= 1

        return cost

    def _format_mana_cost(self, cost: Dict[str, int]) -> str:
        """
        Convert a cost dict back into a mana string.
        """

        parts = []

        if cost["generic"] > 0:
            parts.append(f"{{{cost['generic']}}}")

        for symbol, amount in cost.items():
            if symbol == "generic":
                continue
            for _ in range(amount):
                parts.append(f"{{{symbol}}}")

        return "".join(parts)
