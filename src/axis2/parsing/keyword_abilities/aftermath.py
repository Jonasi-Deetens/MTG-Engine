# axis2/parsing/keyword_abilities/aftermath.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class AftermathParser:
    """Parses Aftermath keyword ability (spell modifier for split cards)"""
    
    keyword_name = "aftermath"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Aftermath pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "graveyard" in lower and "exile" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Aftermath reminder text"""
        logger.debug(f"[AftermathParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "graveyard" not in lower:
            return []
        
        logger.debug(f"[AftermathParser] Detected Aftermath")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Aftermath keyword without reminder text"""
        logger.debug(f"[AftermathParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[AftermathParser] Detected Aftermath")
        
        return []

