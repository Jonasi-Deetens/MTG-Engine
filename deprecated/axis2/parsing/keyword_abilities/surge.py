# axis2/parsing/keyword_abilities/surge.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

SURGE_RE = re.compile(
    r"surge\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class SurgeParser:
    """Parses Surge keyword ability (spell modifier)"""
    
    keyword_name = "surge"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Surge pattern"""
        lower = reminder_text.lower()
        return "cast a spell" in lower and "surge cost" in lower and "cast another spell" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Surge reminder text"""
        logger.debug(f"[SurgeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast a spell" not in lower or "surge cost" not in lower:
            return []
        
        m = SURGE_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[SurgeParser] Detected Surge cost: {cost_text}")
        
        logger.debug(f"[SurgeParser] Detected Surge")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Surge keyword without reminder text (e.g., 'Surge {1}{R}')"""
        logger.debug(f"[SurgeParser] Parsing keyword only: {keyword_text}")
        
        m = SURGE_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[SurgeParser] Detected Surge cost: {cost_text}")
        
        logger.debug(f"[SurgeParser] Detected Surge")
        
        return []

