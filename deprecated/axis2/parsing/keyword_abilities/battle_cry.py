# axis2/parsing/keyword_abilities/battle_cry.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, AttacksEvent, ContinuousEffect, PTExpression, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class BattleCryParser:
    """Parses Battle Cry keyword ability (triggered ability)"""
    
    keyword_name = "battle cry"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Battle Cry pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and "each other attacking creature gets +1/+0" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Battle Cry reminder text into TriggeredAbility"""
        logger.debug(f"[BattleCryParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or "each other attacking creature gets +1/+0" not in lower:
            return []
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="each_other_attacking_creature",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+1", toughness="+0"),
            text="gets +1/+0 until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks, each other attacking creature gets +1/+0 until end of turn.",
            effects=[pt_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[BattleCryParser] Created TriggeredAbility for Battle Cry")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Battle Cry keyword without reminder text"""
        logger.debug(f"[BattleCryParser] Parsing keyword only: {keyword_text}")
        
        pt_effect = ContinuousEffect(
            kind="pt_mod",
            applies_to="each_other_attacking_creature",
            duration="until_end_of_turn",
            layer=7,
            sublayer="7c",
            pt_value=PTExpression(power="+1", toughness="+0"),
            text="gets +1/+0 until end of turn",
            source_kind="triggered_ability"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks, each other attacking creature gets +1/+0 until end of turn.",
            effects=[pt_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[BattleCryParser] Created TriggeredAbility for Battle Cry")
        
        return [triggered_ability]

