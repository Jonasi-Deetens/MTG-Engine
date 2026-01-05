# axis2/parsing/keyword_abilities/skulk.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class SkulkParser:
    """Parses Skulk keyword ability (simple evasion ability)"""
    
    keyword_name = "skulk"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Skulk pattern"""
        lower = reminder_text.lower()
        return "can't be blocked" in lower and "greater power" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Skulk reminder text"""
        logger.debug(f"[SkulkParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "can't be blocked" not in lower or "greater power" not in lower:
            return []
        
        logger.debug(f"[SkulkParser] Detected Skulk")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Skulk keyword without reminder text"""
        logger.debug(f"[SkulkParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[SkulkParser] Detected Skulk")
        
        return []

