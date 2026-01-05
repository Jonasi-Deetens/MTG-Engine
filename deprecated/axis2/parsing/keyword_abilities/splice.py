# axis2/parsing/keyword_abilities/splice.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

SPLICE_RE = re.compile(
    r"splice\s+onto\s+(\w+)\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class SpliceParser:
    """Parses Splice keyword ability (spell modifier)"""
    
    keyword_name = "splice"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Splice pattern"""
        lower = reminder_text.lower()
        return "cast an" in lower and "reveal this card" in lower and "add this card's effects" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Splice reminder text"""
        logger.debug(f"[SpliceParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast an" not in lower or "reveal this card" not in lower:
            return []
        
        m = SPLICE_RE.search(reminder_text)
        if not m:
            return []
        
        splice_type = m.group(1).strip()
        cost_text = m.group(2).strip()
        
        logger.debug(f"[SpliceParser] Detected Splice onto {splice_type} with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Splice keyword without reminder text (e.g., 'Splice onto Arcane {1}{R}')"""
        logger.debug(f"[SpliceParser] Parsing keyword only: {keyword_text}")
        
        m = SPLICE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[SpliceParser] No splice type or cost found in keyword text")
            return []
        
        splice_type = m.group(1).strip()
        cost_text = m.group(2).strip()
        
        logger.debug(f"[SpliceParser] Detected Splice onto {splice_type} with cost: {cost_text}")
        
        return []

