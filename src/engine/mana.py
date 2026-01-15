from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from .state import GameObject, GameState

MANA_SYMBOL_PATTERN = re.compile(r"\{([^}]+)\}")
MANA_COLORS = {"W", "U", "B", "R", "G"}


@dataclass
class ManaCost:
    generic: int = 0
    colored: Dict[str, int] = None
    hybrids: List[Tuple[str, str]] = None
    two_brids: List[Tuple[int, str]] = None
    phyrexian: List[str] = None
    colorless: int = 0
    x_value: int = 0

    def __post_init__(self) -> None:
        self.colored = self.colored or {}
        self.hybrids = self.hybrids or []
        self.two_brids = self.two_brids or []
        self.phyrexian = self.phyrexian or []


def mana_cost_snapshot(cost: ManaCost) -> Dict[str, Any]:
    return {
        "generic": cost.generic,
        "colored": dict(cost.colored),
        "hybrids": list(cost.hybrids),
        "two_brids": list(cost.two_brids),
        "phyrexian": list(cost.phyrexian),
        "colorless": cost.colorless,
        "x_value": cost.x_value,
    }


def parse_mana_cost(cost: Optional[str], x_value: int = 0) -> ManaCost:
    result = ManaCost(x_value=x_value)
    if not cost:
        return result

    symbols = MANA_SYMBOL_PATTERN.findall(cost)
    for symbol in symbols:
        symbol = symbol.upper()
        if symbol.isdigit():
            result.generic += int(symbol)
            continue
        if symbol == "X":
            result.generic += x_value
            continue
        if symbol == "C":
            result.colorless += 1
            continue
        if symbol in MANA_COLORS:
            result.colored[symbol] = result.colored.get(symbol, 0) + 1
            continue
        if "/" in symbol:
            parts = symbol.split("/")
            if len(parts) == 2 and parts[1] == "P":
                result.phyrexian.append(parts[0])
                continue
            if len(parts) == 2 and parts[0].isdigit() and parts[1] in MANA_COLORS:
                result.two_brids.append((int(parts[0]), parts[1]))
                continue
            if len(parts) == 2 and parts[0] in MANA_COLORS and parts[1] in MANA_COLORS:
                result.hybrids.append((parts[0], parts[1]))
                continue
        if symbol == "S":
            result.colorless += 1
            continue

    return result


def can_pay_cost(mana_pool: Dict[str, int], cost: ManaCost) -> bool:
    available = dict(mana_pool)
    for color, amount in cost.colored.items():
        if available.get(color, 0) < amount:
            return False
        available[color] -= amount
    for _ in cost.hybrids:
        if not any(available.get(color, 0) > 0 for color in cost.hybrids[0]):
            return False
    for hybrid in cost.hybrids:
        if available.get(hybrid[0], 0) > 0:
            available[hybrid[0]] -= 1
        elif available.get(hybrid[1], 0) > 0:
            available[hybrid[1]] -= 1
        else:
            return False
    for two_brid in cost.two_brids:
        if available.get(two_brid[1], 0) > 0:
            available[two_brid[1]] -= 1
        else:
            cost.generic += two_brid[0]
    if available.get("C", 0) < cost.colorless:
        return False
    available["C"] = available.get("C", 0) - cost.colorless
    available_generic = sum(available.values())
    return available_generic >= cost.generic


def pay_cost(game_state: GameState, player_id: int, cost: ManaCost) -> None:
    player = game_state.get_player(player_id)
    pool = player.mana_pool

    for color, amount in cost.colored.items():
        if pool.get(color, 0) < amount:
            raise ValueError("Not enough mana to pay cost.")
        pool[color] -= amount

    for hybrid in cost.hybrids:
        if pool.get(hybrid[0], 0) > 0:
            pool[hybrid[0]] -= 1
        elif pool.get(hybrid[1], 0) > 0:
            pool[hybrid[1]] -= 1
        else:
            raise ValueError("Not enough mana to pay hybrid cost.")

    for two_brid in cost.two_brids:
        if pool.get(two_brid[1], 0) > 0:
            pool[two_brid[1]] -= 1
        else:
            cost.generic += two_brid[0]

    for phyrexian in cost.phyrexian:
        if pool.get(phyrexian, 0) > 0:
            pool[phyrexian] -= 1
        else:
            player.life -= 2

    if pool.get("C", 0) < cost.colorless:
        raise ValueError("Not enough colorless mana.")
    pool["C"] = pool.get("C", 0) - cost.colorless

    generic_needed = cost.generic
    for color in list(pool.keys()):
        if generic_needed <= 0:
            break
        available = pool.get(color, 0)
        if available <= 0:
            continue
        spend = min(available, generic_needed)
        pool[color] -= spend
        generic_needed -= spend
    if generic_needed > 0:
        raise ValueError("Not enough mana to pay generic cost.")


def can_pay_cost_with_payment(
    mana_pool: Dict[str, int],
    cost: ManaCost,
    payment: Dict[str, int],
    payment_detail: Optional[Dict[str, Any]] = None,
) -> bool:
    if (cost.hybrids or cost.two_brids or cost.phyrexian) and not payment_detail:
        return False
    if any(amount < 0 for amount in payment.values()):
        return False
    for color, amount in payment.items():
        if mana_pool.get(color, 0) < amount:
            return False
    if payment_detail:
        return _can_pay_with_detail(mana_pool, cost, payment_detail)
    return _can_pay_simple(mana_pool, cost, payment)


def _can_pay_simple(mana_pool: Dict[str, int], cost: ManaCost, payment: Dict[str, int]) -> bool:
    for color, amount in cost.colored.items():
        if payment.get(color, 0) < amount:
            return False
    if payment.get("C", 0) < cost.colorless:
        return False
    total_paid = sum(payment.values())
    total_required = cost.generic + cost.colorless + sum(cost.colored.values())
    return total_paid >= total_required


