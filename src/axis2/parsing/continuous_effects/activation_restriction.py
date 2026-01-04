# axis2/parsing/continuous_effects/activation_restriction.py

from typing import Optional
from .base import ContinuousEffectParser, ParseResult
from axis2.schema import ContinuousEffect, RestrictionData, ParseContext
from axis2.parsing.layers import assign_layer_to_effect
import re


class ActivationRestrictionParser(ContinuousEffectParser):
    priority = 35
    
    def can_parse(self, text: str, ctx: ParseContext) -> bool:
        lower = text.lower()
        return ("can't be activated" in lower or "cannot be activated" in lower) and "activated abilities" in lower
    
    def parse(self, text: str, ctx: ParseContext, applies_to: Optional[str] = None,
              condition=None, duration: Optional[str] = None) -> ParseResult:
        lower = text.lower()
        
        if "activated abilities" in lower and ("can't be activated" in lower or "cannot be activated" in lower):
            restriction = RestrictionData()
            restriction.keyword = "activated_abilities_cannot_be_activated"
            
            effect = ContinuousEffect(
                kind="activation_restriction",
                applies_to=applies_to or "enchanted_creature",
                condition=condition,
                text=text,
                restriction=restriction,
                duration=duration,
                layer=6,
            )
            
            assign_layer_to_effect(effect)
            
            return ParseResult(
                matched=True,
                effect=effect,
                consumed_text=text
            )
        
        return ParseResult(matched=False)

