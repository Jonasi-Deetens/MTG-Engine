# axis2/parsing/keyword_abilities/foretell.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

FORETELL_RE = re.compile(
    r"foretell\s+(.+)",
    re.IGNORECASE
)


class ForetellParser:
    """Parses Foretell keyword ability (special action + spell modifier)"""
    
    keyword_name = "foretell"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Foretell pattern"""
        lower = reminder_text.lower()
        return "exile this card" in lower and "hand" in lower and "face down" in lower and "foretell cost" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Foretell reminder text"""
        logger.debug(f"[ForetellParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exile this card" not in lower or "hand" not in lower or "face down" not in lower:
            return []
        
        m = FORETELL_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[ForetellParser] Detected Foretell cost: {cost_text}")
        
        logger.debug(f"[ForetellParser] Detected Foretell")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Foretell keyword without reminder text (e.g., 'Foretell {2}{G}{G}')"""
        logger.debug(f"[ForetellParser] Parsing keyword only: {keyword_text}")
        
        m = FORETELL_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[ForetellParser] Detected Foretell cost: {cost_text}")
        
        logger.debug(f"[ForetellParser] Detected Foretell")
        
        return []

