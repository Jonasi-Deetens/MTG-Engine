# axis2/parsing/keyword_abilities/emerge.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

EMERGE_RE = re.compile(
    r"emerge\s*(?:from\s+[^—]+)?\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class EmergeParser:
    """Parses Emerge keyword ability (spell modifier)"""
    
    keyword_name = "emerge"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Emerge pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "sacrificing" in lower and "emerge cost" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Emerge reminder text"""
        logger.debug(f"[EmergeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "sacrificing" not in lower:
            return []
        
        m = EMERGE_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[EmergeParser] Detected Emerge cost: {cost_text}")
        
        logger.debug(f"[EmergeParser] Detected Emerge")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Emerge keyword without reminder text (e.g., 'Emerge {6}{G}{G}{G}')"""
        logger.debug(f"[EmergeParser] Parsing keyword only: {keyword_text}")
        
        m = EMERGE_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[EmergeParser] Detected Emerge cost: {cost_text}")
        
        logger.debug(f"[EmergeParser] Detected Emerge")
        
        return []

