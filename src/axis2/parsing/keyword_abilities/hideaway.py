# axis2/parsing/keyword_abilities/hideaway.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, LookAndPickEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

HIDEAWAY_RE = re.compile(
    r"hideaway\s+(\d+)",
    re.IGNORECASE
)


class HideawayParser:
    """Parses Hideaway keyword ability (triggered ability)"""
    
    keyword_name = "hideaway"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Hideaway pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and "look at" in lower and "top" in lower and "exile" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Hideaway reminder text into TriggeredAbility"""
        logger.debug(f"[HideawayParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower or "look at" not in lower or "exile" not in lower:
            return []
        
        m = HIDEAWAY_RE.search(reminder_text)
        if not m:
            logger.debug(f"[HideawayParser] No hideaway value found in reminder text")
            return []
        
        hideaway_value = int(m.group(1))
        
        look_and_pick_effect = LookAndPickEffect(
            look_at=hideaway_value,
            source_zone="library",
            reveal_up_to=1,
            reveal_types=None,
            put_revealed_into="exile",
            put_rest_into="bottom",
            rest_order="random",
            optional=False
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this permanent enters the battlefield, look at the top {hideaway_value} cards of your library. Exile one of them face down and put the rest on the bottom of your library in a random order.",
            effects=[look_and_pick_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[HideawayParser] Created TriggeredAbility for Hideaway {hideaway_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Hideaway keyword without reminder text (e.g., 'Hideaway 4')"""
        logger.debug(f"[HideawayParser] Parsing keyword only: {keyword_text}")
        
        m = HIDEAWAY_RE.search(keyword_text)
        if not m:
            logger.debug(f"[HideawayParser] No hideaway value found in keyword text")
            return []
        
        hideaway_value = int(m.group(1))
        
        look_and_pick_effect = LookAndPickEffect(
            look_at=hideaway_value,
            source_zone="library",
            reveal_up_to=1,
            reveal_types=None,
            put_revealed_into="exile",
            put_rest_into="bottom",
            rest_order="random",
            optional=False
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this permanent enters the battlefield, look at the top {hideaway_value} cards of your library. Exile one of them face down and put the rest on the bottom of your library in a random order.",
            effects=[look_and_pick_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[HideawayParser] Created TriggeredAbility for Hideaway {hideaway_value}")
        
        return [triggered_ability]

