# axis2/parsing/keyword_abilities/haunt.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DiesEvent, ChangeZoneEffect, Subject, ParseContext, Effect, TargetingRules, TargetingRestriction

logger = logging.getLogger(__name__)


class HauntParser:
    """Parses Haunt keyword ability (triggered ability)"""
    
    keyword_name = "haunt"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Haunt pattern"""
        lower = reminder_text.lower()
        return "dies" in lower and "exile it" in lower and "haunting target creature" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Haunt reminder text into TriggeredAbility"""
        logger.debug(f"[HauntParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "dies" not in lower or "exile it" not in lower or "haunting" not in lower:
            return []
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="exile",
            owner="owner"
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"],
            restrictions=[]
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this permanent is put into a graveyard from the battlefield, exile it haunting target creature.",
            effects=[exile_effect],
            event=DiesEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[HauntParser] Created TriggeredAbility for Haunt")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Haunt keyword without reminder text"""
        logger.debug(f"[HauntParser] Parsing keyword only: {keyword_text}")
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="exile",
            owner="owner"
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"],
            restrictions=[]
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this permanent is put into a graveyard from the battlefield, exile it haunting target creature.",
            effects=[exile_effect],
            event=DiesEvent(subject="self"),
            targeting=targeting,
            trigger_filter=None
        )
        
        logger.debug(f"[HauntParser] Created TriggeredAbility for Haunt")
        
        return [triggered_ability]

