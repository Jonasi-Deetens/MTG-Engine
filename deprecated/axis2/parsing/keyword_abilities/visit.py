# axis2/parsing/keyword_abilities/visit.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, ParseContext, Effect

logger = logging.getLogger(__name__)


class VisitParser:
    """Parses Visit keyword ability (triggered ability for Attractions)"""
    
    keyword_name = "visit"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Visit pattern"""
        lower = reminder_text.lower()
        return "roll to visit" in lower and "attractions" in lower and "result" in lower and "lit up" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Visit reminder text"""
        logger.debug(f"[VisitParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "roll to visit" not in lower or "attractions" not in lower:
            return []
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever you roll to visit your Attractions, if the result is equal to a number that is lit up on this Attraction, [effect].",
            effects=[],  # Effect is parsed from the "Visit — [Effect]" text
            event="roll_to_visit_attractions",
            targeting=None,
            trigger_filter=None,
            condition="result_matches_lit_number"
        )
        
        logger.debug(f"[VisitParser] Created TriggeredAbility for Visit")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Visit keyword without reminder text (e.g., 'Visit — Create a Food token.')"""
        logger.debug(f"[VisitParser] Parsing keyword only: {keyword_text}")
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever you roll to visit your Attractions, if the result is equal to a number that is lit up on this Attraction, [effect].",
            effects=[],
            event="roll_to_visit_attractions",
            targeting=None,
            trigger_filter=None,
            condition="result_matches_lit_number"
        )
        
        logger.debug(f"[VisitParser] Created TriggeredAbility for Visit")
        
        return [triggered_ability]

