# axis2/parsing/keyword_abilities/enlist.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ContinuousEffect, TriggeredAbility, AttacksEvent, PTExpression, DynamicValue, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class EnlistParser:
    """Parses Enlist keyword ability (static + triggered ability)"""
    
    keyword_name = "enlist"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Enlist pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and "tap" in lower and "creature" in lower and ("power" in lower or "+x/+0" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Enlist reminder text into TriggeredAbility"""
        logger.debug(f"[EnlistParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or "tap" not in lower or "creature" not in lower:
            return []
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+X", toughness="+0"),
            dynamic=DynamicValue(kind="enlisted_creature_power"),
            text="gets +X/+0 until end of turn, where X is the tapped creature's power",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="As this creature attacks, you may tap up to one untapped creature you control that you didn't choose to attack with and that either has haste or has been under your control continuously since this turn began. When you do, this creature gets +X/+0 until end of turn, where X is the tapped creature's power.",
            effects=[pt_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="may_tap_creature_for_enlist"
        )
        
        logger.debug(f"[EnlistParser] Created TriggeredAbility for Enlist")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Enlist keyword without reminder text"""
        logger.debug(f"[EnlistParser] Parsing keyword only: {keyword_text}")
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="self",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+X", toughness="+0"),
            dynamic=DynamicValue(kind="enlisted_creature_power"),
            text="gets +X/+0 until end of turn, where X is the tapped creature's power",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="As this creature attacks, you may tap up to one untapped creature you control that you didn't choose to attack with and that either has haste or has been under your control continuously since this turn began. When you do, this creature gets +X/+0 until end of turn, where X is the tapped creature's power.",
            effects=[pt_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="may_tap_creature_for_enlist"
        )
        
        logger.debug(f"[EnlistParser] Created TriggeredAbility for Enlist")
        
        return [triggered_ability]

