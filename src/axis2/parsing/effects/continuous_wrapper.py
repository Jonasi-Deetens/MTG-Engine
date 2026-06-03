# axis2/parsing/effects/continuous_wrapper.py

from .base import EffectParser, ParseResult
from axis2.schema import ParseContext, ContinuousEffect
from axis2.parsing.continuous_effects.dispatcher import parse_continuous_effects
from axis2.parsing.continuous_effects.utils import guess_applies_to, detect_duration
import re


class ContinuousEffectWrapperParser(EffectParser):
    priority = 45
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        lower = text.lower()
        
        # Don't match replacement effect patterns - these should be handled by replacement wrapper
        if "damage would be dealt" in lower and "instead" in lower:
            return False
        
        continuous_indicators = (
            "gains ", "gain ", "has ", "have ", "gets ", "get ",
            "loses ", "lose ", "is ", "are ", "becomes ", "become "
        )
        return any(indicator in lower for indicator in continuous_indicators)
    
    def parse(self, text: str, ctx: ParseContext) -> ParseResult:
        lower = text.lower()
        
        if any(lower.startswith(starter) for starter in ("when ", "whenever ", "at the beginning", "at the end")):
            return ParseResult(matched=False)
        
        applies_to = guess_applies_to(text)
        duration = detect_duration(text)
        
        continuous_effects = parse_continuous_effects(text, ctx)
        
        if continuous_effects:
            return ParseResult(
                matched=True,
                effects=continuous_effects,
                consumed_text=text
            )
        
        return ParseResult(matched=False)

