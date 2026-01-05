# axis2/parsing/triggers/zone_change.py

from .base import TriggerParser, ParseResult
from .patterns import ZONE_CHANGE_TRIGGER_RE
from axis2.schema import ZoneChangeEvent

class ZoneChangeParser(TriggerParser):
    """Parses zone change triggers: 'when X is put into Y from Z'"""
    priority = 50  # High priority - specific pattern

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "is put into" in text.lower()

    def parse(self, text: str) -> ParseResult:
        m = ZONE_CHANGE_TRIGGER_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            event = ZoneChangeEvent(
                subject=m.group(1).strip(),
                from_zone=m.group(3).strip(),
                to_zone=m.group(2).strip()
            )

            return ParseResult(
                matched=True,
                event=event
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse zone change trigger: {e}"]
            )

