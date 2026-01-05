# axis2/parsing/keyword_abilities/fortify.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ChangeZoneEffect, Subject, ParseContext, Effect, TargetingRules, TargetingRestriction
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

FORTIFY_RE = re.compile(
    r"fortify\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class FortifyParser:
    """Parses Fortify keyword ability (activated ability)"""
    
    keyword_name = "fortify"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Fortify pattern"""
        lower = reminder_text.lower()
        return "attach" in lower and "target land" in lower and ("sorcery" in lower or "fortify only" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Fortify reminder text into ActivatedAbility"""
        logger.debug(f"[FortifyParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attach" not in lower or "target land" not in lower:
            return []
        
        m = FORTIFY_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        attach_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="battlefield",
            owner="owner",
            attach_to="target_land"
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["land"],
            restrictions=[TargetingRestriction(type="controller", conditions=[{"controller": "you"}])]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[attach_effect],
            conditions=[],
            targeting=targeting,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[FortifyParser] Created ActivatedAbility for Fortify")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Fortify keyword without reminder text (e.g., 'Fortify {3}')"""
        logger.debug(f"[FortifyParser] Parsing keyword only: {keyword_text}")
        
        m = FORTIFY_RE.search(keyword_text)
        if not m:
            logger.debug(f"[FortifyParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        attach_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="battlefield",
            owner="owner",
            attach_to="target_land"
        )
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["land"],
            restrictions=[TargetingRestriction(type="controller", conditions=[{"controller": "you"}])]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[attach_effect],
            conditions=[],
            targeting=targeting,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[FortifyParser] Created ActivatedAbility for Fortify {cost_text}")
        
        return [activated_ability]

