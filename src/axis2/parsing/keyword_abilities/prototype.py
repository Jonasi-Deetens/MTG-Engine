# axis2/parsing/keyword_abilities/prototype.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class PrototypeParser:
    """Parses Prototype keyword ability (spell modifier)"""
    
    keyword_name = "prototype"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Prototype pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and ("different mana cost" in lower or "different" in lower or "prototype" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Prototype reminder text"""
        logger.debug(f"[PrototypeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower and "prototype" not in lower:
            return []
        
        logger.debug(f"[PrototypeParser] Detected Prototype")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Prototype keyword without reminder text"""
        logger.debug(f"[PrototypeParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[PrototypeParser] Detected Prototype")
        
        return []

