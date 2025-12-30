# axis2/parsing/activated.py

import re

from axis1.schema import Axis1Face
from axis2.schema import ActivatedAbility, ManaCost, DiscardCost
from axis2.parsing.costs import parse_cost, parse_tap_cost, parse_discard_cost, parse_sacrifice_cost
from axis2.parsing.effects import parse_effect_text
from axis2.parsing.targeting import parse_targeting

def parse_activated_abilities(axis1_face: Axis1Face) -> list[ActivatedAbility]:
    activated = []

    for a in getattr(axis1_face, "activated_abilities", []):
        costs = [parse_cost(c) for c in getattr(a, "cost_parts", [])]

        tap_cost = parse_tap_cost(getattr(a, "cost", None))
        if tap_cost:
            costs.append(tap_cost)

        sacrifice_cost = parse_sacrifice_cost(getattr(a, "cost", "") or getattr(a, "text", ""))
        if sacrifice_cost:
            costs.append(sacrifice_cost)

        # Mana cost inside {}
        mana_symbols = re.findall(r"\{[^}]+\}", getattr(a, "cost", "") or getattr(a, "text", ""))
        if mana_symbols:
            costs.append(ManaCost(symbols=mana_symbols))

        discard_cost = parse_discard_cost(getattr(a, "cost", "") or getattr(a, "text", ""))
        if discard_cost:
            costs.append(discard_cost)

        effects = parse_effect_text(getattr(a, "effect", ""))
        targeting = parse_targeting(getattr(a, "effect", ""))

        # Fallback: Axis1 failed to split cost/effect
        cost_text, effect_text = None, None
        if (not costs and not effects) and hasattr(a, "text"):
            cost_text, effect_text = split_full_ability(getattr(a, "text", ""))

        if cost_text:
            # Mana cost inside {}
            mana_symbols = re.findall(r"\{[^}]+\}", cost_text)
            if mana_symbols:
                costs.append(ManaCost(symbols=mana_symbols))

            # Discard cost
            discard_cost = parse_discard_cost(cost_text)
            if discard_cost:
                costs.append(discard_cost)

            # Parse effects
            effects = parse_effect_text(effect_text)
            targeting = parse_targeting(effect_text)

        activated.append(
            ActivatedAbility(
                costs=costs,
                effects=effects,
                conditions=getattr(a, "activation_conditions", None),
                targeting=targeting,
                timing="instant",
            )
        )

    return activated


ABILITY_SPLIT_RE = re.compile(r"^(.*?):\s*(.*)$")

def split_full_ability(text: str):
    m = ABILITY_SPLIT_RE.match(text)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()
