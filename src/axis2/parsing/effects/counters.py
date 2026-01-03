# axis2/parsing/effects/counters.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import PutCounterEffect, ParseContext

# Pattern for "put a +1/+1 counter on target creature"
COUNTER_TARGET_RE = re.compile(
    r"put\s+(?:a|an)\s+(\+?\d+/\+\d+|\w+)\s+counter\s+on\s+target\s+([a-zA-Z ]+)",
    re.IGNORECASE
)

# Pattern for "put a +1/+1 counter on this creature"
COUNTER_THIS_RE = re.compile(
    r"put\s+(?:a|an)\s+(\+?\d+/\+\d+|\w+)\s+counter\s+on\s+this\s+([a-zA-Z ]+)",
    re.IGNORECASE
)

class CounterParser(EffectParser):
    """Parses counter effects: 'put a +1/+1 counter on target creature' or 'put a +1/+1 counter on this creature'"""
    priority = 50  # Common effect
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "counter" in text.lower() and "put" in text.lower()
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        # Try "this creature" pattern first
        m = COUNTER_THIS_RE.search(text)
        if m:
            counter_type = m.group(1).strip()  # e.g., "+1/+1"
            return ParseResult(
                matched=True,
                effect=PutCounterEffect(
                    counter_type=counter_type,
                    amount=1
                ),
                consumed_text=text
            )
        
        # Try "target creature" pattern
        m = COUNTER_TARGET_RE.search(text)
        if m:
            counter_type = m.group(1).strip()  # e.g., "+1/+1"
            return ParseResult(
                matched=True,
                effect=PutCounterEffect(
                    counter_type=counter_type,
                    amount=1
                ),
                consumed_text=text
            )

        return ParseResult(matched=False)

