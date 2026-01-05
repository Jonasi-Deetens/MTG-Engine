# axis2/parsing/keyword_abilities/fabricate.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, PutCounterEffect, CreateTokenEffect, Subject, ParseContext, Effect

logger = logging.getLogger(__name__)

FABRICATE_RE = re.compile(
    r"fabricate\s+(\d+)",
    re.IGNORECASE
)


class FabricateParser:
    """Parses Fabricate keyword ability (triggered ability)"""
    
    keyword_name = "fabricate"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Fabricate pattern"""
        lower = reminder_text.lower()
        return "enters" in lower and ("+1/+1 counter" in lower or "servo" in lower) and ("or" in lower or "if you don't" in lower)
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Fabricate reminder text into TriggeredAbility"""
        logger.debug(f"[FabricateParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "enters" not in lower:
            return []
        
        m = FABRICATE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[FabricateParser] No fabricate value found in reminder text")
            return []
        
        fabricate_value = int(m.group(1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=fabricate_value,
            subject=Subject(scope="self")
        )
        
        create_token_effect = CreateTokenEffect(
            amount=fabricate_value,
            token={
                "name": "Servo",
                "power": 1,
                "toughness": 1,
                "colors": [],
                "types": ["artifact", "creature"],
                "subtypes": ["Servo"]
            },
            controller="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this permanent enters the battlefield, you may put {fabricate_value} +1/+1 counters on it. If you don't, create {fabricate_value} 1/1 colorless Servo artifact creature tokens.",
            effects=[put_counter_effect, create_token_effect],  # Choice is handled by Axis3
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[FabricateParser] Created TriggeredAbility for Fabricate {fabricate_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Fabricate keyword without reminder text (e.g., 'Fabricate 1')"""
        logger.debug(f"[FabricateParser] Parsing keyword only: {keyword_text}")
        
        m = FABRICATE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[FabricateParser] No fabricate value found in keyword text")
            return []
        
        fabricate_value = int(m.group(1))
        
        put_counter_effect = PutCounterEffect(
            counter_type="+1/+1",
            amount=fabricate_value,
            subject=Subject(scope="self")
        )
        
        create_token_effect = CreateTokenEffect(
            amount=fabricate_value,
            token={
                "name": "Servo",
                "power": 1,
                "toughness": 1,
                "colors": [],
                "types": ["artifact", "creature"],
                "subtypes": ["Servo"]
            },
            controller="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this permanent enters the battlefield, you may put {fabricate_value} +1/+1 counters on it. If you don't, create {fabricate_value} 1/1 colorless Servo artifact creature tokens.",
            effects=[put_counter_effect, create_token_effect],  # Choice is handled by Axis3
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[FabricateParser] Created TriggeredAbility for Fabricate {fabricate_value}")
        
        return [triggered_ability]

