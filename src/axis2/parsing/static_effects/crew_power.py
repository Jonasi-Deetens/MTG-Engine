# axis2/parsing/static_effects/crew_power.py

from typing import Optional
from .base import StaticEffectParser, ParseResult
from .patterns import CREW_POWER_RE, NUMBER_WORDS
from axis2.schema import StaticEffect, Subject, ParseContext

class CrewPowerParser(StaticEffectParser):
    """Parses crew power bonus effects: 'crews vehicles as though its power were 2 greater'"""
    priority = 45  # Medium priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "crews vehicles" in text.lower() and "power" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = CREW_POWER_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            raw = m.group(1).lower()

            if raw.isdigit():
                bonus = int(raw)
            else:
                bonus = NUMBER_WORDS.get(raw)
                if bonus is None:
                    return ParseResult(matched=False)

            from axis2.parsing.layers import parse_static_layer
            layer, sublayer = parse_static_layer("rules")
            effect = StaticEffect(
                kind="as_though",
                subject=Subject(scope="self"),
                value={
                    "action": "crew",
                    "parameter": "power",
                    "modifier": bonus
                },
                layer=layer,
                sublayer=sublayer,
                zones=["battlefield"]
            )

            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse crew power: {e}"]
            )

