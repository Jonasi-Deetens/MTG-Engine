# axis2/parsing/keyword_abilities/decayed.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ContinuousEffect, TriggeredAbility, AttacksEvent, ChangeZoneEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class DecayedParser:
    """Parses Decayed keyword ability (static + triggered ability)"""
    
    keyword_name = "decayed"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Decayed pattern"""
        lower = reminder_text.lower()
        return "can't block" in lower and "attacks" in lower and "sacrifice" in lower and "end of combat" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Decayed reminder text into ContinuousEffect and TriggeredAbility"""
        logger.debug(f"[DecayedParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "can't block" not in lower or "attacks" not in lower or "sacrifice" not in lower:
            return []
        
        blocking_restriction = ContinuousEffect(
            kind="blocking_restriction",
            applies_to="self",
            duration="permanent",
            layer=6,
            sublayer="6a",
            value={"can_block": False},
            source_kind="static_ability"
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this creature attacks, sacrifice it at end of combat.",
            effects=[sacrifice_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[DecayedParser] Created ContinuousEffect and TriggeredAbility for Decayed")
        
        return [blocking_restriction, triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Decayed keyword without reminder text"""
        logger.debug(f"[DecayedParser] Parsing keyword only: {keyword_text}")
        
        blocking_restriction = ContinuousEffect(
            kind="blocking_restriction",
            applies_to="self",
            duration="permanent",
            layer=6,
            sublayer="6a",
            value={"can_block": False},
            source_kind="static_ability"
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this creature attacks, sacrifice it at end of combat.",
            effects=[sacrifice_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[DecayedParser] Created ContinuousEffect and TriggeredAbility for Decayed")
        
        return [blocking_restriction, triggered_ability]

