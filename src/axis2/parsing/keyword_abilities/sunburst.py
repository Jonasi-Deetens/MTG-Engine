# axis2/parsing/keyword_abilities/sunburst.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class SunburstParser:
    """Parses Sunburst keyword ability (replacement effect)"""
    
    keyword_name = "sunburst"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Sunburst pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and ("+1/+1 counter" in lower or "charge counter" in lower) and "color of mana" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Sunburst reminder text into ReplacementEffect"""
        logger.debug(f"[SunburstParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower or ("+1/+1 counter" not in lower and "charge counter" not in lower):
            return []
        
        counter_type = "+1/+1" if "+1/+1 counter" in lower else "charge"
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": counter_type,
                "amount": "colors_of_mana_spent",
                "condition": "cast_from_stack"
            },
            zones=["battlefield"]
        )
        
        logger.debug(f"[SunburstParser] Created ReplacementEffect for Sunburst")
        
        return [replacement_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Sunburst keyword without reminder text"""
        logger.debug(f"[SunburstParser] Parsing keyword only: {keyword_text}")
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "+1/+1",
                "amount": "colors_of_mana_spent",
                "condition": "cast_from_stack"
            },
            zones=["battlefield"]
        )
        
        logger.debug(f"[SunburstParser] Created ReplacementEffect for Sunburst")
        
        return [replacement_effect]

