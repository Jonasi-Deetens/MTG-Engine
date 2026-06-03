# axis2/parsing/keyword_abilities/infect.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ContinuousEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class InfectParser:
    """Parses Infect keyword ability (static ability)"""
    
    keyword_name = "infect"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Infect pattern"""
        lower = reminder_text.lower()
        return "deals damage" in lower and ("-1/-1 counter" in lower or "poison counter" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Infect reminder text into ContinuousEffect"""
        logger.debug(f"[InfectParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "deals damage" not in lower:
            return []
        
        continuous_effect = ContinuousEffect(
            kind="damage_modification",
            applies_to="damage_dealt_by_self",
            duration="permanent",
            layer=6,
            value={"damage_to_creatures_becomes_counters": True, "counter_type": "-1/-1", "damage_to_players_becomes_poison": True},
            source_kind="static_ability"
        )
        
        logger.debug(f"[InfectParser] Created ContinuousEffect for Infect")
        
        return [continuous_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Infect keyword without reminder text"""
        logger.debug(f"[InfectParser] Parsing keyword only: {keyword_text}")
        
        continuous_effect = ContinuousEffect(
            kind="damage_modification",
            applies_to="damage_dealt_by_self",
            duration="permanent",
            layer=6,
            value={"damage_to_creatures_becomes_counters": True, "counter_type": "-1/-1", "damage_to_players_becomes_poison": True},
            source_kind="static_ability"
        )
        
        logger.debug(f"[InfectParser] Created ContinuousEffect for Infect")
        
        return [continuous_effect]

