# axis2/parsing/keyword_abilities/outlast.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, PutCounterEffect, Subject, ParseContext, Effect, TapCost
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

OUTLAST_RE = re.compile(
    r"outlast\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class OutlastParser:
    """Parses Outlast keyword ability (activated ability)"""
    
    keyword_name = "outlast"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Outlast pattern"""
        lower = reminder_text.lower()
        return "put a +1/+1 counter" in lower and "sorcery" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Outlast reminder text into ActivatedAbility"""
        logger.debug(f"[OutlastParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "put a +1/+1 counter" not in lower:
            return []
        
        m = OUTLAST_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(TapCost())
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[put_counter_effect],
            conditions=[],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[OutlastParser] Created ActivatedAbility for Outlast")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Outlast keyword without reminder text (e.g., 'Outlast {2}{W}')"""
        logger.debug(f"[OutlastParser] Parsing keyword only: {keyword_text}")
        
        m = OUTLAST_RE.search(keyword_text)
        if not m:
            logger.debug(f"[OutlastParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(TapCost())
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[put_counter_effect],
            conditions=[],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[OutlastParser] Created ActivatedAbility for Outlast {cost_text}")
        
        return [activated_ability]

