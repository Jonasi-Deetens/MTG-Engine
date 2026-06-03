# axis2/parsing/keyword_abilities/undying.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DiesEvent, ChangeZoneEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class UndyingParser:
    """Parses Undying keyword ability (triggered ability)"""
    
    keyword_name = "undying"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Undying pattern"""
        lower = reminder_text.lower()
        return "dies" in lower and "no +1/+1 counters" in lower and "return it to the battlefield" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Undying reminder text into TriggeredAbility"""
        logger.debug(f"[UndyingParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "dies" not in lower or "no +1/+1 counters" not in lower or "return it to the battlefield" not in lower:
            return []
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="battlefield",
            owner="owner",
            counters={"+1/+1": 1}
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this permanent is put into a graveyard from the battlefield, if it had no +1/+1 counters on it, return it to the battlefield under its owner's control with a +1/+1 counter on it.",
            effects=[return_effect],
            event=DiesEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="no_+1/+1_counters_on_it"
        )
        
        logger.debug(f"[UndyingParser] Created TriggeredAbility for Undying")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Undying keyword without reminder text"""
        logger.debug(f"[UndyingParser] Parsing keyword only: {keyword_text}")
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="battlefield",
            owner="owner",
            counters={"+1/+1": 1}
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this permanent is put into a graveyard from the battlefield, if it had no +1/+1 counters on it, return it to the battlefield under its owner's control with a +1/+1 counter on it.",
            effects=[return_effect],
            event=DiesEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="no_+1/+1_counters_on_it"
        )
        
        logger.debug(f"[UndyingParser] Created TriggeredAbility for Undying")
        
        return [triggered_ability]

