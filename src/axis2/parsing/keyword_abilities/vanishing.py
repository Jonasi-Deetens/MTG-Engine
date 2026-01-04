# axis2/parsing/keyword_abilities/vanishing.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, TriggeredAbility, Subject, ParseContext, Effect, RemoveCounterEffect, ChangeZoneEffect

logger = logging.getLogger(__name__)

VANISHING_RE = re.compile(
    r"vanishing\s+(\d+)",
    re.IGNORECASE
)


class VanishingParser:
    """Parses Vanishing keyword ability (replacement effect + triggered abilities)"""
    
    keyword_name = "vanishing"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Vanishing pattern"""
        lower = reminder_text.lower()
        return "enters the battlefield" in lower and "time counter" in lower and ("beginning of your upkeep" in lower or "remove a time counter" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Vanishing reminder text into ReplacementEffect and TriggeredAbilities"""
        logger.debug(f"[VanishingParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters the battlefield" not in lower or "time counter" not in lower:
            return []
        
        m = VANISHING_RE.search(reminder_text)
        if not m:
            logger.debug(f"[VanishingParser] No vanishing value found in reminder text")
            return []
        
        vanishing_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "time", "amount": vanishing_value},
            zones=["battlefield"]
        )
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="time",
            amount=1,
            subject=Subject(scope="self")
        )
        
        upkeep_trigger = TriggeredAbility(
            condition_text="At the beginning of your upkeep, if this permanent has a time counter on it, remove a time counter from it.",
            effects=[remove_counter_effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        last_counter_trigger = TriggeredAbility(
            condition_text="When the last time counter is removed from this permanent, sacrifice it.",
            effects=[sacrifice_effect],
            event="last_time_counter_removed",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[VanishingParser] Created ReplacementEffect and TriggeredAbilities for Vanishing {vanishing_value}")
        
        return [replacement_effect, upkeep_trigger, last_counter_trigger]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Vanishing keyword without reminder text (e.g., 'Vanishing 2')"""
        logger.debug(f"[VanishingParser] Parsing keyword only: {keyword_text}")
        
        m = VANISHING_RE.search(keyword_text)
        if not m:
            logger.debug(f"[VanishingParser] No vanishing value found in keyword text")
            return []
        
        vanishing_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "time", "amount": vanishing_value},
            zones=["battlefield"]
        )
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="time",
            amount=1,
            subject=Subject(scope="self")
        )
        
        upkeep_trigger = TriggeredAbility(
            condition_text="At the beginning of your upkeep, if this permanent has a time counter on it, remove a time counter from it.",
            effects=[remove_counter_effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        last_counter_trigger = TriggeredAbility(
            condition_text="When the last time counter is removed from this permanent, sacrifice it.",
            effects=[sacrifice_effect],
            event="last_time_counter_removed",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[VanishingParser] Created ReplacementEffect and TriggeredAbilities for Vanishing {vanishing_value}")
        
        return [replacement_effect, upkeep_trigger, last_counter_trigger]

