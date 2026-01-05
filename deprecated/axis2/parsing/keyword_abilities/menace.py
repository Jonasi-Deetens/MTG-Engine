# axis2/parsing/keyword_abilities/menace.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class MenaceParser:
    """Parses Menace keyword ability (simple evasion ability)"""
    
    keyword_name = "menace"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Menace pattern"""
        lower = reminder_text.lower()
        return "can't be blocked" in lower and "two or more creatures" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Menace reminder text"""
        logger.debug(f"[MenaceParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "can't be blocked" not in lower or "two or more creatures" not in lower:
            return []
        
        logger.debug(f"[MenaceParser] Detected Menace")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Menace keyword without reminder text"""
        logger.debug(f"[MenaceParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[MenaceParser] Detected Menace")
        
        return []

