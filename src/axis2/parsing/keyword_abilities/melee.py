# axis2/parsing/keyword_abilities/melee.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, AttacksEvent, ContinuousEffect, PTExpression, DynamicValue, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class MeleeParser:
    """Parses Melee keyword ability (triggered ability)"""
    
    keyword_name = "melee"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Melee pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and "gets +1/+1" in lower and "opponent" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Melee reminder text into TriggeredAbility"""
        logger.debug(f"[MeleeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or "gets +1/+1" not in lower or "opponent" not in lower:
            return []
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+X", toughness="+X"),
            dynamic=DynamicValue(kind="opponents_attacked_this_combat"),
            text="gets +1/+1 until end of turn for each opponent you attacked with a creature this combat",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks, it gets +1/+1 until end of turn for each opponent you attacked with a creature this combat.",
            effects=[pt_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[MeleeParser] Created TriggeredAbility for Melee")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Melee keyword without reminder text"""
        logger.debug(f"[MeleeParser] Parsing keyword only: {keyword_text}")
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+X", toughness="+X"),
            dynamic=DynamicValue(kind="opponents_attacked_this_combat"),
            text="gets +1/+1 until end of turn for each opponent you attacked with a creature this combat",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks, it gets +1/+1 until end of turn for each opponent you attacked with a creature this combat.",
            effects=[pt_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[MeleeParser] Created TriggeredAbility for Melee")
        
        return [triggered_ability]

