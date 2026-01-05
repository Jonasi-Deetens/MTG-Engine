# axis2/parsing/keyword_abilities/disturb.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

DISTURB_RE = re.compile(
    r"disturb\s*—\s*(.+)",
    re.IGNORECASE
)


class DisturbParser:
    """Parses Disturb keyword ability (spell modifier)"""
    
    keyword_name = "disturb"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Disturb pattern"""
        lower = reminder_text.lower()
        return "cast this card" in lower and "transformed" in lower and "graveyard" in lower and "disturb cost" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Disturb reminder text"""
        logger.debug(f"[DisturbParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this card" not in lower or "transformed" not in lower or "graveyard" not in lower:
            return []
        
        m = DISTURB_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[DisturbParser] Detected Disturb cost: {cost_text}")
        
        logger.debug(f"[DisturbParser] Detected Disturb")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Disturb keyword without reminder text (e.g., 'Disturb — {1}{U}')"""
        logger.debug(f"[DisturbParser] Parsing keyword only: {keyword_text}")
        
        m = DISTURB_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[DisturbParser] Detected Disturb cost: {cost_text}")
        
        logger.debug(f"[DisturbParser] Detected Disturb")
        
        return []

