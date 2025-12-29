# axis3/compilers/replacement_compiler.py

import re
from typing import Optional

from axis3.effects.base import ReplacementEffect
from axis3.engine.abilities.effects.exile import ExileEffect
from axis3.engine.abilities.effects.tap import TapEffect
from axis3.engine.abilities.effects.draw import DrawCardEffect
from axis3.engine.abilities.effects.damage import DealDamageEffect


def compile_replacement_effect(identifier: str) -> Optional[ReplacementEffect]:
    """
    Convert a replacement-effect identifier (string) into a real ReplacementEffect object.
    """

    ident = identifier.lower().strip()

    # ------------------------------------------------------------
    # 1. Dies → exile instead
    # ------------------------------------------------------------
    if ident == "dies_exile_instead":
        return ReplacementEffect(
            event="dies",
            replace_with=ExileEffect(),
            condition=None
        )

    # ------------------------------------------------------------
    # 2. Enter tapped
    # ------------------------------------------------------------
    if ident == "enter_tapped":
        return ReplacementEffect(
            event="enter_battlefield",
            replace_with=TapEffect(),
            condition=None
        )

    # ------------------------------------------------------------
    # 3. Draw replacement
    #    "If you would draw a card, draw two instead."
    # ------------------------------------------------------------
    if ident == "draw_replacement":
        return ReplacementEffect(
            event="draw",
            replace_with=DrawCardEffect(count=2),
            condition=None
        )

    # ------------------------------------------------------------
    # 4. Damage replacement
    #    "If a source would deal damage..."
    # ------------------------------------------------------------
    if ident == "damage_replacement":
        # Example: double damage
        return ReplacementEffect(
            event="deal_damage",
            replace_with=DealDamageEffect(amount=2, target="same"),
            condition=None
        )

    # ------------------------------------------------------------
    # Unknown identifier
    # ------------------------------------------------------------
    return None
