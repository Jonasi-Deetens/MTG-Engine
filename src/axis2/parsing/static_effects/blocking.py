# axis2/parsing/static_effects/blocking.py

from typing import Optional
from .base import StaticEffectParser, ParseResult
from .patterns import BLOCKING_RESTRICTION_RE, NUMBER_WORDS
from axis2.schema import StaticEffect, Subject, ParseContext

class BlockingParser(StaticEffectParser):
    """Parses blocking restriction effects: 'each creature you control can't be blocked by more than one'"""
    priority = 50  # Medium priority

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "be blocked by more than" in text.lower()

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = BLOCKING_RESTRICTION_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            raw = m.group(1).strip().lower()
            token = raw.split()[0]  # handle "one creature", "1 creature"

            if token.isdigit():
                max_blockers = int(token)
            elif token in NUMBER_WORDS:
                max_blockers = NUMBER_WORDS[token]
            else:
                return ParseResult(matched=False)

            effect = StaticEffect(
                kind="blocking_restriction",
                subject=Subject(
                    scope="each",
                    controller="you",
                    types=["creature"]
                ),
                value={"max_blockers": max_blockers},
                layer="rules",
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
                errors=[f"Failed to parse blocking restriction: {e}"]
            )

