# axis2/parsing/effects/protection.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import CantBeBlockedEffect, ContinuousEffect, DynamicValue, Subject, ParseContext

CANT_BE_BLOCKED_RE = re.compile(
    r"target creature can'?t be blocked",
    re.IGNORECASE
)

PROT_CHOICE_RE = re.compile(
    r"gains?\s+protection\s+from\s+the\s+color\s+of\s+your\s+choice",
    re.I
)

class ProtectionParser(EffectParser):
    """Parses protection and blocking effects"""
    priority = 30  # Generic effect
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return "protection" in lower or "can't be blocked" in lower or "cannot be blocked" in lower
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        # Cant be blocked
        if CANT_BE_BLOCKED_RE.search(text):
            return ParseResult(
                matched=True,
                effect=CantBeBlockedEffect(
                    subject="target_creature",
                    duration="until_end_of_turn"
                ),
                consumed_text=text
            )
        
        # Protection from color of choice
        m = PROT_CHOICE_RE.search(text)
        if m:
            return ParseResult(
                matched=True,
                effect=ContinuousEffect(
                    kind="grant_protection",
                    applies_to="target",
                    text=text,
                    protection_from=[
                        DynamicValue(kind="chosen_color", subject=Subject(scope="this_ability"))
                    ],
                    duration="until_end_of_turn"
                ),
                consumed_text=text
            )
        
        return ParseResult(matched=False)

