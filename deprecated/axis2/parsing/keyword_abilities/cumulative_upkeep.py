# axis2/parsing/keyword_abilities/cumulative_upkeep.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, PutCounterEffect, ParseContext, Effect, Subject, ChangeZoneEffect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

CUMULATIVE_UPKEEP_RE = re.compile(
    r"cumulative\s+upkeep\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class CumulativeUpkeepParser:
    """Parses Cumulative upkeep keyword ability (triggered ability with cost)"""
    
    keyword_name = "cumulative upkeep"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Cumulative upkeep pattern"""
        lower = reminder_text.lower()
        return "age counter" in lower and "upkeep" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cumulative upkeep reminder text into TriggeredAbility"""
        logger.debug(f"[CumulativeUpkeepParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "age counter" not in lower or "upkeep" not in lower:
            return []
        
        m = CUMULATIVE_UPKEEP_RE.search(reminder_text)
        cost_text = None
        if m:
            cost_text = m.group(1).strip()
        
        condition_text = "At the beginning of your upkeep, if this permanent is on the battlefield"
        
        effects = [
            PutCounterEffect(counter_type="age", amount=1)
        ]
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=effects,
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        
        logger.debug(f"[CumulativeUpkeepParser] Created TriggeredAbility for Cumulative upkeep")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Cumulative upkeep keyword without reminder text (e.g., 'Cumulative upkeep {G}')"""
        logger.debug(f"[CumulativeUpkeepParser] Parsing keyword only: {keyword_text}")
        
        m = CUMULATIVE_UPKEEP_RE.search(keyword_text)
        if not m:
            logger.debug(f"[CumulativeUpkeepParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        condition_text = "At the beginning of your upkeep, if this permanent is on the battlefield"
        
        effects = [
            PutCounterEffect(counter_type="age", amount=1)
        ]
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=effects,
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        
        logger.debug(f"[CumulativeUpkeepParser] Created TriggeredAbility for Cumulative upkeep {cost_text}")
        
        return [triggered_ability]

