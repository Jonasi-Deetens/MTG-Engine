# axis2/parsing/replacement_effects/damage.py

from typing import Optional
from .base import ReplacementEffectParser, ParseResult
from .patterns import RE_DAMAGE_PREVENTION
from axis2.schema import ReplacementEffect, Subject
import re

class DamageParser(ReplacementEffectParser):
    """Parses damage prevention/redirection replacement effects"""
    priority = 35  # Medium priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "damage would be dealt" in text.lower()

    def parse(self, text: str) -> ParseResult:
        if not RE_DAMAGE_PREVENTION.search(text):
            return ParseResult(matched=False)

        lower = text.lower()

        if "prevent" in lower:
            # detect "prevent the next N damage"
            m = re.search(r"prevent the next (\w+)", lower)
            amount = m.group(1) if m else "all"

            effect = ReplacementEffect(
                kind="prevent_damage",
                event="damage",
                subject=Subject(scope="self"),
                value={"amount": amount},
                zones=["battlefield"]
            )
        elif "instead" in lower:
            effect = ReplacementEffect(
                kind="redirect_damage",
                event="damage",
                subject=Subject(scope="self"),
                value={"action": "redirect"},
                zones=["battlefield"]
            )
        else:
            return ParseResult(matched=False)

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

