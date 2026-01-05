# axis2/parsing/keyword_abilities/ingest.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DealsDamageEvent, ChangeZoneEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class IngestParser:
    """Parses Ingest keyword ability (triggered ability)"""
    
    keyword_name = "ingest"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Ingest pattern"""
        lower = reminder_text.lower()
        return "deals combat damage to a player" in lower and "exiles the top card" in lower and "library" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ingest reminder text into TriggeredAbility"""
        logger.debug(f"[IngestParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "deals combat damage to a player" not in lower or "exiles the top card" not in lower:
            return []
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="top_card", controller="damaged_player", filters={"zone": "library"}),
            from_zone="library",
            to_zone="exile",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature deals combat damage to a player, that player exiles the top card of their library.",
            effects=[exile_effect],
            event=DealsDamageEvent(subject="self", damage_type="combat", target="player"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[IngestParser] Created TriggeredAbility for Ingest")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Ingest keyword without reminder text"""
        logger.debug(f"[IngestParser] Parsing keyword only: {keyword_text}")
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="top_card", controller="damaged_player", filters={"zone": "library"}),
            from_zone="library",
            to_zone="exile",
            owner="owner"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature deals combat damage to a player, that player exiles the top card of their library.",
            effects=[exile_effect],
            event=DealsDamageEvent(subject="self", damage_type="combat", target="player"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[IngestParser] Created TriggeredAbility for Ingest")
        
        return [triggered_ability]

