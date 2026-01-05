# axis2/parsing/keyword_abilities/changeling.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class ChangelingParser:
    """Parses Changeling keyword ability (characteristic-defining, no parsing needed)"""
    
    keyword_name = "changeling"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Changeling pattern"""
        lower = reminder_text.lower()
        return "every creature type" in lower or "all creature types" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Changeling reminder text"""
        logger.debug(f"[ChangelingParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "every creature type" not in lower and "all creature types" not in lower:
            return []
        
        logger.debug(f"[ChangelingParser] Detected Changeling (characteristic-defining, no effects needed)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Changeling keyword without reminder text"""
        logger.debug(f"[ChangelingParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[ChangelingParser] Detected Changeling (characteristic-defining, no effects needed)")
        
        return []

