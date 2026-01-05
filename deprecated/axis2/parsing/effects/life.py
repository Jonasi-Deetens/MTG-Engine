# axis2/parsing/effects/life.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import GainLifeEffect, GainLifeEqualToPowerEffect, ParseContext

GAIN_LIFE_EQUAL_RE = re.compile(
    r"gain life equal to (?:that|its) card'?s ([a-z ]+)",
    re.IGNORECASE
)

class LifeParser(EffectParser):
    """Parses life gain effects"""
    priority = 50  # Common effect
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "life" in text.lower() and ("gain" in text.lower() or "gains" in text.lower())
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        s = text.lower()
        
        # Check for "gain life equal to that card's power"
        m = GAIN_LIFE_EQUAL_RE.search(text)
        if m:
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

            return ParseResult(
                matched=True,
                effect=GainLifeEqualToPowerEffect(
                    source="that_card",
                    stat=stat
                ),
                consumed_text=text
            )
        
        # Check for simple "gains N life" or "you gain N life"
        if "gains" in s and "life" in s:
            m = re.search(r"(?:you\s+)?gains?\s+(\d+)\s+life", text, re.I)
            if m:
                amount = int(m.group(1))
                return ParseResult(
                    matched=True,
                    effect=GainLifeEffect(amount=amount, subject="player"),
                    consumed_text=text
                )
        
        # Check for "you gain N life"
        if "you gain" in s and "life" in s:
            m = re.search(r"you\s+gain\s+(\d+)\s+life", text, re.I)
            if m:
                amount = int(m.group(1))
                return ParseResult(
                    matched=True,
                    effect=GainLifeEffect(amount=amount, subject="player"),
                    consumed_text=text
                )
        
        return ParseResult(matched=False)

