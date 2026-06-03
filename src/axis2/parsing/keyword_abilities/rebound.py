# axis2/parsing/keyword_abilities/rebound.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import ReplacementEffect, TriggeredAbility, ChangeZoneEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class ReboundParser:
    """Parses Rebound keyword ability (replacement effect + triggered ability)"""
    
    keyword_name = "rebound"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Rebound pattern"""
        lower = reminder_text.lower()
        return "cast this spell from your hand" in lower and "exile it" in lower and "next upkeep" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Rebound reminder text into ReplacementEffect and TriggeredAbility"""
        logger.debug(f"[ReboundParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell from your hand" not in lower or "exile it" not in lower:
            return []
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="stack",
            to_zone="exile",
            owner="owner"
        )
        
        replacement_effect = ReplacementEffect(
            kind="zone_change",
            event="would_go_to_graveyard_from_stack",
            subject=Subject(scope="self"),
            instead_effects=[exile_effect],
            condition="cast_from_hand",
            zones=["stack"]
        )
        
        cast_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="exile",
            to_zone="stack",
            owner="owner"
        )
        
        upkeep_trigger = TriggeredAbility(
            condition_text="At the beginning of your next upkeep, you may cast this card from exile without paying its mana cost.",
            effects=[cast_effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ReboundParser] Created ReplacementEffect and TriggeredAbility for Rebound")
        
        return [replacement_effect, upkeep_trigger]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Rebound keyword without reminder text"""
        logger.debug(f"[ReboundParser] Parsing keyword only: {keyword_text}")
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="stack",
            to_zone="exile",
            owner="owner"
        )
        
        replacement_effect = ReplacementEffect(
            kind="zone_change",
            event="would_go_to_graveyard_from_stack",
            subject=Subject(scope="self"),
            instead_effects=[exile_effect],
            condition="cast_from_hand",
            zones=["stack"]
        )
        
        cast_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone="exile",
            to_zone="stack",
            owner="owner"
        )
        
        upkeep_trigger = TriggeredAbility(
            condition_text="At the beginning of your next upkeep, you may cast this card from exile without paying its mana cost.",
            effects=[cast_effect],
            event="upkeep",
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ReboundParser] Created ReplacementEffect and TriggeredAbility for Rebound")
        
        return [replacement_effect, upkeep_trigger]

