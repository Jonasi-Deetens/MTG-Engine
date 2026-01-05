# axis2/parsing/replacement_effects/zone_change.py

from typing import Optional
from .base import ReplacementEffectParser, ParseResult
from .patterns import RE_WOULD_GO_TO_GRAVEYARD
from .utils import parse_subject_from_text, parse_instead_actions
from axis2.schema import ReplacementEffect, Subject

class ZoneChangeParser(ReplacementEffectParser):
    """Parses zone change replacement effects: 'if X would be put into a graveyard from anywhere, Y instead'"""
    priority = 50  # High priority - specific pattern

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "would be put into" in text.lower() and "graveyard" in text.lower()

    def parse(self, text: str) -> ParseResult:
        m = RE_WOULD_GO_TO_GRAVEYARD.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            subject_raw = m.group(1)
            action_raw = m.group(2)

            subject = parse_subject_from_text(subject_raw)
            actions = parse_instead_actions(action_raw)

            effect = ReplacementEffect(
                kind="zone_change_replacement",
                event="move_to_graveyard",
                subject=subject,
                value={"instead": actions},
                zones=["anywhere"]
            )

            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse zone change replacement: {e}"]
            )

