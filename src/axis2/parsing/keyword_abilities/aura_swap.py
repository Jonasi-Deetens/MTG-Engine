# axis2/parsing/keyword_abilities/aura_swap.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ChangeZoneEffect, Subject, ParseContext, Effect, TargetingRules, TargetingRestriction
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

AURA_SWAP_RE = re.compile(
    r"aura swap\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class AuraSwapParser:
    """Parses Aura Swap keyword ability (activated ability)"""
    
    keyword_name = "aura swap"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Aura Swap pattern"""
        lower = reminder_text.lower()
        return "exchange" in lower and "aura" in lower and "hand" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Aura Swap reminder text into ActivatedAbility"""
        logger.debug(f"[AuraSwapParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exchange" not in lower or "aura" not in lower:
            return []
        
        m = AURA_SWAP_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_to_hand_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="hand",
            owner="owner"
        )
        
        put_onto_battlefield_effect = ChangeZoneEffect(
            subject=Subject(scope="aura_from_hand"),
            from_zone="hand",
            to_zone="battlefield",
            owner="owner"
        )
        
        effects = [return_to_hand_effect, put_onto_battlefield_effect]
        
        targeting = TargetingRules(
            required=False,
            min=0,
            max=1,
            legal_targets=["aura"],
            restrictions=[TargetingRestriction(type="zone", conditions=[{"zone": "hand"}])]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[],
            targeting=targeting,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[AuraSwapParser] Created ActivatedAbility for Aura Swap")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Aura Swap keyword without reminder text (e.g., 'Aura swap {2}{U}')"""
        logger.debug(f"[AuraSwapParser] Parsing keyword only: {keyword_text}")
        
        m = AURA_SWAP_RE.search(keyword_text)
        if not m:
            logger.debug(f"[AuraSwapParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_to_hand_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="hand",
            owner="owner"
        )
        
        put_onto_battlefield_effect = ChangeZoneEffect(
            subject=Subject(scope="aura_from_hand"),
            from_zone="hand",
            to_zone="battlefield",
            owner="owner"
        )
        
        effects = [return_to_hand_effect, put_onto_battlefield_effect]
        
        targeting = TargetingRules(
            required=False,
            min=0,
            max=1,
            legal_targets=["aura"],
            restrictions=[TargetingRestriction(type="zone", conditions=[{"zone": "hand"}])]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[],
            targeting=targeting,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[AuraSwapParser] Created ActivatedAbility for Aura Swap {cost_text}")
        
        return [activated_ability]

