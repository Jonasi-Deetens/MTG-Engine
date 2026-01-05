# axis2/parsing/keyword_abilities/equip.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string
from axis2.parsing.effects.dispatcher import parse_effect_text
from axis2.parsing.targeting import parse_targeting

logger = logging.getLogger(__name__)

EQUIP_COST_RE = re.compile(
    r"equip\s+(?:planeswalker\s+)?(\{[^}]+\}(?:\s*\{[^}]+\})*)",
    re.IGNORECASE
)


class EquipParser:
    """Parses Equip keyword ability (activated ability)"""
    
    keyword_name = "equip"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Equip doesn't typically have reminder text, but check for it"""
        lower = reminder_text.lower()
        return "attach" in lower and "creature" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Equip reminder text into ActivatedAbility"""
        logger.debug(f"[EquipParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attach" not in lower or "creature" not in lower:
            return []
        
        cost_match = EQUIP_COST_RE.search(reminder_text)
        if not cost_match:
            return []
        
        cost_text = cost_match.group(1).strip()
        costs = parse_cost_string(cost_text)
        
        effect_text = "Attach this to target creature you control."
        effects = parse_effect_text(effect_text, ctx)
        targeting = parse_targeting(effect_text)
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[{"type": "timing", "value": "sorcery_only"}],
            targeting=targeting,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[EquipParser] Created ActivatedAbility for Equip")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Equip keyword without reminder text (e.g., 'Equip {2}')"""
        logger.debug(f"[EquipParser] Parsing keyword only: {keyword_text}")
        
        m = EQUIP_COST_RE.search(keyword_text)
        if not m:
            logger.debug(f"[EquipParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        costs = parse_cost_string(cost_text)
        
        effect_text = "Attach this to target creature you control."
        effects = parse_effect_text(effect_text, ctx)
        targeting = parse_targeting(effect_text)
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=effects,
            conditions=[{"type": "timing", "value": "sorcery_only"}],
            targeting=targeting,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[EquipParser] Created ActivatedAbility for Equip {cost_text}")
        
        return [activated_ability]

