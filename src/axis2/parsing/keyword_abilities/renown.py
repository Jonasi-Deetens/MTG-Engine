# axis2/parsing/keyword_abilities/renown.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DealsDamageEvent, PutCounterEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

RENOWN_RE = re.compile(
    r"renown\s+(\d+)",
    re.IGNORECASE
)


class RenownParser:
    """Parses Renown keyword ability (triggered ability)"""
    
    keyword_name = "renown"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Renown pattern"""
        lower = reminder_text.lower()
        return "deals combat damage to a player" in lower and "renowned" in lower and "+1/+1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Renown reminder text into TriggeredAbility"""
        logger.debug(f"[RenownParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "deals combat damage to a player" not in lower or "renowned" not in lower:
            return []
        
        m = RENOWN_RE.search(reminder_text)
        if not m:
            logger.debug(f"[RenownParser] No renown value found in reminder text")
            return []
        
        renown_value = int(m.group(1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=renown_value,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this creature deals combat damage to a player, if it isn't renowned, put {renown_value} +1/+1 counters on it and it becomes renowned.",
            effects=[put_counter_effect],
            event=DealsDamageEvent(subject="self", damage_type="combat", target="player"),
            targeting=None,
            trigger_filter=None,
            condition="not_renowned"
        )
        
        logger.debug(f"[RenownParser] Created TriggeredAbility for Renown {renown_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Renown keyword without reminder text (e.g., 'Renown 1')"""
        logger.debug(f"[RenownParser] Parsing keyword only: {keyword_text}")
        
        m = RENOWN_RE.search(keyword_text)
        if not m:
            logger.debug(f"[RenownParser] No renown value found in keyword text")
            return []
        
        renown_value = int(m.group(1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=renown_value,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this creature deals combat damage to a player, if it isn't renowned, put {renown_value} +1/+1 counters on it and it becomes renowned.",
            effects=[put_counter_effect],
            event=DealsDamageEvent(subject="self", damage_type="combat", target="player"),
            targeting=None,
            trigger_filter=None,
            condition="not_renowned"
        )
        
        logger.debug(f"[RenownParser] Created TriggeredAbility for Renown {renown_value}")
        
        return [triggered_ability]

