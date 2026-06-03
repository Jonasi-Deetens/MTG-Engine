# axis2/parsing/triggers/damage.py

from .base import TriggerParser, ParseResult
from .patterns import DEALS_DAMAGE_RE
from axis2.schema import DealsDamageEvent

class DamageParser(TriggerParser):
    """Parses damage triggers: 'when X deals damage to Y'"""
    priority = 45  # High priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "deals" in text.lower() and "damage" in text.lower()

    def parse(self, text: str) -> ParseResult:
        m = DEALS_DAMAGE_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            event = DealsDamageEvent(
                subject=m.group(1).strip(),
                target=m.group(3).strip(),
                damage_type=(m.group(2).strip() if m.group(2) else "any")
            )

            return ParseResult(
                matched=True,
                event=event
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse damage trigger: {e}"]
            )

