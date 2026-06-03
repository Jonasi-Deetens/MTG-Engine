# axis2/parsing/replacement_effects/enter_tapped.py

from typing import Optional
from .base import ReplacementEffectParser, ParseResult
from .patterns import RE_ENTER_TAPPED
from axis2.schema import ReplacementEffect, Subject

class EnterTappedParser(ReplacementEffectParser):
    """Parses enter tapped replacement effects: 'enters the battlefield tapped'"""
    priority = 40  # Medium priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "enters the battlefield tapped" in text.lower() or "enter the battlefield tapped" in text.lower()

    def parse(self, text: str) -> ParseResult:
        if not RE_ENTER_TAPPED.search(text):
            return ParseResult(matched=False)

        effect = ReplacementEffect(
            kind="enter_tapped",
            event="enter_battlefield",
            subject=Subject(scope="self"),
            value={"tapped": True},
            zones=["battlefield"]
        )

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

