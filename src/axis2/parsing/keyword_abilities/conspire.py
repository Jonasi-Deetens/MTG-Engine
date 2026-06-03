# axis2/parsing/keyword_abilities/conspire.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class ConspireParser:
    """Parses Conspire keyword ability (spell modifier)"""
    
    keyword_name = "conspire"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Conspire pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "tap two" in lower and "copy it" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Conspire reminder text"""
        logger.debug(f"[ConspireParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "tap two" not in lower:
            return []
        
        logger.debug(f"[ConspireParser] Detected Conspire")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Conspire keyword without reminder text"""
        logger.debug(f"[ConspireParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[ConspireParser] Detected Conspire")
        
        return []

