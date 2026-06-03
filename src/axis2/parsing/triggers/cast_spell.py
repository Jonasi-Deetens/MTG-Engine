# axis2/parsing/triggers/cast_spell.py

from .base import TriggerParser, ParseResult
from .patterns import CAST_SPELL_RE
from .utils import parse_spell_filter
from axis2.schema import CastSpellEvent

class CastSpellParser(TriggerParser):
    """Parses cast spell triggers: 'whenever you cast a spell'"""
    priority = 30  # Lower priority

    def can_parse(self, text: str) -> bool:
        # ⚠️ CHEAP CHECK ONLY
        return "cast" in text.lower() and "spell" in text.lower()

    def parse(self, text: str) -> ParseResult:
        m = CAST_SPELL_RE.search(text)
        if not m:
            return ParseResult(matched=False)

        try:
            spell_filter = parse_spell_filter(m.group(2).strip())
            event = CastSpellEvent(subject=m.group(1).strip(), spell_filter=spell_filter)

            return ParseResult(
                matched=True,
                event=event
            )
        except (ValueError, AttributeError) as e:
            return ParseResult(
                matched=True,
                errors=[f"Failed to parse cast spell trigger: {e}"]
            )

