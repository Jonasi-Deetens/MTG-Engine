# axis2/parsing/keyword_abilities/living_weapon.py

from typing import List
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, CreateTokenEffect, ChangeZoneEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)


class LivingWeaponParser:
    """Parses Living Weapon keyword ability (triggered ability)"""
    
    keyword_name = "living weapon"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Living Weapon pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and "germ" in lower and "token" in lower and "attach" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Living Weapon reminder text into TriggeredAbility"""
        logger.debug(f"[LivingWeaponParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower or "germ" not in lower or "token" not in lower:
            return []
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "Phyrexian Germ",
                "power": 0,
                "toughness": 0,
                "colors": ["black"],
                "types": ["creature"],
                "subtypes": ["Phyrexian", "Germ"]
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
            condition_text="When this Equipment enters the battlefield, create a 0/0 black Phyrexian Germ creature token, then attach this Equipment to it.",
            effects=[create_token_effect, attach_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[LivingWeaponParser] Created TriggeredAbility for Living Weapon")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Living Weapon keyword without reminder text"""
        logger.debug(f"[LivingWeaponParser] Parsing keyword only: {keyword_text}")
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "Phyrexian Germ",
                "power": 0,
                "toughness": 0,
                "colors": ["black"],
                "types": ["creature"],
                "subtypes": ["Phyrexian", "Germ"]
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
            condition_text="When this Equipment enters the battlefield, create a 0/0 black Phyrexian Germ creature token, then attach this Equipment to it.",
            effects=[create_token_effect, attach_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[LivingWeaponParser] Created TriggeredAbility for Living Weapon")
        
        return [triggered_ability]

