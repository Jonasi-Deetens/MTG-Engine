# axis2/parsing/continuous_effects/protection.py

from typing import Optional
from .base import ContinuousEffectParser, ParseResult
from .patterns import PROT_RE
from axis2.schema import ContinuousEffect, ParseContext
import re

class ProtectionParser(ContinuousEffectParser):
    """Parses protection effects: 'protection from red'"""
    priority = 35  # Medium priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "protection from" in text.lower()

    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        m = PROT_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        raw = m.group(1).lower()
        parts = re.split(r",|and", raw)

        colors = []
        for p in parts:
            clean = p.strip()
            if clean.startswith("from "):
                clean = clean[5:]
            if clean:
                colors.append(clean)

        effect = ContinuousEffect(
            kind="grant_protection",
            applies_to=applies_to,
            protection_from=colors,
            duration=duration,
            text=text,
        )

        return ParseResult(
            matched=True,
            effect=effect,
            consumed_text=text
        )

