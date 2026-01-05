# axis2/parsing/keyword_abilities/bestow.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

BESTOW_RE = re.compile(
    r"bestow\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class BestowParser:
    """Parses Bestow keyword ability (spell modifier)"""
    
    keyword_name = "bestow"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Bestow pattern"""
        lower = reminder_text.lower()
        return "cast this card" in lower and "bestow cost" in lower and "aura" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Bestow reminder text"""
        logger.debug(f"[BestowParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this card" not in lower or "bestow cost" not in lower:
            return []
        
        m = BESTOW_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[BestowParser] Detected Bestow cost: {cost_text}")
        
        logger.debug(f"[BestowParser] Detected Bestow")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Bestow keyword without reminder text (e.g., 'Bestow {5}{U}')"""
        logger.debug(f"[BestowParser] Parsing keyword only: {keyword_text}")
        
        m = BESTOW_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[BestowParser] Detected Bestow cost: {cost_text}")
        
        logger.debug(f"[BestowParser] Detected Bestow")
        
        return []

