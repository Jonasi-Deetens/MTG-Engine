# axis2/parsing/keyword_abilities/crew.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ContinuousEffect, Subject, ParseContext, Effect, TapCost
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

CREW_RE = re.compile(
    r"crew\s+(\d+)",
    re.IGNORECASE
)


class CrewParser:
    """Parses Crew keyword ability (activated ability)"""
    
    keyword_name = "crew"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Crew pattern"""
        lower = reminder_text.lower()
        return "tap" in lower and "creatures" in lower and "total power" in lower and "becomes an artifact creature" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Crew reminder text into ActivatedAbility"""
        logger.debug(f"[CrewParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "tap" not in lower or "creatures" not in lower or "becomes an artifact creature" not in lower:
            return []
        
        m = CREW_RE.search(reminder_text)
        if not m:
            logger.debug(f"[CrewParser] No crew value found in reminder text")
            return []
        
        crew_value = int(m.group(1))
        
        costs = []
        costs.append(TapCost())  # Tap creatures with total power >= crew_value
        
        type_change_effect = ContinuousEffect(
            kind="type_add",
            applies_to="self",
            duration="until_end_of_turn",
            layer=4,
            type_change={"add_types": ["creature"], "add_subtypes": []},
            source_kind="activated_ability"
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[type_change_effect],
            conditions=[{"crew_power_requirement": crew_value}],
            targeting=None,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[CrewParser] Created ActivatedAbility for Crew {crew_value}")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Crew keyword without reminder text (e.g., 'Crew 3')"""
        logger.debug(f"[CrewParser] Parsing keyword only: {keyword_text}")
        
        m = CREW_RE.search(keyword_text)
        if not m:
            logger.debug(f"[CrewParser] No crew value found in keyword text")
            return []
        
        crew_value = int(m.group(1))
        
        costs = []
        costs.append(TapCost())  # Tap creatures with total power >= crew_value
        
        type_change_effect = ContinuousEffect(
            kind="type_add",
            applies_to="self",
            duration="until_end_of_turn",
            layer=4,
            type_change={"add_types": ["creature"], "add_subtypes": []},
            source_kind="activated_ability"
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[type_change_effect],
            conditions=[{"crew_power_requirement": crew_value}],
            targeting=None,
            timing="instant",
            is_mana_ability=False
        )
        
        logger.debug(f"[CrewParser] Created ActivatedAbility for Crew {crew_value}")
        
        return [activated_ability]

