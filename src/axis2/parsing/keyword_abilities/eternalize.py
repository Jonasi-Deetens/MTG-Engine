# axis2/parsing/keyword_abilities/eternalize.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, CreateTokenEffect, ChangeZoneEffect, Subject, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

ETERNALIZE_RE = re.compile(
    r"eternalize\s+(.+)",
    re.IGNORECASE
)


class EternalizeParser:
    """Parses Eternalize keyword ability (activated ability)"""
    
    keyword_name = "eternalize"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Eternalize pattern"""
        lower = reminder_text.lower()
        return "exile this card" in lower and "graveyard" in lower and "create a token" in lower and "copy" in lower and "zombie" in lower and "4/4" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Eternalize reminder text into ActivatedAbility"""
        logger.debug(f"[EternalizeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exile this card" not in lower or "create a token" not in lower or "copy" not in lower:
            return []
        
        m = ETERNALIZE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[EternalizeParser] No eternalize cost found in reminder text")
            return []
        
        cost_text = m.group(1).strip()
        costs = parse_cost_string(cost_text)
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="exile",
            owner="owner"
        )
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "copy_of_self",
                "is_copy": True,
                "power": 4,
                "toughness": 4,
                "colors": ["black"],
                "types": ["creature"],
                "subtypes": ["zombie"],
                "remove_mana_cost": True
            },
            controller="you"
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[exile_effect, create_token_effect],
            conditions=[{"kind": "exile_self_from_graveyard_as_cost"}, {"kind": "activate_only_as_sorcery"}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[EternalizeParser] Created ActivatedAbility for Eternalize")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Eternalize keyword without reminder text (e.g., 'Eternalize {3}{W}{W}')"""
        logger.debug(f"[EternalizeParser] Parsing keyword only: {keyword_text}")
        
        m = ETERNALIZE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[EternalizeParser] No eternalize cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        costs = parse_cost_string(cost_text)
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="graveyard",
            to_zone="exile",
            owner="owner"
        )
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "copy_of_self",
                "is_copy": True,
                "power": 4,
                "toughness": 4,
                "colors": ["black"],
                "types": ["creature"],
                "subtypes": ["zombie"],
                "remove_mana_cost": True
            },
            controller="you"
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[exile_effect, create_token_effect],
            conditions=[{"kind": "exile_self_from_graveyard_as_cost"}, {"kind": "activate_only_as_sorcery"}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[EternalizeParser] Created ActivatedAbility for Eternalize")
        
        return [activated_ability]

