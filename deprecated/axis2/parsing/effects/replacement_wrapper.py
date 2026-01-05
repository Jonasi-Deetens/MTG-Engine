# axis2/parsing/effects/replacement_wrapper.py

"""
Wrapper to parse replacement effects from triggered ability effect text.
This allows replacement effects to be created by triggered abilities.
"""

from .base import EffectParser, ParseResult
from axis2.schema import Effect, ParseContext
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
        # ⚠️ CHEAP CHECK ONLY
        # Check for replacement effect patterns
        # Text pattern: "damage that would be dealt... is dealt to... instead"
        lower = text.lower()
        has_damage_redirection = (
            "damage" in lower and "would be dealt" in lower and "instead" in lower and 
            ("is dealt to" in lower or "is dealt " in lower)
        )
        logger.debug(f"[ReplacementWrapper] can_parse check: '{text[:80]}...' -> {has_damage_redirection}")
        return has_damage_redirection
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        print(f"[ReplacementWrapper PRINT] parse called with: '{text[:100]}...'")
        logger.debug(f"[ReplacementWrapper] parse called with: '{text[:100]}...'")
        # Try damage redirection first (most common in triggered abilities)
        damage_parser = ReplacementDamageParser()
        can_parse_result = damage_parser.can_parse(text)
        print(f"[ReplacementWrapper PRINT] Damage parser can_parse: {can_parse_result}")
        if can_parse_result:
            logger.debug(f"[ReplacementWrapper] Damage parser can_parse=True, calling parse...")
            result = damage_parser.parse(text, ctx)
            print(f"[ReplacementWrapper PRINT] Damage parser result: matched={result.matched}, effect={result.effect}")
            logger.debug(f"[ReplacementWrapper] Damage parser result: matched={result.matched}, effect={result.effect}")
            if result.matched and result.effect:
                # Convert ReplacementEffect to Effect for the effects registry
                print(f"[ReplacementWrapper PRINT] Returning ReplacementEffect: {result.effect.kind}")
                logger.debug(f"[ReplacementWrapper] Returning ReplacementEffect: {result.effect.kind}")
                return ParseResult(
                    matched=True,
                    effect=result.effect,  # ReplacementEffect is a subclass of Effect
                    consumed_text=result.consumed_text,
                    errors=result.errors
                )
            else:
                print(f"[ReplacementWrapper PRINT] Damage parser matched=False or no effect")
                logger.debug(f"[ReplacementWrapper] Damage parser matched=False or no effect")
        else:
            print(f"[ReplacementWrapper PRINT] Damage parser can_parse=False")
            logger.debug(f"[ReplacementWrapper] Damage parser can_parse=False")
        
        return ParseResult(matched=False)

