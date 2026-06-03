# axis2/parsing/keyword_abilities/replicate.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

REPLICATE_RE = re.compile(
    r"replicate\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class ReplicateParser:
    """Parses Replicate keyword ability (spell modifier)"""
    
    keyword_name = "replicate"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Replicate pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "copy it" in lower and "replicate cost" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Replicate reminder text"""
        logger.debug(f"[ReplicateParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "copy it" not in lower:
            return []
        
        m = REPLICATE_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[ReplicateParser] Detected Replicate with cost: {cost_text}")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Replicate keyword without reminder text (e.g., 'Replicate {R}')"""
        logger.debug(f"[ReplicateParser] Parsing keyword only: {keyword_text}")
        
        m = REPLICATE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ReplicateParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        logger.debug(f"[ReplicateParser] Detected Replicate with cost: {cost_text}")
        
        return []

