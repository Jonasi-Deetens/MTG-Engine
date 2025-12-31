# axis2/parsing/activated.py

import re
from axis1.schema import Axis1Face
from axis2.schema import ActivatedAbility, ParseContext
from axis2.parsing.costs import parse_cost_string
from axis2.parsing.effects import parse_effect_text
from axis2.parsing.targeting import parse_targeting

def strip_parenthetical(text: str) -> str:
    out = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(depth - 1, 0)
        elif depth == 0:
            out.append(ch)
    return "".join(out)

ABILITY_SPLIT_RE = re.compile(r"^(.*?):\s*(.*)$")

def split_full_ability(text: str):
    """
    Splits "COST: EFFECT" into ("COST", "EFFECT").
    """
    m = ABILITY_SPLIT_RE.match(text)
    if not m:
        return None, None
    return m.group(1).strip(), m.group(2).strip()


def parse_activated_abilities(axis1_face: Axis1Face, ctx: ParseContext) -> list[ActivatedAbility]:
    """
    Modern, clean activated-ability parser.

    Axis1Face.activated_abilities contains objects with:
        - cost (raw string)
        - effect (raw string)
        - text (fallback)
        - cost_parts (legacy)
    """

    activated = []
    print(f"Activated abilities: {axis1_face.activated_abilities}")

    for a in getattr(axis1_face, "activated_abilities", []):
        raw_cost = getattr(a, "cost", "") or ""
        raw_effect = getattr(a, "effect", "") or ""
        raw_text = getattr(a, "text", "") or ""
        raw_effect = strip_parenthetical(raw_effect)
        # ------------------------------------------------------------
        # 1. Parse costs using the new multi-part cost parser
        # ------------------------------------------------------------
        costs = []
        if raw_cost:
            costs = parse_cost_string(raw_cost)

        # ------------------------------------------------------------
        # 2. Parse effects
        # ------------------------------------------------------------
        effects = parse_effect_text(raw_effect, ctx)
        targeting = parse_targeting(raw_effect)

        # ------------------------------------------------------------
        # 3. Fallback: Axis1 failed to split cost/effect
        # ------------------------------------------------------------
        if (not costs and not effects) and raw_text:
            cost_text, effect_text = split_full_ability(raw_text)
            effect_text = strip_parenthetical(effect_text)

            if cost_text:
                costs = parse_cost_string(cost_text)

            if effect_text:
                effects = parse_effect_text(effect_text, ctx)
                targeting = parse_targeting(effect_text)

        # ------------------------------------------------------------
        # 4. Build the ActivatedAbility
        # ------------------------------------------------------------
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
