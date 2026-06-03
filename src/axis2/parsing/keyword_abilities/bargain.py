# axis2/parsing/keyword_abilities/bargain.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class BargainParser:
    """Parses Bargain keyword ability (spell modifier)"""
    
    keyword_name = "bargain"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Bargain pattern"""
        lower = reminder_text.lower()
        return "sacrifice" in lower and ("artifact" in lower or "enchantment" in lower or "token" in lower) and "cast this spell" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Bargain reminder text"""
        logger.debug(f"[BargainParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "sacrifice" not in lower or "cast this spell" not in lower:
            return []
        
        logger.debug(f"[BargainParser] Detected Bargain (spell modifier, handled by Axis3)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Bargain keyword without reminder text"""
        logger.debug(f"[BargainParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[BargainParser] Detected Bargain (spell modifier, handled by Axis3)")
        
        return []

