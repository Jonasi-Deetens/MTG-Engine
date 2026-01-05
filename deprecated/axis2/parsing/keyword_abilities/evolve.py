# axis2/parsing/keyword_abilities/evolve.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, PutCounterEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class EvolveParser:
    """Parses Evolve keyword ability (triggered ability)"""
    
    keyword_name = "evolve"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Evolve pattern"""
        lower = reminder_text.lower()
        return "creature enters" in lower and "greater power or toughness" in lower and "+1/+1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Evolve reminder text into TriggeredAbility"""
        logger.debug(f"[EvolveParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "creature enters" not in lower or "greater power or toughness" not in lower:
            return []
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever a creature you control enters the battlefield, if that creature's power is greater than this creature's power and/or that creature's toughness is greater than this creature's toughness, put a +1/+1 counter on this creature.",
            effects=[put_counter_effect],
            event=EntersBattlefieldEvent(subject="creature_you_control"),
            targeting=None,
            trigger_filter=None,
            condition="entering_creature_has_greater_power_or_toughness"
        )
        
        logger.debug(f"[EvolveParser] Created TriggeredAbility for Evolve")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Evolve keyword without reminder text"""
        logger.debug(f"[EvolveParser] Parsing keyword only: {keyword_text}")
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever a creature you control enters the battlefield, if that creature's power is greater than this creature's power and/or that creature's toughness is greater than this creature's toughness, put a +1/+1 counter on this creature.",
            effects=[put_counter_effect],
            event=EntersBattlefieldEvent(subject="creature_you_control"),
            targeting=None,
            trigger_filter=None,
            condition="entering_creature_has_greater_power_or_toughness"
        )
        
        logger.debug(f"[EvolveParser] Created TriggeredAbility for Evolve")
        
        return [triggered_ability]

