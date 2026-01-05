# axis2/parsing/keyword_abilities/cleave.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

CLEAVE_RE = re.compile(
    r"cleave\s+(.+)",
    re.IGNORECASE
)


class CleaveParser:
    """Parses Cleave keyword ability (spell modifier)"""
    
    keyword_name = "cleave"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Cleave pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "cleave cost" in lower and "remove" in lower and "square brackets" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cleave reminder text"""
        logger.debug(f"[CleaveParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "cleave cost" not in lower:
            return []
        
        m = CLEAVE_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[CleaveParser] Detected Cleave cost: {cost_text}")
        
        logger.debug(f"[CleaveParser] Detected Cleave")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cleave keyword without reminder text (e.g., 'Cleave {1}{B}{B}{G}')"""
        logger.debug(f"[CleaveParser] Parsing keyword only: {keyword_text}")
        
        m = CLEAVE_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[CleaveParser] Detected Cleave cost: {cost_text}")
        
        logger.debug(f"[CleaveParser] Detected Cleave")
        
        return []

