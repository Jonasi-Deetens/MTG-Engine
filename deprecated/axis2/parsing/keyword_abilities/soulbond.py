# axis2/parsing/keyword_abilities/soulbond.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, ContinuousEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class SoulbondParser:
    """Parses Soulbond keyword ability (two triggered abilities)"""
    
    keyword_name = "soulbond"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Soulbond pattern"""
        lower = reminder_text.lower()
        return "pair" in lower and "enters the battlefield" in lower and "paired" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Soulbond reminder text into two TriggeredAbilities"""
        logger.debug(f"[SoulbondParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "pair" not in lower or "enters the battlefield" not in lower:
            return []
        
        pairing_effect = ContinuousEffect(
            kind="pairing",
            applies_to="self_and_another_creature",
            duration="as_long_as_both_remain_creatures_under_control",
            layer=6,
            value={"pairing_type": "soulbond"},
            source_kind="triggered_ability"
        )
        
        etb_trigger = TriggeredAbility(
            condition_text="When this creature enters the battlefield, if you control both this creature and another creature and both are unpaired, you may pair this creature with another unpaired creature you control for as long as both remain creatures on the battlefield under your control.",
            effects=[pairing_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="you_control_unpaired_creature"
        )
        
        other_etb_trigger = TriggeredAbility(
            condition_text="Whenever another creature you control enters the battlefield, if you control both that creature and this one and both are unpaired, you may pair that creature with this creature for as long as both remain creatures on the battlefield under your control.",
            effects=[pairing_effect],
            event=EntersBattlefieldEvent(subject="creature_you_control"),
            targeting=None,
            trigger_filter=None,
            condition="both_unpaired"
        )
        
        logger.debug(f"[SoulbondParser] Created two TriggeredAbilities for Soulbond")
        
        return [etb_trigger, other_etb_trigger]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Soulbond keyword without reminder text"""
        logger.debug(f"[SoulbondParser] Parsing keyword only: {keyword_text}")
        
        pairing_effect = ContinuousEffect(
            kind="pairing",
            applies_to="self_and_another_creature",
            duration="as_long_as_both_remain_creatures_under_control",
            layer=6,
            value={"pairing_type": "soulbond"},
            source_kind="triggered_ability"
        )
        
        etb_trigger = TriggeredAbility(
            condition_text="When this creature enters the battlefield, if you control both this creature and another creature and both are unpaired, you may pair this creature with another unpaired creature you control for as long as both remain creatures on the battlefield under your control.",
            effects=[pairing_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="you_control_unpaired_creature"
        )
        
        other_etb_trigger = TriggeredAbility(
            condition_text="Whenever another creature you control enters the battlefield, if you control both that creature and this one and both are unpaired, you may pair that creature with this creature for as long as both remain creatures on the battlefield under your control.",
            effects=[pairing_effect],
            event=EntersBattlefieldEvent(subject="creature_you_control"),
            targeting=None,
            trigger_filter=None,
            condition="both_unpaired"
        )
        
        logger.debug(f"[SoulbondParser] Created two TriggeredAbilities for Soulbond")
        
        return [etb_trigger, other_etb_trigger]

