# axis2/parsing/keyword_abilities/devoid.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class DevoidParser:
    """Parses Devoid keyword ability (characteristic-defining ability)"""
    
    keyword_name = "devoid"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Devoid pattern"""
        lower = reminder_text.lower()
        return "no color" in lower or "colorless" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Devoid reminder text"""
        logger.debug(f"[DevoidParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "no color" not in lower and "colorless" not in lower:
            return []
        
        logger.debug(f"[DevoidParser] Detected Devoid")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Devoid keyword without reminder text"""
        logger.debug(f"[DevoidParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[DevoidParser] Detected Devoid")
        
        return []

