# axis2/parsing/keyword_abilities/impending.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, TriggeredAbility, ContinuousEffect, EntersBattlefieldEvent, RemoveCounterEffect, Subject, TypeChangeData, ParseContext, Effect

logger = logging.getLogger(__name__)

IMPENDING_RE = re.compile(
    r"impending\s+(\d+)\s*—\s*(\{.+?\})",
    re.IGNORECASE
)


class ImpendingParser:
    """Parses Impending keyword ability (spell modifier + replacement effect + static ability + triggered ability)"""
    
    keyword_name = "impending"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Impending pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "impending cost" in lower and "time counter" in lower and "isn't a creature" in lower and "end step" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Impending reminder text into ReplacementEffect, ContinuousEffect, and TriggeredAbility"""
        logger.debug(f"[ImpendingParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "time counter" not in lower or "isn't a creature" not in lower:
            return []
        
        m = IMPENDING_RE.search(reminder_text)
        if not m:
            logger.debug(f"[ImpendingParser] No impending value or cost found in reminder text")
            return []
        
        impending_value = int(m.group(1))
        impending_cost = m.group(2).strip()
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "time",
                "amount": impending_value
            },
            zones=["battlefield"],
            condition="impending_cost_was_paid"
        )
        
        continuous_effect = ContinuousEffect(
            kind="type_remove",
            text="As long as this permanent has a time counter on it, if it was cast for its impending cost, it's not a creature.",
            applies_to="self",
            duration="permanent",
            layer=4,
            type_change=TypeChangeData(remove_types=["creature"]),
            condition="has_time_counters_and_impending_cost_was_paid",
            source_kind="static_ability"
        )
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="time",
            amount=1,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="At the beginning of your end step, if this permanent was cast for its impending cost and there is at least one time counter on it, remove a time counter from it.",
            effects=[remove_counter_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None,
            condition="impending_cost_was_paid_and_has_time_counters"
        )
        
        logger.debug(f"[ImpendingParser] Created ReplacementEffect, ContinuousEffect, and TriggeredAbility for Impending {impending_value}")
        
        return [replacement_effect, continuous_effect, triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Impending keyword without reminder text (e.g., 'Impending 4 — {1}{G}{G}')"""
        logger.debug(f"[ImpendingParser] Parsing keyword only: {keyword_text}")
        
        m = IMPENDING_RE.search(keyword_text)
        if not m:
            logger.debug(f"[ImpendingParser] No impending value or cost found in keyword text")
            return []
        
        impending_value = int(m.group(1))
        impending_cost = m.group(2).strip()
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "time",
                "amount": impending_value
            },
            zones=["battlefield"],
            condition="impending_cost_was_paid"
        )
        
        continuous_effect = ContinuousEffect(
            kind="type_remove",
            text="As long as this permanent has a time counter on it, if it was cast for its impending cost, it's not a creature.",
            applies_to="self",
            duration="permanent",
            layer=4,
            type_change=TypeChangeData(remove_types=["creature"]),
            condition="has_time_counters_and_impending_cost_was_paid",
            source_kind="static_ability"
        )
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="time",
            amount=1,
            subject=Subject(scope="self")
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="At the beginning of your end step, if this permanent was cast for its impending cost and there is at least one time counter on it, remove a time counter from it.",
            effects=[remove_counter_effect],
            event="end_step",
            targeting=None,
            trigger_filter=None,
            condition="impending_cost_was_paid_and_has_time_counters"
        )
        
        logger.debug(f"[ImpendingParser] Created ReplacementEffect, ContinuousEffect, and TriggeredAbility for Impending {impending_value}")
        
        return [replacement_effect, continuous_effect, triggered_ability]

