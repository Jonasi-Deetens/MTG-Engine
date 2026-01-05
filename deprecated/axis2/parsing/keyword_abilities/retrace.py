# axis2/parsing/keyword_abilities/retrace.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class RetraceParser:
    """Parses Retrace keyword ability (spell modifier)"""
    
    keyword_name = "retrace"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Retrace pattern"""
        lower = reminder_text.lower()
        return "cast this card from your graveyard" in lower and "discarding a land card" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Retrace reminder text"""
        logger.debug(f"[RetraceParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this card from your graveyard" not in lower or "discarding a land card" not in lower:
            return []
        
        logger.debug(f"[RetraceParser] Detected Retrace")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Retrace keyword without reminder text"""
        logger.debug(f"[RetraceParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[RetraceParser] Detected Retrace")
        
        return []

