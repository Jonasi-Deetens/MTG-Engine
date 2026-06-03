# axis2/parsing/keyword_abilities/ravenous.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, TriggeredAbility, EntersBattlefieldEvent, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class RavenousParser:
    """Parses Ravenous keyword ability (replacement effect + triggered ability)"""
    
    keyword_name = "ravenous"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Ravenous pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and "x +1/+1 counter" in lower and ("x is 5" in lower or "draw a card" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ravenous reminder text into ReplacementEffect and TriggeredAbility"""
        logger.debug(f"[RavenousParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower or "+1/+1 counter" not in lower:
            return []
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "+1/+1",
                "amount": "X"
            },
            zones=["battlefield"]
        )
        
        draw_trigger = TriggeredAbility(
            condition_text="When this permanent enters, if X is 5 or more, draw a card.",
            effects=[],  # Axis3 handles the draw
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="X_is_5_or_more"
        )
        
        logger.debug(f"[RavenousParser] Created ReplacementEffect and TriggeredAbility for Ravenous")
        
        return [replacement_effect, draw_trigger]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ravenous keyword without reminder text"""
        logger.debug(f"[RavenousParser] Parsing keyword only: {keyword_text}")
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "+1/+1",
                "amount": "X"
            },
            zones=["battlefield"]
        )
        
        draw_trigger = TriggeredAbility(
            condition_text="When this permanent enters, if X is 5 or more, draw a card.",
            effects=[],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="X_is_5_or_more"
        )
        
        logger.debug(f"[RavenousParser] Created ReplacementEffect and TriggeredAbility for Ravenous")
        
        return [replacement_effect, draw_trigger]

