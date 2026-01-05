# axis2/parsing/keyword_abilities/dethrone.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, AttacksEvent, PutCounterEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class DethroneParser:
    """Parses Dethrone keyword ability (triggered ability)"""
    
    keyword_name = "dethrone"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Dethrone pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and "most life" in lower and "+1/+1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Dethrone reminder text into TriggeredAbility"""
        logger.debug(f"[DethroneParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or "most life" not in lower or "+1/+1 counter" not in lower:
            return []
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks the player with the most life or tied for most life, put a +1/+1 counter on this creature.",
            effects=[put_counter_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="attacking_player_with_most_life"
        )
        
        logger.debug(f"[DethroneParser] Created TriggeredAbility for Dethrone")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Dethrone keyword without reminder text"""
        logger.debug(f"[DethroneParser] Parsing keyword only: {keyword_text}")
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks the player with the most life or tied for most life, put a +1/+1 counter on this creature.",
            effects=[put_counter_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="attacking_player_with_most_life"
        )
        
        logger.debug(f"[DethroneParser] Created TriggeredAbility for Dethrone")
        
        return [triggered_ability]

