# axis2/parsing/keyword_abilities/extort.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, CastSpellEvent, GainLifeEffect, Subject, ParseContext, Effect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)


class ExtortParser:
    """Parses Extort keyword ability (triggered ability)"""
    
    keyword_name = "extort"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Extort pattern"""
        lower = reminder_text.lower()
        return "cast a spell" in lower and "pay" in lower and "opponent loses" in lower and "gain life" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Extort reminder text into TriggeredAbility"""
        logger.debug(f"[ExtortParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast a spell" not in lower or "opponent loses" not in lower:
            return []
        
        gain_life_effect = GainLifeEffect(
            amount="total_life_lost_by_opponents",
            subject="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever you cast a spell, you may pay {W/B}. If you do, each opponent loses 1 life and you gain life equal to the total life lost this way.",
            effects=[gain_life_effect],
            event=CastSpellEvent(subject="you"),
            targeting=None,
            trigger_filter=None,
            condition="may_pay_W/B"
        )
        
        logger.debug(f"[ExtortParser] Created TriggeredAbility for Extort")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Extort keyword without reminder text"""
        logger.debug(f"[ExtortParser] Parsing keyword only: {keyword_text}")
        
        gain_life_effect = GainLifeEffect(
            amount="total_life_lost_by_opponents",
            subject="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever you cast a spell, you may pay {W/B}. If you do, each opponent loses 1 life and you gain life equal to the total life lost this way.",
            effects=[gain_life_effect],
            event=CastSpellEvent(subject="you"),
            targeting=None,
            trigger_filter=None,
            condition="may_pay_W/B"
        )
        
        logger.debug(f"[ExtortParser] Created TriggeredAbility for Extort")
        
        return [triggered_ability]

