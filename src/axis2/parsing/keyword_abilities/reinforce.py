# axis2/parsing/keyword_abilities/reinforce.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, PutCounterEffect, Subject, ParseContext, Effect, TargetingRules, DiscardCost
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

REINFORCE_RE = re.compile(
    r"reinforce\s+(\d+)\s*—\s*(.+)",
    re.IGNORECASE
)


class ReinforceParser:
    """Parses Reinforce keyword ability (activated ability from hand)"""
    
    keyword_name = "reinforce"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Reinforce pattern"""
        lower = reminder_text.lower()
        return "discard this card" in lower and "+1/+1 counter" in lower and "target creature" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Reinforce reminder text into ActivatedAbility"""
        logger.debug(f"[ReinforceParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "discard this card" not in lower or "+1/+1 counter" not in lower:
            return []
        
        m = REINFORCE_RE.search(reminder_text)
        if not m:
            return []
        
        reinforce_value = int(m.group(1))
        cost_text = m.group(2).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(DiscardCost(amount=1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=reinforce_value
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"],
            restrictions=[]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[put_counter_effect],
            conditions=[],
            targeting=targeting,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[ReinforceParser] Created ActivatedAbility for Reinforce {reinforce_value}")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Reinforce keyword without reminder text (e.g., 'Reinforce 1 — {1}{W}')"""
        logger.debug(f"[ReinforceParser] Parsing keyword only: {keyword_text}")
        
        m = REINFORCE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ReinforceParser] No reinforce value or cost found in keyword text")
            return []
        
        reinforce_value = int(m.group(1))
        cost_text = m.group(2).strip()
        
        costs = parse_cost_string(cost_text)
        costs.append(DiscardCost(amount=1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=reinforce_value
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"],
            restrictions=[]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[put_counter_effect],
            conditions=[],
            targeting=targeting,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[ReinforceParser] Created ActivatedAbility for Reinforce {reinforce_value} {cost_text}")
        
        return [activated_ability]

