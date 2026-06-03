# axis2/parsing/keyword_abilities/gravestorm.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, CastSpellEvent, Subject, ParseContext, Effect, SpellFilter

logger = logging.getLogger(__name__)


class GravestormParser:
    """Parses Gravestorm keyword ability (triggered ability on stack)"""
    
    keyword_name = "gravestorm"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Gravestorm pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "copy it" in lower and "permanent.*put into.*graveyard" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Gravestorm reminder text into TriggeredAbility"""
        logger.debug(f"[GravestormParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "copy it" not in lower:
            return []
        
        triggered_ability = TriggeredAbility(
            condition_text="When you cast this spell, copy it for each permanent that was put into a graveyard from the battlefield this turn. If the spell has any targets, you may choose new targets for any of the copies.",
            effects=[],  # Copy effect is handled by Axis3 based on event
            event=CastSpellEvent(subject="this_spell", spell_filter=SpellFilter()),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[GravestormParser] Created TriggeredAbility for Gravestorm")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Gravestorm keyword without reminder text"""
        logger.debug(f"[GravestormParser] Parsing keyword only: {keyword_text}")
        
        triggered_ability = TriggeredAbility(
            condition_text="When you cast this spell, copy it for each permanent that was put into a graveyard from the battlefield this turn. If the spell has any targets, you may choose new targets for any of the copies.",
            effects=[],  # Copy effect is handled by Axis3 based on event
            event=CastSpellEvent(subject="this_spell", spell_filter=SpellFilter()),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[GravestormParser] Created TriggeredAbility for Gravestorm")
        
        return [triggered_ability]

