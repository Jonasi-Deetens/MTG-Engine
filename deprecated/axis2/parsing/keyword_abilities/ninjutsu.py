# axis2/parsing/keyword_abilities/ninjutsu.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ChangeZoneEffect, Subject, ParseContext, Effect, TargetingRules, TargetingRestriction
from axis2.parsing.costs import parse_cost_string
from axis2.parsing.targeting import parse_targeting

logger = logging.getLogger(__name__)

NINJUTSU_RE = re.compile(
    r"(?:commander\s+)?ninjutsu\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class NinjutsuParser:
    """Parses Ninjutsu keyword ability (activated ability)"""
    
    keyword_name = "ninjutsu"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Ninjutsu pattern"""
        lower = reminder_text.lower()
        return "return an unblocked" in lower and "put this card onto the battlefield" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ninjutsu reminder text into ActivatedAbility"""
        logger.debug(f"[NinjutsuParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "return an unblocked" not in lower or "put this card onto the battlefield" not in lower:
            return []
        
        m = NINJUTSU_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="target", types=["creature"]),
            from_zone="battlefield",
            to_zone="hand",
            owner="owner"
        )
        
        put_onto_battlefield_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="hand",
            to_zone="battlefield",
            owner="owner",
            tapped=True
        )
        
        effects = [return_effect, put_onto_battlefield_effect]
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"],
            restrictions=[TargetingRestriction(type="combat", conditions=[{"unblocked": True, "attacking": True, "controller": "you"}])]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[],
            targeting=targeting,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[NinjutsuParser] Created ActivatedAbility for Ninjutsu")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ninjutsu keyword without reminder text (e.g., 'Ninjutsu {1}{U}')"""
        logger.debug(f"[NinjutsuParser] Parsing keyword only: {keyword_text}")
        
        m = NINJUTSU_RE.search(keyword_text)
        if not m:
            logger.debug(f"[NinjutsuParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="target", types=["creature"]),
            from_zone="battlefield",
            to_zone="hand",
            owner="owner"
        )
        
        put_onto_battlefield_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="hand",
            to_zone="battlefield",
            owner="owner",
            tapped=True
        )
        
        effects = [return_effect, put_onto_battlefield_effect]
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"],
            restrictions=[TargetingRestriction(type="combat", conditions=[{"unblocked": True, "attacking": True, "controller": "you"}])]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[],
            targeting=targeting,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[NinjutsuParser] Created ActivatedAbility for Ninjutsu {cost_text}")
        
        return [activated_ability]


class CommanderNinjutsuParser:
    """Parses Commander ninjutsu keyword ability (activated ability)"""
    
    keyword_name = "commander ninjutsu"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Commander ninjutsu pattern"""
        lower = reminder_text.lower()
        return "return an unblocked" in lower and ("command zone" in lower or "hand" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Commander ninjutsu reminder text into ActivatedAbility"""
        logger.debug(f"[CommanderNinjutsuParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "return an unblocked" not in lower:
            return []
        
        m = NINJUTSU_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="target", types=["creature"]),
            from_zone="battlefield",
            to_zone="hand",
            owner="owner"
        )
        
        put_onto_battlefield_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="hand",
            to_zone="battlefield",
            owner="owner",
            tapped=True
        )
        
        effects = [return_effect, put_onto_battlefield_effect]
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"],
            restrictions=[TargetingRestriction(type="combat", conditions=[{"unblocked": True, "attacking": True, "controller": "you"}])]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[],
            targeting=targeting,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[CommanderNinjutsuParser] Created ActivatedAbility for Commander ninjutsu")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Commander ninjutsu keyword without reminder text"""
        logger.debug(f"[CommanderNinjutsuParser] Parsing keyword only: {keyword_text}")
        
        m = NINJUTSU_RE.search(keyword_text)
        if not m:
            logger.debug(f"[CommanderNinjutsuParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        return_effect = ChangeZoneEffect(
            subject=Subject(scope="target", types=["creature"]),
            from_zone="battlefield",
            to_zone="hand",
            owner="owner"
        )
        
        put_onto_battlefield_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="hand",
            to_zone="battlefield",
            owner="owner",
            tapped=True
        )
        
        effects = [return_effect, put_onto_battlefield_effect]
        
        targeting = TargetingRules(
            required=True,
            min=1,
            max=1,
            legal_targets=["creature"],
            restrictions=[TargetingRestriction(type="combat", conditions=[{"unblocked": True, "attacking": True, "controller": "you"}])]
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[],
            targeting=targeting,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[CommanderNinjutsuParser] Created ActivatedAbility for Commander ninjutsu {cost_text}")
        
        return [activated_ability]

