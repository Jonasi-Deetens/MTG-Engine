# axis2/parsing/effects.py

import re
from typing import List
from axis2.schema import (
    DealDamageEffect, DrawCardsEffect, AddManaEffect,
    PutOntoBattlefieldEffect, SymbolicValue, 
    PutCounterEffect, CounterSpellEffect, CreateTokenEffect, EquipEffect, 
    GainLifeEffect, SearchEffect, CantBeBlockedEffect, GainLifeEqualToPowerEffect, 
    ReturnCardFromGraveyardEffect, DraftFromSpellbookEffect, PTBoostEffect,
    ChangeZoneEffect, ScryEffect, SurveilEffect, Subject, LookAndPickEffect,
    ParseContext, TransformEffect, ConditionalEffect, DestroyEffect, ShuffleEffect, 
    RevealEffect
)
from axis2.parsing.subject import parse_subject, subject_from_text
from axis2.parsing.spell_continuous_effects import parse_spell_continuous_effect

COLOR_MAP = {
    "white": "W",
    "blue": "U",
    "black": "B",
    "red": "R",
    "green": "G",
}

def split_effect_sentences(text: str) -> List[str]:
    print(f"[split_effect_sentences] Raw input: {repr(text)}")
    # DO NOT split on commas — they appear inside OR-lists.
    text = text.replace("\n", " ")

    # Normalize "then" into a sentence boundary
    text = re.sub(r"(?<!this way,)\s+then\b", ". then", text, flags=re.I)
    print(f"[split_effect_sentences] After re.sub: {repr(text)}")

    parts = re.split(r"[.;]", text)
    print(f"[split_effect_sentences] After splitting on [.;]: {parts}")

    # Remove empty or whitespace-only parts BEFORE returning
    cleaned = []
    for p in parts:
        s = p.strip()
        print(f"[split_effect_sentences] Checking part: {repr(p)} -> stripped: {repr(s)}")
        if s:
            cleaned.append(s)

    print(f"[split_effect_sentences] Cleaned parts: {cleaned}")
    return cleaned

IF_THIS_WAY_RE = re.compile(r"if .* this way", re.I)

def parse_effect_text(text, ctx: ParseContext):
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
    
    print(f"Parsing look and pick: {text}")
    # Look and pick
    # Global look-and-pick only if no conditional clause is present
    if "this way" not in text.lower():
        look_pick = parse_look_and_pick(text)
        if look_pick:
            effects.append(look_pick)

    # ------------------------------------------------------------
    # 2. Parse each sentence independently
    # ------------------------------------------------------------
    for sentence in sentences:
        s = sentence.strip()
        if not s:
            continue
        # ------------------------------------------------------------
        # CONDITIONAL: "If a card is put into exile this way, ..."
        # ------------------------------------------------------------
        m = IF_THIS_WAY_RE.search(s)
        if m:
            # Collect all sentences AFTER this one as the conditional body
            # Remove the conditional prefix from the same sentence
            inner_text = IF_THIS_WAY_RE.sub("", s).strip()


            inner_effects = parse_effect_text(inner_text, ctx)

            effects.append(
                ConditionalEffect(
                    condition="exiled_this_way",
                    effects=inner_effects
                )
            )
            continue

        print(f"Parsing effect: {s}")

        search = parse_search_effect(s)
        if search:
            effects.append(search)

        basic_land_search = parse_basic_land_search(s)
        if basic_land_search:
            effects.extend(basic_land_search)

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

        # PT boost
        pt_boost = parse_pt_boost(s)
        if pt_boost:
            effects.append(pt_boost)
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

        # Transform
        transform = parse_transform(s, ctx)
        if transform:
            effects.append(transform)
            continue

        # Destroy
        destroy = parse_destroy(s, ctx)
        if destroy:
            effects.append(destroy)
            continue

        # Basic land search plural
        plural_search = parse_basic_land_search_plural(s)
        if plural_search:
            effects.extend(plural_search)
            continue

        # Reveal those cards
        reveal = parse_reveal_those(s)
        if reveal:
            effects.append(reveal)
            continue

        # Put one onto the battlefield tapped
        put_one = parse_put_one_battlefield_tapped(s)
        if put_one:
            effects.append(put_one)

        # Put the other into your hand
        put_other = parse_put_other_into_hand(s)
        if put_other:
            effects.append(put_other)
            continue

        # Shuffle
        shuffle = parse_shuffle(s)
        if shuffle:
            effects.append(shuffle)
            continue

        # Move to zone
        print(f"Parsing change zone: {s}")
        change_zone = parse_change_zone(s, ctx)
        if change_zone:
            effects.append(change_zone)
            continue
            
        print(f"Parsing spell continuous effect: {s}")
        # Spell continuous effect
        spell_continuous = parse_spell_continuous_effect(s, ctx)
        if spell_continuous:
            effects.append(spell_continuous)
            continue

        # 2c. Damage
        damage = parse_damage(s, ctx)
        if damage:
            effects.append(damage)
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

