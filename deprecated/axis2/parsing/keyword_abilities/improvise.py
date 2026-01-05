# axis2/parsing/keyword_abilities/improvise.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class ImproviseParser:
    """Parses Improvise keyword ability (spell modifier)"""
    
    keyword_name = "improvise"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Improvise pattern"""
        lower = reminder_text.lower()
        return "artifacts" in lower and "cast this spell" in lower and "pay for" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Improvise reminder text"""
        logger.debug(f"[ImproviseParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "artifacts" not in lower or "cast this spell" not in lower:
            return []
        
        logger.debug(f"[ImproviseParser] Detected Improvise")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Improvise keyword without reminder text"""
        logger.debug(f"[ImproviseParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[ImproviseParser] Detected Improvise")
        
        return []

