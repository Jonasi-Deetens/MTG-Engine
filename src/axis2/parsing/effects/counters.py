# axis2/parsing/effects/counters.py

import re
from .base import EffectParser, ParseResult
from axis2.schema import PutCounterEffect, RemoveCounterEffect, Subject, ParseContext

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


# Pattern for "remove a time counter from it"
REMOVE_COUNTER_RE = re.compile(
    r"remove\s+(?:a|an|one|(\d+))\s+(\w+)\s+counter\s+from\s+(it|this\s+\w+|target\s+\w+)",
    re.IGNORECASE
)

# Pattern for "remove X counters" (without "from")
REMOVE_COUNTER_SIMPLE_RE = re.compile(
    r"remove\s+(?:a|an|one|(\d+))\s+(\w+)\s+counter",
    re.IGNORECASE
)

class RemoveCounterParser(EffectParser):
    """Parses counter removal effects: 'remove a time counter from it'"""
    priority = 50  # Common effect
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        lower = text.lower()
        return "counter" in lower and "remove" in lower
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        t = text.strip()
        
        # Try "remove X counter from Y" pattern first
        m = REMOVE_COUNTER_RE.search(t)
        if m:
            amount_str = m.group(1)  # May be None if "a", "an", or "one"
            counter_type = m.group(2).strip()  # e.g., "time"
            subject_text = m.group(3).strip()  # e.g., "it", "this permanent"
            
            # Parse amount (default to 1 if "a", "an", or "one")
            if amount_str:
                amount = int(amount_str)
            else:
                amount = 1
            
            # Create subject from text
            subject = None
            if subject_text.lower() == "it":
                subject = Subject(scope="self")
            elif "this" in subject_text.lower():
                subject = Subject(scope="self")
            elif "target" in subject_text.lower():
                subject = Subject(scope="target")
            
            return ParseResult(
                matched=True,
                effect=RemoveCounterEffect(
                    counter_type=counter_type,
                    amount=amount,
                    subject=subject
                ),
                consumed_text=text
            )
        
        # Try simpler pattern "remove X counter" (without "from")
        m = REMOVE_COUNTER_SIMPLE_RE.search(t)
        if m:
            amount_str = m.group(1)
            counter_type = m.group(2).strip()
            
            if amount_str:
                amount = int(amount_str)
            else:
                amount = 1  # "a", "an", or "one"
            
            # Default to "self" if no subject specified
            subject = Subject(scope="self")
            
            return ParseResult(
                matched=True,
                effect=RemoveCounterEffect(
                    counter_type=counter_type,
                    amount=amount,
                    subject=subject
                ),
                consumed_text=text
            )
        
        return ParseResult(matched=False)

