# axis2/parsing/keyword_abilities/devour.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

DEVOUR_RE = re.compile(
    r"devour\s+(\d+|X)",
    re.IGNORECASE
)


class DevourParser:
    """Parses Devour keyword ability (replacement effect)"""
    
    keyword_name = "devour"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Devour pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and "sacrifice" in lower and "+1/+1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Devour reminder text into ReplacementEffect"""
        logger.debug(f"[DevourParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower or "sacrifice" not in lower or "+1/+1 counter" not in lower:
            return []
        
        m = DEVOUR_RE.search(reminder_text)
        if not m:
            logger.debug(f"[DevourParser] No devour value found in reminder text")
            return []
        
        devour_value = m.group(1)
        
        if devour_value.upper() == "X":
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={"counter_type": "+1/+1", "amount": "devoured_creatures_count", "condition": "may_sacrifice_creatures"},
                zones=["battlefield"]
            )
        else:
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={"counter_type": "+1/+1", "amount": f"{int(devour_value)}_per_devoured_creature", "condition": "may_sacrifice_creatures"},
                zones=["battlefield"]
            )
        
        logger.debug(f"[DevourParser] Created ReplacementEffect for Devour {devour_value}")
        
        return [replacement_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Devour keyword without reminder text (e.g., 'Devour 1')"""
        logger.debug(f"[DevourParser] Parsing keyword only: {keyword_text}")
        
        m = DEVOUR_RE.search(keyword_text)
        if not m:
            logger.debug(f"[DevourParser] No devour value found in keyword text")
            return []
        
        devour_value = m.group(1)
        
        if devour_value.upper() == "X":
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={"counter_type": "+1/+1", "amount": "devoured_creatures_count", "condition": "may_sacrifice_creatures"},
                zones=["battlefield"]
            )
        else:
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={"counter_type": "+1/+1", "amount": f"{int(devour_value)}_per_devoured_creature", "condition": "may_sacrifice_creatures"},
                zones=["battlefield"]
            )
        
        logger.debug(f"[DevourParser] Created ReplacementEffect for Devour {devour_value}")
        
        return [replacement_effect]

