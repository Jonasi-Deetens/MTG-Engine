# axis2/parsing/static_effects.py

import re
from axis2.schema import StaticEffect, DayboundEffect, NightboundEffect
from axis2.helpers import cleaned_oracle_text

NUMBER_WORDS = {
    "zero": 0,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}

def parse_static_effects(axis1_face):
    """
    Combine Axis1 static effects (if any) with Axis2-detected static effects
    like Daybound/Nightbound and blocking restrictions.
    """
    effects = []

    # ------------------------------------------------------------
    # 1. Axis1-provided static effects
    # ------------------------------------------------------------
    raw_effects = getattr(axis1_face, "static_effects", [])
    for raw in raw_effects:
        effects.append(
            StaticEffect(
                kind=raw["kind"],
                subject=raw["subject"],
                value=raw["value"],
                layer=raw["layering"],
                zones=raw["zones"],
            )
        )

    # ------------------------------------------------------------
    # 2. Axis2-detected static effects from oracle text
    # ------------------------------------------------------------
    text = cleaned_oracle_text(axis1_face)

    # Daybound / Nightbound
    if "daybound" in text:
        effects.append(DayboundEffect())

    if "nightbound" in text:
        effects.append(NightboundEffect())

    # Blocking restriction
    blocking = parse_blocking_restriction(text)
    if blocking:
        effects.append(blocking)

    # Crew power bonus
    crew_power = parse_crew_power_bonus(text)
    if crew_power:
        effects.append(crew_power)

    # Grant haste
    haste = parse_grant_haste(text)
    if haste:
        effects.append(haste)

    # Play with the top card of their libraries revealed
    top_reveal = parse_top_reveal(text)
    if top_reveal:
        effects.append(top_reveal)

    # Noninstant, nonsorcery cards on top of a library are on the battlefield
    zone_addition = parse_zone_addition(text)
    if zone_addition:
        effects.append(zone_addition)

    return effects

BLOCKING_RESTRICTION_RE = re.compile(
    r"each creature you control can\s*'?t?\s*be blocked by more than (\w+)",
    re.IGNORECASE
)

def parse_blocking_restriction(text: str):
    m = BLOCKING_RESTRICTION_RE.search(text)
    if not m:
        return None

    raw = m.group(1).strip().lower()
    token = raw.split()[0]  # handle "one creature", "1 creature"

    if token.isdigit():
        max_blockers = int(token)
    elif token in NUMBER_WORDS:
        max_blockers = NUMBER_WORDS[token]
    else:
        return None

    return StaticEffect(
        kind="blocking_restriction",
        subject="your_creatures",
        value={"max_blockers": max_blockers},
        layer="rules",
        zones=["battlefield"]
    )

CREW_POWER_RE = re.compile(
    r"crews vehicles as though its power were (\w+) greater",
    re.IGNORECASE
)

def parse_crew_power_bonus(text: str):
    m = CREW_POWER_RE.search(text)
    if not m:
        return None

    raw = m.group(1).lower()

    if raw.isdigit():
        bonus = int(raw)
    else:
        bonus = NUMBER_WORDS.get(raw)
        if bonus is None:
            return None

    return StaticEffect(
        kind="as_though",
        subject="this_creature",
        value={
            "action": "crew",
            "parameter": "power",
            "modifier": bonus
        },
        layer="rules",
        zones=["battlefield"]
    )

HASTE_GRANT_RE = re.compile(
    r"all creatures have haste",
    re.IGNORECASE
)

def parse_grant_haste(text):
    if HASTE_GRANT_RE.search(text):
        return StaticEffect(
            kind="grant_keyword",
            subject="all_creatures",
            value={"keyword": "haste"},
            layer="abilities",
            zones=["battlefield"]
        )
    return None

TOP_REVEAL_RE = re.compile(
    r"play with the top card of their libraries revealed",
    re.IGNORECASE
)

def parse_top_reveal(text):
    if TOP_REVEAL_RE.search(text):
        return StaticEffect(
            kind="as_though",
            subject="players",
            value={
                "action": "reveal",
                "parameter": "top_of_library",
                "state": True
            },
            layer="rules",
            zones=["library"]
        )
    return None

ZONE_ADD_RE = re.compile(
    r"noninstant, nonsorcery cards on top of a library are on the battlefield",
    re.IGNORECASE
)

def parse_zone_addition(text):
    if ZONE_ADD_RE.search(text):
        return StaticEffect(
            kind="zone_addition",
            subject="top_of_library_noninstant_nonsorcery",
            value={"additional_zone": "battlefield"},
            layer="rules",
            zones=["library"]
        )
    return None
