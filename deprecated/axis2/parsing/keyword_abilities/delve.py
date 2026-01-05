# axis2/parsing/keyword_abilities/delve.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class DelveParser:
    """Parses Delve keyword ability (spell modifier)"""
    
    keyword_name = "delve"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Delve pattern"""
        lower = reminder_text.lower()
        return "exile" in lower and "graveyard" in lower and "casting this spell" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Delve reminder text"""
        logger.debug(f"[DelveParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exile" not in lower or "graveyard" not in lower:
            return []
        
        logger.debug(f"[DelveParser] Detected Delve")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Delve keyword without reminder text"""
        logger.debug(f"[DelveParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[DelveParser] Detected Delve")
        
        return []

