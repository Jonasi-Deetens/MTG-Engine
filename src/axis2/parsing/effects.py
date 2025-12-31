# axis2/parsing/effects.py

import re
from axis2.schema import (
    DealDamageEffect, DrawCardsEffect, AddManaEffect,
    PutOntoBattlefieldEffect, SymbolicValue, 
    PutCounterEffect, CounterSpellEffect, CreateTokenEffect, EquipEffect, 
    GainLifeEffect, SearchEffect, CantBeBlockedEffect, GainLifeEqualToPowerEffect, 
    ReturnCardFromGraveyardEffect, DraftFromSpellbookEffect, PTBoostEffect,
    ChangeZoneEffect, ScryEffect, SurveilEffect, Subject
)
from axis2.parsing.subject import parse_subject
from axis2.parsing.spell_continuous_effects import parse_spell_continuous_effect

COLOR_MAP = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}

SENTENCE_SPLIT_RE = re.compile(r"\.\s+")

def _subject_from_text(raw: str) -> Subject:
    t = raw.lower().strip()

    # Linked exiled card (Oblivion Ring, Banishing Light, etc.)
    if "the exiled card" in t:
        return Subject(
            scope="linked_exiled_card",
            controller=None,
            types=None,
            filters={"source": "self"}
        )

    # Another target nonland permanent
    if "another" in t or "target" in t:
        return Subject(
            scope="target",
            controller=None,
            types=["permanent"],
            filters={"nonland": True, "not_self": "self"}
        )

    # Fallback: treat as a generic target
    return Subject(
        scope="target",
        controller=None,
        types=None,
        filters={"raw": raw}
    )


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

        print(f"Parsing effect: {s}")

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

        # Return card from graveyard
        ret = parse_return_card(s)
        if ret:
            effects.append(ret)
            continue

        # Gain life equal to that card's power
        gle = parse_gain_life_equal(s)
        if gle:
            effects.append(gle)
            continue

        # Draft a card from a spellbook
        spellbook = parse_spellbook_effect(s)
        if spellbook:
            effects.append(spellbook)
            continue

        print(f"Parsing spell continuous effect: {s}")
        # Spell continuous effect
        spell_continuous = parse_spell_continuous_effect(s)
        if spell_continuous:
            effects.append(spell_continuous)
            continue

        # PT boost
        pt_boost = parse_pt_boost(s)
        if pt_boost:
            effects.append(pt_boost)
            continue

        # Move to zone
        change_zone = parse_change_zone(s)
        if change_zone:
            effects.append(change_zone)
            continue

        # Scry
        scry = parse_scry(s)
        if scry:
            effects.append(scry)
            continue

        # Surveil
        surveil = parse_surveil(s)
        if surveil:
            effects.append(surveil)
            continue


        # 2c. Damage
        if "deals" in s.lower() and "damage" in s.lower():
            words = s.lower().split()
            m = re.search(r"deals\s+(\w+)\s+damage", s, re.I)
            amount = m.group(1)
            subject = parse_subject(s.lower())

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
    r"counter (target )?spell",
    re.IGNORECASE
)

def parse_counter_spell(text: str):
    """
    Parses effects like:
      'Counter that spell.'
    """
    if COUNTER_SPELL_RE.search(text):
        return CounterSpellEffect(target="target_spell")
    return None

GENERAL_TOKEN_RE = re.compile(
    r"create (\w+) (\d+)/(\d+) ([a-z ]+? creature) tokens? with ([a-z ,]+)",
    re.IGNORECASE
)

