# axis2/parsing/triggers/attacks.py

from .base import TriggerParser, ParseResult
from .patterns import ATTACKS_RE
from axis2.schema import AttacksEvent

class AttacksParser(TriggerParser):
    """Parses attacks triggers: 'whenever X attacks'"""
    priority = 25  # Lower priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "attacks" in text.lower()

    def parse(self, text: str) -> ParseResult:
        m = ATTACKS_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        # Extract subject from the trigger text
        # Pattern: "whenever X attacks" -> extract X
        # Try to extract the subject (e.g., "this permanent", "target creature", etc.)
        subject = "this permanent"  # Default
        if "this" in text.lower():
            # Extract "this X" pattern
            import re
            this_match = re.search(r"(?:when|whenever)\s+(this\s+\w+)", text, re.IGNORECASE)
            if this_match:
                subject = this_match.group(1)
        elif "target" in text.lower():
            # Extract "target X" pattern
            import re
            target_match = re.search(r"(?:when|whenever)\s+(target\s+\w+)", text, re.IGNORECASE)
            if target_match:
                subject = target_match.group(1)

        return ParseResult(
            matched=True,
            event=AttacksEvent(subject=subject)
        )

