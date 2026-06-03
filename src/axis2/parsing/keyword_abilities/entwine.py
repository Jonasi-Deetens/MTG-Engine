# axis2/parsing/keyword_abilities/entwine.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

ENTWINE_RE = re.compile(
    r"entwine\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class EntwineParser:
    """Parses Entwine keyword ability (spell modifier with cost)"""
    
    keyword_name = "entwine"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Entwine pattern"""
        lower = reminder_text.lower()
        return "choose all" in lower or "choose both" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Entwine reminder text"""
        logger.debug(f"[EntwineParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "choose all" not in lower and "choose both" not in lower:
            return []
        
        m = ENTWINE_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[EntwineParser] Detected Entwine with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Entwine keyword without reminder text (e.g., 'Entwine — Sacrifice three lands.')"""
        logger.debug(f"[EntwineParser] Parsing keyword only: {keyword_text}")
        
        m = ENTWINE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[EntwineParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[EntwineParser] Detected Entwine with cost: {cost_text}")
        
        return []

