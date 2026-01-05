# axis2/parsing/static_effects/haste.py

from typing import Optional
from .base import StaticEffectParser, ParseResult
from .patterns import HASTE_GRANT_RE
from axis2.schema import StaticEffect, Subject, ParseContext

class HasteParser(StaticEffectParser):
    """Parses haste grant effects: 'all creatures have haste'"""
    priority = 40  # Medium priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "all creatures have haste" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if not HASTE_GRANT_RE.search(text):
            return ParseResult(matched=False)

        from axis2.parsing.layers import parse_static_layer
        layer, sublayer = parse_static_layer("abilities")
        effect = StaticEffect(
            kind="grant_keyword",
            subject=Subject(
                scope="each",
                types=["creature"]
            ),
            value={"keyword": "haste"},
            layer=layer,
            sublayer=sublayer,
            zones=["battlefield"]
        )

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

