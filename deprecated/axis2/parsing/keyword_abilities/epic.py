# axis2/parsing/keyword_abilities/epic.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class EpicParser:
    """Parses Epic keyword ability (spell modifier)"""
    
    keyword_name = "epic"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Epic pattern"""
        lower = reminder_text.lower()
        return "can't cast spells" in lower and "beginning of each of your upkeeps" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Epic reminder text"""
        logger.debug(f"[EpicParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "can't cast spells" not in lower or "beginning of each of your upkeeps" not in lower:
            return []
        
        logger.debug(f"[EpicParser] Detected Epic")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Epic keyword without reminder text"""
        logger.debug(f"[EpicParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[EpicParser] Detected Epic")
        
        return []

