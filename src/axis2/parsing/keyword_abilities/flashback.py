# axis2/parsing/keyword_abilities/flashback.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

FLASHBACK_RE = re.compile(
    r"flashback\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class FlashbackParser:
    """Parses Flashback keyword ability (spell modifier with cost)"""
    
    keyword_name = "flashback"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Flashback pattern"""
        lower = reminder_text.lower()
        return "cast this card from your graveyard" in lower or "flashback cost" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Flashback reminder text"""
        logger.debug(f"[FlashbackParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this card from your graveyard" not in lower and "flashback cost" not in lower:
            return []
        
        m = FLASHBACK_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[FlashbackParser] Detected Flashback with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Flashback keyword without reminder text (e.g., 'Flashback {G}')"""
        logger.debug(f"[FlashbackParser] Parsing keyword only: {keyword_text}")
        
        m = FLASHBACK_RE.search(keyword_text)
        if not m:
            logger.debug(f"[FlashbackParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[FlashbackParser] Detected Flashback with cost: {cost_text}")
        
        return []

