# axis2/parsing/keyword_abilities/escape.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect, PutCounterEffect

logger = logging.getLogger(__name__)

ESCAPE_RE = re.compile(
    r"escape\s*—\s*(.+)",
    re.IGNORECASE
)

ESCAPE_WITH_COUNTERS_RE = re.compile(
    r"escapes?\s+with\s+(\d+)\s+\+1/\+1\s+counter",
    re.IGNORECASE
)


class EscapeParser:
    """Parses Escape keyword ability (spell modifier + optional replacement effect)"""
    
    keyword_name = "escape"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Escape pattern"""
        lower = reminder_text.lower()
        return "cast this card" in lower and "graveyard" in lower and ("escape cost" in lower or "exile" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Escape reminder text"""
        logger.debug(f"[EscapeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this card" not in lower or "graveyard" not in lower:
            return []
        
        m = ESCAPE_RE.search(reminder_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[EscapeParser] Detected Escape cost: {cost_text}")
        
        effects = []
        
        m_counters = ESCAPE_WITH_COUNTERS_RE.search(reminder_text)
        if m_counters:
            counter_amount = int(m_counters.group(1))
            logger.debug(f"[EscapeParser] Detected 'escapes with {counter_amount} +1/+1 counters'")
            
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                applies_to="self",
                event="enters_battlefield",
                condition="escaped",
                value={"counter_type": "+1/+1", "amount": counter_amount}
            )
            effects.append(replacement_effect)
        
        logger.debug(f"[EscapeParser] Detected Escape")
        
        return effects
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Escape keyword without reminder text (e.g., 'Escape — {3}{G}{G}, Exile four other cards from your graveyard')"""
        logger.debug(f"[EscapeParser] Parsing keyword only: {keyword_text}")
        
        m = ESCAPE_RE.search(keyword_text)
        if m:
            cost_text = m.group(1).strip()
            logger.debug(f"[EscapeParser] Detected Escape cost: {cost_text}")
        
        logger.debug(f"[EscapeParser] Detected Escape")
        
        return []

