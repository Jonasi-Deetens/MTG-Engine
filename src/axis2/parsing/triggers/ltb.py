# axis2/parsing/triggers/ltb.py

from .base import TriggerParser, ParseResult
from .patterns import LTB_RE
from axis2.schema import LeavesBattlefieldEvent

class LTBParser(TriggerParser):
    """Parses leaves-the-battlefield triggers: 'when X leaves the battlefield'"""
    priority = 35  # Medium priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "leaves the battlefield" in text.lower()

    def parse(self, text: str) -> ParseResult:
        m = LTB_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            event = LeavesBattlefieldEvent(subject=m.group(1).strip())

            return ParseResult(
                matched=True,
                event=event
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse LTB trigger: {e}"]
            )

