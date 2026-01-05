# axis2/parsing/keyword_abilities/demonstrate.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, CastSpellEvent, ParseContext, Effect

logger = logging.getLogger(__name__)


class DemonstrateParser:
    """Parses Demonstrate keyword ability (triggered ability on spells)"""
    
    keyword_name = "demonstrate"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Demonstrate pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "copy" in lower and "opponent" in lower and "copy" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Demonstrate reminder text into TriggeredAbility"""
        logger.debug(f"[DemonstrateParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "copy" not in lower:
            return []
        
        triggered_ability = TriggeredAbility(
            condition_text="When you cast this spell, you may copy it and you may choose new targets for the copy. If you copy the spell, choose an opponent. That player copies the spell and may choose new targets for that copy.",
            effects=[],  # Axis3 handles the copying
            event=CastSpellEvent(subject="this_spell"),
            targeting=None,
            trigger_filter=None,
            condition="may_choose"
        )
        
        logger.debug(f"[DemonstrateParser] Created TriggeredAbility for Demonstrate")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Demonstrate keyword without reminder text"""
        logger.debug(f"[DemonstrateParser] Parsing keyword only: {keyword_text}")
        
        triggered_ability = TriggeredAbility(
            condition_text="When you cast this spell, you may copy it and you may choose new targets for the copy. If you copy the spell, choose an opponent. That player copies the spell and may choose new targets for that copy.",
            effects=[],
            event=CastSpellEvent(subject="this_spell"),
            targeting=None,
            trigger_filter=None,
            condition="may_choose"
        )
        
        logger.debug(f"[DemonstrateParser] Created TriggeredAbility for Demonstrate")
        
        return [triggered_ability]

