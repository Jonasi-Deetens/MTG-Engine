# axis2/parsing/replacement_effects/delayed.py

from typing import Optional
from .base import ReplacementEffectParser, ParseResult
from .patterns import RE_DELAYED_REPLACEMENT
from .utils import parse_delayed_subject
from axis2.schema import ReplacementEffect

class DelayedParser(ReplacementEffectParser):
    """Parses delayed replacement effects: 'the next time X would Y this turn'"""
    priority = 55  # Highest priority - very specific pattern

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "the next time" in text.lower() and "would" in text.lower() and "this turn" in text.lower()

    def parse(self, text: str) -> ParseResult:
        m = RE_DELAYED_REPLACEMENT.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            event_subject_raw = m.group(1)
            event_action_raw = m.group(2)

            subject = parse_delayed_subject(event_subject_raw)

            effect = ReplacementEffect(
                kind="delayed_prevent_damage",
                event="damage",
                subject=subject,
                value={"amount": "all"},
                zones=["anywhere"],
                next_event_only=True,
                duration="until_end_of_turn"
            )

            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse delayed replacement: {e}"]
            )

