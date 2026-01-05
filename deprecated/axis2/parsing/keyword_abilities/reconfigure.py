# axis2/parsing/keyword_abilities/reconfigure.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ChangeZoneEffect, Subject, TargetingRules, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

RECONFIGURE_RE = re.compile(
    r"reconfigure\s+(.+)",
    re.IGNORECASE
)


class ReconfigureParser:
    """Parses Reconfigure keyword ability (activated abilities)"""
    
    keyword_name = "reconfigure"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Reconfigure pattern"""
        lower = reminder_text.lower()
        return "attach" in lower and "creature" in lower and "unattach" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Reconfigure reminder text into ActivatedAbilities"""
        logger.debug(f"[ReconfigureParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attach" not in lower or "creature" not in lower:
            return []
        
        m = RECONFIGURE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[ReconfigureParser] No reconfigure cost found in reminder text")
            return []
        
        cost_text = m.group(1).strip()
        costs = parse_cost_string(cost_text)
        
        attach_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone=None,
            to_zone="battlefield",
            attach_to="target_creature_you_control"
        )
        
        attach_ability = ActivatedAbility(
            costs=costs,
            effects=[attach_effect],
            conditions=[{"kind": "activate_only_as_sorcery"}],
            targeting=TargetingRules(required=True, min=1, max=1, legal_targets=["creature_you_control"]),
            timing="sorcery",
            is_mana_ability=False
        )
        
        unattach_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone=None,
            to_zone="battlefield",
            attach_to=None
        )
        
        unattach_ability = ActivatedAbility(
            costs=costs,
            effects=[unattach_effect],
            conditions=[{"kind": "activate_only_as_sorcery"}, {"kind": "only_if_attached_to_creature"}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[ReconfigureParser] Created two ActivatedAbilities for Reconfigure")
        
        return [attach_ability, unattach_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Reconfigure keyword without reminder text (e.g., 'Reconfigure {2}')"""
        logger.debug(f"[ReconfigureParser] Parsing keyword only: {keyword_text}")
        
        m = RECONFIGURE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ReconfigureParser] No reconfigure cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        costs = parse_cost_string(cost_text)
        
        attach_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone=None,
            to_zone="battlefield",
            attach_to="target_creature_you_control"
        )
        
        attach_ability = ActivatedAbility(
            costs=costs,
            effects=[attach_effect],
            conditions=[{"kind": "activate_only_as_sorcery"}],
            targeting=TargetingRules(required=True, min=1, max=1, legal_targets=["creature_you_control"]),
            timing="sorcery",
            is_mana_ability=False
        )
        
        unattach_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone=None,
            to_zone="battlefield",
            attach_to=None
        )
        
        unattach_ability = ActivatedAbility(
            costs=costs,
            effects=[unattach_effect],
            conditions=[{"kind": "activate_only_as_sorcery"}, {"kind": "only_if_attached_to_creature"}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[ReconfigureParser] Created two ActivatedAbilities for Reconfigure")
        
        return [attach_ability, unattach_ability]

