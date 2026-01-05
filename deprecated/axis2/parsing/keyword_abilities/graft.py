# axis2/parsing/keyword_abilities/graft.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, TriggeredAbility, EntersBattlefieldEvent, Subject, ParseContext, Effect, PutCounterEffect, RemoveCounterEffect

logger = logging.getLogger(__name__)

GRAFT_RE = re.compile(
    r"graft\s+(\d+)",
    re.IGNORECASE
)


class GraftParser:
    """Parses Graft keyword ability (replacement effect + triggered ability)"""
    
    keyword_name = "graft"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Graft pattern"""
        lower = reminder_text.lower()
        return "enters the battlefield" in lower and "+1/+1 counter" in lower and "move" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Graft reminder text into ReplacementEffect and TriggeredAbility"""
        logger.debug(f"[GraftParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters the battlefield" not in lower or "+1/+1 counter" not in lower:
            return []
        
        m = GRAFT_RE.search(reminder_text)
        if not m:
            logger.debug(f"[GraftParser] No graft value found in reminder text")
            return []
        
        graft_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": graft_value},
            zones=["battlefield"]
        )
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever another creature enters the battlefield, if this permanent has a +1/+1 counter on it, you may move a +1/+1 counter from this permanent onto that creature.",
            effects=[remove_counter_effect, put_counter_effect],
            event=EntersBattlefieldEvent(subject="another_creature"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[GraftParser] Created ReplacementEffect and TriggeredAbility for Graft {graft_value}")
        
        return [replacement_effect, triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Graft keyword without reminder text (e.g., 'Graft 3')"""
        logger.debug(f"[GraftParser] Parsing keyword only: {keyword_text}")
        
        m = GRAFT_RE.search(keyword_text)
        if not m:
            logger.debug(f"[GraftParser] No graft value found in keyword text")
            return []
        
        graft_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "+1/+1", "amount": graft_value},
            zones=["battlefield"]
        )
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="+1/+1",
            amount=1,
            subject=Subject(scope="self")
        )
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=1
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever another creature enters the battlefield, if this permanent has a +1/+1 counter on it, you may move a +1/+1 counter from this permanent onto that creature.",
            effects=[remove_counter_effect, put_counter_effect],
            event=EntersBattlefieldEvent(subject="another_creature"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[GraftParser] Created ReplacementEffect and TriggeredAbility for Graft {graft_value}")
        
        return [replacement_effect, triggered_ability]

