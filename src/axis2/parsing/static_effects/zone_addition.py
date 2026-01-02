# axis2/parsing/static_effects/zone_addition.py

from typing import Optional
from .base import StaticEffectParser, ParseResult
from .patterns import ZONE_ADD_RE
from axis2.schema import StaticEffect, Subject, ParseContext

class ZoneAdditionParser(StaticEffectParser):
    """Parses zone addition effects: 'noninstant, nonsorcery cards on top of a library are on the battlefield'"""
    priority = 30  # Lower priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "on top of a library are on the battlefield" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        if not ZONE_ADD_RE.search(text):
            return ParseResult(matched=False)

        from axis2.parsing.layers import parse_static_layer
        layer, sublayer = parse_static_layer("rules")
        effect = StaticEffect(
            kind="zone_addition",
            subject=Subject(
                scope="each",
                types=["card"],
                filters={
                    "location": "top_of_library",
                    "noninstant": True,
                    "nonsorcery": True
                }
            ),
            value={"additional_zone": "battlefield"},
            layer=layer,
            sublayer=sublayer,
            zones=["library"]
        )

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

