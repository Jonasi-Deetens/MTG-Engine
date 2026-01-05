# axis2/parsing/keyword_abilities/offering.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

OFFERING_RE = re.compile(
    r"(\w+)\s+offering",
    re.IGNORECASE
)


class OfferingParser:
    """Parses Offering keyword ability (spell modifier)"""
    
    keyword_name = "offering"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Offering pattern"""
        lower = reminder_text.lower()
        return "sacrifice" in lower and "cast this card" in lower and "instant" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Offering reminder text"""
        logger.debug(f"[OfferingParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "sacrifice" not in lower or "cast this card" not in lower:
            return []
        
        m = OFFERING_RE.search(reminder_text)
        if not m:
            return []
        
        offering_type = m.group(1).strip()
        
        logger.debug(f"[OfferingParser] Detected {offering_type} offering")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Offering keyword without reminder text (e.g., 'Rat offering')"""
        logger.debug(f"[OfferingParser] Parsing keyword only: {keyword_text}")
        
        m = OFFERING_RE.search(keyword_text)
        if not m:
            logger.debug(f"[OfferingParser] No offering type found in keyword text")
            return []
        
        offering_type = m.group(1).strip()
        
        logger.debug(f"[OfferingParser] Detected {offering_type} offering")
        
        return []

