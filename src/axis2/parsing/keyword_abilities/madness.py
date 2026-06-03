# axis2/parsing/keyword_abilities/madness.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

MADNESS_RE = re.compile(
    r"madness\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class MadnessParser:
    """Parses Madness keyword ability (spell modifier with cost)"""
    
    keyword_name = "madness"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Madness pattern"""
        lower = reminder_text.lower()
        return "discard this card" in lower and "madness cost" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Madness reminder text"""
        logger.debug(f"[MadnessParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "discard this card" not in lower or "madness cost" not in lower:
            return []
        
        m = MADNESS_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[MadnessParser] Detected Madness with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Madness keyword without reminder text (e.g., 'Madness {1}{B}')"""
        logger.debug(f"[MadnessParser] Parsing keyword only: {keyword_text}")
        
        m = MADNESS_RE.search(keyword_text)
        if not m:
            logger.debug(f"[MadnessParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[MadnessParser] Detected Madness with cost: {cost_text}")
        
        return []

