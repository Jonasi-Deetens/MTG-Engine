# axis2/parsing/keyword_abilities/craft.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ChangeZoneEffect, Subject, ParseContext, Effect, ManaCost, TargetingRules
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

CRAFT_RE = re.compile(
    r"craft\s+with\s+(.+?)\s+(\{.+?\})",
    re.IGNORECASE
)


class CraftParser:
    """Parses Craft keyword ability (activated ability)"""
    
    keyword_name = "craft"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Craft pattern"""
        lower = reminder_text.lower()
        return "exile this" in lower and "exile" in lower and ("permanents you control" in lower or "cards in your graveyard" in lower) and "return this card" in lower and "transformed" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Craft reminder text into ActivatedAbility"""
        logger.debug(f"[CraftParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exile this" not in lower or "return this card" not in lower or "transformed" not in lower:
            return []
        
        m = CRAFT_RE.search(reminder_text)
        if not m:
            logger.debug(f"[CraftParser] No craft cost found in reminder text")
            return []
        
        materials_text = m.group(1).strip()
        cost_text = m.group(2).strip()
        
        costs = parse_cost_string(cost_text)
        
        exile_self_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="exile"
        )
        
        exile_materials_effect = ChangeZoneEffect(
            subject=Subject(scope="materials_from_permanents_or_graveyard"),
            from_zone=None,
            to_zone="exile"
        )
        
        return_transformed_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="exile",
            to_zone="battlefield"
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[exile_self_effect, exile_materials_effect, return_transformed_effect],
            conditions=[{"kind": "activate_only_as_sorcery"}, {"kind": "craft_materials", "materials": materials_text}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[CraftParser] Created ActivatedAbility for Craft")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Craft keyword without reminder text (e.g., 'Craft with artifact {3}{W}')"""
        logger.debug(f"[CraftParser] Parsing keyword only: {keyword_text}")
        
        m = CRAFT_RE.search(keyword_text)
        if not m:
            logger.debug(f"[CraftParser] No craft cost found in keyword text")
            return []
        
        materials_text = m.group(1).strip()
        cost_text = m.group(2).strip()
        
        costs = parse_cost_string(cost_text)
        
        exile_self_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="exile"
        )
        
        exile_materials_effect = ChangeZoneEffect(
            subject=Subject(scope="materials_from_permanents_or_graveyard"),
            from_zone=None,
            to_zone="exile"
        )
        
        return_transformed_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="exile",
            to_zone="battlefield"
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[exile_self_effect, exile_materials_effect, return_transformed_effect],
            conditions=[{"kind": "activate_only_as_sorcery"}, {"kind": "craft_materials", "materials": materials_text}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[CraftParser] Created ActivatedAbility for Craft")
        
        return [activated_ability]

