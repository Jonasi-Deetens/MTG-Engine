# axis2/parsing/keyword_abilities/spree.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class SpreeParser:
    """Parses Spree keyword ability (spell modifier)"""
    
    keyword_name = "spree"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Spree pattern"""
        lower = reminder_text.lower()
        return "choose one or more" in lower and "additional cost" in lower and "modes" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Spree reminder text"""
        logger.debug(f"[SpreeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "choose" not in lower or "modes" not in lower:
            return []
        
        logger.debug(f"[SpreeParser] Detected Spree (spell modifier, handled by Axis3)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Spree keyword without reminder text"""
        logger.debug(f"[SpreeParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[SpreeParser] Detected Spree (spell modifier, handled by Axis3)")
        
        return []

