# axis2/parsing/keyword_abilities/awaken.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

AWAKEN_RE = re.compile(
    r"awaken\s+(\d+)\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class AwakenParser:
    """Parses Awaken keyword ability (spell modifier)"""
    
    keyword_name = "awaken"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Awaken pattern"""
        lower = reminder_text.lower()
        return "cast this card" in lower and "awaken cost" in lower and "land" in lower and "becomes" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Awaken reminder text"""
        logger.debug(f"[AwakenParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this card" not in lower or "awaken cost" not in lower:
            return []
        
        m = AWAKEN_RE.search(reminder_text)
        if m:
            awaken_value = m.group(1)
            cost_text = m.group(2).strip()
            logger.debug(f"[AwakenParser] Detected Awaken {awaken_value} with cost: {cost_text}")
        
        logger.debug(f"[AwakenParser] Detected Awaken")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Awaken keyword without reminder text (e.g., 'Awaken 3—{5}{W}')"""
        logger.debug(f"[AwakenParser] Parsing keyword only: {keyword_text}")
        
        m = AWAKEN_RE.search(keyword_text)
        if m:
            awaken_value = m.group(1)
            cost_text = m.group(2).strip()
            logger.debug(f"[AwakenParser] Detected Awaken {awaken_value} with cost: {cost_text}")
        
        logger.debug(f"[AwakenParser] Detected Awaken")
        
        return []

