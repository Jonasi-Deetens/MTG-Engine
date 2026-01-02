# axis2/parsing/static_effects.py

import re
from axis2.schema import StaticEffect, DayboundEffect, NightboundEffect, Subject, ParseContext
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

def parse_static_effects(axis1_face, ctx: ParseContext):
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

    # ------------------------------------------------------------ 
    # 3. General static effects (NEW) 
    # ------------------------------------------------------------ 
    ctx = ParseContext( 
        card_name=axis1_face.name, 
        primary_type=axis1_face.card_types[0].lower(), 
        face_name=axis1_face.name, 
        face_types=[t.lower() for t in axis1_face.card_types], 
    ) 
    effects.extend(parse_general_static_effects(text, ctx))

    return effects

def parse_general_static_effects(text: str, ctx: ParseContext) -> list[StaticEffect]:
    effects = []
    t = text.lower()

    # ------------------------------------------------------------
    # 1. "You may cast spells as though they had flash."
    # ------------------------------------------------------------
    if "as though they had flash" in t or "as though it had flash" in t:
        effects.append(
            StaticEffect(
                kind="timing_override",
                subject=Subject(
                    scope="self",
                    controller="you",
                    types=["spell"],
                    filters={}
                ),
                value={"as_flash": True},
                layer="rules",
                zones=["hand", "stack"],
            )
        )

    # ------------------------------------------------------------
    # 2. General cost modification ("artifact spells you cast cost {1} less")
    # ------------------------------------------------------------
    cost_mod = parse_cost_modification(text, ctx)
    if cost_mod:
        effects.append(cost_mod)

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
        subject=Subject( 
            scope="each", 
            controller="you", 
            types=["creature"] 
        ),
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
        subject=Subject(scope="self"),
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
            subject=Subject(
                scope="each",
                types=["creature"]
            ),
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
            subject=Subject(
                scope="each",
                types=["player"]
            ),
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
            subject=Subject(
                scope="each",
                types=["card"],
                filters={
                    "location": "top_of_library",
                    "noninstant": True,
                    "nonsorcery": True
                }
            ),
            value={"additional_zone": "battlefield"},
            layer="rules",
            zones=["library"]
        )
    return None

COST_MOD_RE = re.compile(
    r"(?P<types>[a-zA-Z ,]+?) spells? (?P<controller>you|your opponents?|opponents?) cast cost \{(?P<amount>\d+)\} (?P<direction>less|more) to cast",
    re.IGNORECASE
)

def parse_cost_modification(text: str, ctx: ParseContext):
    m = COST_MOD_RE.search(text)
    if not m:
        return None

    raw_types = m.group("types").strip()
    controller_word = m.group("controller")
    amount = int(m.group("amount"))
    direction = m.group("direction")

    # Determine controller
    controller = "you" if "you" in controller_word else "opponent"

    # Determine sign
    delta = -amount if direction == "less" else amount

    # Parse types (artifact, creature, instant and sorcery, etc.)
    types = []
    for part in re.split(r",|and", raw_types):
        p = part.strip()
        if p in ["artifact", "creature", "enchantment", "planeswalker", "instant", "sorcery", "noncreature"]:
            types.append(p)
        elif p == "instant and sorcery":
            types.extend(["instant", "sorcery"])
        elif p == "noncreature":
            types.append("noncreature")

    # Build subject
    subject = Subject(
        scope="each",
        controller=controller,
        types=types + ["spell"],  # always spells
        filters={}
    )

    return StaticEffect(
        kind="cost_modification",
        subject=subject,
        value={"generic": delta},
        layer="cost_modification",
        zones=None
    )
