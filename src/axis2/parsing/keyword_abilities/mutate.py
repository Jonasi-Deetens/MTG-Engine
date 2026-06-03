# axis2/parsing/keyword_abilities/mutate.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

MUTATE_RE = re.compile(
    r"mutate\s+(.+)",
    re.IGNORECASE
)


class MutateParser:
    """Parses Mutate keyword ability (spell modifier)"""
    
    keyword_name = "mutate"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Mutate pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "mutate cost" in lower and "target non-human creature" in lower and "mutate" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Mutate reminder text"""
        logger.debug(f"[MutateParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "mutate cost" not in lower:
            return []
        
        m = MUTATE_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[MutateParser] Detected Mutate cost: {cost_text}")
        
        logger.debug(f"[MutateParser] Detected Mutate")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Mutate keyword without reminder text (e.g., 'Mutate {2}{W}')"""
        logger.debug(f"[MutateParser] Parsing keyword only: {keyword_text}")
        
        m = MUTATE_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[MutateParser] Detected Mutate cost: {cost_text}")
        
        logger.debug(f"[MutateParser] Detected Mutate")
        
        return []

