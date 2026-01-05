# axis2/parsing/keyword_abilities/flanking.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, ContinuousEffect, PTExpression, ParseContext, Effect

logger = logging.getLogger(__name__)


class FlankingParser:
    """Parses Flanking keyword ability (triggered ability)"""
    
    keyword_name = "flanking"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Flanking pattern"""
        lower = reminder_text.lower()
        return "becomes blocked" in lower and "blocking creature gets" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Flanking reminder text into TriggeredAbility"""
        logger.debug(f"[FlankingParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "becomes blocked" not in lower or "blocking creature gets" not in lower:
            return []
        
        condition_text = "Whenever this creature becomes blocked by a creature without flanking"
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="blocking_creature",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(
                power="-1",
                toughness="-1"
            ),
            text="the blocking creature gets -1/-1 until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[pt_effect],
            event="becomes_blocked",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[FlankingParser] Created TriggeredAbility for Flanking")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Flanking keyword without reminder text"""
        logger.debug(f"[FlankingParser] Parsing keyword only: {keyword_text}")
        
        condition_text = "Whenever this creature becomes blocked by a creature without flanking"
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="blocking_creature",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(
                power="-1",
                toughness="-1"
            ),
            text="the blocking creature gets -1/-1 until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[pt_effect],
            event="becomes_blocked",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[FlankingParser] Created TriggeredAbility for Flanking")
        
        return [triggered_ability]

