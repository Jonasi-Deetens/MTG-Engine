# axis2/parsing/keyword_abilities/riot.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect, ContinuousEffect, GrantedAbility

logger = logging.getLogger(__name__)


class RiotParser:
    """Parses Riot keyword ability (replacement effect)"""
    
    keyword_name = "riot"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Riot pattern"""
        lower = reminder_text.lower()
        return "enters the battlefield" in lower and ("+1/+1 counter" in lower or "haste" in lower) and ("choice" in lower or "or" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Riot reminder text into ReplacementEffect"""
        logger.debug(f"[RiotParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters the battlefield" not in lower:
            return []
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": 1, "alternative": "haste", "condition": "may_choose"},
            zones=["battlefield"]
        )
        
        haste_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="self",
            duration="permanent",
            layer=6,
            abilities=[GrantedAbility(kind="haste")],
            condition="riot_alternative_chosen",
            source_kind="static_ability"
        )
        
        logger.debug(f"[RiotParser] Created ReplacementEffect and ContinuousEffect for Riot")
        
        return [replacement_effect, haste_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Riot keyword without reminder text"""
        logger.debug(f"[RiotParser] Parsing keyword only: {keyword_text}")
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": 1, "alternative": "haste", "condition": "may_choose"},
            zones=["battlefield"]
        )
        
        haste_effect = ContinuousEffect(
            kind="grant_ability",
            applies_to="self",
            duration="permanent",
            layer=6,
            abilities=[GrantedAbility(kind="haste")],
            condition="riot_alternative_chosen",
            source_kind="static_ability"
        )
        
        logger.debug(f"[RiotParser] Created ReplacementEffect and ContinuousEffect for Riot")
        
        return [replacement_effect, haste_effect]

