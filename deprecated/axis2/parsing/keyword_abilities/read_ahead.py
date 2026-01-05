# axis2/parsing/keyword_abilities/read_ahead.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class ReadAheadParser:
    """Parses Read Ahead keyword ability (replacement effect for Sagas)"""
    
    keyword_name = "read ahead"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Read Ahead pattern"""
        lower = reminder_text.lower()
        return "choose a chapter" in lower and "lore counter" in lower and ("saga" in lower or "read ahead" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Read Ahead reminder text into ReplacementEffect"""
        logger.debug(f"[ReadAheadParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "choose" not in lower or "lore counter" not in lower:
            return []
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "lore",
                "amount": "chosen_number_from_one_to_final_chapter",
                "condition": "may_choose"
            },
            zones=["battlefield"]
        )
        
        logger.debug(f"[ReadAheadParser] Created ReplacementEffect for Read Ahead")
        
        return [replacement_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Read Ahead keyword without reminder text"""
        logger.debug(f"[ReadAheadParser] Parsing keyword only: {keyword_text}")
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "lore",
                "amount": "chosen_number_from_one_to_final_chapter",
                "condition": "may_choose"
            },
            zones=["battlefield"]
        )
        
        logger.debug(f"[ReadAheadParser] Created ReplacementEffect for Read Ahead")
        
        return [replacement_effect]