def _can_pay_with_detail(
    mana_pool: Dict[str, int],
    cost: ManaCost,
    payment_detail: Dict[str, Any],
) -> bool:
    pool = dict(mana_pool)
    generic_required = cost.generic
    hybrid_choices = payment_detail.get("hybrid_choices", [])
    two_brid_choices = payment_detail.get("two_brid_choices", [])
    phyrexian_choices = payment_detail.get("phyrexian_choices", [])

    if len(hybrid_choices) != len(cost.hybrids):
        return False
    if len(two_brid_choices) != len(cost.two_brids):
        return False
    if len(phyrexian_choices) != len(cost.phyrexian):
        return False

    for color, amount in cost.colored.items():
        if pool.get(color, 0) < amount:
            return False
        pool[color] -= amount

    for choice, (color_a, color_b) in zip(hybrid_choices, cost.hybrids):
        if choice not in (color_a, color_b):
            return False
        if pool.get(choice, 0) <= 0:
            return False
        pool[choice] -= 1

    for choice, (generic_value, color) in zip(two_brid_choices, cost.two_brids):
        if choice:
            if pool.get(color, 0) <= 0:
                return False
            pool[color] -= 1
        else:
            generic_required += generic_value

    for pay_life, color in zip(phyrexian_choices, cost.phyrexian):
        if pay_life:
            continue
        if pool.get(color, 0) <= 0:
            return False
        pool[color] -= 1

    if pool.get("C", 0) < cost.colorless:
        return False
    pool["C"] = pool.get("C", 0) - cost.colorless
    available_generic = sum(pool.values())
    return available_generic >= generic_required


def pay_cost_with_payment(
    game_state: GameState,
    player_id: int,
    cost: ManaCost,
    payment: Dict[str, int],
    payment_detail: Optional[Dict[str, Any]] = None,
) -> None:
    if not can_pay_cost_with_payment(game_state.get_player(player_id).mana_pool, cost, payment, payment_detail):
        raise ValueError("Invalid mana payment.")
    pool = game_state.get_player(player_id).mana_pool
    if payment_detail:
        _pay_with_detail(game_state, player_id, cost, payment_detail)
        return
    for color, amount in payment.items():
        pool[color] = pool.get(color, 0) - amount


def _pay_with_detail(
    game_state: GameState,
    player_id: int,
    cost: ManaCost,
    payment_detail: Dict[str, Any],
) -> None:
    player = game_state.get_player(player_id)
    pool = player.mana_pool
    generic_required = cost.generic
    hybrid_choices = payment_detail.get("hybrid_choices", [])
    two_brid_choices = payment_detail.get("two_brid_choices", [])
    phyrexian_choices = payment_detail.get("phyrexian_choices", [])

    if len(hybrid_choices) != len(cost.hybrids):
        raise ValueError("Invalid hybrid choices.")
    if len(two_brid_choices) != len(cost.two_brids):
        raise ValueError("Invalid two-brid choices.")
    if len(phyrexian_choices) != len(cost.phyrexian):
        raise ValueError("Invalid phyrexian choices.")

    for color, amount in cost.colored.items():
        if pool.get(color, 0) < amount:
            raise ValueError("Not enough mana to pay cost.")
        pool[color] -= amount

    for choice, (color_a, color_b) in zip(hybrid_choices, cost.hybrids):
        if choice not in (color_a, color_b):
            raise ValueError("Invalid hybrid choice.")
        if pool.get(choice, 0) <= 0:
            raise ValueError("Not enough mana for hybrid cost.")
        pool[choice] -= 1

    for choice, (generic_value, color) in zip(two_brid_choices, cost.two_brids):
        if choice:
            if pool.get(color, 0) <= 0:
                raise ValueError("Not enough mana for two-brid cost.")
            pool[color] -= 1
        else:
            generic_required += generic_value

    for pay_life, color in zip(phyrexian_choices, cost.phyrexian):
        if pay_life:
            player.life -= 2
        else:
            if pool.get(color, 0) <= 0:
                raise ValueError("Not enough mana for phyrexian cost.")
            pool[color] -= 1

    if pool.get("C", 0) < cost.colorless:
        raise ValueError("Not enough colorless mana.")
    pool["C"] = pool.get("C", 0) - cost.colorless
    generic_needed = generic_required
    for color in list(pool.keys()):
        if generic_needed <= 0:
            break
        available = pool.get(color, 0)
        if available <= 0:
            continue
        spend = min(available, generic_needed)
        pool[color] -= spend
        generic_needed -= spend
    if generic_needed > 0:
        raise ValueError("Not enough mana to pay generic cost.")


def produce_mana_for_object(game_state: GameState, obj: GameObject) -> Dict[str, int]:
    if "Land" not in obj.types:
        raise ValueError("Only lands may activate default mana abilities.")

    land_types = {"Plains": "W", "Island": "U", "Swamp": "B", "Mountain": "R", "Forest": "G"}
    for land_type, mana in land_types.items():
        if land_type in (obj.type_line or "") or land_type in obj.name:
            return {mana: 1}

    if obj.oracle_text:
        symbols = MANA_SYMBOL_PATTERN.findall(obj.oracle_text)
        mana: Dict[str, int] = {}
        for symbol in symbols:
            symbol = symbol.upper()
            if symbol in MANA_COLORS or symbol == "C":
                mana[symbol] = mana.get(symbol, 0) + 1
        if mana:
            return mana

    raise ValueError("No mana ability available for this permanent.")


