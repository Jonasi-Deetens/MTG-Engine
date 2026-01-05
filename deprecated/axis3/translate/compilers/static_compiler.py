# axis3/compilers/static_compiler.py

import re
from typing import Optional

from axis3.effects.base import StaticEffect


def compile_static_effect(identifier: str) -> Optional[StaticEffect]:
    """
    Convert a static-effect identifier (string) into a real layered StaticEffect object.
    """

    ident = identifier.lower().strip()

    # ------------------------------------------------------------
    # 1. P/T modifiers
    #    pt_modifier_creatures_you_control_1_1
    # ------------------------------------------------------------
    m = re.match(r"pt_modifier_(other_)?creatures_you_control_(-?\d+)_(-?\d+)", ident)
    if m:
        other = bool(m.group(1))
        power = int(m.group(2))
        toughness = int(m.group(3))

        subject = "other_creatures_you_control" if other else "creatures_you_control"

        return StaticEffect(
            kind="buff",
            subject=subject,
            value={"power": power, "toughness": toughness},
            layering="layer_7c",
            zones=["battlefield"]
        )

    # ------------------------------------------------------------
    # 2. Opponent debuffs
    #    pt_modifier_creatures_opponents_control_-1_-1
    # ------------------------------------------------------------
    m = re.match(r"pt_modifier_creatures_opponents_control_(-?\d+)_(-?\d+)", ident)
    if m:
        power = int(m.group(1))
        toughness = int(m.group(2))

        return StaticEffect(
            kind="buff",
            subject="creatures_opponents_control",
            value={"power": power, "toughness": toughness},
            layering="layer_7c",
            zones=["battlefield"]
        )

    # ------------------------------------------------------------
    # 3. Cost reductions by color
    #    cost_reduction_color_blue_{1}
    # ------------------------------------------------------------
    m = re.match(r"cost_reduction_color_(\w+)_(\{[^\}]+\})", ident)
    if m:
        color = m.group(1)
        amount = m.group(2)

        return StaticEffect(
            kind="cost_reduction",
            subject=f"{color}_spells_you_cast",
            value={"amount": amount},
            layering="layer_7b",
            zones=["battlefield"]
        )

    # ------------------------------------------------------------
    # 4. Type-based cost reductions
    #    cost_reduction_type_creature_{1}
    # ------------------------------------------------------------
    m = re.match(r"cost_reduction_type_(\w+)_(\{[^\}]+\})", ident)
    if m:
        stype = m.group(1)
        amount = m.group(2)

        return StaticEffect(
            kind="cost_reduction",
            subject=f"{stype}_spells_you_cast",
            value={"amount": amount},
            layering="layer_7b",
            zones=["battlefield"]
        )

    # ------------------------------------------------------------
    # 5. Tribal cost reductions
    #    cost_reduction_tribal_elf_{1}
    # ------------------------------------------------------------
    m = re.match(r"cost_reduction_tribal_(\w+)_(\{[^\}]+\})", ident)
    if m:
        tribe = m.group(1)
        amount = m.group(2)

        return StaticEffect(
            kind="cost_reduction",
            subject=f"{tribe}_spells_you_cast",
            value={"amount": amount},
            layering="layer_7b",
            zones=["battlefield"]
        )

    # ------------------------------------------------------------
    # 6. Opponent spell tax
    #    opponent_spells_cost_more_{1}
    # ------------------------------------------------------------
    m = re.match(r"opponent_spells_cost_more_(\{[^\}]+\})", ident)
    if m:
        amount = m.group(1)

        return StaticEffect(
            kind="cost_increase",
            subject="spells_opponents_cast",
            value={"amount": amount},
            layering="layer_7b",
            zones=["battlefield"]
        )

    # ------------------------------------------------------------
    # 7. Life gain prevention
    # ------------------------------------------------------------
    if ident == "opponents_cannot_gain_life":
        return StaticEffect(
            kind="restriction",
            subject="opponents",
            value={"cannot_gain_life": True},
            layering="layer_7b",
            zones=["battlefield"]
        )

    if ident == "players_cannot_gain_life":
        return StaticEffect(
            kind="restriction",
            subject="players",
            value={"cannot_gain_life": True},
            layering="layer_7b",
            zones=["battlefield"]
        )

    # ------------------------------------------------------------
    # Unknown identifier
    # ------------------------------------------------------------
    return None
