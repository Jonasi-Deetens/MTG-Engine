# axis2/parsing/keyword_abilities/overload.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

OVERLOAD_RE = re.compile(
    r"overload\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class OverloadParser:
    """Parses Overload keyword ability (spell modifier)"""
    
    keyword_name = "overload"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Overload pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "overload cost" in lower and "target" in lower and "each" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Overload reminder text"""
        logger.debug(f"[OverloadParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "overload cost" not in lower:
            return []
        
        m = OVERLOAD_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[OverloadParser] Detected Overload cost: {cost_text}")
        
        logger.debug(f"[OverloadParser] Detected Overload")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Overload keyword without reminder text (e.g., 'Overload {X}{X}{R}{R}')"""
        logger.debug(f"[OverloadParser] Parsing keyword only: {keyword_text}")
        
        m = OVERLOAD_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[OverloadParser] Detected Overload cost: {cost_text}")
        
        logger.debug(f"[OverloadParser] Detected Overload")
        
        return []

