# axis2/parsing/keyword_abilities/compleated.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class CompleatedParser:
    """Parses Compleated keyword ability (replacement effect)"""
    
    keyword_name = "compleated"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Compleated pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and "loyalty counter" in lower and "phyrexian mana" in lower or "pay life" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Compleated reminder text into ReplacementEffect"""
        logger.debug(f"[CompleatedParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower or "loyalty counter" not in lower:
            return []
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "loyalty",
                "amount": "loyalty_counters_minus_two_per_phyrexian_mana_paid_with_life"
            },
            zones=["battlefield"]
        )
        
        logger.debug(f"[CompleatedParser] Created ReplacementEffect for Compleated")
        
        return [replacement_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Compleated keyword without reminder text"""
        logger.debug(f"[CompleatedParser] Parsing keyword only: {keyword_text}")
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "loyalty",
                "amount": "loyalty_counters_minus_two_per_phyrexian_mana_paid_with_life"
            },
            zones=["battlefield"]
        )
        
        logger.debug(f"[CompleatedParser] Created ReplacementEffect for Compleated")
        
        return [replacement_effect]

