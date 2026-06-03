# axis2/parsing/effects/look_pick.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import LookAndPickEffect, ParseContext
from .patterns import NUMBER_WORDS

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

class LookAndPickParser(EffectParser):
    """Parses look-and-pick effects: 'look at top N, reveal up to X, put rest...'"""
    priority = 90  # High priority (specific pattern)
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "look at" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        t = text.lower()
        optional = "you may" in t

        # 1. Look at top N
        m = LOOK_RE.search(t)
        if not m:
            return ParseResult(matched=False)

        raw = m.group(1)
        look_at = int(raw) if raw.isdigit() else NUMBER_WORDS.get(raw, 1)

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
            reveal_up_to = int(raw) if raw.isdigit() else NUMBER_WORDS.get(raw, 1)
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

        return ParseResult(
            matched=True,
            effect=LookAndPickEffect(
                look_at=look_at,
                source_zone=source_zone,
                reveal_up_to=reveal_up_to,
                reveal_types=reveal_types,
                put_revealed_into=put_revealed_into,
                put_rest_into=put_rest_into,
                rest_order=rest_order,
                optional=optional,
            ),
            consumed_text=text
        )

