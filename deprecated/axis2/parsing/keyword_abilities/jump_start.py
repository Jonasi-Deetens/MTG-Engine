# axis2/parsing/keyword_abilities/jump_start.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class JumpStartParser:
    """Parses Jump-Start keyword ability (spell modifier)"""
    
    keyword_name = "jump-start"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Jump-Start pattern"""
        lower = reminder_text.lower()
        return "cast this card" in lower and "graveyard" in lower and "discarding a card" in lower and "exile" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Jump-Start reminder text"""
        logger.debug(f"[JumpStartParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this card" not in lower or "graveyard" not in lower or "discarding a card" not in lower:
            return []
        
        logger.debug(f"[JumpStartParser] Detected Jump-Start")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Jump-Start keyword without reminder text"""
        logger.debug(f"[JumpStartParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[JumpStartParser] Detected Jump-Start")
        
        return []

