# axis2/parsing/replacement_effects.py

import re
from typing import List, Optional
from axis2.schema import ReplacementEffect

# Regex patterns
AS_ENTERS_RE = re.compile(r"as this .* enters", re.IGNORECASE)
DIES_RE = re.compile(r"if .* would die", re.IGNORECASE)
DRAW_RE = re.compile(r"if .* would draw", re.IGNORECASE)
DAMAGE_RE = re.compile(r"if .* damage would be dealt", re.IGNORECASE)
ENTER_TAPPED_RE = re.compile(r"enter the battlefield tapped", re.IGNORECASE)
PUT_INTO_GRAVEYARD_RE = re.compile(r"would be put into a graveyard", re.IGNORECASE)


def parse_replacement_effects(text: str) -> List[ReplacementEffect]:
    effects = []
    if not text:
        return effects

    lower = text.lower()

    # -----------------------------
    # 1. As-enters replacement
    # -----------------------------
    if AS_ENTERS_RE.search(lower):
        effects.append(
            ReplacementEffect(
                kind="as_enters",
                text=text,
                applies_to="this_permanent"
            )
        )
        return effects

    # -----------------------------
    # 2. Dies → exile / return / instead
    # -----------------------------
    if DIES_RE.search(lower):
        if "exile" in lower:
            effects.append(
                ReplacementEffect(
                    kind="dies_to_exile",
                    text=text,
                    applies_to="creature",
                    new_action="exile"
                )
            )
        elif "return" in lower:
            effects.append(
                ReplacementEffect(
                    kind="dies_to_return",
                    text=text,
                    applies_to="creature",
                    new_action="return_to_hand"
                )
            )
        else:
            effects.append(
                ReplacementEffect(
                    kind="dies_replacement",
                    text=text,
                    applies_to="creature"
                )
            )
        return effects

    # -----------------------------
    # 3. Draw replacement
    # -----------------------------
    if DRAW_RE.search(lower):
        # detect "draw two instead"
        m = re.search(r"draw (\w+) instead", lower)
        amount = m.group(1) if m else None

        effects.append(
            ReplacementEffect(
                kind="draw_instead",
                text=text,
                applies_to="you",
                amount=amount,
                new_action="draw_extra"
            )
        )
        return effects

    # -----------------------------
    # 4. Damage prevention
    # -----------------------------
    if DAMAGE_RE.search(lower):
        if "prevent" in lower:
            # detect "prevent the next N damage"
            m = re.search(r"prevent the next (\w+)", lower)
            amount = m.group(1) if m else "all"

            effects.append(
                ReplacementEffect(
                    kind="prevent_damage",
                    text=text,
                    applies_to="target_or_self",
                    amount=amount,
                    new_action="prevent"
                )
            )
            return effects

        if "instead" in lower:
            effects.append(
                ReplacementEffect(
                    kind="redirect_damage",
                    text=text,
                    applies_to="target_or_self",
                    new_action="redirect"
                )
            )
            return effects

    # -----------------------------
    # 5. ETB modifications
    # -----------------------------
    if ENTER_TAPPED_RE.search(lower):
        effects.append(
            ReplacementEffect(
                kind="enter_tapped",
                text=text,
                applies_to="creature"
            )
        )
        return effects

    # -----------------------------
    # 6. Graveyard → exile
    # -----------------------------
    if PUT_INTO_GRAVEYARD_RE.search(lower) and "exile" in lower:
        effects.append(
            ReplacementEffect(
                kind="zone_change_to_exile",
                text=text,
                applies_to="card"
            )
        )
        return effects

    # -----------------------------
    # 7. No match
    # -----------------------------
    return []
