# axis2/parsing/keyword_abilities/scavenge.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, PutCounterEffect, ChangeZoneEffect, Subject, ParseContext, Effect, TargetingRules
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

SCAVENGE_RE = re.compile(
    r"scavenge\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class ScavengeParser:
    """Parses Scavenge keyword ability (activated ability from graveyard)"""
    
    keyword_name = "scavenge"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Scavenge pattern"""
        lower = reminder_text.lower()
        return "exile this card" in lower and "graveyard" in lower and "+1/+1 counter" in lower and "power" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Scavenge reminder text into ActivatedAbility"""
        logger.debug(f"[ScavengeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exile this card" not in lower or "graveyard" not in lower:
            return []
        
        m = SCAVENGE_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        # Note: Exiling this card from graveyard is part of the cost
        # This is handled by Axis3 during cost payment
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount="power_of_exiled_card",
            subject=Subject(scope="target", types=["creature"])
        )
        
        targeting = TargetingRules(required=True, min=1, max=1, legal_targets=["creature"])
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[put_counter_effect],
            conditions=[{"exile_from_graveyard": True}],  # Exile this card from graveyard as part of cost
            targeting=targeting,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[ScavengeParser] Created ActivatedAbility for Scavenge")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Scavenge keyword without reminder text (e.g., 'Scavenge {3}{B}{G}')"""
        logger.debug(f"[ScavengeParser] Parsing keyword only: {keyword_text}")
        
        m = SCAVENGE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ScavengeParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        # Note: Exiling this card from graveyard is part of the cost
        # This is handled by Axis3 during cost payment
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount="power_of_exiled_card",
            subject=Subject(scope="target", types=["creature"])
        )
        
        targeting = TargetingRules(required=True, min=1, max=1, legal_targets=["creature"])
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[put_counter_effect],
            conditions=[{"exile_from_graveyard": True}],  # Exile this card from graveyard as part of cost
            targeting=targeting,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[ScavengeParser] Created ActivatedAbility for Scavenge {cost_text}")
        
        return [activated_ability]

