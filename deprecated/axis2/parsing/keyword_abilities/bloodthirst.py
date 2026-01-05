# axis2/parsing/keyword_abilities/bloodthirst.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect, PutCounterEffect

logger = logging.getLogger(__name__)

BLOODTHIRST_RE = re.compile(
    r"bloodthirst\s+(\d+|X)",
    re.IGNORECASE
)


class BloodthirstParser:
    """Parses Bloodthirst keyword ability (replacement effect)"""
    
    keyword_name = "bloodthirst"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Bloodthirst pattern"""
        lower = reminder_text.lower()
        return "opponent was dealt damage" in lower and "enters the battlefield" in lower and "+1/+1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Bloodthirst reminder text into ReplacementEffect"""
        logger.debug(f"[BloodthirstParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "opponent was dealt damage" not in lower or "enters the battlefield" not in lower:
            return []
        
        m = BLOODTHIRST_RE.search(reminder_text)
        if not m:
            logger.debug(f"[BloodthirstParser] No bloodthirst value found in reminder text")
            return []
        
        bloodthirst_value = m.group(1)
        
        if bloodthirst_value.upper() == "X":
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={"counter_type": "+1/+1", "amount": "damage_dealt_to_opponents_this_turn"},
                zones=["battlefield"],
                condition="opponent_was_dealt_damage_this_turn"
            )
        else:
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={"counter_type": "+1/+1", "amount": int(bloodthirst_value)},
                zones=["battlefield"],
                condition="opponent_was_dealt_damage_this_turn"
            )
        
        logger.debug(f"[BloodthirstParser] Created ReplacementEffect for Bloodthirst {bloodthirst_value}")
        
        return [replacement_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Bloodthirst keyword without reminder text (e.g., 'Bloodthirst 1')"""
        logger.debug(f"[BloodthirstParser] Parsing keyword only: {keyword_text}")
        
        m = BLOODTHIRST_RE.search(keyword_text)
        if not m:
            logger.debug(f"[BloodthirstParser] No bloodthirst value found in keyword text")
            return []
        
        bloodthirst_value = m.group(1)
        
        if bloodthirst_value.upper() == "X":
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={"counter_type": "+1/+1", "amount": "damage_dealt_to_opponents_this_turn"},
                zones=["battlefield"],
                condition="opponent_was_dealt_damage_this_turn"
            )
        else:
            replacement_effect = ReplacementEffect(
                kind="enters_with_counters",
                event="enters_battlefield",
                subject=Subject(scope="self"),
                value={"counter_type": "+1/+1", "amount": int(bloodthirst_value)},
                zones=["battlefield"],
                condition="opponent_was_dealt_damage_this_turn"
            )
        
        logger.debug(f"[BloodthirstParser] Created ReplacementEffect for Bloodthirst {bloodthirst_value}")
        
        return [replacement_effect]

