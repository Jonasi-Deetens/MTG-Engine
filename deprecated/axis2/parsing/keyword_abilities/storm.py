# axis2/parsing/keyword_abilities/storm.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class StormParser:
    """Parses Storm keyword ability (spell modifier)"""
    
    keyword_name = "storm"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Storm pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "copy it" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Storm reminder text"""
        logger.debug(f"[StormParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "copy it" not in lower:
            return []
        
        logger.debug(f"[StormParser] Detected Storm")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Storm keyword without reminder text"""
        logger.debug(f"[StormParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[StormParser] Detected Storm")
        
        return []

