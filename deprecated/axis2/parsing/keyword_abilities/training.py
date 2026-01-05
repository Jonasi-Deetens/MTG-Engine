# axis2/parsing/keyword_abilities/training.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, AttacksEvent, PutCounterEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class TrainingParser:
    """Parses Training keyword ability (triggered ability)"""
    
    keyword_name = "training"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Training pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and "another creature" in lower and "greater power" in lower and "+1/+1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Training reminder text into TriggeredAbility"""
        logger.debug(f"[TrainingParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or "another creature" not in lower or "greater power" not in lower or "+1/+1 counter" not in lower:
            return []
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature and at least one other creature with power greater than this creature's power attack, put a +1/+1 counter on this creature.",
            effects=[put_counter_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="at_least_one_other_attacking_creature_with_greater_power"
        )
        
        logger.debug(f"[TrainingParser] Created TriggeredAbility for Training")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Training keyword without reminder text"""
        logger.debug(f"[TrainingParser] Parsing keyword only: {keyword_text}")
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature and at least one other creature with power greater than this creature's power attack, put a +1/+1 counter on this creature.",
            effects=[put_counter_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="at_least_one_other_attacking_creature_with_greater_power"
        )
        
        logger.debug(f"[TrainingParser] Created TriggeredAbility for Training")
        
        return [triggered_ability]

