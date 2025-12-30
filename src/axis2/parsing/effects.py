# axis2/parsing/effects.py

import re
from axis2.schema import (
    DealDamageEffect, DrawCardsEffect, AddManaEffect,
    PutOntoBattlefieldEffect, SymbolicValue, 
    PutCounterEffect, CounterSpellEffect, CreateTokenEffect, EquipEffect, 
    GainLifeEffect, SearchEffect, CantBeBlockedEffect
)

COLOR_MAP = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}

SENTENCE_SPLIT_RE = re.compile(r"\.\s+")

def split_effect_sentences(text: str):
    """
    Splits effect text into sentences.
    Example:
      'Counter that spell. That player creates X tokens.'
    -> ['Counter that spell', 'That player creates X tokens']
    """
    text = text.strip()
    if not text:
        return []

    # Remove trailing period if present
    if text.endswith("."):
        text = text[:-1]

    parts = SENTENCE_SPLIT_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def parse_effect_text(text):
    """
    Convert raw English effect text into semantic Effect objects.
    Now supports multi-sentence effects.
    """
    effects = []
    if not text:
        return effects

    # ------------------------------------------------------------
    # 1. Split into sentences
    # ------------------------------------------------------------
    sentences = split_effect_sentences(text)


    search = parse_search_effect(text)
    if search:
        effects.append(search)
    # ------------------------------------------------------------
    # 2. Parse each sentence independently
    # ------------------------------------------------------------
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue

        # Detect Equip keyword ability
        if s.strip().lower().startswith("equip"):
            effects.append(EquipEffect())
            continue


        # 2a. Put onto battlefield
        put = parse_put_onto_battlefield(s)
        if put:
            effects.append(put)
            continue

        # 2b. +1/+1 counters
        counter = parse_put_counter(s)
        if counter:
            effects.append(counter)
            continue

        # Counter spell
        counter_spell = parse_counter_spell(s)
        if counter_spell:
            effects.append(counter_spell)
            continue

        # Create tokens
        token_eff = parse_create_token(s)
        if token_eff:
            effects.append(token_eff)
            continue

        # Cant be blocked
        cant_be_blocked = parse_cant_be_blocked(s)
        if cant_be_blocked:
            effects.append(cant_be_blocked)
            continue

        # 2c. Damage
        if "deals" in s.lower() and "damage" in s.lower():
            words = s.lower().split()
            m = re.search(r"deals\s+(\w+)\s+damage", s, re.I)
            amount = m.group(1)
            if "player or planeswalker" in s.lower():
                subject = "player_or_planeswalker"
            elif "target player" in s.lower():
                subject = "player"
            elif "target creature" in s.lower():
                subject = "creature"
            elif "any target" in s.lower():
                subject = "any_target"

            effects.append(DealDamageEffect(amount=amount, subject=subject))
            continue

        # 2d. Draw cards
        if "draw" in s.lower() and "card" in s.lower():
            words = s.lower().split()
            amount = 1
            for w in words:
                if w.isdigit():
                    amount = int(w)
                    break
            effects.append(DrawCardsEffect(amount=amount))
            continue

        # 2e. Add mana
        if "add" in s.lower() and "{" in s:
            mana = []
            buf = ""
            inside = False
            for ch in s:
                if ch == "{":
                    inside = True
                    buf = "{"
                elif ch == "}":
                    inside = False
                    buf += "}"
                    mana.append(buf)
                    buf = ""
                elif inside:
                    buf += ch
            effects.append(AddManaEffect(mana=mana))
            continue

        # --------------------------------------------------------
        # 2f. Gain life
        # --------------------------------------------------------

        if "gains" in s.lower() and "life" in s.lower():
            m = re.search(r"gains\s+(\w+)\s+life", s, re.I)
            amount = m.group(1)
            effects.append(GainLifeEffect(amount=amount, subject="player"))
            continue


    return effects


# ------------------------------------------------------------
# PUT ONTO BATTLEFIELD PARSER
# ------------------------------------------------------------

PUT_RE = re.compile(
    r"put (?:an|a) ([^ ]+) card .*?from your hand onto the battlefield",
    re.IGNORECASE
)

MV_CONSTRAINT_RE = re.compile(
    r"mana value (?:less than or equal to|<=) (.+?)(?= from| onto| card|$)",
    re.IGNORECASE
)

def parse_put_onto_battlefield(text: str):
    """
    Parses effects like:
      'you may put an artifact card with mana value less than or equal to that damage
       from your hand onto the battlefield'
    """
    m = PUT_RE.search(text)
    if not m:
        return None

    card_type = m.group(1).capitalize()

    # Optionality
    optional = "you may" in text.lower()

    # Constraint
    constraint = None
    mv = MV_CONSTRAINT_RE.search(text)
    if mv:
        raw = mv.group(1).strip()
        constraint = {
            "mana_value_lte": SymbolicValue(
                kind="variable",
                expression=raw
            )
        }

    return PutOntoBattlefieldEffect(
        zone_from="hand",
        card_filter={"types": [card_type]},
        tapped=False,
        attacking=False,
        constraint=constraint,
        optional=optional,
    )

