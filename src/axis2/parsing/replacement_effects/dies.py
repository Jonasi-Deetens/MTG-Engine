# axis2/parsing/replacement_effects/dies.py

from typing import Optional
from .base import ReplacementEffectParser, ParseResult
from .patterns import RE_WOULD_DIE
from .utils import parse_subject_from_text, parse_instead_actions
from axis2.schema import ReplacementEffect

class DiesParser(ReplacementEffectParser):
    """Parses dies replacement effects: 'if X would die, Y instead'"""
    priority = 45  # High priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "would die" in text.lower() and "instead" in text.lower()

    def parse(self, text: str) -> ParseResult:
        m = RE_WOULD_DIE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            subject_raw = m.group(1)
            action_raw = m.group(2)

            subject = parse_subject_from_text(subject_raw)
            actions = parse_instead_actions(action_raw)

            effect = ReplacementEffect(
                kind="dies_replacement",
                event="would_die",
                subject=subject,
                value={"instead": actions},
                zones=["battlefield"]
            )

            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse dies replacement: {e}"]
            )