SIMPLE_ARTIFACT_TOKEN_RE = re.compile(
    r"create (?:a|an|one)?\s*(treasure|food|clue|blood|gold)\s+token",
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
    # Pattern 2: Simple artifact tokens (Treasure, Food, Clue, Blood, Gold)
    # ------------------------------------------------------------
    m = SIMPLE_ARTIFACT_TOKEN_RE.search(t)
    if m:
        token_name = m.group(1).strip().capitalize()

        return CreateTokenEffect(
            amount=1,
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


    # ------------------------------------------------------------
    # Pattern 3: Simple creature tokens
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

REVEAL_THOSE_RE = re.compile(
    r"reveal those cards",
    re.IGNORECASE
)

def parse_reveal_those(text: str):
    if REVEAL_THOSE_RE.search(text):
        return RevealEffect(subject=Subject(scope="searched_cards"))
    return None

SEARCH_BASIC_LAND_RE = re.compile(
    r"^(its controller|that player|you)\s+may\s+search\s+their\s+library\s+for\s+a\s+basic\s+land\s+card\b",
    re.IGNORECASE
)

PUT_ONE_BF_TAPPED_RE = re.compile(
    r"put one onto the battlefield tapped",
    re.IGNORECASE
)

def parse_put_one_battlefield_tapped(text: str):
    if PUT_ONE_BF_TAPPED_RE.search(text):
        return ChangeZoneEffect(
            subject=Subject(scope="searched_card", index=0),
            to_zone="battlefield",
            tapped=True
        )
    return None

PUT_OTHER_HAND_RE = re.compile(
    r"the other into your hand",
    re.IGNORECASE
)

def parse_put_other_into_hand(text: str):
    if PUT_OTHER_HAND_RE.search(text):
        return ChangeZoneEffect(
            subject=Subject(scope="searched_card", index=1),
            to_zone="hand"
        )
    return None

SHUFFLE_RE = re.compile(r"shuffle", re.IGNORECASE)

def parse_shuffle(text: str):
    if SHUFFLE_RE.search(text):
        return ShuffleEffect(subject=Subject(scope="you"))
    return None


def parse_basic_land_search(text: str):
    """
    Handles effects like:
      'Its controller may search their library for a basic land card,
       put it onto the battlefield, then shuffle.'
    This is general enough to be reused for any similar templating.
    """
    t = text.lower()

    if not SEARCH_BASIC_LAND_RE.search(t):
        return None

    # Detect whether the effect includes a battlefield placement
    put_on_battlefield = "put it onto the battlefield" in t or \
                         "put that card onto the battlefield" in t or \
                         "put them onto the battlefield" in t

    effects = []

    # 1. Search effect
    effects.append(
        SearchEffect(
            zones=["library"],
            card_names=None,
            card_filter={"types": ["land"], "subtypes": ["basic"]},
            optional=True,
            put_onto_battlefield=put_on_battlefield,
            shuffle_if_library_searched=True,
            max_results=1
        )
    )

    # 2. If the card is put onto the battlefield, add the zone-change effect
    if put_on_battlefield:
        effects.append(
            ChangeZoneEffect(
                subject=Subject(scope="searched_card"),
                to_zone="battlefield"
            )
        )

    return effects

SEARCH_BASIC_LANDS_PLURAL_RE = re.compile(
    r"search your library for up to (one|two|three|\d+) basic land cards",
    re.IGNORECASE
)

def parse_basic_land_search_plural(text: str):
    m = SEARCH_BASIC_LANDS_PLURAL_RE.search(text)
    if not m:
        return None

    raw = m.group(1).lower()
    max_n = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]

    return [
        SearchEffect(
            zones=["library"],
            card_names=None,
            card_filter={"types":["land"], "subtypes":["basic"]},
            optional=False,
            max_results=max_n,
            put_onto_battlefield=False,
            shuffle_if_library_searched=True
        )
    ]


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
        shuffle_if_library_searched="shuffle" in text.lower(),
        max_results=len(card_names),
        card_filter=None
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

RETURN_FROM_GRAVEYARD_TO_HAND_RE = re.compile(
    r"return\s+(?P<subject>.+?)\s+from\s+(?P<from_zone>your graveyard|the graveyard|a graveyard)\s+to\s+(?:its|their|his|her|the)?\s*owner'?s hand",
    re.IGNORECASE
)

RETURN_HAND_RE = re.compile(
    r"return\s+(?P<subject>.+?)\s+(?:from\s+your\s+graveyard\s+)?to\s+your\s+hand",
    re.IGNORECASE
)


RETURN_BATTLEFIELD_RE = re.compile(
    r"return\s+(?P<subject>.+?)\s+to\s+the battlefield",
    re.IGNORECASE
)

ONTO_BATTLEFIELD_RE = re.compile(
    r"put\s+(?P<subject>.+?)\s+onto\s+the battlefield",
    re.IGNORECASE
)

EXILE_RE = re.compile(
    r"exile\s+(?P<subject>.+?)(?:$|\.|,)",
    re.IGNORECASE
)

GRAVEYARD_RE = re.compile(
    r"put\s+(?P<subject>.+?)\s+into\s+(?:its|their|your|his|her)?\s*owner'?s?\s*graveyard",
    re.IGNORECASE
)

LIBRARY_RE = re.compile(
    r"put\s+(?P<subject>.+?)\s+on\s+(?P<position>top|the bottom)\s+of\s+(?:its|their|your)?\s*owner'?s library",
    re.IGNORECASE
)

ZONE_FROM_RE = re.compile( 
    r"from\s+(?:a|any|the|your|their|its)\s+(graveyard|hand|library|battlefield|exile)", 
    re.IGNORECASE 
)

def _extract_restrictions(subject_text: str):
    """
    Extracts clauses like:
      - "that isn't a God"
      - "that is not legendary"
      - "that is a creature"
    Returns (clean_subject, filters_dict)
    """
    filters = {}

    # match "that isn't a God"
    m = re.search(r"that\s+(?:is|isn't|is not)\s+([a-z ]+)", subject_text, re.IGNORECASE)
    if m:
        raw = m.group(1).strip()

        # remove leading articles
        raw = re.sub(r"^(a|an|the)\s+", "", raw)

        # detect negation
        if "isn't" in subject_text or "is not" in subject_text:
            filters["not_subtype"] = raw
        else:
            filters["subtype"] = raw

        # remove the clause from subject text
        subject_text = re.sub(r"that\s+(?:is|isn't|is not)\s+[a-z ]+", "", subject_text, flags=re.IGNORECASE).strip()

    m = ZONE_FROM_RE.search(subject_text)
    if m:
        zone = m.group(1).lower()
        filters["zone"] = zone

        # Remove the zone clause from the subject text
        subject_text = ZONE_FROM_RE.sub("", subject_text).strip()

    return subject_text, filters


def parse_change_zone(text: str, ctx: ParseContext):
    # Do not parse "put it onto the battlefield" generically
    # when the sentence contains a search effect.
    if "put it onto the battlefield" in text.lower():
        return None

    # Prevent mis-parsing conditional clauses like "exiled this way"
    lower = text.lower()
    if "exiled this way" in lower:
        return None

    t = text.strip()
    print("TEXT BEFORE PARSE:", repr(t))

    # 1. Return from graveyard → hand
    m = RETURN_FROM_GRAVEYARD_TO_HAND_RE.search(t)
    if m:
        subject_text = m.group("subject").strip()
        subject_text, filters = _extract_restrictions(subject_text)
        print("SUBJECT BEFORE PARSE:", repr(subject_text))

        return ChangeZoneEffect(
            subject=subject_from_text(subject_text, ctx, extra_filters=filters),
            from_zone="graveyard",
            to_zone="hand"
        )

    # 2. Return → hand (no from-zone clause)
    m = RETURN_HAND_RE.search(t)
    if m:
        subject_text = m.group("subject").strip()
        subject_text, filters = _extract_restrictions(subject_text)
        print("SUBJECT BEFORE PARSE:", repr(subject_text))
        return ChangeZoneEffect(
            subject=subject_from_text(subject_text, ctx, extra_filters=filters),
            to_zone="hand"
        )

    # 3. Return → battlefield
    m = RETURN_BATTLEFIELD_RE.search(t)
    if m:
        subject_text = m.group("subject").strip()
        subject_text, filters = _extract_restrictions(subject_text)
        print("SUBJECT BEFORE PARSE:", repr(subject_text))
        return ChangeZoneEffect(
            subject=subject_from_text(subject_text, ctx, extra_filters=filters),
            to_zone="battlefield"
        )

    # 4. Put onto battlefield
    m = ONTO_BATTLEFIELD_RE.search(t)
    if m:
        subject_text = m.group("subject").strip()
        subject_text, filters = _extract_restrictions(subject_text)
        print("SUBJECT BEFORE PARSE:", repr(subject_text))
        return ChangeZoneEffect(
            subject=subject_from_text(subject_text, ctx, extra_filters=filters),
            to_zone="battlefield"
        )

    # 5. Exile
    m = EXILE_RE.search(t)
    if m:
        subject_text = m.group("subject").strip()
        subject_text, filters = _extract_restrictions(subject_text)
        print("SUBJECT BEFORE PARSE:", repr(subject_text))

        if subject_text.lower().startswith("target"):
            # Extract the type after "target"
            words = subject_text.split()
            if len(words) >= 2:
                type_word = words[1]  # "creature"
                # Build filters from the rest of the phrase
                extra_filters = filters.copy()
                if "opponent controls" in subject_text.lower():
                    extra_filters["opponent_controls"] = True

                return ChangeZoneEffect(
                    subject=Subject(
                        scope="target",
                        types=[type_word],
                        filters=extra_filters
                    ),
                    to_zone="exile"
                )

        # FALLBACK: normal subject parsing
        return ChangeZoneEffect(
            subject=subject_from_text(subject_text, ctx, extra_filters=filters),
            to_zone="exile"
        )


    # 6. Put into graveyard
    m = GRAVEYARD_RE.search(t)
    if m:
        subject_text = m.group("subject").strip()
        subject_text, filters = _extract_restrictions(subject_text)
        print("SUBJECT BEFORE PARSE:", repr(subject_text))
        return ChangeZoneEffect(
            subject=subject_from_text(subject_text, ctx, extra_filters=filters),
            to_zone="graveyard"
        )

    # 7. Put on top/bottom of library
    m = LIBRARY_RE.search(t)
    if m:
        subject_text = m.group("subject").strip()
        subject_text, filters = _extract_restrictions(subject_text)
        print("SUBJECT BEFORE PARSE:", repr(subject_text))
        position = m.group("position").strip()
        return ChangeZoneEffect(
            subject=subject_from_text(subject_text, ctx, extra_filters=filters),
            to_zone="library",
            position=position
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

LOOK_RE = re.compile(
    r"look at the top (\d+|one|two|three|four|five|six|seven|eight|nine|ten) cards? of your library",
    re.IGNORECASE
)

REVEAL_RE = re.compile(
    r"reveal up to (\d+|one|two|three|four|five|six|seven|eight|nine|ten) ([a-z ]+) cards? from among them",
    re.IGNORECASE
)

PUT_ONE_INTO_HAND_RE = re.compile(
    r"put (?:one|a|that) (?:of those )?cards? into your hand",
    re.IGNORECASE
)

PUT_REVEALED_RE = re.compile(
    r"put (?:them|the revealed cards?) into your hand",
    re.IGNORECASE
)

PUT_REST_RE = re.compile(
    r"put the rest on the bottom of your library(?: in a (random) order)?",
    re.IGNORECASE
)

PUT_CHOSEN_GRAVE_RE = re.compile(
    r"put (?:one|a|that) card into your graveyard",
    re.IGNORECASE
)

PUT_REST_GRAVE_RE = re.compile(
    r"(?:put )?the rest into your graveyard",
    re.IGNORECASE
)

PUT_REST_EXILE_RE = re.compile(
    r"exile the rest",
    re.IGNORECASE
)


PUT_CHOSEN_EXILE_RE = re.compile(
    r"exile (?:one|a|that) card",
    re.IGNORECASE
)

PUT_CHOSEN_TOP_RE = re.compile(
    r"put (?:one|a|that) card on top of your library",
    re.IGNORECASE
)

PUT_REST_TOP_RE = re.compile(
    r"put the rest on top of your library(?: in any order)?",
    re.IGNORECASE
)

SOURCE_ZONE_RE = re.compile(
    r"look at the top \d+ cards? of (?:target|that|your|an opponent's) (\w+)",
    re.IGNORECASE
)

def parse_look_and_pick(text: str):
    t = text.lower()
    optional = "you may" in t

    # 1. Look at top N
    m = LOOK_RE.search(t)
    if not m:
        return None

    raw = m.group(1)
    look_at = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]

    # Defaults
    reveal_up_to = None
    reveal_types = None
    put_revealed_into = None
    put_rest_into = None
    rest_order = None
    source_zone = "library"

    # Chosen card destinations
    if PUT_CHOSEN_GRAVE_RE.search(t):
        put_revealed_into = "graveyard"
    if PUT_CHOSEN_EXILE_RE.search(t):
        put_revealed_into = "exile"
    if PUT_CHOSEN_TOP_RE.search(t):
        put_revealed_into = "top"
    if PUT_ONE_INTO_HAND_RE.search(t):
        put_revealed_into = "hand"

    # 2. Reveal up to N of type X
    m = REVEAL_RE.search(t)
    if m:
        raw = m.group(1)
        reveal_up_to = int(raw) if raw.isdigit() else NUMBER_WORDS[raw]
        reveal_types = [m.group(2).strip()]

    # 3. Put revealed into hand
    if PUT_REVEALED_RE.search(t):
        put_revealed_into = "hand"

    # 4. Put rest — PRIORITIZED ORDER
    if PUT_REST_GRAVE_RE.search(t):
        put_rest_into = "graveyard"
    elif PUT_REST_EXILE_RE.search(t):
        put_rest_into = "exile"
    elif PUT_REST_TOP_RE.search(t):
        put_rest_into = "top"
    else:
        m = PUT_REST_RE.search(t)
        if m:
            put_rest_into = "bottom"
            rest_order = "random" if m.group(1) else "ordered"

    return LookAndPickEffect(
        look_at=look_at,
        source_zone=source_zone,
        reveal_up_to=reveal_up_to,
        reveal_types=reveal_types,
        put_revealed_into=put_revealed_into,
        put_rest_into=put_rest_into,
        rest_order=rest_order,
        optional=optional,
    )


TRANSFORM_RE = re.compile(
    r"\btransform\s+(?P<subject>.+?)(?:\.|,|;|$)",
    re.IGNORECASE,
)

def parse_transform(text: str, ctx: ParseContext):
    t = text.lower()
    m = TRANSFORM_RE.search(t)
    if not m:
        return None

    subject_text = m.group("subject").strip()
    subject = subject_from_text(subject_text, ctx)
    return TransformEffect(subject=subject)

DESTROY_RE = re.compile(
    r"\bdestroy\s+(?P<subject>[^.;]+)",
    re.IGNORECASE,
)

def parse_destroy(text: str, ctx: ParseContext):
    t = text.lower()
    m = DESTROY_RE.search(t)
    if not m:
        return None

    subject_text = m.group("subject").strip()
    subject = subject_from_text(subject_text, ctx)

    return DestroyEffect(subject=subject)

DAMAGE_RE = re.compile(
    r"deals?\s+(?P<amount>\d+)\s+damage\s+to\s+(?P<subject>.+?)(?:\.|,|;|$)",
    re.IGNORECASE,
)

def parse_damage(text: str, ctx: ParseContext):
    t = text.lower()
    m = DAMAGE_RE.search(t)
    if not m:
        return None

    amount = int(m.group("amount"))
    subject_text = m.group("subject").strip()
    subject = subject_from_text(subject_text, ctx)

    return DealDamageEffect(amount=amount, subject=subject)
