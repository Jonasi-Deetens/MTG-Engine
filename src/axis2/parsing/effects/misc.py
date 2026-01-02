# axis2/parsing/effects/misc.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import (
    ScryEffect, SurveilEffect, RevealEffect, CounterSpellEffect,
    ReturnCardFromGraveyardEffect, DraftFromSpellbookEffect, PTBoostEffect,
    ShuffleEffect, Subject, EquipEffect, ParseContext
)

SCRY_RE = re.compile(r"\bscry\s+(\d+)\b", re.IGNORECASE)

SURVEIL_RE = re.compile(r"\bsurveil\s+(\d+)\b", re.IGNORECASE)

REVEAL_THOSE_RE = re.compile(
    r"reveal those cards",
    re.IGNORECASE
)

COUNTER_SPELL_RE = re.compile(
    r"counter (target )?spell",
    re.IGNORECASE
)

RETURN_CARD_RE = re.compile(
    r"return (?:up to )?target ([a-z ]+?) card from (?:your|an opponent's|a|their) graveyard to (?:your|its owner's|their) ([a-z ]+)",
    re.IGNORECASE
)

SPELLBOOK_RE = re.compile(
    r"draft a card from ([a-zA-Z ]+)'s spellbook",
    re.IGNORECASE
)

PT_BOOST_RE = re.compile(
    r"target creature gets \+(\d+)/\+(\d+) until end of turn",
    re.IGNORECASE
)

SHUFFLE_RE = re.compile(r"shuffle", re.IGNORECASE)

class ScryParser(EffectParser):
    """Parses scry effects"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "scry" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = SCRY_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        return ParseResult(
            matched=True,
            effect=ScryEffect(amount=int(m.group(1))),
            consumed_text=text
        )

class SurveilParser(EffectParser):
    """Parses surveil effects"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "surveil" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = SURVEIL_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        return ParseResult(
            matched=True,
            effect=SurveilEffect(amount=int(m.group(1))),
            consumed_text=text
        )

class RevealThoseParser(EffectParser):
    """Parses 'reveal those cards' effects"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "reveal those" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if REVEAL_THOSE_RE.search(text):
            return ParseResult(
                matched=True,
                effect=RevealEffect(subject=Subject(scope="searched_cards")),
                consumed_text=text
            )
        return ParseResult(matched=False)

class CounterSpellParser(EffectParser):
    """Parses counter spell effects"""
    priority = 50
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "counter" in text.lower() and "spell" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if COUNTER_SPELL_RE.search(text):
            return ParseResult(
                matched=True,
                effect=CounterSpellEffect(target="target_spell"),
                consumed_text=text
            )
        return ParseResult(matched=False)

class ReturnCardParser(EffectParser):
    """Parses return card from graveyard effects"""
    priority = 40
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "return" in text.lower() and "graveyard" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = RETURN_CARD_RE.search(text)
        if not m:
            return ParseResult(matched=False)

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

        return ParseResult(
            matched=True,
            effect=ReturnCardFromGraveyardEffect(
                subtype=subtype,
                controller="you",
                destination_zone=dest_zone
            ),
            consumed_text=text
        )

class SpellbookParser(EffectParser):
    """Parses spellbook draft effects"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "spellbook" in text.lower() and "draft" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = SPELLBOOK_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        return ParseResult(
            matched=True,
            effect=DraftFromSpellbookEffect(source=m.group(1).strip()),
            consumed_text=text
        )

class PTBoostParser(EffectParser):
    """Parses power/toughness boost effects"""
    priority = 50
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "gets" in text.lower() and ("+" in text or "power" in text.lower() or "toughness" in text.lower())
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = PT_BOOST_RE.search(text)
        if not m:
            return ParseResult(matched=False)
        return ParseResult(
            matched=True,
            effect=PTBoostEffect(
                power=int(m.group(1)),
                toughness=int(m.group(2)),
                duration="until_end_of_turn"
            ),
            consumed_text=text
        )

class ShuffleParser(EffectParser):
    """Parses shuffle effects"""
    priority = 20  # Low priority, very generic
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return "shuffle" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if SHUFFLE_RE.search(text):
            return ParseResult(
                matched=True,
                effect=ShuffleEffect(subject=Subject(scope="you")),
                consumed_text=text
            )
        return ParseResult(matched=False)

class EquipParser(EffectParser):
    """Parses Equip keyword ability"""
    priority = 30
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        return text.strip().lower().startswith("equip")
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if text.strip().lower().startswith("equip"):
            return ParseResult(
                matched=True,
                effect=EquipEffect(),
                consumed_text=text
            )
        return ParseResult(matched=False)

