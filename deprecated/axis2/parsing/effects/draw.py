# axis2/parsing/effects/draw.py

from .base import EffectParser, ParseResult
from axis2.schema import DrawCardsEffect, ParseContext

class DrawParser(EffectParser):
    """Parses draw effects: 'draw N cards'"""
    priority = 30  # Generic effect
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "draw" in text.lower() and "card" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        s = text.lower()
        if "draw" not in s or "card" not in s:
            return ParseResult(matched=False)
        
        try:
            words = s.split()
            amount = 1
            for w in words:
                if w.isdigit():
                    amount = int(w)
                    break
            
            return ParseResult(
                matched=True,
                effect=DrawCardsEffect(amount=amount),
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse draw: {e}"]
            )

