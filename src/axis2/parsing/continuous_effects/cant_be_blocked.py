# axis2/parsing/continuous_effects/cant_be_blocked.py

from typing import Optional
from .base import ContinuousEffectParser, ParseResult
from axis2.schema import ContinuousEffect, ParseContext
import re

class CantBeBlockedParser(ContinuousEffectParser):
    """Parses 'can't be blocked by X creatures' effects"""
    priority = 20  # Lower priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return ("can't be blocked" in lower or "cannot be blocked" in lower) and "by" in lower

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        m = re.search(
            r"(?:can't|cannot) be blocked by ([a-z]+) creatures",
            text,
            re.I
        )
        if not m:
            return ParseResult(matched=False)

        color = m.group(1).lower()
        restriction = {"colors": [color]}

        effect = ContinuousEffect(
            kind="cant_be_blocked_by",
            applies_to=applies_to,
            condition=condition,
            text=text,
            color_change=None,
            type_change=None,
            abilities=None,
            pt_value=None,
            dynamic=None,
            protection_from=None,
            control_change=None,
            cost_change=None,
            rule_change=None,
            restriction=restriction,
            duration=duration,
        )

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