SIMPLE_TOKEN_RE = re.compile(
    r"create (\w+) ([a-z ]+? creature) tokens?",
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

RETURN_CARD_RE = re.compile(
    r"return (?:up to )?target ([a-z ]+?) card from (?:your|an opponent's|a|their) graveyard to (?:your|its owner's|their) ([a-z ]+)",
    re.IGNORECASE
)

GAIN_LIFE_EQUAL_RE = re.compile(
    r"gain life equal to (?:that|its) card'?s ([a-z ]+)",
    re.IGNORECASE
)

def parse_return_card(s: str):
    m = RETURN_CARD_RE.search(s)
    if not m:
        return None

    subtype = m.group(1).strip()
    dest_zone = m.group(2).strip()

    # normalize destination zone
    zone_map = {
        "hand": "hand",
        "battlefield": "battlefield",
        "battlefield tapped": "battlefield_tapped",
        "command zone": "command_zone",
    }
    dest_zone = zone_map.get(dest_zone, dest_zone)

    return ReturnCardFromGraveyardEffect(
        subtype=subtype,
        controller="you",      # still correct for this card
        destination_zone=dest_zone
    )

def parse_gain_life_equal(s: str):
    m = GAIN_LIFE_EQUAL_RE.search(s)
    if not m:
        return None

    stat = m.group(1).strip().lower()

    # Normalize common stat names
    stat_map = {
        "power": "power",
        "toughness": "toughness",
        "mana value": "mana_value",
        "converted mana cost": "mana_value",
        "cmc": "mana_value",
    }
    stat = stat_map.get(stat, stat)

    return GainLifeEqualToPowerEffect(
        source="that_card",
        stat=stat
    )

SPELLBOOK_RE = re.compile(
    r"draft a card from ([a-zA-Z ]+)'s spellbook",
    re.IGNORECASE
)

def parse_spellbook_effect(text: str):
    m = SPELLBOOK_RE.search(text)
    if not m:
        return None
    return DraftFromSpellbookEffect(source=m.group(1).strip())

PT_BOOST_RE = re.compile(
    r"target creature gets \+(\d+)/\+(\d+) until end of turn",
    re.IGNORECASE
)

def parse_pt_boost(text: str):
    m = PT_BOOST_RE.search(text)
    if not m:
        return None
    return PTBoostEffect(
        power=int(m.group(1)),
        toughness=int(m.group(2)),
        duration="until_end_of_turn"
    )

RETURN_HAND_RE = re.compile(
    r"return\s+(.+?)\s+to\s+(?:its|their|his|her|that|the)?\s*owner'?s hand",
    re.IGNORECASE
)
GRAVEYARD_RE = re.compile(
    r"put\s+(.+?)\s+into\s+(?:its|their|your|his|her)?\s*owner'?s?\s*graveyard",
    re.IGNORECASE
)

LIBRARY_RE = re.compile(
    r"put\s+(.+?)\s+on\s+(top|the bottom)\s+of\s+(?:its|their|your)?\s*owner'?s library",
    re.IGNORECASE
)

EXILE_RE = re.compile(
    r"exile\s+(.+?)\b",
    re.IGNORECASE
)

RETURN_BATTLEFIELD_RE = re.compile(
    r"return\s+(.+?)\s+to\s+the battlefield",
    re.IGNORECASE
)

ONTO_BATTLEFIELD_RE = re.compile(
    r"put\s+(.+?)\s+onto\s+the battlefield",
    re.IGNORECASE
)


def parse_change_zone(text: str):
    # return to hand
    m = RETURN_HAND_RE.search(text)
    if m:
        return ChangeZoneEffect(
            subject=_subject_from_text(m.group(1).strip()),
            to_zone="hand"
        )

    # graveyard
    m = GRAVEYARD_RE.search(text)
    if m:
        return ChangeZoneEffect(
            subject=_subject_from_text(m.group(1).strip()),
            to_zone="graveyard"
        )

    # library (top/bottom)
    m = LIBRARY_RE.search(text)
    if m:
        return ChangeZoneEffect(
            subject=_subject_from_text(m.group(1).strip()),
            to_zone="library",
            position=m.group(2).strip()
        )

    # exile
    m = EXILE_RE.search(text)
    if m:
        return ChangeZoneEffect(
            subject=_subject_from_text(m.group(1).strip()),
            to_zone="exile"
        )

    # return to battlefield
    m = RETURN_BATTLEFIELD_RE.search(text)
    if m:
        return ChangeZoneEffect(
            subject=_subject_from_text(m.group(1).strip()),
            to_zone="battlefield"
        )

    # put onto battlefield
    m = ONTO_BATTLEFIELD_RE.search(text)
    if m:
        return ChangeZoneEffect(
            subject=_subject_from_text(m.group(1).strip()),
            to_zone="battlefield"
        )

    return None

SCRY_RE = re.compile(r"\bscry\s+(\d+)\b", re.IGNORECASE)
def parse_scry(text: str):
    m = SCRY_RE.search(text)
    if not m:
        return None
    return ScryEffect(amount=int(m.group(1)))

SURVEIL_RE = re.compile(r"\bsurveil\s+(\d+)\b", re.IGNORECASE)
def parse_surveil(text: str):
    m = SURVEIL_RE.search(text)
    if not m:
        return None
    return SurveilEffect(amount=int(m.group(1)))