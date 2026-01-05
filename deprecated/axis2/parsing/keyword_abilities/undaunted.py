# axis2/parsing/keyword_abilities/undaunted.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class UndauntedParser:
    """Parses Undaunted keyword ability (spell modifier)"""
    
    keyword_name = "undaunted"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Undaunted pattern"""
        lower = reminder_text.lower()
        return "costs" in lower and "less" in lower and "opponent" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Undaunted reminder text"""
        logger.debug(f"[UndauntedParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "costs" not in lower or "less" not in lower or "opponent" not in lower:
            return []
        
        logger.debug(f"[UndauntedParser] Detected Undaunted")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Undaunted keyword without reminder text"""
        logger.debug(f"[UndauntedParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[UndauntedParser] Detected Undaunted")
        
        return []

