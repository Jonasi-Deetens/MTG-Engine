# axis2/parsing/keyword_abilities/living_metal.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ContinuousEffect, TypeChangeData, ParseContext, Effect

logger = logging.getLogger(__name__)


class LivingMetalParser:
    """Parses Living Metal keyword ability (static ability)"""
    
    keyword_name = "living metal"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Living Metal pattern"""
        lower = reminder_text.lower()
        return "your turn" in lower and ("vehicle" in lower or "creature" in lower) and "artifact creature" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Living Metal reminder text into ContinuousEffect"""
        logger.debug(f"[LivingMetalParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "your turn" not in lower or "creature" not in lower:
            return []
        
        continuous_effect = ContinuousEffect(
            kind="type_add",
            text="During your turn, this permanent is an artifact creature in addition to its other types.",
            applies_to="self",
            duration="permanent",
            layer=4,
            type_change=TypeChangeData(add_types=["creature"]),
            condition="during_your_turn",
            source_kind="static_ability"
        )
        
        logger.debug(f"[LivingMetalParser] Created ContinuousEffect for Living Metal")
        
        return [continuous_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Living Metal keyword without reminder text"""
        logger.debug(f"[LivingMetalParser] Parsing keyword only: {keyword_text}")
        
        continuous_effect = ContinuousEffect(
            kind="type_add",
            text="During your turn, this permanent is an artifact creature in addition to its other types.",
            applies_to="self",
            duration="permanent",
            layer=4,
            type_change=TypeChangeData(add_types=["creature"]),
            condition="during_your_turn",
            source_kind="static_ability"
        )
        
        logger.debug(f"[LivingMetalParser] Created ContinuousEffect for Living Metal")
        
        return [continuous_effect]

