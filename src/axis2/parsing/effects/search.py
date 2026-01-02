# axis2/parsing/effects/search.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import SearchEffect, ChangeZoneEffect, Subject, ParseContext
from .patterns import NUMBER_WORDS

SEARCH_BASIC_LAND_RE = re.compile(
    r"^(its controller|that player|you)\s+may\s+search\s+their\s+library\s+for\s+a\s+basic\s+land\s+card\b",
    re.IGNORECASE
)

SEARCH_BASIC_LANDS_PLURAL_RE = re.compile(
    r"search your library for up to (one|two|three|\d+) basic land cards",
    re.IGNORECASE
)

SEARCH_RE = re.compile(
    r"you may search your ([a-z ,/and]+) for a card named ([A-Za-z ]+?)"
    r"(?: and/or a card named ([A-Za-z ]+?))?"
    r"(?= and put| and put them| and put it| and put onto|$)",
    re.IGNORECASE
)

AURA_SEARCH_RE = re.compile(
    r"""
    you\s+may\s+search\s+your\s+library\s+for\s+an?\s+
    aura\s+card
    \s+with\s+mana\s+value\s+less\s+than\s+or\s+equal\s+to\s+that\s+aura
    \s+and\s+with\s+a\s+different\s+name\s+than\s+each\s+aura\s+you\s+control
    """,
    re.I | re.X,
)

class SearchParser(EffectParser):
    """Parses search effects"""
    priority = 80  # High priority (search is specific)
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "search" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        t = text.lower()
        effects = []
        
        # Try basic land search (plural)
        m = SEARCH_BASIC_LANDS_PLURAL_RE.search(text)
        if m:
            raw = m.group(1).lower()
            max_n = int(raw) if raw.isdigit() else NUMBER_WORDS.get(raw, 1)
            
            return ParseResult(
                matched=True,
                effects=[
                    SearchEffect(
                        zones=["library"],
                        card_names=None,
                        card_filter={"types":["land"], "subtypes":["basic"]},
                        optional=False,
                        max_results=max_n,
                        put_onto_battlefield=False,
                        shuffle_if_library_searched=True
                    )
                ],
                consumed_text=text
            )
        
        # Try basic land search (singular)
        if SEARCH_BASIC_LAND_RE.search(t):
            put_on_battlefield = "put it onto the battlefield" in t or \
                                 "put that card onto the battlefield" in t or \
                                 "put them onto the battlefield" in t

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

            # If the card is put onto the battlefield, add the zone-change effect
            if put_on_battlefield:
                effects.append(
                    ChangeZoneEffect(
                        subject=Subject(scope="searched_card"),
                        to_zone="battlefield"
                    )
                )

            return ParseResult(
                matched=True,
                effects=effects,
                consumed_text=text
            )
        
        # Try general search
        m = SEARCH_RE.search(text)
        if m:
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

            return ParseResult(
                matched=True,
                effect=SearchEffect(
                    zones=zones,
                    card_names=card_names,
                    optional=True,
                    put_onto_battlefield="put" in text.lower(),
                    shuffle_if_library_searched="shuffle" in text.lower(),
                    max_results=len(card_names),
                    card_filter=None
                ),
                consumed_text=text
            )
        
        return ParseResult(matched=False)

class LightpawsSearchParser(EffectParser):
    """Parses Lightpaws-specific aura search effect"""
    priority = 100  # Very specific pattern
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "search" in text.lower() and "aura" in text.lower() and "mana value" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = AURA_SEARCH_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        
        # Remove the matched part and parse the remainder
        remainder = AURA_SEARCH_RE.sub("", text).strip().lstrip(",").strip()
        
        effects = [
            SearchEffect(
                zones=["library"],
                card_filter={
                    "types": ["aura"],
                    "mana_value_lte": "that_aura",
                    "different_name_than_each_aura_you_control": True,
                },
                optional=True,
                max_results=1,
                card_names=None,
                put_onto_battlefield=False,
                shuffle_if_library_searched=False,
            )
        ]
        
        # ⚠️ If this parser needs to parse remainder text,
        # it can call registry.parse() internally with bounded depth:
        # For Lightpaws, the remainder ("put that card attached...") will be
        # handled by ZoneChangeParser when the full text is parsed
        # This avoids recursion in the dispatcher
        
        return ParseResult(
            matched=True,
            effects=effects,
            consumed_text=text
        )

