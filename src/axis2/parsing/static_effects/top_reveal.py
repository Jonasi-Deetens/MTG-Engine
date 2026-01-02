# axis2/parsing/static_effects/top_reveal.py

from typing import Optional
from .base import StaticEffectParser, ParseResult
from .patterns import TOP_REVEAL_RE
from axis2.schema import StaticEffect, Subject, ParseContext

class TopRevealParser(StaticEffectParser):
    """Parses top reveal effects: 'play with the top card of their libraries revealed'"""
    priority = 35  # Lower priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "top card" in text.lower() and "revealed" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if not TOP_REVEAL_RE.search(text):
            return ParseResult(matched=False)

        effect = StaticEffect(
            kind="as_though",
            subject=Subject(
                scope="each",
                types=["player"]
            ),
            value={
                "action": "reveal",
                "parameter": "top_of_library",
                "state": True
            },
            layer="rules",
            zones=["library"]
        )

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

