# axis2/parsing/keyword_abilities/offspring.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, CreateTokenEffect, ParseContext, Effect

logger = logging.getLogger(__name__)

OFFSPRING_RE = re.compile(
    r"offspring\s+(\{.+?\})",
    re.IGNORECASE
)


class OffspringParser:
    """Parses Offspring keyword ability (spell modifier + triggered ability)"""
    
    keyword_name = "offspring"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Offspring pattern"""
        lower = reminder_text.lower()
        return "pay an additional" in lower and "cast this spell" in lower and "enters" in lower and "create a token" in lower and "copy" in lower and "1/1" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Offspring reminder text into TriggeredAbility"""
        logger.debug(f"[OffspringParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "pay an additional" not in lower or "enters" not in lower or "create a token" not in lower or "1/1" not in lower:
            return []
        
        m = OFFSPRING_RE.search(reminder_text)
        if not m:
            logger.debug(f"[OffspringParser] No offspring cost found in reminder text")
            return []
        
        offspring_cost = m.group(1).strip()
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "copy_of_self",
                "is_copy": True,
                "power": 1,
                "toughness": 1
            },
            controller="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this permanent enters, if its offspring cost was paid, create a token that's a copy of it, except it's 1/1.",
            effects=[create_token_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="offspring_cost_was_paid"
        )
        
        logger.debug(f"[OffspringParser] Created TriggeredAbility for Offspring")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Offspring keyword without reminder text (e.g., 'Offspring {4}')"""
        logger.debug(f"[OffspringParser] Parsing keyword only: {keyword_text}")
        
        m = OFFSPRING_RE.search(keyword_text)
        if not m:
            logger.debug(f"[OffspringParser] No offspring cost found in keyword text")
            return []
        
        offspring_cost = m.group(1).strip()
        
        create_token_effect = CreateTokenEffect(
            amount=1,
            token={
                "name": "copy_of_self",
                "is_copy": True,
                "power": 1,
                "toughness": 1
            },
            controller="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this permanent enters, if its offspring cost was paid, create a token that's a copy of it, except it's 1/1.",
            effects=[create_token_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="offspring_cost_was_paid"
        )
        
        logger.debug(f"[OffspringParser] Created TriggeredAbility for Offspring")
        
        return [triggered_ability]

