# axis2/parsing/keyword_abilities/gift.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

GIFT_RE = re.compile(
    r"gift\s+a\s+(\w+)",
    re.IGNORECASE
)


class GiftParser:
    """Parses Gift keyword ability (spell modifier)"""
    
    keyword_name = "gift"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Gift pattern"""
        lower = reminder_text.lower()
        return "promise" in lower and "opponent" in lower and "gift" in lower and ("cast this spell" in lower or "enters" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Gift reminder text"""
        logger.debug(f"[GiftParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "promise" not in lower or "opponent" not in lower or "gift" not in lower:
            return []
        
        m = GIFT_RE.search(reminder_text)
        if not m:
            logger.debug(f"[GiftParser] No gift type found in reminder text")
            return []
        
        gift_type = m.group(1).strip()
        
        logger.debug(f"[GiftParser] Detected Gift (spell modifier, handled by Axis3)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Gift keyword without reminder text (e.g., 'Gift a Food', 'Gift a card')"""
        logger.debug(f"[GiftParser] Parsing keyword only: {keyword_text}")
        
        m = GIFT_RE.search(keyword_text)
        if not m:
            logger.debug(f"[GiftParser] No gift type found in keyword text")
            return []
        
        gift_type = m.group(1).strip()
        
        logger.debug(f"[GiftParser] Detected Gift (spell modifier, handled by Axis3)")
        
        return []

