# axis2/parsing/keyword_abilities/saddle.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, ContinuousEffect, RuleChangeData, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

SADDLE_RE = re.compile(
    r"saddle\s+(\d+)",
    re.IGNORECASE
)


class SaddleParser:
    """Parses Saddle keyword ability (activated ability)"""
    
    keyword_name = "saddle"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Saddle pattern"""
        lower = reminder_text.lower()
        return "tap" in lower and "creatures" in lower and "power" in lower and "saddled" in lower and "end of turn" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Saddle reminder text into ActivatedAbility"""
        logger.debug(f"[SaddleParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "tap" not in lower or "creatures" not in lower or "saddled" not in lower:
            return []
        
        m = SADDLE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[SaddleParser] No saddle value found in reminder text")
            return []
        
        saddle_value = int(m.group(1))
        
        continuous_effect = ContinuousEffect(
            kind="grant_designation",
            text=f"This permanent becomes saddled until end of turn.",
            applies_to="self",
            duration="until_end_of_turn",
            layer=1,
            rule_change=RuleChangeData(kind="saddled_designation")
        )
        
        activated_ability = ActivatedAbility(
            costs=[],  # Axis3 handles tap cost with min_power requirement
            effects=[continuous_effect],
            conditions=[{"kind": "activate_only_as_sorcery"}, {"kind": "saddle_cost", "min_power": saddle_value}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[SaddleParser] Created ActivatedAbility for Saddle {saddle_value}")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Saddle keyword without reminder text (e.g., 'Saddle 1')"""
        logger.debug(f"[SaddleParser] Parsing keyword only: {keyword_text}")
        
        m = SADDLE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[SaddleParser] No saddle value found in keyword text")
            return []
        
        saddle_value = int(m.group(1))
        
        continuous_effect = ContinuousEffect(
            kind="grant_designation",
            text=f"This permanent becomes saddled until end of turn.",
            applies_to="self",
            duration="until_end_of_turn",
            layer=1,
            rule_change=RuleChangeData(kind="saddled_designation")
        )
        
        activated_ability = ActivatedAbility(
            costs=[],  # Axis3 handles tap cost with min_power requirement
            effects=[continuous_effect],
            conditions=[{"kind": "activate_only_as_sorcery"}, {"kind": "saddle_cost", "min_power": saddle_value}],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[SaddleParser] Created ActivatedAbility for Saddle {saddle_value}")
        
        return [activated_ability]

