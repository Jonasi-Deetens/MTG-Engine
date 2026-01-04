# axis2/parsing/keyword_abilities/split_second.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class SplitSecondParser:
    """Parses Split Second keyword ability (spell modifier)"""
    
    keyword_name = "split second"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Split Second pattern"""
        lower = reminder_text.lower()
        return "spell is on the stack" in lower and "can't cast spells" in lower and "activate abilities" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Split Second reminder text"""
        logger.debug(f"[SplitSecondParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "spell is on the stack" not in lower or "can't cast spells" not in lower:
            return []
        
        logger.debug(f"[SplitSecondParser] Detected Split Second")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Split Second keyword without reminder text"""
        logger.debug(f"[SplitSecondParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[SplitSecondParser] Detected Split Second")
        
        return []

