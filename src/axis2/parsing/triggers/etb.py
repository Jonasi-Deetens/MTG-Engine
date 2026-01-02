# axis2/parsing/triggers/etb.py

from .base import TriggerParser, ParseResult
from .patterns import ETB_RE
from axis2.schema import EntersBattlefieldEvent

class ETBParser(TriggerParser):
    """Parses enters-the-battlefield triggers: 'when X enters the battlefield'"""
    priority = 40  # Medium priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "enters" in text.lower() and ("when" in text.lower() or "whenever" in text.lower())

    def parse(self, text: str) -> ParseResult:
        m = ETB_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            event = EntersBattlefieldEvent(subject=m.group(1).strip())

            return ParseResult(
                matched=True,
                event=event
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse ETB trigger: {e}"]
            )

