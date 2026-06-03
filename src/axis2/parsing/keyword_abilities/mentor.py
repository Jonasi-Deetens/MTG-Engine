# axis2/parsing/keyword_abilities/mentor.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, AttacksEvent, PutCounterEffect, Subject, TargetingRules, ParseContext, Effect

logger = logging.getLogger(__name__)


class MentorParser:
    """Parses Mentor keyword ability (triggered ability)"""
    
    keyword_name = "mentor"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Mentor pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and "+1/+1 counter" in lower and "attacking creature" in lower and "lesser power" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Mentor reminder text into TriggeredAbility"""
        logger.debug(f"[MentorParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or "+1/+1 counter" not in lower or "attacking creature" not in lower:
            return []
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="target", types=["creature"])
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["attacking_creature"],
            restrictions=[{"power_less_than": "this_creature"}]
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks, put a +1/+1 counter on target attacking creature with power less than this creature's power.",
            effects=[put_counter_effect],
            event=AttacksEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[MentorParser] Created TriggeredAbility for Mentor")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Mentor keyword without reminder text"""
        logger.debug(f"[MentorParser] Parsing keyword only: {keyword_text}")
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="target", types=["creature"])
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["attacking_creature"],
            restrictions=[{"power_less_than": "this_creature"}]
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks, put a +1/+1 counter on target attacking creature with power less than this creature's power.",
            effects=[put_counter_effect],
            event=AttacksEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[MentorParser] Created TriggeredAbility for Mentor")
        
        return [triggered_ability]

