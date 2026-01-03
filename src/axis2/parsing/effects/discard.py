# axis2/parsing/effects/discard.py

import re
from typing import Optional
from .base import EffectParser, ParseResult
from axis2.schema import DiscardEffect, Subject, ParseContext, SymbolicValue

# Pattern: "target player discards a card", "target player discards X cards", etc.
DISCARD_RE = re.compile(
    r"(?:target\s+)?(?:player|opponent)\s+discards\s+(?:a|an|(\d+)|(\w+))\s+card(?:s)?",
    re.IGNORECASE
)

# Pattern for "discards X cards" where X is a number word
NUMBER_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
}


class DiscardParser(EffectParser):
    """
    Parser for discard effects: "target player discards a card"
    """
    priority = 50  # Medium-high priority
    
    def can_parse(self, text: str, ctx: Optional[ParseContext] = None) -> bool:
        """Check if text contains discard pattern."""
        text_lower = text.lower()
        return "discard" in text_lower and ("player" in text_lower or "opponent" in text_lower)
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        """Parse discard effect."""
        text = text.strip()
        
        m = DISCARD_RE.search(text)
        if not m:
            return ParseResult(matched=False, errors=[f"Could not match discard pattern: {text[:50]}..."])
        
        # Extract amount
        amount = 1  # Default
        if m.group(1):  # Numeric amount
            amount = int(m.group(1))
        elif m.group(2):  # Word amount
            word = m.group(2).lower()
            amount = NUMBER_WORDS.get(word, 1)
        
        # Extract subject (target player)
        subject = Subject(
            scope="target",
            types=["player"]
        )
        
        # Check if it's "opponent" instead of "player"
        if "opponent" in text.lower():
            subject.controller = "opponent"
        
        effect = DiscardEffect(
            subject=subject,
            amount=amount
        )
        
        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

