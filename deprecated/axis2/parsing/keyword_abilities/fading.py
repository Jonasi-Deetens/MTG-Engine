# axis2/parsing/keyword_abilities/fading.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, ReplacementEffect, PutCounterEffect, RemoveCounterEffect, ChangeZoneEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

FADING_RE = re.compile(
    r"fading\s+(\d+)",
    re.IGNORECASE
)


class FadingParser:
    """Parses Fading keyword ability (replacement effect + triggered ability)"""
    
    keyword_name = "fading"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Fading pattern"""
        lower = reminder_text.lower()
        return "fade counter" in lower and ("enters" in lower or "upkeep" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Fading reminder text into ReplacementEffect and TriggeredAbility"""
        logger.debug(f"[FadingParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "fade counter" not in lower:
            return []
        
        m = FADING_RE.search(reminder_text)
        if not m:
            logger.debug(f"[FadingParser] No fading value found in reminder text")
            return []
        
        fade_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "fade", "amount": fade_value},
            zones=["battlefield"]
        )
        
        condition_text = "At the beginning of your upkeep, remove a fade counter from this permanent. If you can't, sacrifice the permanent."
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="fade",
            amount=1,
            subject=Subject(scope="self")
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[remove_counter_effect, sacrifice_effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[FadingParser] Created ReplacementEffect and TriggeredAbility for Fading {fade_value}")
        
        return [replacement_effect, triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Fading keyword without reminder text (e.g., 'Fading 3')"""
        logger.debug(f"[FadingParser] Parsing keyword only: {keyword_text}")
        
        m = FADING_RE.search(keyword_text)
        if not m:
            logger.debug(f"[FadingParser] No fading value found in keyword text")
            return []
        
        fade_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={"counter_type": "fade", "amount": fade_value},
            zones=["battlefield"]
        )
        
        condition_text = "At the beginning of your upkeep, remove a fade counter from this permanent. If you can't, sacrifice the permanent."
        
        remove_counter_effect = RemoveCounterEffect(
            counter_type="fade",
            amount=1,
            subject=Subject(scope="self")
        )
        
        sacrifice_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="battlefield",
            to_zone="graveyard",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=condition_text,
            effects=[remove_counter_effect, sacrifice_effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[FadingParser] Created ReplacementEffect and TriggeredAbility for Fading {fade_value}")
        
        return [replacement_effect, triggered_ability]

