# axis2/parsing/keyword_abilities/squad.py

from typing import List
import re
import logging
from .base import KeywordAbilityParser
from axis2.schema import TriggeredAbility, EntersBattlefieldEvent, CreateTokenEffect, ParseContext, Effect

logger = logging.getLogger(__name__)

SQUAD_RE = re.compile(
    r"squad\s+(.+)",
    re.IGNORECASE
)


class SquadParser:
    """Parses Squad keyword ability (spell modifier + triggered ability)"""
    
    keyword_name = "squad"
    priority = 50
    
    def can_parse_reminder(self, reminder_text: str) -> bool:
        """Check if reminder text contains Squad pattern"""
        lower = reminder_text.lower()
        return "cast this spell" in lower and "squad cost" in lower and "any number of times" in lower and "create" in lower and "token" in lower
    
    def parse_reminder(self, reminder_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Squad reminder text into TriggeredAbility"""
        logger.debug(f"[SquadParser] Parsing reminder text: {reminder_text[:100]}")
        
        lower = reminder_text.lower()
        if "cast this spell" not in lower or "squad cost" not in lower or "create" not in lower or "token" not in lower:
            return []
        
        m = SQUAD_RE.search(reminder_text)
        if not m:
            logger.debug(f"[SquadParser] No squad cost found in reminder text")
            return []
        
        cost_text = m.group(1).strip()
        
        create_token_effect = CreateTokenEffect(
            amount="number_of_times_squad_cost_was_paid",
            token={
                "name": "copy_of_self",
                "is_copy": True
            },
            controller="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this creature enters, if its squad cost was paid, create a token that's a copy of it for each time its squad cost was paid.",
            effects=[create_token_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="squad_cost_was_paid"
        )
        
        logger.debug(f"[SquadParser] Created TriggeredAbility for Squad")
        
        return [triggered_ability]
    
    def parse_keyword_only(self, keyword_text: str, ctx: ParseContext) -> List[Effect]:
        """Parse Squad keyword without reminder text (e.g., 'Squad {2}')"""
        logger.debug(f"[SquadParser] Parsing keyword only: {keyword_text}")
        
        m = SQUAD_RE.search(keyword_text)
        if not m:
            logger.debug(f"[SquadParser] No squad cost found in keyword text")
            return []
        
        cost_text = m.group(1).strip()
        
        create_token_effect = CreateTokenEffect(
            amount="number_of_times_squad_cost_was_paid",
            token={
                "name": "copy_of_self",
                "is_copy": True
            },
            controller="you"
        )
        
        triggered_ability = TriggeredAbility(
            condition_text="When this creature enters, if its squad cost was paid, create a token that's a copy of it for each time its squad cost was paid.",
            effects=[create_token_effect],
            event=EntersBattlefieldEvent(subject="self"),
            targeting=None,
            trigger_filter=None,
            condition="squad_cost_was_paid"
        )
        
        logger.debug(f"[SquadParser] Created TriggeredAbility for Squad")
        
        return [triggered_ability]

