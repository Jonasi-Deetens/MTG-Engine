# axis2/parsing/triggers/attacks.py

from .base import TriggerParser, ParseResult
from .patterns import ATTACKS_RE

class AttacksParser(TriggerParser):
    """Parses attacks triggers: 'whenever X attacks'"""
    priority = 25  # Lower priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "attacks" in text.lower()

    def parse(self, text: str) -> ParseResult:
        if not ATTACKS_RE.search(text):
            return ParseResult(matched=False)

        # Returns string "attacks" as the event type
        return ParseResult(
            matched=True,
            event="attacks"
        )

