# axis2/parsing/keyword_abilities/convoke.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)


class ConvokeParser:
    """Parses Convoke keyword ability (spell modifier)"""
    
    keyword_name = "convoke"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Convoke pattern"""
        lower = reminder_text.lower()
        return "tap" in lower and "creature" in lower and "cast this spell" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Convoke reminder text"""
        logger.debug(f"[ConvokeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "tap" not in lower or "creature" not in lower:
            return []
        
        logger.debug(f"[ConvokeParser] Detected Convoke")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Convoke keyword without reminder text"""
        logger.debug(f"[ConvokeParser] Parsing keyword only: {keyword_text}")
        
        logger.debug(f"[ConvokeParser] Detected Convoke")
        
        return []

