# axis2/parsing/keyword_abilities/companion.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class CompanionParser:
    """Parses Companion keyword ability (deck construction keyword)"""
    
    keyword_name = "companion"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Companion pattern"""
        lower = reminder_text.lower()
        return "companion" in lower and ("starting deck" in lower or "outside the game" in lower or "put it into your hand" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Companion reminder text"""
        logger.debug(f"[CompanionParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "companion" not in lower:
            return []
        
        logger.debug(f"[CompanionParser] Detected Companion (deck construction only)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Companion keyword without reminder text (e.g., 'Companion — Your starting deck contains only cards with mana value 3 or greater and land cards.')"""
        logger.debug(f"[CompanionParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[CompanionParser] Detected Companion (deck construction only)")
        
        return []

