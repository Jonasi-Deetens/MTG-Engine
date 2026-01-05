# axis2/parsing/keyword_abilities/suspend.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, TriggeredAbility, Subject, ParseContext, Effect, ChangeZoneEffect, RemoveCounterEffect
from axis2.parsing.costs import parse_cost_string

logger = logging.getLogger(__name__)

SUSPEND_RE = re.compile(
    r"suspend\s+(\d+)\s*—\s*(.+)",
    re.IGNORECASE
)


class SuspendParser:
    """Parses Suspend keyword ability (static ability + triggered abilities)"""
    
    keyword_name = "suspend"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Suspend pattern"""
        lower = reminder_text.lower()
        return "exile it" in lower and "time counter" in lower and ("beginning of your upkeep" in lower or "remove a time counter" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Suspend reminder text into ReplacementEffect and TriggeredAbilities"""
        logger.debug(f"[SuspendParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "exile it" not in lower or "time counter" not in lower:
            return []
        
        m = SUSPEND_RE.search(reminder_text)
        if not m:
            logger.debug(f"[SuspendParser] No suspend value or cost found in reminder text")
            return []
        
        suspend_value = int(m.group(1))
        cost_text = m.group(2).strip()
        
        costs = parse_cost_string(cost_text)
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="hand",
            to_zone="exile",
            owner="owner"
        )
        
        replacement_effect = ReplacementEffect(
            kind="alternative_cast",
            event="would_cast_from_hand",
            subject=Subject(scope="self"),
            instead_effects=[exile_effect],
            value={"counter_type": "time", "amount": suspend_value},
            zones=["hand"]
        )
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="time",
            amount=1,
            subject=Subject(scope="self")
        )
        
        upkeep_trigger = TriggeredAbility(
            condition_text="At the beginning of your upkeep, if this card is suspended, remove a time counter from it.",
            effects=[remove_counter_effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        cast_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="exile",
            to_zone="stack",
            owner="owner"
        )
        
        last_counter_trigger = TriggeredAbility(
            condition_text="When the last time counter is removed from this card, if it's exiled, you may play it without paying its mana cost if able.",
            effects=[cast_effect],
            event="last_time_counter_removed",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[SuspendParser] Created ReplacementEffect and TriggeredAbilities for Suspend {suspend_value}")
        
        return [replacement_effect, upkeep_trigger, last_counter_trigger]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Suspend keyword without reminder text (e.g., 'Suspend 4 — {W}{U}')"""
        logger.debug(f"[SuspendParser] Parsing keyword only: {keyword_text}")
        
        m = SUSPEND_RE.search(keyword_text)
        if not m:
            logger.debug(f"[SuspendParser] No suspend value or cost found in keyword text")
            return []
        
        suspend_value = int(m.group(1))
        cost_text = m.group(2).strip()
        
        costs = parse_cost_string(cost_text)
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="hand",
            to_zone="exile",
            owner="owner"
        )
        
        replacement_effect = ReplacementEffect(
            kind="alternative_cast",
            event="would_cast_from_hand",
            subject=Subject(scope="self"),
            instead_effects=[exile_effect],
            value={"counter_type": "time", "amount": suspend_value},
            zones=["hand"]
        )
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="time",
            amount=1,
            subject=Subject(scope="self")
        )
        
        upkeep_trigger = TriggeredAbility(
            condition_text="At the beginning of your upkeep, if this card is suspended, remove a time counter from it.",
            effects=[remove_counter_effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        cast_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="exile",
            to_zone="stack",
            owner="owner"
        )
        
        last_counter_trigger = TriggeredAbility(
            condition_text="When the last time counter is removed from this card, if it's exiled, you may play it without paying its mana cost if able.",
            effects=[cast_effect],
            event="last_time_counter_removed",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[SuspendParser] Created ReplacementEffect and TriggeredAbilities for Suspend {suspend_value}")
        
        return [replacement_effect, upkeep_trigger, last_counter_trigger]

