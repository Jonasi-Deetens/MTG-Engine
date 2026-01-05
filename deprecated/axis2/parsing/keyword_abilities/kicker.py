# axis2/parsing/keyword_abilities/kicker.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

KICKER_RE = re.compile(
    r"(?:multi)?kicker\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class KickerParser:
    """Parses Kicker keyword ability (spell modifier with cost)"""
    
    keyword_name = "kicker"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Kicker pattern"""
        lower = reminder_text.lower()
        return "pay an additional" in lower and "cast this spell" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Kicker reminder text"""
        logger.debug(f"[KickerParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "pay an additional" not in lower or "cast this spell" not in lower:
            return []
        
        m = KICKER_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[KickerParser] Detected Kicker with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Kicker keyword without reminder text (e.g., 'Kicker {2}{B}')"""
        logger.debug(f"[KickerParser] Parsing keyword only: {keyword_text}")
        
        m = KICKER_RE.search(keyword_text)
        if not m:
            logger.debug(f"[KickerParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[KickerParser] Detected Kicker with cost: {cost_text}")
        
        return []


class MultikickerParser:
    """Parses Multikicker keyword ability (spell modifier with cost)"""
    
    keyword_name = "multikicker"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Multikicker pattern"""
        lower = reminder_text.lower()
        return "pay an additional" in lower and "any number of times" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Multikicker reminder text"""
        logger.debug(f"[MultikickerParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "pay an additional" not in lower or "any number of times" not in lower:
            return []
        
        m = KICKER_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[MultikickerParser] Detected Multikicker with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Multikicker keyword without reminder text (e.g., 'Multikicker {1}{R}')"""
        logger.debug(f"[MultikickerParser] Parsing keyword only: {keyword_text}")
        
        m = KICKER_RE.search(keyword_text)
        if not m:
            logger.debug(f"[MultikickerParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[MultikickerParser] Detected Multikicker with cost: {cost_text}")
        
        return []

