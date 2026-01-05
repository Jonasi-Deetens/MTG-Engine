# axis2/parsing/keyword_abilities/exalted.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, AttacksEvent, ContinuousEffect, PTExpression, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class ExaltedParser:
    """Parses Exalted keyword ability (triggered ability)"""
    
    keyword_name = "exalted"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Exalted pattern"""
        lower = reminder_text.lower()
        return "attacks alone" in lower and "gets +1/+1" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Exalted reminder text into TriggeredAbility"""
        logger.debug(f"[ExaltedParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks alone" not in lower or "gets +1/+1" not in lower:
            return []
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="attacking_creature",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+1", toughness="+1"),
            text="gets +1/+1 until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever a creature you control attacks alone, that creature gets +1/+1 until end of turn.",
            effects=[pt_effect],
            event=AttacksEvent(subject="creature_you_control"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ExaltedParser] Created TriggeredAbility for Exalted")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Exalted keyword without reminder text"""
        logger.debug(f"[ExaltedParser] Parsing keyword only: {keyword_text}")
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="attacking_creature",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+1", toughness="+1"),
            text="gets +1/+1 until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever a creature you control attacks alone, that creature gets +1/+1 until end of turn.",
            effects=[pt_effect],
            event=AttacksEvent(subject="creature_you_control"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ExaltedParser] Created TriggeredAbility for Exalted")
        
        return [triggered_ability]