COUNTER_RE = re.compile(
    r"put (?:a|an) \+1/\+1 counter on target ([a-zA-Z ]+)",
    re.IGNORECASE
)

def parse_put_counter(text: str):
    m = COUNTER_RE.search(text)
    if not m:
        return None

    return PutCounterEffect(
        counter_type="+1/+1",
        amount=1
    )

COUNTER_SPELL_RE = re.compile(
    r"counter that spell",
    re.IGNORECASE
)

def parse_counter_spell(text: str):
    """
    Parses effects like:
      'Counter that spell.'
    """
    if COUNTER_SPELL_RE.search(text):
        return CounterSpellEffect(target="that_spell")
    return None
GENERAL_TOKEN_RE = re.compile(
    r"create (\w+) (\d+)/(\d+) ([a-z ]+?) creature tokens? with ([a-z ,]+)",
    re.IGNORECASE
)

SIMPLE_TOKEN_RE = re.compile(
    r"create (\w+) ([a-z ]+?) tokens?",
    re.IGNORECASE
)

NUMBER_WORDS = {
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

def parse_amount(word: str):
    word = word.lower()
    if word.isdigit():
        return int(word)
    if word in NUMBER_WORDS:
        return NUMBER_WORDS[word]
    if word == "x":
        return SymbolicValue(kind="variable", expression="X")
    return 1  # fallback

def parse_create_token(text: str):
    t = text.lower()

    # ------------------------------------------------------------
    # Pattern 1: Full creature token with stats
    # ------------------------------------------------------------
    m = GENERAL_TOKEN_RE.search(t)
    if m:
        amount_word = m.group(1)
        power = int(m.group(2))
        toughness = int(m.group(3))
        raw_types = m.group(4).strip()
        raw_abilities = m.group(5).strip()

        amount = parse_amount(amount_word)

        # Parse colors and types
        colors = []
        types = []
        subtypes = []
        color_words = ["white", "blue", "black", "red", "green"]
        special_words = ["colorless"]  # don't convert this to a subtype

        parts = raw_types.split()
        for p in parts:
            if p in color_words:
                colors.append(COLOR_MAP[p])
            elif p == "artifact":
                types.append("Artifact")
            elif p == "creature":
                types.append("Creature")
            elif p in special_words:
                # ignore "colorless" for now; colors=[] already encodes it
                continue
            else:
                subtypes.append(p.capitalize())


        # Parse abilities
        abilities = [a.strip().capitalize() for a in raw_abilities.split(",")]

        return CreateTokenEffect(
            amount=amount,
            token={
                "name": None,
                "power": power,
                "toughness": toughness,
                "colors": colors,
                "types": types,
                "subtypes": subtypes,
                "abilities": abilities,
            },
            controller="you",
        )

    # ------------------------------------------------------------
    # Pattern 2: Simple tokens (Treasure, Food, Clue)
    # ------------------------------------------------------------
    m = SIMPLE_TOKEN_RE.search(t)
    if m:
        amount_word = m.group(1)
        token_name = m.group(2).strip().capitalize()

        amount = parse_amount(amount_word)

        return CreateTokenEffect(
            amount=amount,
            token={
                "name": token_name,
                "power": None,
                "toughness": None,
                "colors": [],
                "types": ["Artifact"],
                "subtypes": [token_name],
                "abilities": [],
            },
            controller="you",
        )

    return None


SEARCH_RE = re.compile(
    r"you may search your ([a-z ,/and]+) for a card named ([A-Za-z ]+?)"
    r"(?: and/or a card named ([A-Za-z ]+?))?"
    r"(?= and put| and put them| and put it| and put onto|$)",
    re.IGNORECASE
)

def parse_search_effect(text: str):
    m = SEARCH_RE.search(text)
    if not m:
        return None

    zones_raw = m.group(1)
    name1 = m.group(2).strip()
    name2 = m.group(3).strip() if m.group(3) else None

    zones = []
    if "graveyard" in zones_raw:
        zones.append("graveyard")
    if "hand" in zones_raw:
        zones.append("hand")
    if "library" in zones_raw:
        zones.append("library")

    card_names = [name1]
    if name2:
        card_names.append(name2)

    return SearchEffect(
        zones=zones,
        card_names=card_names,
        optional=True,
        put_onto_battlefield="put" in text.lower(),
        shuffle_if_library_searched="shuffle" in text.lower()
    )

CANT_BE_BLOCKED_RE = re.compile(
    r"target creature can'?t be blocked",
    re.IGNORECASE
)

def parse_cant_be_blocked(text: str):
    if CANT_BE_BLOCKED_RE.search(text):
        return CantBeBlockedEffect(
            subject="target_creature",
            duration="until_end_of_turn"
        )
    return None
