# axis2/parsing/keyword_abilities/freerunning.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

FREERUNNING_RE = re.compile(
    r"freerunning\s+(\{.+?\})",
    re.IGNORECASE
)


class FreerunningParser:
    """Parses Freerunning keyword ability (spell modifier)"""
    
    keyword_name = "freerunning"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Freerunning pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "freerunning cost" in lower and ("assassin" in lower or "commander" in lower) and "combat damage" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Freerunning reminder text"""
        logger.debug(f"[FreerunningParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "freerunning cost" not in lower:
            return []
        
        m = FREERUNNING_RE.search(reminder_text)
        if not m:
            logger.debug(f"[FreerunningParser] No freerunning cost found in reminder text")
            return []
        
        freerunning_cost = m.group(1).strip()
        
        logger.debug(f"[FreerunningParser] Detected Freerunning (spell modifier, handled by Axis3)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Freerunning keyword without reminder text (e.g., 'Freerunning {1}{B}')"""
        logger.debug(f"[FreerunningParser] Parsing keyword only: {keyword_text}")
        
        m = FREERUNNING_RE.search(keyword_text)
        if not m:
            logger.debug(f"[FreerunningParser] No freerunning cost found in keyword text")
            return []
        
        freerunning_cost = m.group(1).strip()
        
        logger.debug(f"[FreerunningParser] Detected Freerunning (spell modifier, handled by Axis3)")
        
        return []

