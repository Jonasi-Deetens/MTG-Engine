# axis2/parsing/keyword_abilities/afterlife.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, DiesEvent, CreateTokenEffect, ParseContext, Effect

logger = logging.getLogger(__name__)

AFTERLIFE_RE = re.compile(
    r"afterlife\s+(\d+)",
    re.IGNORECASE
)


class AfterlifeParser:
    """Parses Afterlife keyword ability (triggered ability)"""
    
    keyword_name = "afterlife"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Afterlife pattern"""
        lower = reminder_text.lower()
        return "dies" in lower and "spirit" in lower and "token" in lower and "flying" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Afterlife reminder text into TriggeredAbility"""
        logger.debug(f"[AfterlifeParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "dies" not in lower or "spirit" not in lower or "token" not in lower:
            return []
        
        m = AFTERLIFE_RE.search(reminder_text)
        if not m:
            logger.debug(f"[AfterlifeParser] No afterlife value found in reminder text")
            return []
        
        afterlife_value = int(m.group(1))
        
        create_token_effect = CreateTokenEffect(
            amount=afterlife_value,
            token={
                "name": "Spirit",
                "power": 1,
                "toughness": 1,
                "colors": ["white", "black"],
                "types": ["creature"],
                "subtypes": ["Spirit"],
                "abilities": ["flying"]
            },
            controller="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this permanent is put into a graveyard from the battlefield, create {afterlife_value} 1/1 white and black Spirit creature tokens with flying.",
            effects=[create_token_effect],
            event=DiesEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[AfterlifeParser] Created TriggeredAbility for Afterlife {afterlife_value}")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Afterlife keyword without reminder text (e.g., 'Afterlife 1')"""
        logger.debug(f"[AfterlifeParser] Parsing keyword only: {keyword_text}")
        
        m = AFTERLIFE_RE.search(keyword_text)
        if not m:
            logger.debug(f"[AfterlifeParser] No afterlife value found in keyword text")
            return []
        
        afterlife_value = int(m.group(1))
        
        create_token_effect = CreateTokenEffect(
            amount=afterlife_value,
            token={
                "name": "Spirit",
                "power": 1,
                "toughness": 1,
                "colors": ["white", "black"],
                "types": ["creature"],
                "subtypes": ["Spirit"],
                "abilities": ["flying"]
            },
            controller="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text=f"When this permanent is put into a graveyard from the battlefield, create {afterlife_value} 1/1 white and black Spirit creature tokens with flying.",
            effects=[create_token_effect],
            event=DiesEvent(subject="self"),
            targeting=None,
            trigger_filter=None
        )
        
        logger.debug(f"[AfterlifeParser] Created TriggeredAbility for Afterlife {afterlife_value}")
        
        return [triggered_ability]

