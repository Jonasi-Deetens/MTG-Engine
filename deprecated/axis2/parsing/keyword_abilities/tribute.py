# axis2/parsing/keyword_abilities/tribute.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, TriggeredAbility, EntersBattlefieldEvent, PutCounterEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

TRIBUTE_RE = re.compile(
    r"tribute\s+(\d+)",
    re.IGNORECASE
)


class TributeParser:
    """Parses Tribute keyword ability (static ability + triggered abilities)"""
    
    keyword_name = "tribute"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Tribute pattern"""
        lower = reminder_text.lower()
        return "enters the battlefield" in lower and "opponent" in lower and "+1/+1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Tribute reminder text into ReplacementEffect"""
        logger.debug(f"[TributeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters the battlefield" not in lower or "opponent" not in lower:
            return []
        
        m = TRIBUTE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[TributeParser] No tribute value found in reminder text")
            return []
        
        tribute_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": tribute_value, "condition": "opponent_may_choose"},
            zones=["battlefield"]
        )
        
        logger.debug(f"[TributeParser] Created ReplacementEffect for Tribute {tribute_value}")
        
        return [replacement_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Tribute keyword without reminder text (e.g., 'Tribute 3')"""
        logger.debug(f"[TributeParser] Parsing keyword only: {keyword_text}")
        
        m = TRIBUTE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[TributeParser] No tribute value found in keyword text")
            return []
        
        tribute_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": tribute_value, "condition": "opponent_may_choose"},
            zones=["battlefield"]
        )
        
        logger.debug(f"[TributeParser] Created ReplacementEffect for Tribute {tribute_value}")
        
        return [replacement_effect]

