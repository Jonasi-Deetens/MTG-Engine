# axis2/parsing/keyword_abilities/myriad.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, AttacksEvent, CreateTokenEffect, ChangeZoneEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class MyriadParser:
    """Parses Myriad keyword ability (triggered ability)"""
    
    keyword_name = "myriad"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Myriad pattern"""
        lower = reminder_text.lower()
        return "attacks" in lower and "token" in lower and "copy" in lower and "exile" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Myriad reminder text into TriggeredAbility"""
        logger.debug(f"[MyriadParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "attacks" not in lower or "token" not in lower or "copy" not in lower:
            return []
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "copy_of_self",
                "is_copy": True,
                "tapped": True,
                "attacking": True
            },
            controller="you"
        )
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="created_tokens"),
            from_zone="battlefield",
            to_zone="exile",
            owner="owner"
        )
        
        end_combat_trigger = TriggeredAbility(
            condition_text="At end of combat, exile the tokens created by myriad.",
            effects=[exile_effect],
            event="end_combat",
            targeting=None,
            trigger_filter=None
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks, for each opponent other than defending player, you may create a token that's a copy of this creature that's tapped and attacking that player or a planeswalker they control. If one or more tokens are created this way, exile the tokens at end of combat.",
            effects=[create_token_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[MyriadParser] Created TriggeredAbility and delayed TriggeredAbility for Myriad")
        
        return [triggered_ability, end_combat_trigger]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Myriad keyword without reminder text"""
        logger.debug(f"[MyriadParser] Parsing keyword only: {keyword_text}")
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "copy_of_self",
                "is_copy": True,
                "tapped": True,
                "attacking": True
            },
            controller="you"
        )
        
        exile_effect = ChangeZoneEffect(
            subject=Subject(scope="created_tokens"),
            from_zone="battlefield",
            to_zone="exile",
            owner="owner"
        )
        
        end_combat_trigger = TriggeredAbility(
            condition_text="At end of combat, exile the tokens created by myriad.",
            effects=[exile_effect],
            event="end_combat",
            targeting=None,
            trigger_filter=None
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="Whenever this creature attacks, for each opponent other than defending player, you may create a token that's a copy of this creature that's tapped and attacking that player or a planeswalker they control. If one or more tokens are created this way, exile the tokens at end of combat.",
            effects=[create_token_effect],
            event=AttacksEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[MyriadParser] Created TriggeredAbility and delayed TriggeredAbility for Myriad")
        
        return [triggered_ability, end_combat_trigger]

