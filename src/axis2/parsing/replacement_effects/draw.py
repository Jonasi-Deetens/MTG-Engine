# axis2/parsing/replacement_effects/draw.py

from typing import Optional
from .base import ReplacementEffectParser, ParseResult
from .patterns import RE_DRAW_REPLACEMENT
from axis2.schema import ReplacementEffect, Subject
import re

class DrawParser(ReplacementEffectParser):
    """Parses draw replacement effects: 'if X would draw, draw Y instead'"""
    priority = 30  # Lower priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "would draw" in text.lower() and "instead" in text.lower()

    def parse(self, text: str) -> ParseResult:
        if not RE_DRAW_REPLACEMENT.search(text):
            return ParseResult(matched=False)

        lower = text.lower()
        m = re.search(r"draw (\w+) instead", lower)
        amount = m.group(1) if m else None

        effect = ReplacementEffect(
            kind="draw_replacement",
            event="draw",
            subject=Subject(scope="self"),
            value={"amount": amount},
            zones=["anywhere"]
        )

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

