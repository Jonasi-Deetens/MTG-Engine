# axis2/parsing/keyword_abilities/unleash.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, ContinuousEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class UnleashParser:
    """Parses Unleash keyword ability (two static abilities)"""
    
    keyword_name = "unleash"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Unleash pattern"""
        lower = reminder_text.lower()
        return "enter" in lower and "+1/+1 counter" in lower and "can't block" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Unleash reminder text into ReplacementEffect and ContinuousEffect"""
        logger.debug(f"[UnleashParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enter" not in lower or "+1/+1 counter" not in lower or "can't block" not in lower:
            return []
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": 1, "condition": "may_choose"},
            zones=["battlefield"]
        )
        
        block_restriction = ContinuousEffect(
            kind="blocking_restriction",
            applies_to="self",
            duration="permanent",
            layer=6,
            value={"restriction": "cannot_block_if_has_+1/+1_counter"},
            source_kind="static_ability"
        )
        
        logger.debug(f"[UnleashParser] Created ReplacementEffect and ContinuousEffect for Unleash")
        
        return [replacement_effect, block_restriction]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Unleash keyword without reminder text"""
        logger.debug(f"[UnleashParser] Parsing keyword only: {keyword_text}")
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": 1, "condition": "may_choose"},
            zones=["battlefield"]
        )
        
        block_restriction = ContinuousEffect(
            kind="blocking_restriction",
            applies_to="self",
            duration="permanent",
            layer=6,
            value={"restriction": "cannot_block_if_has_+1/+1_counter"},
            source_kind="static_ability"
        )
        
        logger.debug(f"[UnleashParser] Created ReplacementEffect and ContinuousEffect for Unleash")
        
        return [replacement_effect, block_restriction]

