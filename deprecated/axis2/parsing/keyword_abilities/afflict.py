# axis2/parsing/keyword_abilities/afflict.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DealDamageEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

AFFLICT_RE = re.compile(
    r"afflict\s+(\d+)",
    re.IGNORECASE
)


class AfflictParser:
    """Parses Afflict keyword ability (triggered ability)"""
    
    keyword_name = "afflict"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Afflict pattern"""
        lower = reminder_text.lower()
        return "becomes blocked" in lower and "defending player loses" in lower and "life" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Afflict reminder text into TriggeredAbility"""
        logger.debug(f"[AfflictParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "becomes blocked" not in lower or "defending player loses" not in lower:
            return []
        
        m = AFFLICT_RE.search(reminder_text)
        if not m:
            logger.debug(f"[AfflictParser] No afflict value found in reminder text")
            return []
        
        afflict_value = int(m.group(1))
        
        lose_life_effect = DealDamageEffect(
            amount=afflict_value,
            subject=Subject(scope="defending_player")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"Whenever this creature becomes blocked, defending player loses {afflict_value} life.",
            effects=[lose_life_effect],
            event="becomes_blocked",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[AfflictParser] Created TriggeredAbility for Afflict {afflict_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Afflict keyword without reminder text (e.g., 'Afflict 1')"""
        logger.debug(f"[AfflictParser] Parsing keyword only: {keyword_text}")
        
        m = AFFLICT_RE.search(keyword_text)
        if not m:
            logger.debug(f"[AfflictParser] No afflict value found in keyword text")
            return []
        
        afflict_value = int(m.group(1))
        
        lose_life_effect = DealDamageEffect(
            amount=afflict_value,
            subject=Subject(scope="defending_player")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"Whenever this creature becomes blocked, defending player loses {afflict_value} life.",
            effects=[lose_life_effect],
            event="becomes_blocked",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[AfflictParser] Created TriggeredAbility for Afflict {afflict_value}")
        
        return [triggered_ability]

