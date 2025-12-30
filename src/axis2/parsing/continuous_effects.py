import re
from typing import List, Optional

from axis2.schema import (
    ContinuousEffect, PTExpression,
    ColorChangeData, TypeChangeData
)

# -----------------------------
# Regex patterns
# -----------------------------

PT_GETS_RE = re.compile(r"gets\s+([+\-]?\w+)\/([+\-]?\w+)", re.IGNORECASE)
HAS_ABILITY_RE = re.compile(r"has\s+(.+)", re.IGNORECASE)
GAINS_ABILITY_RE = re.compile(r"gains?\s+(.+)", re.IGNORECASE)
IS_COLOR_RE = re.compile(r"is\s+([a-z\s,]+)", re.IGNORECASE)
IS_TYPE_RE = re.compile(r"is\s+(a\s+)?([a-z\s]+)", re.IGNORECASE)
AS_LONG_AS_RE = re.compile(r"as long as (.+?),", re.IGNORECASE)

COLOR_WORD_TO_SYMBOL = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}

ABILITY_KEYWORDS = {
    "flying", "first strike", "double strike", "vigilance", "lifelink",
    "trample", "deathtouch", "haste", "reach", "menace", "hexproof",
    "indestructible", "ward"
}

# -----------------------------
# Helpers
# -----------------------------

def _guess_applies_to(text: str) -> str:
    lower = text.lower()
    if lower.startswith("equipped creature"):
        return "equipped_creature"
    if lower.startswith("enchanted creature"):
        return "enchanted_creature"
    if lower.startswith("creatures you control"):
        return "creatures_you_control"
    if lower.startswith("creature you control"):
        return "creature_you_control"
    if lower.startswith("creatures you don't control"):
        return "creatures_you_dont_control"
    if lower.startswith("this creature"):
        return "this_creature"
    if lower.startswith("this permanent"):
        return "this_permanent"
    return "unknown"


def _parse_pt_mod(text: str) -> Optional[PTExpression]:
    m = PT_GETS_RE.search(text)
    if not m:
        return None
    p = m.group(1).lstrip("+")
    t = m.group(2).lstrip("+")
    return PTExpression(power=p, toughness=t)


def _parse_abilities(text: str) -> Optional[list[str]]:
    lower = text.lower()
    if "has " in lower:
        ability_part = HAS_ABILITY_RE.search(lower).group(1)
    elif "gains " in lower or "gain " in lower:
        ability_part = GAINS_ABILITY_RE.search(lower).group(1)
    else:
        return None

    # Split on "and" or commas
    ability_part = ability_part.replace(", and ", ", ")
    ability_part = ability_part.replace(" and ", ", ")
    raw = [a.strip() for a in ability_part.split(",")]

    abilities = []
    for a in raw:
        a = a.rstrip(".")
        if a.startswith("ward"):
            abilities.append("ward")
        elif a in ABILITY_KEYWORDS:
            abilities.append(a)
    return abilities or None


def _parse_color_change(text: str) -> Optional[ColorChangeData]:
    lower = text.lower()

    if "is all colors" in lower:
        return ColorChangeData(set_colors=["W", "U", "B", "R", "G"])

    m = IS_COLOR_RE.search(lower)
    if not m:
        return None

    words = m.group(1).replace(",", " ").split()
    colors = [COLOR_WORD_TO_SYMBOL[w] for w in words if w in COLOR_WORD_TO_SYMBOL]
    if not colors:
        return None

    if "in addition to its other colors" in lower:
        return ColorChangeData(add_colors=colors)
    return ColorChangeData(set_colors=colors)


def _parse_type_change(text: str) -> Optional[TypeChangeData]:
    lower = text.lower()
    if "is a" not in lower and "is an" not in lower:
        return None

    # crude but effective: extract words after "is a"
    after = lower.split("is a", 1)[1].strip()
    after = after.rstrip(".")
    words = after.split()

    # filter out known types
    types = [w for w in words if w in {"creature", "artifact", "enchantment", "land", "planeswalker"}]
    subtypes = [w for w in words if w not in types]

    if not types and not subtypes:
        return None

    return TypeChangeData(set_types=types + subtypes)


# -----------------------------
# Main parser
# -----------------------------

def parse_continuous_effects(text: str) -> List[ContinuousEffect]:
    effects = []
    if not text:
        return effects

    applies_to = _guess_applies_to(text)

    # 1. Conditional wrapper
    condition = None
    m = AS_LONG_AS_RE.search(text)
    if m:
        condition = m.group(1).strip()
        # remove the condition prefix from the text
        text = text[m.end():].strip()

    # 2. P/T modification
    pt = _parse_pt_mod(text)
    if pt:
        effects.append(
            ContinuousEffect(
                kind="pt_mod",
                applies_to=applies_to,
                pt_value=pt,
                condition=condition,
                text=text,
            )
        )

    # 3. Ability granting
    abilities = _parse_abilities(text)
    if abilities:
        effects.append(
            ContinuousEffect(
                kind="grant_ability",
                applies_to=applies_to,
                abilities=abilities,
                condition=condition,
                text=text,
            )
        )

    # 4. Color change
    color_change = _parse_color_change(text)
    if color_change:
        effects.append(
            ContinuousEffect(
                kind="color_set" if color_change.set_colors else "color_add",
                applies_to=applies_to,
                color_change=color_change,
                condition=condition,
                text=text,
            )
        )   

    # 5. Type change
    type_change = _parse_type_change(text)
    if type_change:
        effects.append(
            ContinuousEffect(
                kind="type_set",
                applies_to=applies_to,
                type_change=type_change,
                condition=condition,
                text=text,
            )
        )

    # 6. Fallback: unknown continuous effect

    return effects