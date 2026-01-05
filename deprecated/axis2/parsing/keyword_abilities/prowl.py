# axis2/parsing/keyword_abilities/prowl.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

PROWL_RE = re.compile(
    r"prowl\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class ProwlParser:
    """Parses Prowl keyword ability (spell modifier)"""
    
    keyword_name = "prowl"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Prowl pattern"""
        lower = reminder_text.lower()
        return "cast this" in lower and "prowl cost" in lower and "combat damage" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Prowl reminder text"""
        logger.debug(f"[ProwlParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this" not in lower or "prowl cost" not in lower:
            return []
        
        m = PROWL_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[ProwlParser] Detected Prowl with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Prowl keyword without reminder text (e.g., 'Prowl {1}{B}')"""
        logger.debug(f"[ProwlParser] Parsing keyword only: {keyword_text}")
        
        m = PROWL_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ProwlParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[ProwlParser] Detected Prowl with cost: {cost_text}")
        
        return []

