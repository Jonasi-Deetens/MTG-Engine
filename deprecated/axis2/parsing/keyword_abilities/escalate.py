# axis2/parsing/keyword_abilities/escalate.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ParseContext, Effect

logger = logging.getLogger(__name__)

ESCALATE_RE = re.compile(
    r"escalate\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class EscalateParser:
    """Parses Escalate keyword ability (spell modifier for modal spells)"""
    
    keyword_name = "escalate"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Escalate pattern"""
        lower = reminder_text.lower()
        return "mode" in lower and "beyond the first" in lower and "additional" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Escalate reminder text"""
        logger.debug(f"[EscalateParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "mode" not in lower or "beyond the first" not in lower:
            return []
        
        m = ESCALATE_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[EscalateParser] Detected Escalate cost: {cost_text}")
        
        logger.debug(f"[EscalateParser] Detected Escalate")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Escalate keyword without reminder text (e.g., 'Escalate {2}')"""
        logger.debug(f"[EscalateParser] Parsing keyword only: {keyword_text}")
        
        m = ESCALATE_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[EscalateParser] Detected Escalate cost: {cost_text}")
        
        logger.debug(f"[EscalateParser] Detected Escalate")
        
        return []

