# axis2/parsing/effects/damage.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import DealDamageEffect, ParseContext
from axis2.parsing.subject import subject_from_text

DAMAGE_RE = re.compile(
    r"deals?\s+(?P<amount>\d+)\s+damage\s+to\s+(?P<subject>.+?)(?:\.|,|;|$)",
    re.IGNORECASE,
)

class DamageParser(EffectParser):
    """Parses damage effects: 'deals N damage to target creature'"""
    priority = 50  # Medium priority
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY - no regex, no parsing
        return "damage" in text.lower() and "deal" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = DAMAGE_RE.search(text.lower())
        if not m:
            return ParseResult(matched=False)
        
        try:
            amount = int(m.group("amount"))
            subject_text = m.group("subject").strip()
            subject = subject_from_text(subject_text, ctx)
            
            return ParseResult(
                matched=True,
                effect=DealDamageEffect(amount=amount, subject=subject),
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,  # We recognized the pattern, but parsing failed
                errors=[f"Failed to parse damage: {e}"]
            )

