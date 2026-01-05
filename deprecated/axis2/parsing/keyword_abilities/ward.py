# axis2/parsing/keyword_abilities/ward.py

from typing import List, Optional
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, CounterSpellEffect, ParseContext, Effect

logger = logging.getLogger(__name__)

WARD_COST_RE = re.compile(
    r"ward\s*(?:—|-)?\s*(\{[^}]+\}|pay\s+(\d+)\s+life|discard\s+(?:a|an|\d+)\s+cards?|sacrifice\s+.*?|collect\s+evidence)",
    re.IGNORECASE
)


class WardParser:
    """Parses Ward keyword ability (triggered ability with cost)"""
    
    keyword_name = "ward"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Ward pattern"""
        lower = reminder_text.lower()
        return "becomes the target" in lower and "counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ward reminder text into TriggeredAbility"""
        logger.debug(f"[WardParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "becomes the target" not in lower or "counter" not in lower:
            return []
        
        cost_text = None
        m = WARD_COST_RE.search(reminder_text)
        if m:
            cost_text = m.group(1) or m.group(0)
        
        condition_text = "Whenever this permanent becomes the target of a spell or ability an opponent controls"
        
        effect = CounterSpellEffect(target="that_spell")
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[effect],
            event="becomes_target",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[WardParser] Created TriggeredAbility for Ward")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ward keyword without reminder text (e.g., 'Ward {2}')"""
        logger.debug(f"[WardParser] Parsing keyword only: {keyword_text}")
        
        m = WARD_COST_RE.search(keyword_text)
        if not m:
            logger.debug(f"[WardParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1) or m.group(0)
        
        condition_text = "Whenever this permanent becomes the target of a spell or ability an opponent controls"
        effect = CounterSpellEffect(target="that_spell")
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[effect],
            event="becomes_target",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[WardParser] Created TriggeredAbility for Ward {cost_text}")
        
        return [triggered_ability]

