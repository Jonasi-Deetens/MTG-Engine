# axis2/parsing/effects/counters.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import PutCounterEffect, ParseContext

COUNTER_RE = re.compile(
    r"put (?:a|an) \+1/\+1 counter on target ([a-zA-Z ]+)",
    re.IGNORECASE
)

class CounterParser(EffectParser):
    """Parses counter effects: 'put a +1/+1 counter on target creature'"""
    priority = 50  # Common effect
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "counter" in text.lower() and "put" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        m = COUNTER_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        return ParseResult(
            matched=True,
            effect=PutCounterEffect(
                counter_type="+1/+1",
                amount=1
            ),
            consumed_text=text
        )

