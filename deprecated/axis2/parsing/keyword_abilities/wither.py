# axis2/parsing/keyword_abilities/wither.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ContinuousEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class WitherParser:
    """Parses Wither keyword ability (static ability)"""
    
    keyword_name = "wither"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Wither pattern"""
        lower = reminder_text.lower()
        return "deals damage" in lower and "-1/-1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Wither reminder text into ContinuousEffect"""
        logger.debug(f"[WitherParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "deals damage" not in lower or "-1/-1 counter" not in lower:
            return []
        
        continuous_effect = ContinuousEffect(
            kind="damage_modification",
            applies_to="damage_dealt_by_self",
            duration="permanent",
            layer=6,
            value={"damage_becomes_counters": True, "counter_type": "-1/-1"},
            source_kind="static_ability"
        )
        
        logger.debug(f"[WitherParser] Created ContinuousEffect for Wither")
        
        return [continuous_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Wither keyword without reminder text"""
        logger.debug(f"[WitherParser] Parsing keyword only: {keyword_text}")
        
        continuous_effect = ContinuousEffect(
            kind="damage_modification",
            applies_to="damage_dealt_by_self",
            duration="permanent",
            layer=6,
            value={"damage_becomes_counters": True, "counter_type": "-1/-1"},
            source_kind="static_ability"
        )
        
        logger.debug(f"[WitherParser] Created ContinuousEffect for Wither")
        
        return [continuous_effect]

