# axis2/parsing/effects/replacement_wrapper.py

"""
Wrapper to parse replacement effects from triggered ability effect text.
This allows replacement effects to be created by triggered abilities.
"""

from .base import EffectParser, ParseResult
from axis2.schema import ParseContext
from axis2.parsing.replacement_effects.damage import DamageParser as ReplacementDamageParser
import logging

logger = logging.getLogger(__name__)


class ReplacementEffectWrapperParser(EffectParser):
    """
    Wraps replacement effect parsers so they can be used in triggered ability effect text.
    This handles cases like "all damage that would be dealt... is dealt to... instead"
    """
    priority = 75  # Very high priority - must match before continuous effects and other generic parsers

    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        lower = text.lower()
        has_damage_redirection = (
            "damage" in lower and "would be dealt" in lower and "instead" in lower
            and ("is dealt to" in lower or "is dealt " in lower)
        )
        logger.debug("[ReplacementWrapper] can_parse %s -> %s", text[:80], has_damage_redirection)
        return has_damage_redirection

    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        damage_parser = ReplacementDamageParser()
        if not damage_parser.can_parse(text):
            return ParseResult(matched=False)

        result = damage_parser.parse(text, ctx)
        if result.matched and result.effect:
            logger.debug("[ReplacementWrapper] matched %s", result.effect.kind)
            return ParseResult(
                matched=True,
                effect=result.effect,
                consumed_text=result.consumed_text,
                errors=result.errors,
            )
        return ParseResult(matched=False)
