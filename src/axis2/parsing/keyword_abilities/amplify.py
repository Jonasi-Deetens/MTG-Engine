# axis2/parsing/keyword_abilities/amplify.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

AMPLIFY_RE = re.compile(
    r"amplify\s+(\d+)",
    re.IGNORECASE
)


class AmplifyParser:
    """Parses Amplify keyword ability (replacement effect)"""
    
    keyword_name = "amplify"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Amplify pattern"""
        lower = reminder_text.lower()
        return "reveal" in lower and "enters" in lower and "+1/+1 counter" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Amplify reminder text into ReplacementEffect"""
        logger.debug(f"[AmplifyParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "reveal" not in lower or "enters" not in lower or "+1/+1 counter" not in lower:
            return []
        
        m = AMPLIFY_RE.search(reminder_text)
        if not m:
            logger.debug(f"[AmplifyParser] No amplify value found in reminder text")
            return []
        
        amplify_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "+1/+1",
                "amount": amplify_value,
                "condition": "reveal_matching_creature_cards_from_hand"
            },
            zones=["battlefield"]
        )
        
        logger.debug(f"[AmplifyParser] Created ReplacementEffect for Amplify {amplify_value}")
        
        return [replacement_effect]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Amplify keyword without reminder text (e.g., 'Amplify 1')"""
        logger.debug(f"[AmplifyParser] Parsing keyword only: {keyword_text}")
        
        m = AMPLIFY_RE.search(keyword_text)
        if not m:
            logger.debug(f"[AmplifyParser] No amplify value found in keyword text")
            return []
        
        amplify_value = int(m.group(1))
        
        replacement_effect = ReplacementEffect(
            kind="enters_with_counters",
            event="enters_battlefield",
            subject=Subject(scope="self"),
            value={
                "counter_type": "+1/+1",
                "amount": amplify_value,
                "condition": "reveal_matching_creature_cards_from_hand"
            },
            zones=["battlefield"]
        )
        
        logger.debug(f"[AmplifyParser] Created ReplacementEffect for Amplify {amplify_value}")
        
        return [replacement_effect]

