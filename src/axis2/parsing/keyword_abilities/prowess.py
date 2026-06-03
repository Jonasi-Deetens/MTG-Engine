# axis2/parsing/keyword_abilities/prowess.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, CastSpellEvent, ContinuousEffect, PTExpression, Subject, ParseContext, Effect, SpellFilter

logger = logging.getLogger(__name__)


class ProwessParser:
    """Parses Prowess keyword ability (triggered ability)"""
    
    keyword_name = "prowess"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Prowess pattern"""
        lower = reminder_text.lower()
        return "cast a noncreature spell" in lower and "gets +1/+1" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Prowess reminder text into TriggeredAbility"""
        logger.debug(f"[ProwessParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast a noncreature spell" not in lower or "gets +1/+1" not in lower:
            return []
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+1", toughness="+1"),
            text="gets +1/+1 until end of turn",
            source_kind="triggered_ability"
        )
        
        spell_filter = SpellFilter(must_not_have_types=["creature"])
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever you cast a noncreature spell, this creature gets +1/+1 until end of turn.",
            effects=[pt_effect],
            event=CastSpellEvent(subject="you", spell_filter=spell_filter),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ProwessParser] Created TriggeredAbility for Prowess")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Prowess keyword without reminder text"""
        logger.debug(f"[ProwessParser] Parsing keyword only: {keyword_text}")
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+1", toughness="+1"),
            text="gets +1/+1 until end of turn",
            source_kind="triggered_ability"
        )
        
        spell_filter = SpellFilter(must_not_have_types=["creature"])
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever you cast a noncreature spell, this creature gets +1/+1 until end of turn.",
            effects=[pt_effect],
            event=CastSpellEvent(subject="you", spell_filter=spell_filter),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ProwessParser] Created TriggeredAbility for Prowess")
        
        return [triggered_ability]

