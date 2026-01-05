# axis2/parsing/keyword_abilities/boast.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

BOAST_RE = re.compile(
    r"boast\s*—\s*(.+?):\s*(.+)",
    re.IGNORECASE
)


class BoastParser:
    """Parses Boast keyword ability (special activated ability)"""
    
    keyword_name = "boast"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Boast pattern"""
        lower = reminder_text.lower()
        return "activate this ability" in lower and "attacked this turn" in lower and "once each turn" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Boast reminder text"""
        logger.debug(f"[BoastParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "activate this ability" not in lower or "attacked this turn" not in lower:
            return []
        
        logger.debug(f"[BoastParser] Detected Boast")
        
        return []
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Boast keyword without reminder text (e.g., 'Boast — {1}: ...')"""
        logger.debug(f"[BoastParser] Parsing keyword only: {keyword_text}")
        
        m = BOAST_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            effect_text = m.group(2).strip()
            logger.debug(f"[BoastParser] Detected Boast cost: {cost_text}, effect: {effect_text[:50]}")
        
        logger.debug(f"[BoastParser] Detected Boast")
        
        return []

