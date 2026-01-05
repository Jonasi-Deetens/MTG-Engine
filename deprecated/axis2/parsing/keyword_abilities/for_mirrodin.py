# axis2/parsing/keyword_abilities/for_mirrodin.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, CreateTokenEffect, ChangeZoneEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class ForMirrodinParser:
    """Parses For Mirrodin! keyword ability (triggered ability)"""
    
    keyword_name = "for mirrodin!"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains For Mirrodin! pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and "create" in lower and "rebel" in lower and "token" in lower and "attach" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse For Mirrodin! reminder text into TriggeredAbility"""
        logger.debug(f"[ForMirrodinParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower or "create" not in lower or "rebel" not in lower or "attach" not in lower:
            return []
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "Rebel",
                "power": 2,
                "toughness": 2,
                "colors": ["red"],
                "types": ["creature"],
                "subtypes": ["Rebel"]
            },
            controller="you"
        )
        
        attach_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone=None,
            to_zone="battlefield",
            attach_to="created_token"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this Equipment enters, create a 2/2 red Rebel creature token, then attach this Equipment to it.",
            effects=[create_token_effect, attach_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ForMirrodinParser] Created TriggeredAbility for For Mirrodin!")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse For Mirrodin! keyword without reminder text"""
        logger.debug(f"[ForMirrodinParser] Parsing keyword only: {keyword_text}")
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "Rebel",
                "power": 2,
                "toughness": 2,
                "colors": ["red"],
                "types": ["creature"],
                "subtypes": ["Rebel"]
            },
            controller="you"
        )
        
        attach_effect = ChangeZoneEffect(
            subject=Subject(scope="self"),
            from_zone=None,
            to_zone="battlefield",
            attach_to="created_token"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this Equipment enters, create a 2/2 red Rebel creature token, then attach this Equipment to it.",
            effects=[create_token_effect, attach_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[ForMirrodinParser] Created TriggeredAbility for For Mirrodin!")
        
        return [triggered_ability]

