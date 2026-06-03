# axis2/parsing/keyword_abilities/buyback.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

BUYBACK_COST_RE = re.compile(
    r"buyback\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class BuybackParser:
    """Parses Buyback keyword ability (spell modifier with cost)"""
    
    keyword_name = "buyback"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Buyback pattern"""
        lower = reminder_text.lower()
        return "pay an additional" in lower and "put this spell" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Buyback reminder text"""
        logger.debug(f"[BuybackParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "pay an additional" not in lower or "put this spell" not in lower:
            return []
        
        m = BUYBACK_COST_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[BuybackParser] Detected Buyback with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Buyback keyword without reminder text (e.g., 'Buyback {3}')"""
        logger.debug(f"[BuybackParser] Parsing keyword only: {keyword_text}")
        
        m = BUYBACK_COST_RE.search(keyword_text)
        if not m:
            logger.debug(f"[BuybackParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[BuybackParser] Detected Buyback with cost: {cost_text}")
        
        return []

