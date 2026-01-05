# axis2/parsing/keyword_abilities/disguise.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

DISGUISE_RE = re.compile(
    r"disguise\s+(\{.+?\})",
    re.IGNORECASE
)


class DisguiseParser:
    """Parses Disguise keyword ability (spell modifier + special action)"""
    
    keyword_name = "disguise"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Disguise pattern"""
        lower = reminder_text.lower()
        return "cast this card face down" in lower and "2/2 creature" in lower and "ward" in lower and "turn it face up" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Disguise reminder text"""
        logger.debug(f"[DisguiseParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this card face down" not in lower or "2/2 creature" not in lower:
            return []
        
        m = DISGUISE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[DisguiseParser] No disguise cost found in reminder text")
            return []
        
        disguise_cost = m.group(1).strip()
        
        logger.debug(f"[DisguiseParser] Detected Disguise (spell modifier + special action, handled by Axis3)")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Disguise keyword without reminder text (e.g., 'Disguise {R/W}{R/W}')"""
        logger.debug(f"[DisguiseParser] Parsing keyword only: {keyword_text}")
        
        m = DISGUISE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[DisguiseParser] No disguise cost found in keyword text")
            return []
        
        disguise_cost = m.group(1).strip()
        
        logger.debug(f"[DisguiseParser] Detected Disguise (spell modifier + special action, handled by Axis3)")
        
        return []

