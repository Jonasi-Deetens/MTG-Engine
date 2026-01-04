# axis2/parsing/keyword_abilities/fuse.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class FuseParser:
    """Parses Fuse keyword ability (spell modifier for split cards)"""
    
    keyword_name = "fuse"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Fuse pattern"""
        lower = reminder_text.lower()
        return "cast both halves" in lower or "split card" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Fuse reminder text"""
        logger.debug(f"[FuseParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast both halves" not in lower and "split card" not in lower:
            return []
        
        logger.debug(f"[FuseParser] Detected Fuse")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Fuse keyword without reminder text"""
        logger.debug(f"[FuseParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[FuseParser] Detected Fuse")
        
        return []

