# axis2/parsing/keyword_abilities/solved.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class SolvedParser:
    """Parses Solved keyword ability (conditional ability modifier)"""
    
    keyword_name = "solved"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Solved pattern"""
        lower = reminder_text.lower()
        return "case" in lower and "solved" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Solved reminder text"""
        logger.debug(f"[SolvedParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "solved" not in lower:
            return []
        
        logger.debug(f"[SolvedParser] Detected Solved (conditional ability modifier, handled by Axis3)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Solved keyword without reminder text (e.g., 'Solved — [Ability text]')"""
        logger.debug(f"[SolvedParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[SolvedParser] Detected Solved (conditional ability modifier, handled by Axis3)")
        
        return []

