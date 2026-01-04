# axis2/parsing/keyword_abilities/affinity.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

AFFINITY_RE = re.compile(
    r"affinity\s+for\s+(.+)",
    re.IGNORECASE
)


class AffinityParser:
    """Parses Affinity keyword ability (spell modifier with cost reduction)"""
    
    keyword_name = "affinity"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Affinity pattern"""
        lower = reminder_text.lower()
        return "costs" in lower and "less to cast" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Affinity reminder text"""
        logger.debug(f"[AffinityParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "costs" not in lower or "less to cast" not in lower:
            return []
        
        m = AFFINITY_RE.search(reminder_text)
        if not m:
            return []
        
        affinity_type = m.group(1).strip()
        
        logger.debug(f"[AffinityParser] Detected Affinity for: {affinity_type}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Affinity keyword without reminder text (e.g., 'Affinity for artifacts')"""
        logger.debug(f"[AffinityParser] Parsing keyword only: {keyword_text}")
        
        m = AFFINITY_RE.search(keyword_text)
        if not m:
            logger.debug(f"[AffinityParser] No affinity type found in keyword text")
            return []
        
        affinity_type = m.group(1).strip()
        
        logger.debug(f"[AffinityParser] Detected Affinity for: {affinity_type}")
        
        return []

