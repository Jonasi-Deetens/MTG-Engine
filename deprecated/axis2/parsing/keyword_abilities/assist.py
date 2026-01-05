# axis2/parsing/keyword_abilities/assist.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class AssistParser:
    """Parses Assist keyword ability (spell modifier)"""
    
    keyword_name = "assist"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Assist pattern"""
        lower = reminder_text.lower()
        return "another player" in lower and "pay" in lower and "cost" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Assist reminder text"""
        logger.debug(f"[AssistParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "another player" not in lower or "pay" not in lower:
            return []
        
        logger.debug(f"[AssistParser] Detected Assist")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Assist keyword without reminder text"""
        logger.debug(f"[AssistParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[AssistParser] Detected Assist")
        
        return []

