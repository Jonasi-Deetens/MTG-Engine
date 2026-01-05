# axis2/parsing/keyword_abilities/level_up.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ActivatedAbility, PutCounterEffect, Subject, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

LEVEL_UP_RE = re.compile(
    r"level\s+up\s*(?:—|-)?\s*(.+)",
    re.IGNORECASE
)


class LevelUpParser:
    """Parses Level Up keyword ability (activated ability)"""
    
    keyword_name = "level up"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Level Up pattern"""
        lower = reminder_text.lower()
        return "put a level counter" in lower and "sorcery" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Level Up reminder text into ActivatedAbility"""
        logger.debug(f"[LevelUpParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "put a level counter" not in lower:
            return []
        
        m = LEVEL_UP_RE.search(reminder_text)
        if not m:
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        put_counter_effect = PutCounterEffect(
            counter_type="level",
            amount=1
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[put_counter_effect],
            conditions=[],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[LevelUpParser] Created ActivatedAbility for Level Up")
        
        return [activated_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Level Up keyword without reminder text (e.g., 'Level up {2}{G}')"""
        logger.debug(f"[LevelUpParser] Parsing keyword only: {keyword_text}")
        
        m = LEVEL_UP_RE.search(keyword_text)
        if not m:
            logger.debug(f"[LevelUpParser] No cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        costs = parse_cost_string(cost_text)
        
        put_counter_effect = PutCounterEffect(
            counter_type="level",
            amount=1
        )
        
        activated_ability = ActivatedAbility(
            costs=costs,
            effects=[put_counter_effect],
            conditions=[],
            targeting=None,
            timing="sorcery",
            is_mana_ability=False
        )
        
        logger.debug(f"[LevelUpParser] Created ActivatedAbility for Level Up {cost_text}")
        
        return [activated_ability]

